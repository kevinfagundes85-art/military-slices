from __future__ import annotations

from datetime import date

from military_slices.acquisition import build_acquisition_horizon
from military_slices.engine import (
    active_gate,
    apply_confirmed_input,
    apply_decision,
    apply_hypotheses,
    apply_starting_vector,
    deterministic_hypotheses,
    new_state,
    orient,
)
from military_slices.models import LifecyclePosition, ServiceComponent, ServiceName, SliceName
from military_slices.path_runtime import refresh_path_state


def _separated_state(profile_id: str):
    return apply_starting_vector(
        new_state(profile_id),
        operating_role="veteran_service_member",
        lifecycle_position=LifecyclePosition.SEPARATED_1_TO_5_YEARS,
        service=ServiceName.NAVY,
        component=ServiceComponent.ACTIVE_DUTY,
        idempotency_key=f"{profile_id}-vector",
    )


def _accepted_direction(profile_id: str):
    started = _separated_state(profile_id)
    text = (
        "I already work in cyber engineering and want to build technology that helps veterans. "
        "I need remote work with predictable hours and little travel."
    )
    state = apply_confirmed_input(
        started,
        orient(text, context=started),
        idempotency_key=f"{profile_id}-input",
    )
    state = apply_hypotheses(state, deterministic_hypotheses(text, []))
    selected = state.career_hypotheses[0]
    return apply_decision(
        state,
        gate_id="career-direction",
        value=f"explore:{selected.title}",
        idempotency_key=f"{profile_id}-direction",
    )


def test_anchor_activates_exactly_one_smallest_consequential_task() -> None:
    state = new_state("frontier-one")
    state.service = ServiceName.COAST_GUARD
    state.human_anchor = "Choose an education or training path"
    state.current_goal = state.human_anchor
    state.transition_date = "2028-04-01"

    updated = refresh_path_state(state, today=date(2026, 8, 24))

    assert len(updated.active_tasks) == 1
    assert "Coast Guard TAP" in updated.active_tasks[0].title
    assert updated.active_tasks[0].affected_slices == [SliceName.EDUCATION]


def test_resolving_frontier_condition_activates_only_the_next_condition() -> None:
    state = _accepted_direction("frontier-advance")
    first_gate = active_gate(state)
    assert first_gate is not None and first_gate.id.startswith("path-task_")
    assert len(state.active_tasks) == 1

    updated = apply_decision(
        state,
        gate_id=first_gate.id,
        value="A small public work sample would test this assumption.",
        idempotency_key="frontier-advance-answer",
    )
    second_gate = active_gate(updated)

    assert second_gate is not None and second_gate.id != first_gate.id
    assert len(updated.active_tasks) == 1
    assert updated.active_tasks[0].title == second_gate.question


def test_unrelated_rich_context_remains_latent_outside_the_frontier() -> None:
    started = _separated_state("frontier-latent")
    education = apply_decision(
        started,
        gate_id="transition-human-anchor",
        value="Choose education or training",
        idempotency_key="frontier-latent-anchor",
    )
    text = (
        "I want a graduate certificate in AI. "
        "I prefer remote work and will stay near family."
    )
    state = apply_confirmed_input(
        education,
        orient(text, context=education),
        idempotency_key="frontier-latent-input",
    )

    assert state.human_anchor is not None
    assert len(state.active_tasks) == 1
    assert state.active_tasks[0].affected_slices == [SliceName.EDUCATION]
    assert state.latent_fact_count >= 1
    horizon = build_acquisition_horizon(state)
    if horizon is not None:
        assert sum(item.foreground for item in horizon.checklist) == 1


def test_material_conflict_is_the_only_foreground_gate() -> None:
    state = apply_confirmed_input(
        new_state("frontier-block"),
        orient("I need immediate income and I plan full-time school after I leave."),
        idempotency_key="frontier-block-input",
    )
    gate = active_gate(state)
    horizon = build_acquisition_horizon(state)

    assert gate is not None and gate.id == "priority-first-six-months"
    assert len(state.active_tasks) <= 1
    assert horizon is not None
    assert horizon.active_gate_id == gate.id
    assert sum(item.foreground for item in horizon.checklist) == 1
    assert all(item.status != "unresolved" for item in horizon.checklist[1:])
