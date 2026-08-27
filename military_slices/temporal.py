from __future__ import annotations

import hashlib
import json
import re
import time
from collections import OrderedDict
from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Literal

from military_slices.models import (
    Authority,
    CanonicalState,
    Decision,
    Fact,
    FeedbackEvent,
    FreshnessClass,
    FreshnessStatus,
    ImpactItem,
    ReceiptPatch,
    SliceName,
    utc_now,
)
from military_slices.path_runtime import anchor_domain

VOLATILE_TTL = timedelta(days=14)
EXTERNAL_EXPIRING_TTL = timedelta(days=1)
FRESHNESS_TTLS = {
    FreshnessClass.VOLATILE: VOLATILE_TTL,
    FreshnessClass.EXTERNAL_EXPIRING: EXTERNAL_EXPIRING_TTL,
}

# These are material invalidation relationships, not a list of possibly related topics.
DEPENDENCIES: dict[str, tuple[str, ...]] = {
    "career_target": ("relocation_willingness", "compensation_floor"),
    "separation_date": (
        "application_timing",
        "education_timing",
        "relocation_timing",
        "resume_readiness_deadline",
    ),
    "relocation_willingness": ("career_search_boundary",),
}

FIELD_SLICES: dict[str, SliceName] = {
    "career_target": SliceName.CAREER,
    "compensation_floor": SliceName.CAREER,
    "work_preference": SliceName.CAREER,
    "application_timing": SliceName.CAREER,
    "career_search_boundary": SliceName.CAREER,
    "education_preference": SliceName.EDUCATION,
    "education_timing": SliceName.EDUCATION,
    "relocation_willingness": SliceName.LOCATION,
    "geographic_preference": SliceName.LOCATION,
    "relocation_timing": SliceName.LOCATION,
    "resume_readiness_deadline": SliceName.RESUME,
    "skillbridge_policy": SliceName.CAREER,
    "program_eligibility": SliceName.EDUCATION,
}


@dataclass(frozen=True)
class ExternalFactUpdate:
    value: str
    statement: str
    evidence_id: str


@dataclass(frozen=True)
class ConsequentialImpactProjection:
    """One read-only interruption that can force model-context re-evaluation.

    This is an ephemeral projection over existing governed state. It is not a
    persisted Gate, Impact, fact, or authorization.
    """

    source: Literal["conflicted_gate", "blocking_impact", "authoritative_interrupt"]
    fact_id: str
    field_key: str
    statement: str
    authority: Authority
    status: FreshnessStatus
    affected_slices: tuple[SliceName, ...]
    impact_id: str | None = None
    gate_id: str | None = None
    question: str | None = None


@dataclass(frozen=True)
class ConsequentialImpactIndex:
    """Version-scoped derived lookup for interruption candidates.

    Building the index is linear in governed facts and belongs at state-write or
    reconstitution time. Reads are bounded by the material candidate surface.
    The index is ephemeral and carries no authority or canonical truth.
    """

    profile_id: str
    source_state_version: int
    authoritative_fact_ids: tuple[str, ...]
    build_ms: float


ExternalRefresher = Callable[[Fact], ExternalFactUpdate | None]

_AUTHORITATIVE_INTERRUPT_TERMS = (
    "restriction",
    "conflict",
    "prohibit",
    "forbid",
    "not permitted",
    "not allowed",
)

_CONSEQUENTIAL_INDEX_CACHE: OrderedDict[tuple[str, int], ConsequentialImpactIndex] = OrderedDict()
_CONSEQUENTIAL_INDEX_CACHE_LIMIT = 512


def build_consequential_impact_index(state: CanonicalState) -> ConsequentialImpactIndex:
    """Build and cache a read-only candidate index for one canonical version."""

    started = time.perf_counter()
    resolved_fields = {
        decision.gate_id.removeprefix("revalidate:")
        for decision in state.decisions
        if decision.gate_id.startswith("revalidate:")
    }
    ids = tuple(
        fact.id
        for fact in sorted(state.facts, key=lambda item: item.id)
        if fact.field_key not in resolved_fields
        and fact.authority == Authority.AUTHORITATIVE_SOURCE
        and fact.status == FreshnessStatus.VALID
        and bool(fact.affected_slices)
        and any(
            term in f"{fact.field_key} {fact.statement}".casefold()
            for term in _AUTHORITATIVE_INTERRUPT_TERMS
        )
    )
    index = ConsequentialImpactIndex(
        profile_id=state.profile_id,
        source_state_version=state.version,
        authoritative_fact_ids=ids,
        build_ms=(time.perf_counter() - started) * 1000,
    )
    key = (state.profile_id, state.version)
    _CONSEQUENTIAL_INDEX_CACHE[key] = index
    _CONSEQUENTIAL_INDEX_CACHE.move_to_end(key)
    while len(_CONSEQUENTIAL_INDEX_CACHE) > _CONSEQUENTIAL_INDEX_CACHE_LIMIT:
        _CONSEQUENTIAL_INDEX_CACHE.popitem(last=False)
    return index


