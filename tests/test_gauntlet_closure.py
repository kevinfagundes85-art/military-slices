from __future__ import annotations

from copy import deepcopy

import pytest

from military_slices.engine import (
    active_gate,
    apply_confirmed_input,
    apply_decision,
    apply_revalidation,
    new_state,
    orient,
    recompute_state,
)
from military_slices.models import CanonicalState, ExecutionState, FreshnessStatus
from military_slices.path_runtime import anchor_domain, resume_target_specificity
from military_slices.temporal import current_impact

FROZEN_TEMPORAL_FAILURES = (
    ("Army", "June 2027", "Program Manager", "Defense Program Manager"),
    ("Navy", "June 2027", "Program Manager", "Defense Program Manager"),
    ("Marine Corps", "June 2027", "Program Manager", "Defense Program Manager"),
    ("Air Force", "June 2027", "Program Manager", "Defense Program Manager"),
    ("Space Force", "June 2027", "Program Manager", "Defense Program Manager"),
    ("Coast Guard", "June 2027", "Program Manager", "Defense Program Manager"),
    ("Army", "December 2028", "Logistics Manager", "Senior Logistics Manager"),
    ("Navy", "June 2028", "Technical Program Manager", "Senior Technical Program Manager"),
    ("Air Force", "January 2027", "Aviation Safety Manager", "Senior Aviation Safety Manager"),
    ("Space Force", "November 2026", "Space Systems Analyst", "Senior Space Systems Analyst"),
)


@pytest.mark.parametrize(("service", "when", "first_target", "next_target"), FROZEN_TEMPORAL_FAILURES)
def test_exact_frozen_preference_last_failures_now_revalidate(
    service: str,
    when: str,
    first_target: str,
    next_target: str,
) -> None:
    state = new_state(f"frozen-{service}")
    state = apply_confirmed_input(
        state,
        orient(
            f"I leave the {service} in {when}. My career target is {first_target}. "
            "I will stay local and want predictable hours."
        ),
        idempotency_key=f"first-{service}-0001",
    )
    assert state.human_anchor == "Find civilian work"
    assert anchor_domain(state.human_anchor) == "employment"

    changed = apply_confirmed_input(
        state,
        orient(f"My career target is {next_target}."),
        idempotency_key=f"change-{service}-0002",
    )
    impact = current_impact(changed)
    assert impact is not None
    assert impact.dependent_field == "relocation_willingness"

    revalidated, wrote = apply_revalidation(
        changed,
        impact_id=impact.id,
        action="confirm",
        value=None,
        idempotency_key=f"confirm-{service}-0003",
    )
    assert wrote
    assert current_impact(revalidated) is None


@pytest.mark.parametrize("service", ("Army", "Navy", "Marine Corps", "Air Force", "Space Force", "Coast Guard"))
def test_frozen_employment_first_controls_remain_passing(service: str) -> None:
    state = apply_confirmed_input(
        new_state(f"control-{service}"),
        orient(
            f"I leave the {service} in June 2027. I want civilian work with predictable hours. "
            "My career target is Program Manager. I will stay local."
        ),
        idempotency_key=f"control-first-{service}-0001",
    )
    changed = apply_confirmed_input(
        state,
        orient("My career target is Defense Program Manager."),
        idempotency_key=f"control-change-{service}-0002",
    )
    assert state.human_anchor == changed.human_anchor == "Find civilian work"
    assert current_impact(changed) is not None


ANCHOR_EQUIVALENCE_PACKETS = (
    "I want civilian work. I will stay local. I want predictable hours.",
    "I will stay local. I want predictable hours. I want civilian work.",
    "Predictable hours matter; I want civilian work; I will stay local.",
    "Stay local, but I want civilian employment with predictable hours.",
    "I want civilian employment with predictable hours, and I will stay local.",
    "My goal is civilian work. Family means I must stay local. Predictable hours matter.",
    "Because family cannot move, I will stay local. My goal is civilian employment.",
    "I prefer predictable hours. My career target is Program Manager. I will stay local.",
    "I will stay local and prefer predictable hours. My career target is Program Manager.",
    "My career target: Program Manager; stay local; predictable hours.",
    "Help me find civilian work. I cannot relocate and I prefer predictable hours.",
    "I cannot relocate. Help me find civilian work with predictable hours.",
    "Compare civilian career options for me. Keep the search local with predictable hours.",
    "Keep the search local. Compare civilian career options with predictable hours.",
    "I need a civilian job before I separate. I will stay local. Predictable hours matter.",
    "Predictable hours matter. Before I separate, I need a civilian job. I will stay local.",
    "Before separation I need civilian work; my family cannot move yet.",
    "My family cannot move yet. I need civilian work before separation.",
    "Civilian work is my goal—local only, with predictable hours.",
    "Local only and predictable hours. My goal is civilian work.",
    "I want to become a program manager. I will not relocate.",
    "I will not relocate. I want to become a program manager.",
    "My job target is Program Manager; remote is preferred.",
    "Remote is preferred. My job target is Program Manager.",
    "I want civilian work, but my spouse cannot move yet and shift work is out.",
)


@pytest.mark.parametrize("text", ANCHOR_EQUIVALENCE_PACKETS)
def test_anchor_equivalence_matrix_is_order_invariant(text: str) -> None:
    state = apply_confirmed_input(
        new_state("equivalence"),
        orient(text),
        idempotency_key=f"equivalence-{ANCHOR_EQUIVALENCE_PACKETS.index(text):04d}",
    )
    assert state.human_anchor == "Find civilian work"
    assert anchor_domain(state.human_anchor) == "employment"
    assert state.path_target_state == "PATH_IDENTIFIED"
    assert active_gate(state) is not None
    assert active_gate(state).id == "planned-transition-date"
    assert state.execution.state == ExecutionState.ACTIVE


