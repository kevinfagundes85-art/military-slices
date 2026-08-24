from __future__ import annotations

import hashlib
import re
from copy import deepcopy
from datetime import UTC, date, datetime, timedelta

from military_slices.models import (
    Authority,
    CanonicalState,
    CareerHypothesis,
    Decision,
    Evidence,
    Fact,
    FeedbackEvent,
    Gate,
    GateState,
    OrientationResult,
    OrientedStatement,
    SliceName,
    SliceProjection,
    SurfaceType,
    utc_now,
)

ALL_SLICES = [
    SliceName.CAREER,
    SliceName.EDUCATION,
    SliceName.LOCATION,
    SliceName.RESUME,
]


def stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("\x1f".join(parts).encode()).hexdigest()[:16]
    return f"{prefix}_{digest}"


def _sentences(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text.strip())
    return [part.strip(" -\t") for part in re.split(r"(?<=[.!?])\s+|\n+", normalized) if part.strip()]


def _slice_hits(statement: str) -> list[SliceName]:
    value = statement.lower()
    hits: list[SliceName] = []
    keywords = {
        SliceName.CAREER: (
            "job",
            "career",
            "work",
            "salary",
            "income",
            "employ",
            "role",
            "industry",
            "defense",
        ),
        SliceName.EDUCATION: (
            "school",
            "degree",
            "college",
            "credential",
            "certif",
            "training",
            "education",
            "gi bill",
        ),
        SliceName.LOCATION: (
            "relocat",
            "move",
            "location",
            "commute",
            "remote",
            "city",
            "state",
            "family",
            "stay near",
            "stay in",
            "near ",
        ),
        SliceName.RESUME: (
            "resume",
            "résumé",
            "cv",
            "mos",
            "rating",
            "afsc",
            "specialty",
            "experience",
            "duty",
            "led",
            "coordinated",
        ),
    }
    for slice_name, terms in keywords.items():
        if any(term in value for term in terms):
            hits.append(slice_name)
    return hits


def _statement_kind(statement: str) -> str:
    value = statement.lower()
    if any(term in value for term in ("don't know", "do not know", "not sure", "uncertain")):
        return "unknown"
    if any(term in value for term in ("can't", "cannot", "won't", "will not", "hate", "must not")):
        return "preference"
    if re.search(
        r"\b(20\d{2}-\d{2}-\d{2}|20\d{2}|january|february|march|april|may|june|july|august|september|october|november|december)\b",
        value,
    ):
        return "date"
    if any(term in value for term in ("want", "need", "goal", "plan", "hope")):
        return "goal"
    return "fact"


def orient(text: str) -> OrientationResult:
    statements: list[OrientedStatement] = []
    affected: list[SliceName] = []
    for sentence in _sentences(text):
        hits = _slice_hits(sentence)
        for slice_name in hits:
            if slice_name not in affected:
                affected.append(slice_name)
        statements.append(
            OrientedStatement(
                text=sentence,
                kind=_statement_kind(sentence),
                affected_slices=hits,
            )
        )

    meaningful = [statement for statement in statements if statement.affected_slices]
    sufficient = bool(meaningful)
    clarification: str | None = None
    if not sufficient:
        clarification = "What decision about your transition would you most like help with first?"
    elif SliceName.CAREER in affected and not any(
        term in text.lower() for term in ("want", "need", "prefer", "don't", "do not", "won't", "hate")
    ):
        clarification = "What would you like more or less of in your next work?"

    if meaningful:
        domains = ", ".join(_slice_label(item) for item in affected)
        summary = f"This could shape {domains}."
    else:
        summary = "There is not enough decision context to choose a useful starting point yet."

    return OrientationResult(
        reviewed_input=text.strip(),
        summary=summary,
        statements=statements,
        affected_slices=affected,
        clarification_question=clarification,
        sufficient=sufficient,
    )


def _slice_label(slice_name: SliceName) -> str:
    return {
        SliceName.CAREER: "work",
        SliceName.EDUCATION: "education",
        SliceName.LOCATION: "location",
        SliceName.RESUME: "your experience story",
    }[slice_name]


def new_state(profile_id: str) -> CanonicalState:
    return CanonicalState(profile_id=profile_id, projections=_build_projections(None))