def consequential_impact_index(state: CanonicalState) -> ConsequentialImpactIndex:
    """Return the derived index for this immutable canonical version."""

    key = (state.profile_id, state.version)
    cached = _CONSEQUENTIAL_INDEX_CACHE.get(key)
    if cached is not None:
        _CONSEQUENTIAL_INDEX_CACHE.move_to_end(key)
        return cached
    return build_consequential_impact_index(state)


def _stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("\x1f".join(parts).encode()).hexdigest()[:16]
    return f"{prefix}_{digest}"


def infer_fact_metadata(
    statement: str,
    affected_slices: list[SliceName],
    kind: str = "fact",
) -> tuple[str, FreshnessClass]:
    text = statement.casefold()
    if any(term in text for term in ("skillbridge", "current policy", "current eligibility", "market data")):
        key = "skillbridge_policy" if "skillbridge" in text or "policy" in text else "program_eligibility"
        return key, FreshnessClass.EXTERNAL_EXPIRING
    if any(term in text for term in ("interview", "active application", "applied to", "current opportunity")):
        return "active_application", FreshnessClass.VOLATILE
    if any(term in text for term in ("deadline", "available until", "temporary availability")):
        if SliceName.RESUME in affected_slices:
            return "resume_readiness_deadline", FreshnessClass.VOLATILE
        return "near_term_deadline", FreshnessClass.VOLATILE
    if any(term in text for term in ("relocat", "remain local", "stay local", "stay in", "willing to move")):
        return "relocation_willingness", FreshnessClass.SLOW
    if any(term in text for term in ("salary", "compensation", "pay floor", "minimum pay")):
        return "compensation_floor", FreshnessClass.SLOW
    if re.search(r"\b(career target|target role|job target|change (?:my )?(?:career|role))\b", text):
        return "career_target", FreshnessClass.SLOW
    if SliceName.EDUCATION in affected_slices and any(
        term in text for term in ("want", "prefer", "plan", "full-time school", "training path")
    ):
        return "education_preference", FreshnessClass.SLOW
    if SliceName.LOCATION in affected_slices and any(
        term in text for term in ("commute", "remote", "city", "state", "location", "near family")
    ):
        return "geographic_preference", FreshnessClass.SLOW
    if SliceName.CAREER in affected_slices and (
        kind in ("preference", "goal")
        or any(term in text for term in ("shift work", "schedule", "travel", "work environment"))
    ):
        return "work_preference", FreshnessClass.SLOW
    if any(term in text for term in ("completed", "earned", "graduated", "historical", "past ")):
        return "historical_achievement", FreshnessClass.STABLE
    return "general_context", FreshnessClass.STABLE


def normalize_fact_metadata(state: CanonicalState) -> CanonicalState:
    """Add deterministic metadata to legacy facts without creating a canonical write."""
    for fact in state.facts:
        if fact.field_key != "general_context":
            continue
        kind = (
            "preference"
            if any(term in fact.statement.casefold() for term in ("prefer", "won't", "will not"))
            else "fact"
        )
        key, freshness = infer_fact_metadata(fact.statement, fact.affected_slices, kind)
        fact.field_key = key
        fact.freshness_class = freshness
    if state.career_target is None:
        accepted = next((item.title for item in state.career_hypotheses if item.status == "accepted"), None)
        state.career_target = accepted
    return state


def fact_is_usable(fact: Fact) -> bool:
    return fact.status == FreshnessStatus.VALID


def _field_values(state: CanonicalState, key: str) -> tuple[str, ...]:
    return tuple(sorted(fact.value for fact in state.facts if fact.field_key == key))


def changed_fields(before: CanonicalState, after: CanonicalState) -> set[str]:
    changed: set[str] = set()
    if before.transition_date != after.transition_date:
        changed.add("separation_date")
    if before.career_target != after.career_target:
        changed.add("career_target")
    keys = {fact.field_key for fact in before.facts + after.facts}
    changed.update(key for key in keys if _field_values(before, key) != _field_values(after, key))
    if before.human_anchor and before.human_anchor != after.human_anchor:
        changed.add("human_anchor")
    return changed


