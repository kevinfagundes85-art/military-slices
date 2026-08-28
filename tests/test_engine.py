from __future__ import annotations

from military_slices.engine import (
    active_gate,
    apply_confirmed_input,
    apply_decision,
    apply_hypotheses,
    deterministic_hypotheses,
    new_state,
    orient,
)
from military_slices.models import GateState, SliceName, SurfaceType

DEMO = (
    "I separate from the Coast Guard in March 2027. I led a maintenance team and coordinated "
    "parts, schedules, inspections, and emergency repairs, but I do not want shift work or "
    "constant travel. My family needs to stay near Tacoma. I am open to a credential if it can "
    "finish before I leave, and I am not sure what civilian job title fits."
)


def test_messy_input_orients_without_inventing_facts() -> None:
    result = orient(DEMO)
    assert result.sufficient is True
    assert set(result.affected_slices) == set(SliceName)
    assert all(statement.text in DEMO for statement in result.statements)
    assert not any("salary" in statement.text.lower() for statement in result.statements)


def test_unclear_input_remains_unclear() -> None:
    result = orient("HELM breaks the internet and this proves everything.")
    assert result.sufficient is False
    assert result.affected_slices == []
    assert result.clarification_question is not None


def test_stay_near_location_language_is_not_lost() -> None:
    result = orient("I need to stay near Tacoma and want steady work.")
    assert SliceName.LOCATION in result.affected_slices


def test_stay_within_distance_location_language_is_not_lost() -> None:
    result = orient("My spouse got a job in Seattle, so we need to stay within 30 minutes.")
    assert SliceName.LOCATION in result.affected_slices


def test_shared_transition_gate_is_one_date_interaction() -> None:
    state = apply_confirmed_input(
        new_state("ms-test"),
        orient("I need a civilian job but do not know when I separate."),
        idempotency_key="input-0001",
    )
    transition_gates = [gate for gate in state.gates if gate.id == "planned-transition-date"]
    assert len(transition_gates) == 1
    assert transition_gates[0].surface == SurfaceType.DATE
    assert set(transition_gates[0].affected_slices) == set(SliceName)
    assert active_gate(state).id == "planned-transition-date"


def test_confirmed_date_closes_shared_gate_and_changes_feedback() -> None:
    state = apply_confirmed_input(
        new_state("ms-test"), orient("I want civilian work near home."), idempotency_key="input-0002"
    )
    state = apply_decision(
        state,
        gate_id="planned-transition-date",
        value="2027-03-15",
        idempotency_key="decision-0001",
    )
    assert state.transition_date == "2027-03-15"
    assert all(gate.id != "planned-transition-date" for gate in state.gates)
    assert len(state.feedback[-1].consequences) >= 3


def test_repeat_input_is_idempotent() -> None:
    state = new_state("ms-test")
    once = apply_confirmed_input(state, orient(DEMO), idempotency_key="input-repeat")
    twice = apply_confirmed_input(once, orient(DEMO), idempotency_key="input-repeat")
    assert twice.version == once.version
    assert len(twice.facts) == len(once.facts)


def test_semantic_repeat_deduplicates_exact_human_statements() -> None:
    state = apply_confirmed_input(new_state("ms-test"), orient(DEMO), idempotency_key="first-0001")
    repeated = apply_confirmed_input(state, orient(DEMO), idempotency_key="second-0001")
    assert len(repeated.facts) == len(state.facts)
    assert repeated.telemetry.duplicate_questions_avoided > 0


def test_conflict_is_typed_and_human_resolvable() -> None:
    state = apply_confirmed_input(
        new_state("ms-test"),
        orient("I need immediate income and I plan full-time school after I leave."),
        idempotency_key="conflict-0001",
    )
    gate = active_gate(state)
    assert gate is not None
    assert gate.id == "priority-first-six-months"
    assert gate.state == GateState.CONFLICTED
    assert gate.surface == SurfaceType.CONFLICT
    resolved = apply_decision(
        state,
        gate_id=gate.id,
        value="A staged combination",
        idempotency_key="conflict-decision",
    )
    assert not resolved.conflicts


