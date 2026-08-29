from __future__ import annotations

import re
from datetime import UTC, datetime
from html import escape
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from military_slices.models import CanonicalState, CareerHypothesis, Fact, FreshnessStatus, Gate, GateState


class PlanNote(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    detail: str | None = None
    source: str | None = None
    date: str | None = None
    date_kind: Literal["known", "veteran_target", "planned"] | None = None
    status: str | None = None


class PlanDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: str
    context: str | None = None
    decided_at: str
    current: bool


class PlanDirection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    status: Literal["Exploring", "Committed"] = "Exploring"
    why: list[str] = Field(default_factory=list)
    alternatives: list[str] = Field(default_factory=list)


class TransitionPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    objective: str | None = None
    direction: PlanDirection | None = None
    what_i_bring: list[PlanNote] = Field(default_factory=list)
    what_matters_to_me: list[PlanNote] = Field(default_factory=list)
    decisions: list[PlanDecision] = Field(default_factory=list)
    active_experiments: list[PlanNote] = Field(default_factory=list)
    completed_experiments: list[PlanNote] = Field(default_factory=list)
    changes: list[PlanNote] = Field(default_factory=list)
    unresolved: list[PlanNote] = Field(default_factory=list)
    next_actions: list[PlanNote] = Field(default_factory=list)
    timeline: list[PlanNote] = Field(default_factory=list)


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value.strip() for value in values if value and value.strip()))


def _human_field(field_key: str) -> str:
    labels = {
        "general_context": "What you told Military SLICES",
        "compensation_floor": "Pay requirement",
        "relocation_willingness": "Location preference",
        "education_priority": "Education preference",
        "application_timing": "Application timing",
        "resume_readiness_deadline": "Résumé deadline",
        "administrative_deadline": "Important deadline",
        "historical_achievement": "Relevant experience",
    }
    return labels.get(field_key, field_key.replace("_", " ").strip().capitalize())


def _fact_note(fact: Fact) -> PlanNote:
    evidence = "You told Military SLICES"
    if fact.evidence_ids:
        evidence = "Based on information you reviewed and approved"
    return PlanNote(title=_human_field(fact.field_key), detail=fact.statement, source=evidence)


def _timeline_sort_key(item: PlanNote) -> tuple[int, str, str]:
    """Put dated plan events in calendar order while preserving deterministic ties."""

    if not item.date:
        return (1, "", item.title.casefold())
    normalized = item.date[:10] if len(item.date) >= 10 else f"{item.date}-01"
    return (0, normalized, item.title.casefold())


def _direction_cycle(state: CanonicalState, direction: CareerHypothesis) -> tuple[list[str], list[str]]:
    learning_prefix = f"While testing the {direction.title} work direction, I learned:"
    next_test_prefix = f"For my next test of the {direction.title} work direction:"
    learnings: list[str] = []
    tests: list[str] = []
    for intent in state.original_intents:
        if intent.casefold().startswith(learning_prefix.casefold()):
            learnings.append(intent[len(learning_prefix) :].strip())
        elif intent.casefold().startswith(next_test_prefix.casefold()):
            tests.append(intent[len(next_test_prefix) :].strip())
    return _unique(learnings), _unique(tests)


def _direction_decision_cycle(state: CanonicalState, direction: CareerHypothesis) -> list[str]:
    selection_index = -1
    expected = direction.title.casefold()
    for index, decision in enumerate(state.decisions):
        if decision.gate_id != "career-direction":
            continue
        selected = decision.value.split(":", 1)[-1].strip().casefold()
        if selected == expected:
            selection_index = index
    return [
        decision.value.strip()
        for decision in state.decisions[selection_index + 1 :]
        if decision.gate_id.startswith("path-task_") and decision.value.strip()
    ]


def _human_decision(gate_id: str, value: str) -> str:
    if gate_id == "starting-vector":
        labels = {
            "veteran_service_member": "Veteran or service member",
            "leaving_within_12_months": "leaving within 12 months",
            "active_duty": "active duty",
            "navy": "Navy",
            "army": "Army",
            "marine_corps": "Marine Corps",
            "air_force": "Air Force",
            "space_force": "Space Force",
            "coast_guard": "Coast Guard",
        }
        return " · ".join(labels.get(part.strip(), part.strip()) for part in value.split(" · "))
    if gate_id == "career-direction" and ":" in value:
        return f"Working direction: {value.split(':', 1)[1].strip()}"
    return value


