from __future__ import annotations

import re
from copy import deepcopy
from datetime import date, timedelta

from military_slices.engine import active_gate, recompute_state, stable_id
from military_slices.models import (
    Authority,
    CanonicalState,
    Decision,
    Fact,
    FeedbackEvent,
    GateState,
    HistoryEntry,
    LensProjection,
    PathProgress,
    ProgressItem,
    SliceName,
    WhatIfBranch,
    utc_now,
)
from military_slices.path_runtime import anchor_domain, derive_execution_state
from military_slices.temporal import propagate_temporal_changes

SLICE_LABELS = {
    SliceName.CAREER: "Career",
    SliceName.EDUCATION: "Education",
    SliceName.LOCATION: "Location",
    SliceName.RESUME: "Your Story",
}

DECISION_SLICES: dict[str, set[SliceName]] = {
    "planned-transition-date": set(SliceName),
    "service-path-identity": set(SliceName),
    "transition-human-anchor": set(SliceName),
    "next-work-preferences": {SliceName.CAREER, SliceName.EDUCATION, SliceName.LOCATION},
    "career-direction": {SliceName.CAREER, SliceName.RESUME},
    "resume-target-role": {SliceName.RESUME, SliceName.CAREER},
    "education-outcome": {SliceName.EDUCATION},
    "location-priority": {SliceName.LOCATION},
    "priority-first-six-months": {SliceName.CAREER, SliceName.EDUCATION},
}


def _status(closed: bool, partial: bool = False) -> GateState:
    if closed:
        return GateState.YES
    return GateState.PARTIAL if partial else GateState.UNKNOWN


def _has_preference(state: CanonicalState) -> bool:
    return any(
        any(
            term in fact.statement.casefold()
            for term in ("want", "prefer", "hate", "won't", "will not", "don't", "do not")
        )
        for fact in state.facts
    )


def path_progress(state: CanonicalState) -> PathProgress:
    domain = anchor_domain(state.human_anchor)
    items = [
        ProgressItem(
            id="human-anchor",
            label="Current target declared",
            state=_status(state.human_anchor is not None),
        )
    ]
    if state.human_anchor is None:
        return PathProgress(target="Choose what matters first", closed=0, total=1, items=items)

    if domain == "resume":
        target_known = "specific target" not in state.human_anchor.casefold()
        evidence_count = sum(SliceName.RESUME in fact.affected_slices for fact in state.facts)
        items.extend(
            [
                ProgressItem(id="resume-target", label="Résumé target bounded", state=_status(target_known)),
                ProgressItem(
                    id="resume-evidence",
                    label="Target evidence available",
                    state=_status(evidence_count > 1, partial=evidence_count == 1),
                ),
            ]
        )
    else:
        items.extend(
            [
                ProgressItem(
                    id="transition-date",
                    label="Working transition timing known",
                    state=_status(state.transition_date is not None),
                ),
                ProgressItem(
                    id="service-path",
                    label="Service path identified",
                    state=_status(state.service is not None),
                ),
            ]
        )
        if domain == "employment":
            items.extend(
                [
                    ProgressItem(
                        id="work-preferences",
                        label="Work conditions bounded",
                        state=_status(_has_preference(state)),
                    ),
                    ProgressItem(
                        id="career-direction",
                        label="Career direction selected",
                        state=_status(
                            any(item.status == "accepted" for item in state.career_hypotheses),
                            partial=bool(state.career_hypotheses),
                        ),
                    ),
                ]
            )
        elif domain == "education":
            relevant = [fact for fact in state.facts if SliceName.EDUCATION in fact.affected_slices]
            items.append(
                ProgressItem(
                    id="education-outcome",
                    label="Education outcome bounded",
                    state=_status(len(relevant) > 1, partial=len(relevant) == 1),
                )
            )
        elif domain == "location":
            relevant = [fact for fact in state.facts if SliceName.LOCATION in fact.affected_slices]
            items.append(
                ProgressItem(
                    id="location-priority",
                    label="Location condition bounded",
                    state=_status(bool(relevant)),
                )
            )
        elif domain == "undecided":
            decided = any(decision.gate_id == "transition-direction" for decision in state.decisions)
            items.append(
                ProgressItem(
                    id="transition-direction",
                    label="Direction chosen for examination",
                    state=_status(decided),
                )
            )

    if state.conflicts:
        items.append(
            ProgressItem(id="active-conflict", label="Material path conflict resolved", state=GateState.CONFLICTED)
        )
    closed = sum(item.state in (GateState.YES, GateState.NO) for item in items)
    return PathProgress(
        target=state.human_anchor,
        closed=closed,
        total=len(items),
        items=items,
    )


