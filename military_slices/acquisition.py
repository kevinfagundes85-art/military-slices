from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Literal

from military_slices.engine import active_gate, orient
from military_slices.models import (
    AcquisitionCandidate,
    AcquisitionChecklistItem,
    AcquisitionHorizon,
    Authority,
    CanonicalState,
    Gate,
    OrientationResult,
    SliceName,
)
from military_slices.path_runtime import ANCHOR_OPTIONS, anchor_domain

AUTHORITY_CONSTRAINTS = [
    "The conversation may nominate explicit human statements but cannot authorize a transition.",
    "Inference remains provisional and cannot become a saved fact.",
    "Only the current Gate may be acted on; later checklist items remain latent.",
    "Every saved change remains bound to the current profile version and human authority.",
]


@dataclass(frozen=True)
class DeterministicAcquisition:
    candidates: list[AcquisitionCandidate]
    matched_checklist_ids: list[str]
    gate_value: str | None
    clarification_question: str | None


def _active_slice(gate: Gate) -> SliceName:
    return gate.affected_slices[0] if gate.affected_slices else SliceName.CAREER


def _usable_fact_refs(
    state: CanonicalState,
    slices: list[SliceName],
    *,
    item_id: str,
) -> list[str]:
    terms = {
        "next-work-preferences": (
            "want",
            "prefer",
            "hate",
            "won't",
            "will not",
            "don't",
            "do not",
            "remote",
            "hybrid",
            "schedule",
            "travel",
            "commute",
        ),
        "career-direction": (
            "build",
            "company",
            "business",
            "startup",
            "organization",
            "career",
            "role",
            "work as",
            "employed as",
        ),
        "education-outcome": ("learn", "degree", "school", "training", "credential", "certification"),
        "location-priority": ("location", "move", "relocat", "commute", "stay", "near "),
    }.get(item_id, ())
    return [
        fact.id
        for fact in state.facts
        if fact.status.value == "valid"
        and any(item in slices for item in fact.affected_slices)
        and (not terms or any(term in fact.statement.casefold() for term in terms))
    ][:8]


def _item(
    state: CanonicalState,
    *,
    item_id: str,
    question: str,
    purpose: str,
    slices: list[SliceName],
    foreground: bool = False,
    status: Literal["unresolved", "satisfied", "latent"] = "latent",
) -> AcquisitionChecklistItem:
    refs = _usable_fact_refs(state, slices, item_id=item_id)
    resolved_status: Literal["unresolved", "satisfied", "latent"] = (
        "satisfied" if refs and not foreground else status
    )
    return AcquisitionChecklistItem(
        id=item_id,
        question=question,
        purpose=purpose,
        affected_slices=slices,
        authority_required=Authority.HUMAN,
        status=resolved_status,
        evidence_refs=refs,
        foreground=foreground,
    )


def _forecast_items(state: CanonicalState, gate: Gate) -> list[AcquisitionChecklistItem]:
    domain = anchor_domain(state.human_anchor)
    items: list[AcquisitionChecklistItem] = []
    if gate.id in {"transition-human-anchor", "transition-direction"} or domain == "undecided":
        items.extend(
            [
                _item(
                    state,
                    item_id="next-work-preferences",
                    question="What conditions would make the work fit you?",
                    purpose="Find work that fits your life, not just the closest job title.",
                    slices=[SliceName.CAREER, SliceName.EDUCATION, SliceName.LOCATION],
                ),
                _item(
                    state,
                    item_id="career-direction",
                    question="Would you rather join an organization, build something yourself, or keep both open?",
                    purpose="Find a direction to explore without making it permanent.",
                    slices=[SliceName.CAREER, SliceName.EDUCATION, SliceName.RESUME],
                ),
            ]
        )
    elif (
        domain == "employment"
        and gate.id != "career-direction"
        and not any(item.status == "accepted" for item in state.career_hypotheses)
    ):
        items.append(
            _item(
                state,
                item_id="career-direction",
                question="Which direction is worth testing first?",
                purpose="Turn a general idea into a direction you can test.",
                slices=[SliceName.CAREER, SliceName.EDUCATION, SliceName.RESUME],
            )
        )
    elif domain == "education":
        items.append(
            _item(
                state,
                item_id="education-outcome",
                question="What should the learning make possible?",
                purpose="Compare programs by what you want them to help you do.",
                slices=[SliceName.EDUCATION],
            )
        )
    elif domain == "location":
        items.append(
            _item(
                state,
                item_id="location-priority",
                question="What location condition must the plan respect?",
                purpose="Focus on the location need that could change your choice.",
                slices=[SliceName.LOCATION],
            )
        )
    return items


def _prompt(state: CanonicalState, gate: Gate) -> str:
    lower = " ".join([state.human_anchor or "", *[fact.statement for fact in state.facts]]).casefold()
    if gate.id == "transition-direction" and any(
        term in lower for term in ("ai", "build", "company", "impact", "veteran")
    ):
        return (
            "You’ve already described a direction. Are you picturing joining an organization doing "
            "that work, building something yourself, or keeping both open?"
        )
    return gate.question


