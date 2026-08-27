"""Deterministic reuse of governed Probe-candidate rejection decisions.

This module adds no Canonical primitive.  It derives a read-only lookup from ordinary
Decision and LineageRecord structures and delegates every write to the existing human
mutation path.
"""

from __future__ import annotations

import hashlib
import json
import time
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Literal

from military_slices.governance import (
    AuthorityGovernor,
    GovernanceError,
    validate_mutation_commit,
)
from military_slices.models import (
    ActorProvenance,
    Authority,
    CanonicalState,
    Decision,
    Gate,
    LineageIntegrity,
    LineageRecord,
)

REJECTION_VALUE = "candidate_relationship_rejected"
REJECTION_MARKER = "state-bound-rejection:v1"

LookupStatus = Literal["SUPPRESSED", "INVALIDATED", "IDENTITY_MISS", "NO_PRIOR_REJECTION"]


@dataclass(frozen=True)
class RejectionIdentity:
    fact_ids: tuple[str, ...]
    effect_dimension: str
    gate_id: str
    gate_version: str
    evidence_lineage_hash: str
    scope_hash: str
    identity_hash: str


@dataclass(frozen=True)
class RejectionLookup:
    status: LookupStatus
    identity: RejectionIdentity
    decision_id: str | None
    invalidation_triggers: tuple[str, ...]
    lookup_ms: float

    @property
    def suppress(self) -> bool:
        return self.status == "SUPPRESSED"


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, separators=(",", ":"), sort_keys=True, default=str).encode()
    return hashlib.sha256(encoded).hexdigest()


def _gate(state: CanonicalState, gate_id: str) -> Gate:
    matches = [gate for gate in state.gates if gate.id == gate_id]
    if len(matches) != 1:
        raise GovernanceError(f"Expected exactly one governed Gate {gate_id!r}.")
    return matches[0]


def gate_contract_version(gate: Gate) -> str:
    """Hash the stable governed decision contract, not its Canonical cache binding."""

    payload = gate.model_dump(mode="json", exclude={"source_state_version", "updated_at", "state", "resolved_value"})
    return _canonical_hash(payload)


def evidence_lineage_hash(state: CanonicalState, fact_ids: tuple[str, ...]) -> str:
    """Hash governed source evidence and direct fact lineage only.

    Mutation/Decision lineage is intentionally excluded: recording a rejection must not
    change the evidence basis that the rejection was about.
    """

    facts_by_id = {fact.id: fact for fact in state.facts}
    missing = [fact_id for fact_id in fact_ids if fact_id not in facts_by_id]
    if missing:
        return _canonical_hash({"missing_fact_ids": sorted(missing)})
    fact_payloads = []
    for fact_id in fact_ids:
        fact = facts_by_id[fact_id]
        fact_payloads.append(
            {
                "id": fact.id,
                "statement": fact.statement,
                "value": fact.value,
                "authority": fact.authority.value,
                "evidence_ids": sorted(fact.evidence_ids),
                "effective_at": fact.effective_at,
                "affected_slices": sorted(item.value for item in fact.affected_slices),
                "field_key": fact.field_key,
                "status": fact.status.value,
                "freshness_class": fact.freshness_class.value,
            }
        )
    direct_lineage = [
        item.model_dump(mode="json")
        for item in state.lineage
        if item.subject_id in {f"fact:{fact_id}" for fact_id in fact_ids}
    ]
    return _canonical_hash({"facts": fact_payloads, "direct_lineage": direct_lineage})


def _material_condition_payload(
    state: CanonicalState,
    gate: Gate,
    fact_ids: tuple[str, ...],
    dimension: str,
) -> Any:
    facts = [fact for fact in state.facts if fact.id in fact_ids]
    if dimension == "anchor":
        return state.human_anchor
    if dimension == "path":
        return state.path_target_state
    if dimension == "lifecycle":
        return {
            "position": state.lifecycle_position.value,
            "transition_month": state.transition_month,
            "transition_date": state.transition_date,
        }
    if dimension == "time_validity":
        return [
            {
                "id": fact.id,
                "effective_at": fact.effective_at,
                "status": fact.status.value,
                "freshness_class": fact.freshness_class.value,
            }
            for fact in facts
        ]
    if dimension == "authority":
        return {
            "facts": sorted((fact.id, fact.authority.value) for fact in facts),
            "gate_required": gate.authority_required.value,
            "gate_set": sorted(item.value for item in gate.authority_set),
        }
    if dimension == "effect_reachability":
        return {
            "fact_slices": sorted(
                (fact.id, tuple(sorted(item.value for item in fact.affected_slices))) for fact in facts
            ),
            "gate_slices": sorted(item.value for item in gate.affected_slices),
            "authorized_scope": sorted(gate.authorized_scope),
        }
    raise GovernanceError(f"Unknown bounded rejection validity dimension {dimension!r}.")