def lens_projections(state: CanonicalState) -> list[LensProjection]:
    gate = active_gate(state)
    active_slices = set(
        gate.affected_slices
        if gate and gate.id not in ("transition-human-anchor", "service-path-identity")
        else []
    )
    for task in state.active_tasks:
        active_slices.update(task.affected_slices)
    result: list[LensProjection] = []
    for slice_name in SliceName:
        pending_impact = next((item for item in state.impacts if item.affected_slice == slice_name), None)
        fact_slices = {slice_name}
        if slice_name == SliceName.CAREER and anchor_domain(state.human_anchor) == "resume":
            fact_slices.add(SliceName.RESUME)
        facts = [
            fact.statement
            for fact in state.facts
            if fact_slices.intersection(fact.affected_slices)
        ]
        open_gates = [
            item
            for item in state.gates
            if slice_name in item.affected_slices and item.state not in (GateState.YES, GateState.NO)
        ]
        decisions = [
            decision.value
            for decision in state.decisions
            if slice_name in DECISION_SLICES.get(decision.gate_id, set())
        ]
        conflicted = sum(item.state == GateState.CONFLICTED for item in open_gates)
        path_relevant = slice_name in active_slices
        if pending_impact:
            summary = pending_impact.message
        elif path_relevant and open_gates:
            summary = f"This area matters because {open_gates[0].why[:1].lower() + open_gates[0].why[1:]}"
        elif path_relevant:
            summary = "This area supports the current target, but it does not need another decision now."
        elif facts:
            summary = "Useful context is known here, but it is not blocking the current target."
        else:
            summary = "Nothing here currently blocks the active path."
        result.append(
            LensProjection(
                name=slice_name,
                label=SLICE_LABELS[slice_name],
                path_relevant=path_relevant,
                fact_count=len(facts),
                closed_gates=len(decisions),
                open_gates=len(open_gates),
                conflicted_gates=conflicted,
                latent_dependencies=len(facts) if not path_relevant else 0,
                summary=summary,
                facts=facts[-6:],
                decisions=decisions[-6:],
                may_have_changed=pending_impact is not None,
            )
        )
    return result


def history_entry(state: CanonicalState, *, current: bool = False) -> HistoryEntry:
    last_feedback = state.feedback[-1].headline if state.feedback else "Initial governed state."
    return HistoryEntry(
        version=state.version,
        recorded_at=state.updated_at,
        human_anchor=state.human_anchor,
        path_target_state=state.path_target_state,
        open_gates=[gate.title for gate in state.gates if gate.state not in (GateState.YES, GateState.NO)],
        closed_decisions=[decision.value for decision in state.decisions[-6:]],
        change_summary=last_feedback,
        current=current,
    )


def _month_date(text: str) -> str | None:
    iso = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", text)
    if iso:
        try:
            return date.fromisoformat(iso.group(1)).isoformat()
        except ValueError:
            return None
    months = {
        name: index
        for index, name in enumerate(
            (
                "january",
                "february",
                "march",
                "april",
                "may",
                "june",
                "july",
                "august",
                "september",
                "october",
                "november",
                "december",
            ),
            start=1,
        )
    }
    match = re.search(r"\b(" + "|".join(months) + r")\s+(20\d{2})\b", text.casefold())
    if match:
        return date(int(match.group(2)), months[match.group(1)], 1).isoformat()
    return None