def test_equal_authority_cross_domain_objectives_require_human_anchor_gate() -> None:
    state = apply_confirmed_input(
        new_state("ambiguous-anchor"),
        orient("I want civilian work. I want to choose an education program."),
        idempotency_key="ambiguous-anchor-0001",
    )
    assert state.human_anchor is None
    assert active_gate(state) is not None
    assert active_gate(state).id == "transition-human-anchor"
    assert state.telemetry.anchor_selection_reason_code == "ambiguous_equal_authority_objectives"


def test_compound_compare_request_preserves_leading_objective_across_conjunctions() -> None:
    state = apply_confirmed_input(
        new_state("compound-compare-anchor"),
        orient(
            "I recently left the Air Force. I want to compare program delivery and customer success work, "
            "keep normal daytime hours, and use my training leadership experience."
        ),
        idempotency_key="compound-compare-anchor-0001",
    )
    assert state.human_anchor == "Find civilian work"
    assert anchor_domain(state.human_anchor) == "employment"


def test_execution_state_active_paralyzed_active_complete_and_persists() -> None:
    state = apply_confirmed_input(
        new_state("execution-journey"),
        orient("I want civilian work with predictable hours."),
        idempotency_key="execution-active-0001",
    )
    assert state.execution.state == ExecutionState.ACTIVE

    state = apply_confirmed_input(
        state,
        orient("I need immediate income and full-time education in the same first six months."),
        idempotency_key="execution-conflict-0002",
    )
    assert state.execution.state == ExecutionState.PARALYZED
    assert state.execution.blocking_gate_id == "priority-first-six-months"
    assert state.execution.blocked_transition is not None

    state = apply_confirmed_input(
        state,
        orient("I led 20 people and managed operational schedules."),
        idempotency_key="execution-resume-evidence-0003",
    )
    assert state.execution.state == ExecutionState.PARALYZED
    assert any("led 20 people" in fact.statement.casefold() for fact in state.facts)

    state = apply_decision(
        state,
        gate_id="priority-first-six-months",
        value="Immediate income",
        idempotency_key="execution-resolve-0004",
    )
    assert state.execution.state == ExecutionState.ACTIVE
    assert state.execution.resolving_authority is not None
    assert state.execution.blocked_transition is None

    state = apply_confirmed_input(
        state,
        orient("I accepted a civilian job as a Program Manager. This goal is complete."),
        idempotency_key="execution-complete-0005",
    )
    assert state.execution.state == ExecutionState.COMPLETE
    assert state.active_tasks == []

    reloaded = CanonicalState.model_validate_json(state.model_dump_json())
    reloaded = recompute_state(reloaded)
    assert reloaded.execution.state == ExecutionState.COMPLETE
    assert reloaded.active_tasks == []


def test_stale_fact_cannot_create_paralysis() -> None:
    state = apply_confirmed_input(
        new_state("stale-no-paralysis"),
        orient("I want civilian work. I will stay local."),
        idempotency_key="stale-anchor-0001",
    )
    relocation = next(fact for fact in state.facts if fact.field_key == "relocation_willingness")
    relocation.status = FreshnessStatus.STALE
    state.conflicts.append("The role requires relocation but the plan says stay local.")
    state = recompute_state(state)
    assert state.execution.state != ExecutionState.PARALYZED


@pytest.mark.parametrize(
    ("text", "expected"),
    (
        ("Make my résumé submission-ready for Senior Program Manager.", "concrete"),
        ("Make my résumé ready for a target role.", "generic"),
        ("Make my résumé ready, but I don't have a target role yet.", "negated"),
        ("Make my résumé ready for some role.", "generic"),
        ("Make my résumé ready for this uploaded job posting.", "concrete"),
    ),
)
def test_resume_target_specificity_matrix(text: str, expected: str) -> None:
    assert resume_target_specificity(text) == expected
    state = apply_confirmed_input(
        new_state(f"resume-{expected}"),
        orient(text),
        idempotency_key=f"resume-{expected}-0001",
    )
    gate_ids = {gate.id for gate in state.gates}
    assert ("resume-target-role" not in gate_ids) == (expected == "concrete")


def test_resume_target_change_and_clear_reopens_gate() -> None:
    state = apply_confirmed_input(
        new_state("resume-change-clear"),
        orient("Make my résumé submission-ready for Project Manager."),
        idempotency_key="resume-concrete-0001",
    )
    assert "resume-target-role" not in {gate.id for gate in state.gates}

    state = apply_confirmed_input(
        state,
        orient("My target role is Operations Manager."),
        idempotency_key="resume-change-0002",
    )
    assert state.career_target == "Operations Manager"

    state = apply_confirmed_input(
        state,
        orient("Clear my target role; I have not chosen the specific role."),
        idempotency_key="resume-clear-0003",
    )
    assert state.career_target is None
    assert "resume-target-role" in {gate.id for gate in state.gates}


def test_legacy_profile_without_execution_normalizes_additively() -> None:
    payload = new_state("legacy-execution").model_dump(mode="json")
    payload.pop("execution")
    legacy = CanonicalState.model_validate(payload)
    assert legacy.execution.state == ExecutionState.ACTIVE
    assert recompute_state(deepcopy(legacy)).execution.derived_from_version == legacy.version