def _extract_transition_date(text: str) -> str | None:
    iso = re.search(r"\b(20\d{2})-(0[1-9]|1[0-2])-([0-2]\d|3[01])\b", text)
    if iso:
        try:
            return date.fromisoformat(iso.group(0)).isoformat()
        except ValueError:
            return None
    months = {
        name.lower(): index
        for index, name in enumerate(
            (
                "",
                "January",
                "February",
                "March",
                "April",
                "May",
                "June",
                "July",
                "August",
                "September",
                "October",
                "November",
                "December",
            )
        )
        if name
    }
    month_year = re.search(r"\b(" + "|".join(months) + r")\s+(20\d{2})\b", text, flags=re.IGNORECASE)
    if month_year:
        return date(int(month_year.group(2)), months[month_year.group(1).lower()], 1).isoformat()
    return None


def _has_income_education_conflict(text: str) -> bool:
    lower = text.lower()
    income = any(term in lower for term in ("immediate income", "need income", "job immediately", "work right away"))
    school = any(term in lower for term in ("full-time school", "school full time", "full-time education"))
    return income and school


def _fact_kind(statement: OrientedStatement) -> str:
    if statement.kind == "preference":
        return "preference"
    if statement.kind == "goal":
        return "goal"
    if statement.kind == "date":
        return "time_anchor"
    return "human_context"


def _merge_human_facts(state: CanonicalState, orientation: OrientationResult) -> list[str]:
    added: list[str] = []
    for statement in orientation.statements:
        if not statement.affected_slices:
            continue
        fact_id = stable_id("fact", _fact_kind(statement), statement.text.casefold())
        if any(existing.id == fact_id for existing in state.facts):
            state.telemetry.duplicate_questions_avoided += 1
            continue
        evidence_id = stable_id("evidence", state.profile_id, statement.text.casefold())
        state.evidence.append(
            Evidence(
                id=evidence_id,
                label="Confirmed transition statement",
                authority=Authority.HUMAN,
                purpose="transition planning",
            )
        )
        state.facts.append(
            Fact(
                id=fact_id,
                statement=statement.text,
                value=statement.text,
                authority=Authority.HUMAN,
                evidence_ids=[evidence_id],
                affected_slices=statement.affected_slices,
            )
        )
        added.append(statement.text)
    return added


def apply_confirmed_input(
    current: CanonicalState,
    orientation: OrientationResult,
    *,
    idempotency_key: str,
) -> CanonicalState:
    if idempotency_key in current.processed_keys:
        return current
    state = deepcopy(current)
    state.original_intents.append(orientation.reviewed_input)
    if not state.current_goal and orientation.sufficient:
        state.current_goal = orientation.reviewed_input
    added = _merge_human_facts(state, orientation)
    extracted_date = _extract_transition_date(orientation.reviewed_input)
    if extracted_date:
        state.transition_date = extracted_date

    if _has_income_education_conflict(orientation.reviewed_input):
        conflict = "Immediate income and full-time education overlap in the first transition period."
        if conflict not in state.conflicts:
            state.conflicts.append(conflict)

    state.gates = _recompute_gates(state)
    state.projections = _build_projections(state)
    consequences = _consequences_for_input(state, orientation, extracted_date)
    headline = "Your plan has a clearer starting point." if added else "Your existing plan was reused."
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
    return state


def _recompute_gates(state: CanonicalState) -> list[Gate]:
    existing = {gate.id: gate for gate in state.gates}
    gates: list[Gate] = []
    if state.conflicts:
        gate = Gate(
            id="priority-first-six-months",
            title="Choose what must lead first",
            question="Which must govern your first six months after separation?",
            why="Income and full-time education both require the same time and attention.",
            state=GateState.CONFLICTED,
            surface=SurfaceType.CONFLICT,
            affected_slices=[SliceName.CAREER, SliceName.EDUCATION],
            authority_required=Authority.HUMAN,
            options=["Immediate income", "Full-time education", "A staged combination"],
            value_score=100,
        )
        gates.append(_preserve_resolution(gate, existing))

    if not state.transition_date:
        gate = Gate(
            id="planned-transition-date",
            title="Anchor the timing",
            question="When do you expect to leave active service?",
            why="One date clarifies application, education, relocation, and résumé timing.",
            state=GateState.UNKNOWN,
            surface=SurfaceType.DATE,
            affected_slices=ALL_SLICES,
            authority_required=Authority.HUMAN,
            value_score=95,
        )
        gates.append(_preserve_resolution(gate, existing))

    preferences = [
        fact
        for fact in state.facts
        if any(
            term in fact.statement.lower()
            for term in ("want", "prefer", "hate", "won't", "will not", "don't", "do not")
        )
    ]
    if not preferences:
        gate = Gate(
            id="next-work-preferences",
            title="Shape the work around you",
            question="What would you like more or less of in your next work?",
            why=(
                "Your preferences prevent the system from recommending the closest title "
                "instead of the right direction."
            ),
            state=GateState.PARTIAL if state.current_goal else GateState.UNKNOWN,
            surface=SurfaceType.TEXT,
            affected_slices=[SliceName.CAREER, SliceName.EDUCATION, SliceName.LOCATION],
            authority_required=Authority.HUMAN,
            value_score=85,
        )
        gates.append(_preserve_resolution(gate, existing))

    if not any(h.status == "accepted" for h in state.career_hypotheses):
        gate = Gate(
            id="career-direction",
            title="Choose a direction to test",
            question="Which direction is worth testing first?",
            why=(
                "A direction lets the system compare real roles, evidence, and gaps instead "
                "of guessing from a military title."
            ),
            state=GateState.PARTIAL if state.career_hypotheses else GateState.UNKNOWN,
            surface=SurfaceType.COMPARE if state.career_hypotheses else SurfaceType.TEXT,
            affected_slices=[SliceName.CAREER, SliceName.EDUCATION, SliceName.RESUME],
            authority_required=Authority.HUMAN,
            options=[h.title for h in state.career_hypotheses if h.status == "candidate"],
            value_score=75,
        )
        gates.append(_preserve_resolution(gate, existing))
    return sorted(gates, key=lambda item: item.value_score, reverse=True)