def _condition_refs(
    state: CanonicalState,
    gate: Gate,
    fact_ids: tuple[str, ...],
    dimensions: tuple[str, ...],
) -> tuple[str, ...]:
    return tuple(
        f"material-condition:{dimension}:sha256:"
        f"{_canonical_hash(_material_condition_payload(state, gate, fact_ids, dimension))}"
        for dimension in sorted(set(dimensions))
    )


def build_rejection_identity(
    state: CanonicalState,
    *,
    fact_ids: list[str] | tuple[str, ...],
    effect_dimension: str,
    gate_id: str,
) -> RejectionIdentity:
    normalized_fact_ids = tuple(sorted(set(fact_ids)))
    if not normalized_fact_ids:
        raise GovernanceError("State-bound rejection requires at least one governed Fact ID.")
    gate = _gate(state, gate_id)
    gate_version = gate_contract_version(gate)
    lineage_hash = evidence_lineage_hash(state, normalized_fact_ids)
    scope = {
        "fact_ids": normalized_fact_ids,
        "effect_dimension": effect_dimension,
        "gate_id": gate_id,
    }
    identity = {
        **scope,
        "gate_version": gate_version,
        "evidence_lineage_hash": lineage_hash,
    }
    return RejectionIdentity(
        fact_ids=normalized_fact_ids,
        effect_dimension=effect_dimension,
        gate_id=gate_id,
        gate_version=gate_version,
        evidence_lineage_hash=lineage_hash,
        scope_hash=_canonical_hash(scope),
        identity_hash=_canonical_hash(identity),
    )


def _reference_value(refs: list[str], prefix: str) -> str | None:
    matches = [item.removeprefix(prefix) for item in refs if item.startswith(prefix)]
    return matches[0] if len(matches) == 1 else None


def _rejection_records(state: CanonicalState) -> list[tuple[Decision, LineageRecord]]:
    decisions = {decision.id: decision for decision in state.decisions if decision.value == REJECTION_VALUE}
    records: list[tuple[Decision, LineageRecord]] = []
    for lineage in state.lineage:
        if REJECTION_MARKER not in lineage.depends_on or not lineage.subject_id.startswith("decision:"):
            continue
        decision = decisions.get(lineage.subject_id.removeprefix("decision:"))
        if decision is not None:
            records.append((decision, lineage))
    return records


def lookup_state_bound_rejection(
    state: CanonicalState,
    *,
    fact_ids: list[str] | tuple[str, ...],
    effect_dimension: str,
    gate_id: str,
    validity_dimensions: list[str] | tuple[str, ...],
) -> RejectionLookup:
    """Return a deterministic read-only suppression disposition."""

    started = time.perf_counter()
    current = build_rejection_identity(
        state,
        fact_ids=fact_ids,
        effect_dimension=effect_dimension,
        gate_id=gate_id,
    )
    gate = _gate(state, gate_id)
    current_conditions = set(
        _condition_refs(state, gate, current.fact_ids, tuple(validity_dimensions))
    )
    same_effect_gate = False
    same_scope: list[tuple[Decision, LineageRecord]] = []
    for decision, lineage in reversed(_rejection_records(state)):
        recorded_effect = _reference_value(lineage.depends_on, "effect-dimension:")
        if decision.gate_id != gate_id or recorded_effect != effect_dimension:
            continue
        same_effect_gate = True
        recorded_scope = _reference_value(lineage.depends_on, "rejection-scope:sha256:")
        if recorded_scope == current.scope_hash:
            same_scope.append((decision, lineage))
            recorded_identity = _reference_value(lineage.depends_on, "rejection-identity:sha256:")
            if recorded_identity == current.identity_hash and set(lineage.valid_while) == current_conditions:
                return RejectionLookup(
                    status="SUPPRESSED",
                    identity=current,
                    decision_id=decision.id,
                    invalidation_triggers=(),
                    lookup_ms=(time.perf_counter() - started) * 1000,
                )
    if same_scope:
        decision, lineage = same_scope[0]
        triggers: list[str] = []
        if _reference_value(lineage.depends_on, "gate-contract:sha256:") != current.gate_version:
            triggers.append("gate_contract_version_changed")
        if _reference_value(lineage.depends_on, "evidence-lineage:sha256:") != current.evidence_lineage_hash:
            triggers.append("evidence_lineage_changed")
        recorded_conditions = set(lineage.valid_while)
        for ref in sorted(recorded_conditions.symmetric_difference(current_conditions)):
            parts = ref.split(":", 3)
            triggers.append(f"material_condition_changed:{parts[1] if len(parts) > 1 else 'unknown'}")
        return RejectionLookup(
            status="INVALIDATED",
            identity=current,
            decision_id=decision.id,
            invalidation_triggers=tuple(sorted(set(triggers))) or ("identity_changed",),
            lookup_ms=(time.perf_counter() - started) * 1000,
        )
    return RejectionLookup(
        status="IDENTITY_MISS" if same_effect_gate else "NO_PRIOR_REJECTION",
        identity=current,
        decision_id=None,
        invalidation_triggers=(),
        lookup_ms=(time.perf_counter() - started) * 1000,
    )


