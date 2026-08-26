from __future__ import annotations

import json
from pathlib import Path

from military_slices.engine import active_gate, apply_confirmed_input, new_state, orient
from military_slices.models import MilitaryStateSubject, PlanningActor
from military_slices.path_runtime import anchor_domain

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "helm_validation_fixtures.json"


def _fixtures() -> dict[str, dict[str, object]]:
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    assert payload["status"] == "synthetic_draft_only"
    assert payload["external_effects"] is False
    return {item["id"]: item for item in payload["fixtures"]}


def test_resume_readiness_fixture_stops_at_target_role_gate() -> None:
    fixture = _fixtures()["career_resume_readiness"]
    state = apply_confirmed_input(
        new_state("ms-fixture-resume"),
        orient(str(fixture["input"])),
        idempotency_key="fixture-resume-0001",
    )

    assert anchor_domain(state.human_anchor) == fixture["expected_anchor"]
    gate = active_gate(state)
    assert gate is not None
    assert gate.id == fixture["expected_gate"]


def test_insufficient_fixture_requests_one_clarification_and_writes_nothing() -> None:
    fixture = _fixtures()["insufficient_orientation"]
    state = new_state("ms-fixture-unclear")
    result = orient(str(fixture["input"]))

    assert result.sufficient is False
    assert result.clarification_question
    assert state.version == fixture["expected_write_count"]
    assert state.mutation_events == []


def test_conflict_fixture_surfaces_human_gate() -> None:
    fixture = _fixtures()["conflicting_priorities"]
    state = apply_confirmed_input(
        new_state("ms-fixture-conflict"),
        orient(str(fixture["input"])),
        idempotency_key="fixture-conflict-0001",
    )

    gate = active_gate(state)
    assert gate is not None
    assert gate.id == fixture["expected_gate"]


def test_spouse_fixture_preserves_actor_subject_boundary() -> None:
    fixture = _fixtures()["spouse_pcs_subject_integrity"]
    state = apply_confirmed_input(
        new_state("ms-fixture-spouse"),
        orient(str(fixture["input"])),
        idempotency_key="fixture-spouse-0001",
    )

    assert state.planning_actor == PlanningActor.MILITARY_SPOUSE
    assert state.military_state_subject == MilitaryStateSubject.PLANNING_ACTOR_SPOUSE
    assert state.transition_date is None