def _preserve_resolution(gate: Gate, existing: dict[str, Gate]) -> Gate:
    previous = existing.get(gate.id)
    if previous and previous.state in (GateState.YES, GateState.NO):
        gate.state = previous.state
        gate.resolved_value = previous.resolved_value
        gate.updated_at = previous.updated_at
    return gate


def active_gate(state: CanonicalState) -> Gate | None:
    unresolved = [gate for gate in state.gates if gate.state not in (GateState.YES, GateState.NO)]
    return max(unresolved, key=lambda item: item.value_score, default=None)


def apply_decision(
    current: CanonicalState,
    *,
    gate_id: str,
    value: str,
    idempotency_key: str,
) -> CanonicalState:
    if idempotency_key in current.processed_keys:
        return current
    state = deepcopy(current)
    matching = next((gate for gate in state.gates if gate.id == gate_id), None)
    if matching is None:
        raise ValueError("That decision is no longer active. Refresh to continue from current state.")
    if matching.state in (GateState.YES, GateState.NO):
        raise ValueError("That decision is already resolved.")

    normalized = value.strip()
    previous_date = state.transition_date
    if gate_id == "planned-transition-date":
        parsed = _extract_transition_date(normalized)
        if parsed is None:
            raise ValueError("Enter a valid transition date.")
        state.transition_date = parsed
        normalized = parsed
    elif gate_id == "next-work-preferences":
        orientation = orient(normalized)
        _merge_human_facts(state, orientation)
    elif gate_id == "priority-first-six-months":
        state.conflicts = [item for item in state.conflicts if "Immediate income and full-time education" not in item]
    elif gate_id == "career-direction":
        rejecting = normalized.casefold().startswith("reject:")
        chosen = normalized.split(":", 1)[1].strip() if ":" in normalized else normalized
        matched = False
        for hypothesis in state.career_hypotheses:
            if hypothesis.title.casefold() != chosen.casefold():
                continue
            matched = True
            if rejecting:
                hypothesis.status = "rejected"
                if hypothesis.title not in state.rejected_roles:
                    state.rejected_roles.append(hypothesis.title)
            else:
                hypothesis.status = "accepted"
        if not matched:
            raise ValueError("That direction is no longer available. Refresh to see current options.")
        normalized = ("Not for me: " if rejecting else "Explore: ") + chosen

    rejecting_career = gate_id == "career-direction" and normalized.startswith("Not for me:")
    matching.state = GateState.PARTIAL if rejecting_career else GateState.YES
    matching.resolved_value = normalized
    matching.updated_at = utc_now()
    state.decisions.append(
        Decision(
            id=stable_id("decision", state.profile_id, gate_id, idempotency_key),
            gate_id=gate_id,
            value=normalized,
        )
    )
    consequences = _decision_consequences(gate_id, previous_date, state.transition_date, normalized)
    state.feedback.append(
        FeedbackEvent(
            id=stable_id("feedback", state.profile_id, idempotency_key),
            headline="That decision changed what comes next.",
            consequences=consequences,
        )
    )
    if rejecting_career:
        state.career_hypotheses = [item for item in state.career_hypotheses if item.status != "rejected"]
        replacements = deterministic_hypotheses(" ".join(fact.statement for fact in state.facts), state.rejected_roles)
        known = {item.title for item in state.career_hypotheses}
        state.career_hypotheses.extend(item for item in replacements if item.title not in known)
    state.gates = _recompute_gates(state)
    state.projections = _build_projections(state)
    state.processed_keys.append(idempotency_key)
    state.updated_at = utc_now()
    state.version += 1
    return state