def _dependencies_for(source: str, before: CanonicalState, after: CanonicalState) -> tuple[str, ...]:
    if source != "human_anchor":
        return DEPENDENCIES.get(source, ())
    if not before.human_anchor or before.human_anchor == after.human_anchor:
        return ()
    domain = anchor_domain(after.human_anchor)
    if domain is None:
        return ()
    return {
        "employment": ("career_target", "relocation_willingness"),
        "education": ("education_preference",),
        "location": ("relocation_willingness",),
        "resume": (),
        "undecided": (),
    }.get(domain, ())


def _material_slices(state: CanonicalState) -> set[SliceName]:
    domain = anchor_domain(state.human_anchor)
    if domain is None:
        material: set[SliceName] = set()
    else:
        material = {
            "employment": {SliceName.CAREER, SliceName.LOCATION, SliceName.RESUME},
            "education": {SliceName.EDUCATION},
            "location": {SliceName.LOCATION},
            "resume": {SliceName.RESUME, SliceName.CAREER},
            "undecided": set(SliceName),
        }.get(domain, set())
    for gate in state.gates:
        material.update(gate.affected_slices)
    for task in state.active_tasks:
        material.update(task.affected_slices)
    return material


def _append_patch(
    state: CanonicalState,
    path: str,
    value: str | None,
    reason: str,
    *,
    operation: Literal["replace", "remove"] = "replace",
) -> None:
    patch = ReceiptPatch(path=path, value=value, reason=reason, operation=operation)
    payload = json.dumps(patch.model_dump(mode="json"), separators=(",", ":"), sort_keys=True).encode()
    state.receipt_deltas.append(patch)
    state.receipt_deltas = state.receipt_deltas[-64:]
    state.telemetry.temporal_patch_bytes += len(payload)
    state.telemetry.temporal_patch_count += 1


def _impact_copy(source_field: str, fact: Fact) -> tuple[str, str, str, str, list[str]]:
    if fact.field_key == "relocation_willingness":
        return (
            "Your new career direction may affect your location plans."
            if source_field == "career_target"
            else "A recent decision may affect your location plans.",
            "Still planning to stay local?",
            "Yes, still staying local",
            "Update location",
            ["Stay local", "Open to relocating", "Only for the right role"],
        )
    labels = {
        "compensation_floor": "compensation needs",
        "application_timing": "job-search timing",
        "education_timing": "education timing",
        "relocation_timing": "moving timeline",
        "resume_readiness_deadline": "résumé timing",
    }
    label = labels.get(fact.field_key, "plan")
    return (
        f"A recent decision may affect your {label}.",
        f"Is your {label} still right?",
        "Yes, still correct",
        "Update",
        [],
    )


def _blocking(state: CanonicalState, field_key: str) -> bool:
    unresolved = [gate for gate in state.gates if gate.state.value not in ("YES", "NO")]
    primary = max(unresolved, key=lambda item: item.value_score, default=None)
    return bool(primary and field_key in primary.dependencies)


def _add_impact(state: CanonicalState, source_field: str, fact: Fact) -> None:
    if any(item.fact_id == fact.id for item in state.impacts):
        return
    affected_slice = FIELD_SLICES.get(
        fact.field_key,
        fact.affected_slices[0] if fact.affected_slices else SliceName.CAREER,
    )
    if affected_slice not in _material_slices(state):
        return
    message, question, confirm_label, update_label, options = _impact_copy(source_field, fact)
    state.impacts.append(
        ImpactItem(
            id=_stable_id("impact", state.profile_id, str(state.version), source_field, fact.id),
            source_field=source_field,
            dependent_field=fact.field_key,
            fact_id=fact.id,
            affected_slice=affected_slice,
            message=message,
            question=question,
            confirm_label=confirm_label,
            update_label=update_label,
            update_options=options,
            blocking=_blocking(state, fact.field_key),
        )
    )
    state.telemetry.temporal_human_prompts += 1


def _mark_stale(state: CanonicalState, fact: Fact, source_field: str) -> None:
    if fact.status == FreshnessStatus.STALE:
        _add_impact(state, source_field, fact)
        return
    fact.status = FreshnessStatus.STALE
    state.telemetry.temporal_fields_marked_stale += 1
    _append_patch(
        state,
        f"facts/{fact.id}/status",
        FreshnessStatus.STALE,
        f"{source_field} changed",
    )
    if fact.field_key == "relocation_willingness":
        state.conflicts = [
            item
            for item in state.conflicts
            if not any(term in item.casefold() for term in ("relocat", "location", "stay local"))
        ]
    _add_impact(state, source_field, fact)