def build_acquisition_horizon(state: CanonicalState) -> AcquisitionHorizon | None:
    """Build a bounded, read-only acquisition projection for the foreground Gate."""
    gate = active_gate(state)
    if gate is None or gate.surface.value in {"compare", "upload"}:
        return None
    foreground = _item(
        state,
        item_id=gate.id,
        question=gate.question,
        purpose=gate.why,
        slices=gate.affected_slices,
        foreground=True,
        status="unresolved",
    )
    checklist: list[AcquisitionChecklistItem] = [foreground]
    seen = {gate.id}
    for item in _forecast_items(state, gate):
        if item.id in seen:
            continue
        checklist.append(item)
        seen.add(item.id)
        if len(checklist) == 4:
            break
    payload = {
        "source_version": state.version,
        "anchor": state.human_anchor,
        "path": state.path_target_state,
        "active_slice": _active_slice(gate).value,
        "active_gate_id": gate.id,
        "prompt": _prompt(state, gate),
        "checklist": [item.model_dump(mode="json") for item in checklist],
        "domain_pack_hash": state.domain_pack.content_hash,
    }
    receipt_hash = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return AcquisitionHorizon(
        **payload,
        explicit_unknowns=[item.question for item in checklist if item.status == "unresolved"],
        authority_constraints=AUTHORITY_CONSTRAINTS,
        receipt_hash=receipt_hash,
    )


def _source_candidates(
    text: str,
    horizon: AcquisitionHorizon,
    *,
    oriented: OrientationResult | None = None,
) -> list[AcquisitionCandidate]:
    oriented = oriented or orient(text)
    candidates: list[AcquisitionCandidate] = []
    cursor = 0
    for statement in oriented.statements:
        start = text.find(statement.text, cursor)
        if start < 0:
            start = text.find(statement.text)
        if start < 0:
            continue
        end = start + len(statement.text)
        cursor = end
        matched = [
            item.id
            for item in horizon.checklist
            if set(item.affected_slices).intersection(statement.affected_slices)
        ]
        candidates.append(
            AcquisitionCandidate(
                text=statement.text,
                source_start=start,
                source_end=end,
                epistemic_type="explicit_human_statement",
                checklist_ids=matched[:4],
                confidence=1,
            )
        )
    return candidates


def _contains_any(lower: str, terms: tuple[str, ...]) -> bool:
    return any(term in lower for term in terms)


def _choice_gate_value(gate: Gate, text: str) -> tuple[str | None, str | None]:
    stripped = text.strip()
    lower = stripped.casefold()
    exact = next((option for option in gate.options if option.casefold() == lower), None)
    if exact:
        return exact, None
    if gate.id == "transition-direction":
        matches: list[str] = []
        if _contains_any(
            lower,
            (
                "work",
                "career",
                "job",
                "company",
                "business",
                "startup",
                "build something",
                "build a",
                "organization",
                "both",
                "founder",
            ),
        ):
            matches.append("Civilian work")
        if _contains_any(lower, ("education", "school", "degree", "training", "credential", "learn ")):
            matches.append("Education or training")
        if _contains_any(lower, ("location", "move", "relocat", "family fit", "where to live")):
            matches.append("Location and family fit")
        if "upskill" in lower and _contains_any(lower, ("company", "build", "work", "career", "job")):
            matches = [item for item in matches if item != "Education or training"]
        matches = list(dict.fromkeys(matches))
        if len(matches) == 1:
            return matches[0], None
        return None, "Which should lead this next step: the work you want to do, learning, or location and family fit?"
    if gate.id == "transition-human-anchor":
        oriented = orient(stripped)
        lower_slices = {item for statement in oriented.statements for item in statement.affected_slices}
        if SliceName.RESUME in lower_slices:
            return "Improve a résumé for a specific goal", None
        if SliceName.EDUCATION in lower_slices and SliceName.CAREER not in lower_slices:
            return "Choose education or training", None
        if SliceName.LOCATION in lower_slices and SliceName.CAREER not in lower_slices:
            return "Plan where to live", None
        if SliceName.CAREER in lower_slices:
            return "Find civilian work", None
        if _contains_any(lower, ("not sure", "still deciding", "don't know", "do not know")):
            return "I am still deciding", None
        return None, "What outcome should lead right now: work, learning, location, or a specific résumé goal?"
    return None, "Choose one of the available directions, or describe which one you mean."


def evaluate_acquisition(
    state: CanonicalState,
    horizon: AcquisitionHorizon,
    text: str,
) -> DeterministicAcquisition:
    """Extract explicit statements and map only the active Gate through deterministic rules."""
    gate = active_gate(state)
    if gate is None or gate.id != horizon.active_gate_id or horizon.source_version != state.version:
        return DeterministicAcquisition([], [], None, "Your plan changed. Continue from the newest question.")
    oriented = orient(text, context=state)
    if oriented.conflicts:
        return DeterministicAcquisition(
            [],
            [],
            None,
            oriented.clarification_question or "Resolve the conflicting information first.",
        )
    candidates = _source_candidates(text, horizon, oriented=oriented)
    path_task_answer = (
        gate.id.startswith("path-task_")
        and bool(candidates)
        and len(text.strip()) >= 12
    )
    if path_task_answer:
        candidates = [
            candidate.model_copy(
                update={
                    "checklist_ids": list(
                        dict.fromkeys([gate.id, *candidate.checklist_ids])
                    )[:4]
                }
            )
            for candidate in candidates
        ]
    matched = list(dict.fromkeys(item for candidate in candidates for item in candidate.checklist_ids))
    if gate.surface.value in {"choice", "conflict"}:
        value, clarification = _choice_gate_value(gate, text)
        return DeterministicAcquisition(candidates, matched, value, clarification)
    if gate.surface.value == "date":
        return DeterministicAcquisition(candidates, matched, text.strip(), None)
    if gate.surface.value == "text":
        relevant = any(gate.id in candidate.checklist_ids for candidate in candidates)
        if not relevant:
            return DeterministicAcquisition(
                candidates,
                matched,
                None,
                "Which part of that answer matters most for this decision?",
            )
        return DeterministicAcquisition(candidates, matched, text.strip(), None)
    return DeterministicAcquisition(candidates, matched, None, "Use the choices shown for this decision.")


def canonical_anchor_option(value: str) -> str:
    return ANCHOR_OPTIONS.get(value, value)