def _build_projections(state: CanonicalState | None) -> list[SliceProjection]:
    if state is None:
        return [
            SliceProjection(name=SliceName.CAREER, label="Work", summary="Ready when you are."),
            SliceProjection(name=SliceName.EDUCATION, label="Education", summary="Ready when it matters."),
            SliceProjection(name=SliceName.LOCATION, label="Location", summary="Ready when it matters."),
            SliceProjection(name=SliceName.RESUME, label="Your story", summary="Ready when you share it."),
        ]
    projections: list[SliceProjection] = []
    for name, label in (
        (SliceName.CAREER, "Work"),
        (SliceName.EDUCATION, "Education"),
        (SliceName.LOCATION, "Location"),
        (SliceName.RESUME, "Your story"),
    ):
        facts = [fact for fact in state.facts if name in fact.affected_slices]
        unresolved = [
            gate
            for gate in state.gates
            if name in gate.affected_slices and gate.state not in (GateState.YES, GateState.NO)
        ]
        if any(gate.state == GateState.CONFLICTED for gate in unresolved):
            status = GateState.CONFLICTED
            summary = "A priority needs your decision."
        elif name == SliceName.CAREER and any(item.status == "accepted" for item in state.career_hypotheses):
            accepted = next(item for item in state.career_hypotheses if item.status == "accepted")
            status = GateState.YES
            summary = f"Exploring {accepted.title}."
        elif name == SliceName.CAREER and state.career_hypotheses:
            status = GateState.PARTIAL
            summary = "Civilian directions are ready to compare."
        elif facts:
            status = GateState.PARTIAL if unresolved else GateState.YES
            summary = {
                SliceName.CAREER: "Your work preferences are shaping the search.",
                SliceName.EDUCATION: "Credential timing is included in the plan.",
                SliceName.LOCATION: "Your location constraints are included.",
                SliceName.RESUME: "Your experience is ready to translate.",
            }[name]
        else:
            status = GateState.UNKNOWN
            summary = "Not affecting this decision."
        projections.append(SliceProjection(name=name, label=label, status=status, summary=summary))
    return projections


def _consequences_for_input(
    state: CanonicalState,
    orientation: OrientationResult,
    transition_date: str | None,
) -> list[str]:
    consequences = [f"Connected your input to {_slice_label(item)}." for item in orientation.affected_slices]
    if transition_date:
        consequences.append("Anchored application, education, relocation, and résumé timing to one date.")
    if state.conflicts:
        consequences.append("Surfaced a priority conflict instead of silently averaging it.")
    if not consequences:
        consequences.append("Preserved your words and reduced the next question to one clarification.")
    return consequences[:4]


def _decision_consequences(
    gate_id: str,
    previous_date: str | None,
    current_date: str | None,
    decision_value: str,
) -> list[str]:
    if gate_id == "planned-transition-date":
        if previous_date and previous_date != current_date:
            return [
                "Reopened only the timing-sensitive work.",
                "Preserved preferences and decisions that the date did not change.",
            ]
        return [
            "Clarified when to begin applications.",
            "Clarified whether education can finish before separation.",
            "Clarified when relocation and résumé work become urgent.",
        ]
    if gate_id == "priority-first-six-months":
        return [
            "Resolved the conflict across work and education.",
            "Made the selected priority govern the first six months.",
        ]
    if gate_id == "career-direction":
        if decision_value.startswith("Not for me:"):
            return ["Removed that direction from future suggestions.", "Kept the remaining options in view."]
        return ["Kept one direction in focus.", "Left the other directions available for later review."]
    return [
        "Applied the preference across work, education, and location.",
        "Reduced the next interaction to unresolved context.",
    ]