def _refresh_external(state: CanonicalState, fact: Fact, refresher: ExternalRefresher | None) -> bool:
    if refresher is None or fact.authority != Authority.AUTHORITATIVE_SOURCE:
        return False
    update = refresher(deepcopy(fact))
    if update is None or not update.evidence_id:
        return False
    fact.value = update.value
    fact.statement = update.statement
    if update.evidence_id not in fact.evidence_ids:
        fact.evidence_ids.append(update.evidence_id)
    fact.status = FreshnessStatus.VALID
    fact.last_validated_at = utc_now()
    state.telemetry.temporal_fields_silently_refreshed += 1
    _append_patch(state, f"facts/{fact.id}/value", fact.value, "authoritative external refresh")
    _append_patch(state, f"facts/{fact.id}/status", FreshnessStatus.VALID, "authoritative external refresh")
    return True


def _expire_time_sensitive(
    state: CanonicalState,
    *,
    now: datetime,
    external_refresher: ExternalRefresher | None,
) -> None:
    for fact in state.facts:
        ttl = FRESHNESS_TTLS.get(fact.freshness_class)
        if ttl is None or fact.status == FreshnessStatus.STALE:
            continue
        validated = fact.last_validated_at.astimezone(UTC)
        if now - validated <= ttl:
            continue
        if fact.freshness_class == FreshnessClass.EXTERNAL_EXPIRING and _refresh_external(
            state, fact, external_refresher
        ):
            continue
        _mark_stale(state, fact, "time")
        if fact.freshness_class == FreshnessClass.EXTERNAL_EXPIRING:
            state.impacts = [item for item in state.impacts if item.fact_id != fact.id]


def propagate_temporal_changes(
    before: CanonicalState,
    after: CanonicalState,
    *,
    now: datetime | None = None,
    external_refresher: ExternalRefresher | None = None,
) -> CanonicalState:
    started = time.perf_counter()
    before = normalize_fact_metadata(deepcopy(before))
    state = normalize_fact_metadata(after)
    current_time = now or utc_now()
    _expire_time_sensitive(state, now=current_time, external_refresher=external_refresher)
    prior_fact_ids = {fact.id for fact in before.facts}
    for source_field in sorted(changed_fields(before, state)):
        dependencies = _dependencies_for(source_field, before, state)
        state.telemetry.temporal_dependencies_evaluated += len(dependencies)
        for dependent_field in dependencies:
            for fact in state.facts:
                if fact.field_key != dependent_field or fact.id not in prior_fact_ids:
                    continue
                if fact.freshness_class == FreshnessClass.STABLE:
                    continue
                if fact.authority == Authority.DETERMINISTIC_RULE:
                    fact.status = FreshnessStatus.VALID
                    fact.last_validated_at = current_time
                    state.telemetry.temporal_fields_silently_refreshed += 1
                    _append_patch(state, f"facts/{fact.id}/last_validated_at", current_time.isoformat(), source_field)
                    continue
                if fact.freshness_class == FreshnessClass.EXTERNAL_EXPIRING and _refresh_external(
                    state, fact, external_refresher
                ):
                    continue
                _mark_stale(state, fact, source_field)
    state.telemetry.temporal_latency_ms += int((time.perf_counter() - started) * 1000)
    return state


def evaluate_elapsed_freshness(
    state: CanonicalState,
    *,
    now: datetime | None = None,
    external_refresher: ExternalRefresher | None = None,
) -> CanonicalState:
    result = normalize_fact_metadata(deepcopy(state))
    _expire_time_sensitive(result, now=now or utc_now(), external_refresher=external_refresher)
    return result


def current_impact(state: CanonicalState) -> ImpactItem | None:
    return min(state.impacts, key=lambda item: (not item.blocking, item.created_at), default=None)