def _date_in_statement(statement: str) -> str | None:
    match = re.search(
        r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+"
        r"(\d{1,2}),\s*(\d{4})\b",
        statement,
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    try:
        return datetime.strptime(match.group(0), "%B %d, %Y").date().isoformat()
    except ValueError:
        return None


def _completed_experiments(state: CanonicalState) -> list[PlanNote]:
    """Project reported findings across every direction, including superseded ones."""
    next_tests: dict[str, str] = {}
    findings: list[PlanNote] = []
    next_test_pattern = re.compile(r"^For my next test of the (.+?) work direction:\s*(.+)$", re.IGNORECASE)
    learning_pattern = re.compile(r"^While testing the (.+?) work direction, I learned:\s*(.+)$", re.IGNORECASE)
    for intent in state.original_intents:
        next_test_match = next_test_pattern.match(intent.strip())
        if next_test_match:
            next_tests[next_test_match.group(1).casefold()] = next_test_match.group(2).strip()
            continue
        learning_match = learning_pattern.match(intent.strip())
        if not learning_match:
            continue
        direction_title = learning_match.group(1).strip()
        test = next_tests.get(direction_title.casefold())
        findings.append(
            PlanNote(
                title=test or f"{direction_title} test",
                detail=learning_match.group(2).strip(),
                source=f"You reported this after testing {direction_title}",
                status="Completed",
            )
        )
    return findings


def _accepted_direction(state: CanonicalState) -> CareerHypothesis | None:
    return next((item for item in state.career_hypotheses if item.status == "accepted"), None)


def _current_gate(state: CanonicalState) -> Gate | None:
    candidates = [
        gate for gate in state.gates if gate.state in {GateState.UNKNOWN, GateState.PARTIAL, GateState.CONFLICTED}
    ]
    return max(candidates, key=lambda gate: gate.value_score, default=None)


def build_transition_plan(state: CanonicalState) -> TransitionPlan:
    direction = _accepted_direction(state)
    direction_decisions = _direction_decision_cycle(state, direction) if direction else []
    plan_direction = None
    if direction:
        direction_reasons = direction_decisions[:-1] if len(direction_decisions) >= 3 else direction_decisions
        plan_direction = PlanDirection(
            title=direction.title,
            why=_unique([direction.rationale, *direction_reasons]),
            alternatives=_unique([item.title for item in state.career_hypotheses if item.status == "candidate"]),
        )

    valid_facts = [fact for fact in state.facts if fact.status == FreshnessStatus.VALID]
    preference_facts = [
        fact
        for fact in valid_facts
        if fact.field_key not in {"general_context", "historical_achievement", "occupational_reference"}
    ]
    what_i_bring = [
        PlanNote(title="Strength", detail=value, source="Direction fit review")
        for value in (direction.capability_matches if direction else [])
    ]
    what_i_bring.extend(
        _fact_note(fact)
        for fact in valid_facts
        if fact.field_key == "historical_achievement"
        and not fact.statement.casefold().startswith("while testing the ")
    )
    if direction:
        what_i_bring.extend(
            PlanNote(title="Supporting source", detail=value, source="Based on") for value in direction.evidence
        )

    latest_by_gate: dict[str, str] = {}
    for decision in state.decisions:
        latest_by_gate[decision.gate_id] = decision.id
    gates_by_id = {gate.id: gate for gate in state.gates}
    current_direction_index = max(
        (index for index, item in enumerate(state.decisions) if item.gate_id == "career-direction"),
        default=-1,
    )
    decisions = [
        PlanDecision(
            decision=_human_decision(decision.gate_id, decision.value),
            context=(gates_by_id[decision.gate_id].title if decision.gate_id in gates_by_id else None),
            decided_at=decision.decided_at.astimezone(UTC).isoformat(),
            current=(
                latest_by_gate[decision.gate_id] == decision.id
                and not (decision.gate_id.startswith("path-task_") and index < current_direction_index)
            ),
        )
        for index, decision in enumerate(state.decisions)
    ]

    active_experiments: list[PlanNote] = []
    completed_experiments = _completed_experiments(state)
    if direction:
        learnings, tests = _direction_cycle(state, direction)
        active_test = tests[-1] if tests else (
            direction_decisions[-1] if len(direction_decisions) >= 3 else direction.first_experiment
        )
        latest_cycle_is_learning = False
        if state.original_intents:
            learning_prefix = f"While testing the {direction.title} work direction, I learned:"
            next_test_prefix = f"For my next test of the {direction.title} work direction:"
            latest_cycle = next(
                (
                    value
                    for value in reversed(state.original_intents)
                    if value.casefold().startswith(learning_prefix.casefold())
                    or value.casefold().startswith(next_test_prefix.casefold())
                ),
                "",
            )
            latest_cycle_is_learning = latest_cycle.casefold().startswith(learning_prefix.casefold())
        if active_test and not latest_cycle_is_learning:
            active_experiments.append(
                PlanNote(
                    title=active_test,
                    detail="Run this test and return with what happened.",
                    source="You chose this test",
                    status="Planned",
                )
            )

    changes = [
        PlanNote(
            title=feedback.headline,
            detail=" ".join(feedback.consequences) or None,
            source="Updated after your approved input",
            date=feedback.created_at.astimezone(UTC).isoformat(),
        )
        for feedback in state.feedback
        if feedback.headline not in {"Your starting point is set.", "That decision changed what comes next."}
    ]
    current_gate = _current_gate(state)
    unresolved: list[PlanNote] = []
    if current_gate:
        unresolved.append(PlanNote(title=current_gate.question, detail=current_gate.why, status="Open"))
    if direction:
        unresolved.extend(
            PlanNote(title=gap, source="Direction fit review", status="Open") for gap in direction.possible_gaps
        )

    next_actions = [PlanNote(title=task.title, detail=task.reason, status="Next") for task in state.active_tasks]
    if active_experiments:
        next_actions.insert(
            0,
            PlanNote(title=active_experiments[0].title, detail="Run the test, then add what happened.", status="Next"),
        )
    elif current_gate:
        next_actions.insert(0, PlanNote(title=current_gate.question, detail=current_gate.why, status="Decide"))

    timeline: list[PlanNote] = []
    if state.transition_month:
        timeline.append(
            PlanNote(
                title="Planned separation month",
                date=state.transition_month,
                date_kind="veteran_target",
                source="You entered this target",
            )
        )
    has_explicit_transition_date = any(decision.gate_id == "planned-transition-date" for decision in state.decisions)
    if state.transition_date and (has_explicit_transition_date or not state.transition_month):
        timeline.append(
            PlanNote(title="Separation date", date=state.transition_date, date_kind="known", source="Current plan")
        )
    if state.pcs_relocation_date:
        timeline.append(
            PlanNote(
                title="Relocation window",
                date=state.pcs_relocation_date,
                date_kind="veteran_target",
                source="You entered this target",
            )
        )
    for fact in valid_facts:
        stated_date = _date_in_statement(fact.statement)
        if fact.effective_at or stated_date or any(term in fact.field_key for term in ("date", "deadline", "timing")):
            is_veteran_target = bool(
                stated_date
                and any(term in fact.statement.casefold() for term in ("want", "plan", " by ", "will "))
            )
            is_known_date = bool(
                stated_date
                and any(
                    term in fact.statement.casefold()
                    for term in (" is ", " starts ", "appointment", " due ", "separation date")
                )
            )
            timeline.append(
                PlanNote(
                    title=_human_field(fact.field_key),
                    detail=fact.statement,
                    date=fact.effective_at or stated_date,
                    date_kind=(
                        "known"
                        if fact.effective_at or is_known_date
                        else ("veteran_target" if is_veteran_target else "planned")
                    ),
                    source="You told Military SLICES",
                )
            )

    timeline.sort(key=_timeline_sort_key)

    return TransitionPlan(
        generated_at=datetime.now(UTC).isoformat(),
        objective=state.human_anchor or state.current_goal,
        direction=plan_direction,
        what_i_bring=what_i_bring,
        what_matters_to_me=[_fact_note(fact) for fact in preference_facts],
        decisions=decisions,
        active_experiments=active_experiments,
        completed_experiments=completed_experiments,
        changes=changes,
        unresolved=unresolved,
        next_actions=next_actions,
        timeline=timeline,
    )


def render_plan_html(plan: TransitionPlan) -> str:
    def note_list(items: list[PlanNote], empty: str) -> str:
        if not items:
            return f"<p class=empty>{escape(empty)}</p>"
        rows = []
        for item in items:
            meta = " · ".join(value for value in (item.status, item.date, item.source) if value)
            rows.append(
                "<li><strong>"
                + escape(item.title)
                + "</strong>"
                + (f"<p>{escape(item.detail)}</p>" if item.detail else "")
                + (f"<small>{escape(meta)}</small>" if meta else "")
                + "</li>"
            )
        return "<ul>" + "".join(rows) + "</ul>"

    direction = "<p class=empty>No working direction has been chosen yet.</p>"
    if plan.direction:
        why = note_list([PlanNote(title=value) for value in plan.direction.why], "No reason has been recorded yet.")
        alternatives = note_list(
            [PlanNote(title=value) for value in plan.direction.alternatives],
            "No alternatives are currently being held open.",
        )
        direction = (
            f"<p class=lead><strong>{escape(plan.direction.title)}</strong> "
            f"<span>{escape(plan.direction.status)}</span></p>"
            f"<h3>Why this direction</h3>{why}<h3>Alternatives kept available</h3>{alternatives}"
        )

    decision_items = [
        PlanNote(
            title=item.decision,
            detail=item.context,
            date=item.decided_at,
            status="Current" if item.current else "Earlier",
        )
        for item in plan.decisions
    ]
    generated = datetime.fromisoformat(plan.generated_at).strftime("%B %d, %Y at %I:%M %p UTC")
    objective = escape(plan.objective or "No objective has been recorded yet.")
    bring = note_list(plan.what_i_bring, "Nothing has been recorded here yet.")
    priorities = note_list(plan.what_matters_to_me, "No preferences or constraints have been recorded yet.")
    decision_history = note_list(decision_items, "No decisions have been recorded yet.")
    active_tests = note_list(plan.active_experiments, "No active test is waiting.")
    findings = note_list(plan.completed_experiments, "No test result has been recorded yet.")
    changes = note_list(plan.changes, "No material plan change has been recorded yet.")
    unresolved = note_list(plan.unresolved, "No unresolved item is currently recorded.")
    next_actions = note_list(plan.next_actions, "No next action is currently recorded.")
    timeline = note_list(plan.timeline, "No important date has been recorded yet.")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>My Military SLICES Transition Plan</title><style>
body{{font:16px/1.55 Arial,sans-serif;color:#17212b;max-width:920px;margin:0 auto;padding:32px}}
h1,h2,h3{{line-height:1.2}}h1{{margin-bottom:4px}}
h2{{margin-top:30px;padding-bottom:8px;border-bottom:2px solid #d5a928}}h3{{font-size:1rem}}
.meta,.empty,small{{color:#5b6874}}.lead{{font-size:1.3rem}}
.lead span{{font-size:.8rem;padding:4px 8px;border:1px solid #888;border-radius:12px}}
ul{{padding-left:22px}}li{{margin:10px 0}}li p{{margin:3px 0}}
@media print{{body{{padding:0}}h2{{break-after:avoid}}li{{break-inside:avoid}}}}
</style></head><body>
<header><p>Military SLICES</p><h1>My transition plan</h1>
<p class="meta">Exported {escape(generated)}</p></header>
<section><h2>My objective</h2><p>{objective}</p></section>
<section><h2>My direction</h2>{direction}</section>
<section><h2>What I bring</h2>{bring}</section>
<section><h2>What matters to me</h2>{priorities}</section>
<section><h2>Decisions I’ve made</h2>{decision_history}</section>
<section><h2>What I’m testing</h2>{active_tests}</section>
<section><h2>What I learned</h2>{findings}</section>
<section><h2>What changed my plan</h2>{changes}</section>
<section><h2>What I still need to figure out</h2>{unresolved}</section>
<section><h2>What I need to do next</h2>{next_actions}</section>
<section><h2>Timeline</h2>{timeline}</section>
<footer><p class="meta">This is a snapshot of information and decisions you reviewed in Military SLICES.
It is planning support, not legal, medical, benefits, financial, or employment advice.</p></footer>
</body></html>"""