def deterministic_hypotheses(text: str, rejected: list[str]) -> list[CareerHypothesis]:
    lower = text.lower()
    families: list[tuple[str, str, list[str]]] = []
    if any(term in lower for term in ("intelligence", "analysis", "brief", "research")):
        families.extend(
            [
                (
                    "Operations Research Analyst",
                    "Uses structured analysis and decision support without requiring a defense setting.",
                    ["O*NET 15-2031.00", "BLS Occupational Outlook Handbook"],
                ),
                (
                    "Business Intelligence Analyst",
                    "Translates complex information into decisions for civilian organizations.",
                    ["O*NET 15-2051.01"],
                ),
                (
                    "Program Management Analyst",
                    "Combines planning, stakeholder coordination, and executive communication.",
                    ["O*NET 13-1111.00"],
                ),
            ]
        )
    elif any(term in lower for term in ("logistics", "supply", "warehouse", "transport")):
        families.extend(
            [
                ("Logistics Analyst", "Builds on supply, movement, and readiness coordination.", ["O*NET 13-1081.02"]),
                (
                    "Supply Chain Planner",
                    "Applies operational planning to civilian inventory and distribution.",
                    ["O*NET 13-1081.00"],
                ),
                ("Operations Manager", "Transfers team, schedule, and resource responsibility.", ["O*NET 11-1021.00"]),
            ]
        )
    elif any(term in lower for term in ("maintenance", "mechanic", "equipment", "aviation")):
        families.extend(
            [
                (
                    "Maintenance Planner",
                    "Uses readiness, scheduling, and equipment history to reduce downtime.",
                    ["O*NET 49-1011.00"],
                ),
                (
                    "Field Service Manager",
                    "Transfers technical leadership and customer-facing troubleshooting.",
                    ["O*NET 49-1011.00"],
                ),
                (
                    "Quality Assurance Specialist",
                    "Applies inspection, procedure, and risk-control experience.",
                    ["O*NET 13-1199.00"],
                ),
            ]
        )
    else:
        families.extend(
            [
                (
                    "Operations Coordinator",
                    "Tests how planning, execution, and cross-team coordination translate.",
                    ["O*NET 13-1082.00"],
                ),
                (
                    "Project Coordinator",
                    "Tests schedule, stakeholder, and delivery responsibility in a new setting.",
                    ["O*NET 13-1082.00"],
                ),
                (
                    "Customer Success Specialist",
                    "Tests coaching, problem-solving, and relationship skills outside defense.",
                    ["O*NET 13-1161.00"],
                ),
            ]
        )
    return [
        CareerHypothesis(
            id=stable_id("career", title),
            title=title,
            rationale=rationale,
            evidence=evidence,
            capability_matches=_role_capabilities(title),
            possible_gaps=_role_gaps(title),
        )
        for title, rationale, evidence in families
        if title not in rejected
    ][:3]


def _role_capabilities(title: str) -> list[str]:
    lower = title.casefold()
    if any(term in lower for term in ("maintenance", "field service", "quality")):
        return ["Operational scheduling", "Inspection and risk control", "Team coordination"]
    if any(term in lower for term in ("analyst", "intelligence", "research")):
        return ["Structured analysis", "Decision support", "Executive communication"]
    if any(term in lower for term in ("logistics", "supply", "operations")):
        return ["Resource planning", "Cross-team coordination", "Operational execution"]
    return ["Planning", "Stakeholder coordination", "Problem solving"]


def _role_gaps(title: str) -> list[str]:
    lower = title.casefold()
    if "maintenance" in lower or "field service" in lower:
        return ["Civilian maintenance-system terminology", "Evidence from comparable job postings"]
    if "quality" in lower:
        return ["Industry-specific quality standards", "Civilian examples with measurable outcomes"]
    if "analyst" in lower:
        return ["Civilian data-tool evidence", "Portfolio examples without protected information"]
    return ["Civilian job-title calibration", "Evidence matched to a real posting"]


def apply_hypotheses(state: CanonicalState, hypotheses: list[CareerHypothesis]) -> CanonicalState:
    updated = deepcopy(state)
    accepted = [item for item in updated.career_hypotheses if item.status == "accepted"]
    updated.career_hypotheses = accepted + hypotheses
    updated.gates = _recompute_gates(updated)
    updated.projections = _build_projections(updated)
    return updated


def transition_window(separation_date: str) -> dict[str, str]:
    parsed = date.fromisoformat(separation_date)
    return {
        "resume_ready_by": (parsed - timedelta(days=180)).isoformat(),
        "applications_begin_by": (parsed - timedelta(days=150)).isoformat(),
        "relocation_decision_by": (parsed - timedelta(days=120)).isoformat(),
        "separation_date": parsed.isoformat(),
    }


def state_age_seconds(state: CanonicalState) -> int:
    return max(0, int((datetime.now(UTC) - state.updated_at).total_seconds()))