def consequential_impact_projection(
    state: CanonicalState,
    *,
    index: ConsequentialImpactIndex | None = None,
) -> ConsequentialImpactProjection | None:
    """Project the smallest material interruption without mutating governed state.

    Precedence is existing conflicted Gate evidence, an existing blocking Impact,
    then an unmaterialized authoritative blocker from any bounded Slice. The
    cross-Slice check is deliberate because an external restriction can change
    the current move even when its source Slice is not active. Ordinary evidence
    and non-blocking reminders remain Latent.
    """

    fact_index = {fact.id: fact for fact in state.facts}
    conflicted = sorted(
        (
            gate
            for gate in state.gates
            if gate.state.value == "CONFLICTED" and gate.required_evidence
        ),
        key=lambda gate: (-gate.value_score, gate.id),
    )
    for gate in conflicted:
        for fact_id in gate.required_evidence:
            fact = fact_index.get(fact_id)
            if fact is not None:
                return ConsequentialImpactProjection(
                    source="conflicted_gate",
                    fact_id=fact.id,
                    field_key=fact.field_key,
                    statement=fact.statement,
                    authority=fact.authority,
                    status=fact.status,
                    affected_slices=tuple(fact.affected_slices),
                    gate_id=gate.id,
                    question=gate.question,
                )

    blocking = sorted(
        (item for item in state.impacts if item.blocking),
        key=lambda item: (item.created_at, item.id),
    )
    for impact in blocking:
        fact = fact_index.get(impact.fact_id)
        if fact is not None:
            return ConsequentialImpactProjection(
                source="blocking_impact",
                fact_id=fact.id,
                field_key=fact.field_key,
                statement=fact.statement,
                authority=fact.authority,
                status=fact.status,
                affected_slices=tuple(fact.affected_slices),
                impact_id=impact.id,
                question=impact.question,
            )

    lookup = index or consequential_impact_index(state)
    for fact_id in lookup.authoritative_fact_ids:
        fact = fact_index.get(fact_id)
        if fact is not None:
            return ConsequentialImpactProjection(
                source="authoritative_interrupt",
                fact_id=fact.id,
                field_key=fact.field_key,
                statement=fact.statement,
                authority=fact.authority,
                status=fact.status,
                affected_slices=tuple(fact.affected_slices),
                question="Does this authoritative information change or block the current next move?",
            )
    return None


def _normalized_update(fact: Fact, value: str) -> tuple[str, str]:
    selected = value.strip()
    if fact.field_key != "relocation_willingness":
        return selected, selected
    mapping = {
        "stay local": ("NO", "I plan to stay local."),
        "open to relocating": ("YES", "I am open to relocating."),
        "only for the right role": ("CONDITIONAL", "I would relocate only for the right role."),
    }
    return mapping.get(selected.casefold(), (selected, selected))


def apply_revalidation_delta(
    current: CanonicalState,
    *,
    impact_id: str,
    action: str,
    value: str | None,
    idempotency_key: str,
) -> tuple[CanonicalState, bool]:
    if idempotency_key in current.processed_keys:
        return current, False
    impact = next((item for item in current.impacts if item.id == impact_id), None)
    if impact is None:
        return current, False
    state = deepcopy(current)
    impact = next(item for item in state.impacts if item.id == impact_id)
    fact = next((item for item in state.facts if item.id == impact.fact_id), None)
    if fact is None:
        raise ValueError("That plan detail is no longer available. Refresh to continue.")
    if action == "dismiss":
        if impact.blocking:
            raise ValueError("Confirm or update this detail before continuing.")
        state.impacts = [item for item in state.impacts if item.id != impact.id]
        _append_patch(
            state,
            f"impacts/{impact.id}",
            None,
            "human deferred non-blocking review",
            operation="remove",
        )
        state.processed_keys.append(idempotency_key)
        state.updated_at = utc_now()
        state.version += 1
        return state, True
    if action == "update" and not value:
        raise ValueError("Choose the updated value before continuing.")
    if action == "update":
        fact.value, fact.statement = _normalized_update(fact, value or "")
        state.telemetry.temporal_bounded_update_flows += 1
        headline = "Your updated choice is now part of the plan."
    else:
        state.telemetry.temporal_one_tap_confirmations += 1
        headline = "That part of your plan is still current."
    fact.status = FreshnessStatus.VALID
    fact.last_validated_at = utc_now()
    state.impacts = [item for item in state.impacts if item.fact_id != fact.id]
    _append_patch(state, f"facts/{fact.id}/status", FreshnessStatus.VALID, "human revalidation")
    _append_patch(
        state,
        f"facts/{fact.id}/last_validated_at",
        fact.last_validated_at.isoformat(),
        "human revalidation",
    )
    if action == "update":
        _append_patch(state, f"facts/{fact.id}/value", fact.value, "human update")
        state = propagate_temporal_changes(current, state)
    state.decisions.append(
        Decision(
            id=_stable_id("decision", state.profile_id, idempotency_key),
            gate_id=f"revalidate:{fact.field_key}",
            value=fact.statement,
            authority=Authority.HUMAN,
        )
    )
    state.feedback.append(
        FeedbackEvent(
            id=_stable_id("feedback", state.profile_id, idempotency_key),
            headline=headline,
            consequences=["Only the affected assumption was updated."],
        )
    )
    state.processed_keys.append(idempotency_key)
    state.updated_at = utc_now()
    state.version += 1
    return state, True
