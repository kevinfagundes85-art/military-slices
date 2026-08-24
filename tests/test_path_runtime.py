from __future__ import annotations

from datetime import date

import pytest

from military_slices.engine import (
    active_gate,
    apply_artifact_input,
    apply_confirmed_input,
    apply_decision,
    new_state,
    orient,
    reconstitute_state,
)
from military_slices.models import ServiceName
from military_slices.path_runtime import PACK_VERSION, path_boundaries, refresh_path_state


def test_installed_pack_version_and_activation_limits_are_locked() -> None:
    boundaries = path_boundaries()
    assert boundaries["version"] == PACK_VERSION
    assert boundaries["activation_rule"]["max_primary_gates"] == 1
    assert boundaries["activation_rule"]["max_active_tasks"] == 3
    assert boundaries["activation_rule"]["max_supporting_changes_visible"] == 3


def test_artifact_evidence_does_not_manufacture_a_human_anchor() -> None:
    state = apply_artifact_input(
        new_state("ms-artifact-anchor"),
        orient("Navy intelligence analyst. Led research and executive briefings. PMP certification in progress."),
        idempotency_key="artifact-anchor-0001",
    )
    assert state.service == ServiceName.NAVY
    assert state.human_anchor is None
    assert state.career_hypotheses == []
    assert len(state.active_tasks) == 1
    assert active_gate(state).id == "transition-human-anchor"


def test_declared_resume_target_suppresses_unrelated_career_activation() -> None:
    state = apply_confirmed_input(
        new_state("ms-resume-target"),
        orient("Make my resume submission-ready for a program management role."),
        idempotency_key="resume-target-0001",
    )
    assert state.human_anchor is not None
    assert state.path_target_state == "PREPARATION_BASELINE_READY"
    assert len(state.active_tasks) == 3
    assert all("career recommendation" not in task.title.casefold() for task in state.active_tasks)
    assert active_gate(state) is None


def test_generic_resume_anchor_requests_target_without_reauthorizing_document() -> None:
    state = apply_artifact_input(
        new_state("ms-resume-routing"),
        orient("Navy analyst. Led research and program planning."),
        idempotency_key="resume-routing-0001",
    )
    state = apply_decision(
        state,
        gate_id="transition-human-anchor",
        value="Improve a résumé for a specific goal",
        idempotency_key="resume-routing-0002",
    )
    assert active_gate(state).id == "resume-target-role"
    state = apply_decision(
        state,
        gate_id="resume-target-role",
        value="program management roles",
        idempotency_key="resume-routing-0003",
    )
    assert active_gate(state) is None
    assert len(state.active_tasks) == 3
    assert state.career_hypotheses == []


def test_legacy_artifact_only_goal_is_not_migrated_as_human_authority() -> None:
    state = new_state("ms-legacy-artifact")
    state.original_intents = ["Shared a document to update my transition plan."]
    state.current_goal = "Currently pursuing a certification."
    state.human_anchor = None
    migrated = reconstitute_state(state)
    assert migrated.current_goal is None
    assert migrated.human_anchor is None
    assert active_gate(migrated).id == "transition-human-anchor"


@pytest.mark.parametrize(
    ("service", "expected_term"),
    [
        (ServiceName.ARMY, "Army TAP"),
        (ServiceName.NAVY, "Navy Initial Counseling"),
        (ServiceName.MARINE_CORPS, "Transition Readiness Program"),
        (ServiceName.AIR_FORCE, "DAF TAP"),
        (ServiceName.SPACE_FORCE, "DAF TAP"),
        (ServiceName.COAST_GUARD, "Coast Guard TAP"),
    ],
)
def test_same_path_uses_service_appropriate_terminology(service: ServiceName, expected_term: str) -> None:
    state = new_state(f"ms-{service}")
    state.service = service
    state.human_anchor = "Choose an education or training path"
    state.current_goal = state.human_anchor
    state.transition_date = "2027-10-01"
    state = refresh_path_state(state, today=date(2026, 8, 24))
    assert len(state.active_tasks) <= 3
    assert expected_term in state.active_tasks[0].title


def test_date_propagates_to_one_bounded_task_horizon() -> None:
    state = new_state("ms-date-path")
    state.service = ServiceName.COAST_GUARD
    state.separation_type = "retirement"
    state.human_anchor = "Choose an education or training path"
    state.current_goal = state.human_anchor
    state.transition_date = "2028-04-01"
    state = refresh_path_state(state, today=date(2026, 8, 24))
    assert state.current_timeline_window == "A"
    assert state.path_target_state == "TRANSITION_PATH_ORIENTED"
    assert 1 <= len(state.active_tasks) <= 3
    assert "Coast Guard TAP" in state.active_tasks[0].title