def _target_relative_scope(state: CanonicalState) -> tuple[list[SliceName], list[str]]:
    gate = active_gate(state)
    if gate is not None:
        declared = DECISION_SLICES.get(gate.id, set()) or set(gate.affected_slices)
        slices = [name for name in SliceName if name in declared]
        if slices:
            return slices, [gate.id]

    domain_slices = {
        "employment": [SliceName.CAREER, SliceName.RESUME],
        "resume": [SliceName.RESUME, SliceName.CAREER],
        "education": [SliceName.EDUCATION],
        "location": [SliceName.LOCATION],
        "undecided": [SliceName.CAREER, SliceName.EDUCATION],
    }
    domain = anchor_domain(state.human_anchor)
    slices = domain_slices.get(domain, []) if domain is not None else []
    if not slices:
        raise ValueError("Establish what matters now before exploring a hypothetical choice.")
    return slices, []


def _parse_modification(state: CanonicalState, text: str) -> tuple[str, str, str, list[SliceName], list[str]]:
    lower = text.casefold()
    if "relocat" in lower or "move" in lower:
        negative = any(term in lower for term in ("would not", "wouldn't", "won't", "not willing", "refuse"))
        value = "NO" if negative else "YES"
        statement = "I would not relocate." if negative else "I would be willing to relocate."
        return (
            "relocation_willingness",
            value,
            statement,
            [SliceName.LOCATION, SliceName.CAREER],
            ["location-compatibility"],
        )
    if any(term in lower for term in ("school full time", "school full-time", "full time school", "full-time school")):
        return (
            "education_priority",
            "FULL_TIME_FIRST",
            "I would pursue full-time education first.",
            [SliceName.EDUCATION, SliceName.CAREER],
            ["priority-first-six-months"],
        )
    parsed = _month_date(lower)
    if parsed is None and "three months earlier" in lower and state.transition_date:
        parsed = (date.fromisoformat(state.transition_date) - timedelta(days=90)).isoformat()
    if parsed:
        return (
            "transition_date",
            parsed,
            f"My transition date would be {parsed}.",
            list(SliceName),
            ["planned-transition-date"],
        )
    if not state.human_anchor:
        raise ValueError("Establish what matters now before exploring a hypothetical choice.")
    slices, gates = _target_relative_scope(state)
    value = re.sub(r"^\s*what\s+if\s+", "", text, flags=re.IGNORECASE).strip()
    if len(value) < 3:
        raise ValueError("Add one possible choice to explore against what matters now.")
    return "target_experiment", value, value, slices, gates