def test_rejected_roles_never_return_from_deterministic_resolver() -> None:
    first = deterministic_hypotheses("I worked in military logistics and supply.", [])
    rejected = [first[0].title]
    second = deterministic_hypotheses("I worked in military logistics and supply.", rejected)
    assert rejected[0] not in [item.title for item in second]


def test_ai_tool_goal_produces_product_builder_directions() -> None:
    hypotheses = deterministic_hypotheses("I want to build AI tools for veterans.", [])

    assert hypotheses[0].title == "Veteran-focused AI product builder"
    assert any("AI product" in item.title for item in hypotheses)


def test_explicit_veteran_transition_work_survives_unrelated_military_background() -> None:
    hypotheses = deterministic_hypotheses(
        "I worked in Navy logistics, but I want to explore veteran transition support.",
        [],
    )

    assert hypotheses[0].title == "Veteran transition program coordinator"
    assert all("Logistics Analyst" != item.title for item in hypotheses)


def test_novel_product_platform_goal_is_transition_relevant() -> None:
    result = orient("I want to build a peer-to-peer disaster logistics platform for Guard families.")

    assert result.sufficient is True
    assert SliceName.CAREER in result.affected_slices
    assert SliceName.LOCATION in result.affected_slices


def test_explicit_rejection_changes_later_reasoning_without_looping() -> None:
    state = apply_confirmed_input(
        new_state("ms-test"),
        orient("I led military maintenance scheduling and do not want shift work."),
        idempotency_key="reject-0001",
    )
    state = apply_hypotheses(
        state,
        deterministic_hypotheses("military maintenance scheduling", []),
    )
    rejected_title = state.career_hypotheses[0].title
    updated = apply_decision(
        state,
        gate_id="career-direction",
        value=f"reject:{rejected_title}",
        idempotency_key="reject-0002",
    )
    assert rejected_title in updated.rejected_roles
    assert rejected_title not in [item.title for item in updated.career_hypotheses]
    assert len(updated.career_hypotheses) <= 3
    career_gate = next(gate for gate in updated.gates if gate.id == "career-direction")
    assert career_gate.state == GateState.PARTIAL
    assert rejected_title not in career_gate.options


def test_exploring_one_direction_does_not_reject_the_others() -> None:
    state = apply_confirmed_input(
        new_state("ms-test"), orient("I led military logistics and prefer steady work."), idempotency_key="select-0001"
    )
    state = apply_hypotheses(state, deterministic_hypotheses("military logistics", []))
    selected = state.career_hypotheses[0].title
    updated = apply_decision(
        state,
        gate_id="career-direction",
        value=f"explore:{selected}",
        idempotency_key="select-0002",
    )
    assert not updated.rejected_roles
    assert any(item.status == "candidate" for item in updated.career_hypotheses)
    assert any(item.status == "accepted" for item in updated.career_hypotheses)


def test_time_change_preserves_unrelated_facts() -> None:
    state = apply_confirmed_input(
        new_state("ms-test"), orient("I want remote work and will not relocate."), idempotency_key="time-0001"
    )
    state = apply_decision(
        state,
        gate_id="planned-transition-date",
        value="2027-03-01",
        idempotency_key="time-0002",
    )
    before = [fact.model_dump() for fact in state.facts]
    state.transition_date = None
    state.gates.append(
        next(
            gate
            for gate in apply_confirmed_input(
                new_state("ms-other"), orient("I want work."), idempotency_key="time-0003"
            ).gates
            if gate.id == "planned-transition-date"
        )
    )
    changed = apply_decision(
        state,
        gate_id="planned-transition-date",
        value="2027-05-01",
        idempotency_key="time-0004",
    )
    assert [fact.model_dump() for fact in changed.facts] == before