def record_state_bound_rejection(
    state: CanonicalState,
    *,
    actor: ActorProvenance,
    idempotency_key: str,
    fact_ids: list[str] | tuple[str, ...],
    effect_dimension: str,
    gate_id: str,
    validity_dimensions: list[str] | tuple[str, ...],
) -> CanonicalState:
    """Record an authorized rejection using existing Decision/Lineage semantics."""

    if idempotency_key in state.processed_keys:
        return state
    previous = deepcopy(state)
    working = deepcopy(state)
    identity = build_rejection_identity(
        working,
        fact_ids=fact_ids,
        effect_dimension=effect_dimension,
        gate_id=gate_id,
    )
    gate = _gate(working, gate_id)
    decision_id = f"decision-state-bound-rejection-{identity.identity_hash[:24]}"
    working.decisions.append(
        Decision(
            id=decision_id,
            gate_id=gate_id,
            value=REJECTION_VALUE,
            authority=Authority.HUMAN,
        )
    )
    working.processed_keys.append(idempotency_key)
    governed = AuthorityGovernor().record_human_mutation(
        state=working,
        actor=actor,
        idempotency_key=idempotency_key,
        expected_version=previous.version,
        result_version=previous.version + 1,
        dependency_refs=[
            REJECTION_MARKER,
            f"rejection-identity:sha256:{identity.identity_hash}",
            f"rejection-scope:sha256:{identity.scope_hash}",
            *(f"input-fact:{fact_id}" for fact_id in identity.fact_ids),
            f"effect-dimension:{effect_dimension}",
            f"gate-contract:sha256:{identity.gate_version}",
            f"evidence-lineage:sha256:{identity.evidence_lineage_hash}",
            f"human-examination:{actor.event_id}",
        ],
        mutation_kind="probe_candidate_rejected",
    )
    governed.lineage.append(
        LineageRecord(
            subject_id=f"decision:{decision_id}",
            depends_on=[
                REJECTION_MARKER,
                f"rejection-identity:sha256:{identity.identity_hash}",
                f"rejection-scope:sha256:{identity.scope_hash}",
                *(f"input-fact:{fact_id}" for fact_id in identity.fact_ids),
                f"effect-dimension:{effect_dimension}",
                f"gate-contract:sha256:{identity.gate_version}",
                f"evidence-lineage:sha256:{identity.evidence_lineage_hash}",
            ],
            valid_while=list(
                _condition_refs(working, gate, identity.fact_ids, tuple(validity_dimensions))
            ),
            invalidated_by=[
                "material-change:source-evidence-lineage",
                "material-change:gate-contract",
                *(f"material-change:{dimension}" for dimension in sorted(set(validity_dimensions))),
            ],
            source_state_version=previous.version,
            authority_refs=[
                f"decision:{decision_id}",
                f"actor:{actor.event_id}",
                f"domain-pack:{governed.domain_pack.content_hash}",
            ],
            integrity=LineageIntegrity.VERIFIED,
        )
    )
    validate_mutation_commit(previous=previous, updated=governed, expected_version=previous.version)
    return governed