def create_what_if(state: CanonicalState, text: str) -> WhatIfBranch:
    kind, value, statement, slices, gates = _parse_modification(state, text)
    hypothetical = deepcopy(state)
    conflicts: list[str] = []
    consequences: list[str] = []
    uncertainty = ["This branch uses only current governed evidence; real program and market conditions may change."]
    if kind == "relocation_willingness":
        existing_negative = any(
            any(
                term in fact.statement.casefold()
                for term in ("won't relocate", "will not relocate", "remain local", "stay local")
            )
            for fact in state.facts
        )
        if value == "YES" and existing_negative:
            conflicts.append("The hypothetical relocation choice conflicts with the current local-only preference.")
        consequences = [
            "The location boundary would change.",
            "Employment options could be reconsidered within the broader boundary.",
            "The current résumé target would remain unchanged.",
        ]
    elif kind == "education_priority":
        if any("income" in fact.statement.casefold() for fact in state.facts):
            conflicts.append("Full-time education first may conflict with the current immediate-income requirement.")
        consequences = [
            "Education would become path-relevant.",
            "Employment timing would need to be checked against the education workload.",
            "The declared target would not change unless explicitly replaced.",
        ]
    elif kind == "transition_date":
        old_window = state.current_timeline_window
        hypothetical.transition_date = value
        hypothetical = recompute_state(hypothetical)
        consequences = [
            f"The transition window would move from {old_window} to {hypothetical.current_timeline_window}.",
            "Only time-dependent tasks and gates would be reconsidered.",
            "The declared target would remain unchanged.",
        ]
    else:
        current_gate = active_gate(state)
        gate_title = current_gate.title if current_gate else "the current decision"
        consequences = [
            f"This possibility would be examined only against the current target: {state.human_anchor}.",
            f"The active decision would remain: {gate_title}.",
            "No current target or confirmed fact changes during this comparison.",
        ]
        uncertainty = [
            "Whether this possibility materially advances the current target still needs evidence "
            "or a real-world test.",
            *uncertainty,
        ]

    evidence = [f"Current governed target: {state.human_anchor}"]
    evidence.extend(
        fact.statement for fact in state.facts if set(fact.affected_slices).intersection(slices)
    )
    evidence = evidence[-6:]
    current_gate = active_gate(state)
    current_summary = [
        f"Current target: {state.human_anchor or 'not yet declared'}",
        f"Path milestone: {state.path_target_state}",
        f"Active gate: {current_gate.title if current_gate else 'none'}",
    ]
    hypothetical_summary = [
        f"Hypothetical change: {statement}",
        *consequences,
    ]
    return WhatIfBranch(
        id=stable_id("whatif", state.profile_id, str(state.version), kind, value),
        source_version=state.version,
        human_anchor=state.human_anchor,
        path_target_state=hypothetical.path_target_state,
        modification_kind=kind,
        modification_value=value,
        statement=statement,
        affected_gates=gates,
        affected_slices=slices,
        consequences=consequences,
        evidence_basis=evidence,
        uncertainty=uncertainty,
        conflicts=conflicts,
        current_summary=current_summary,
        hypothetical_summary=hypothetical_summary,
    )


def promote_what_if(
    current: CanonicalState,
    branch: WhatIfBranch,
    *,
    idempotency_key: str,
) -> CanonicalState:
    if idempotency_key in current.processed_keys:
        return current
    state = deepcopy(current)
    previous_execution = deepcopy(current.execution)
    if branch.modification_kind == "relocation_willingness":
        state.facts = [
            fact
            for fact in state.facts
            if not (
                SliceName.LOCATION in fact.affected_slices
                and any(term in fact.statement.casefold() for term in ("relocat", "remain local", "stay local"))
            )
        ]
    if branch.modification_kind == "transition_date":
        state.transition_date = branch.modification_value
    else:
        state.facts.append(
            Fact(
                id=stable_id("fact", state.profile_id, idempotency_key, branch.modification_kind),
                statement=branch.statement,
                value=branch.modification_value,
                authority=Authority.HUMAN,
                affected_slices=branch.affected_slices,
                field_key=(
                    "target_experiment"
                    if branch.modification_kind == "target_experiment"
                    else "general_context"
                ),
            )
        )
    state.decisions.append(
        Decision(
            id=stable_id("decision", state.profile_id, idempotency_key),
            gate_id=f"what-if:{branch.modification_kind}",
            value=branch.statement,
            authority=Authority.HUMAN,
        )
    )
    if branch.conflicts and branch.modification_kind != "relocation_willingness":
        state.conflicts.extend(item for item in branch.conflicts if item not in state.conflicts)
    state = propagate_temporal_changes(current, state)
    state = recompute_state(state)
    if branch.modification_kind == "target_experiment":
        headline = "Added this possibility to the decision in front of you."
        consequences = [
            "Saved the possibility you explored as context for this decision.",
            "Kept the current direction choice open.",
            "Choose a direction next; this context will carry forward.",
        ]
    else:
        headline = "Used the explored change in your current plan."
        consequences = branch.consequences[:3]
    state.feedback.append(
        FeedbackEvent(
            id=stable_id("feedback", state.profile_id, idempotency_key),
            headline=headline,
            consequences=consequences,
        )
    )
    state.processed_keys.append(idempotency_key)
    state.updated_at = utc_now()
    state.version += 1
    return derive_execution_state(
        state,
        previous=previous_execution,
        resolving_authority=Authority.HUMAN,
    )
