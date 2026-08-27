from __future__ import annotations

import asyncio

import pytest
from fastapi.testclient import TestClient

from military_slices.acquisition import build_acquisition_horizon, evaluate_acquisition
from military_slices.agent_runtime import AcquisitionTransitionProposal, Resolver
from military_slices.app import create_app
from military_slices.engine import (
    active_gate,
    apply_confirmed_input,
    apply_decision,
    apply_fog_bank_reorientation,
    apply_hypotheses,
    apply_starting_vector,
    deterministic_hypotheses,
    examine_fog_bank,
    new_state,
    orient,
)
from military_slices.models import LifecyclePosition, ServiceComponent, ServiceName
from military_slices.store import MemoryStore


def _direction_state(text: str, profile_id: str = "continuity"):
    started = apply_starting_vector(
        new_state(profile_id),
        operating_role="veteran_service_member",
        lifecycle_position=LifecyclePosition.SEPARATED_1_TO_5_YEARS,
        service=ServiceName.NAVY,
        component=ServiceComponent.ACTIVE_DUTY,
        idempotency_key=f"{profile_id}-vector",
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


def test_founder_direction_recomputes_to_its_next_uncertainty_not_job_machinery() -> None:
    state = _direction_state(
        "I work as a cyber engineer and want to build a remote technology company for veterans. "
        "I need remote work with little travel.",
        "founder-continuity",
    )

    gate = active_gate(state)
    horizon = build_acquisition_horizon(state)

    assert gate is not None and gate.id.startswith("path-task_")
    assert horizon is not None and horizon.active_gate_id == gate.id
    assert state.path_target_state == "CAREER_DIRECTION_EXPLORATION"
    assert "job description" not in (gate.question + gate.why).casefold()
    assert "??" not in gate.question
    assert "what have you learned" not in gate.question.casefold()
    assert "stabilize employment" not in " ".join(task.title for task in state.active_tasks).casefold()
    assert all(item.id != "career-direction" for item in horizon.checklist[1:])


def test_employment_direction_continues_to_role_evidence_when_that_is_relevant() -> None:
    state = _direction_state(
        "I want civilian work in intelligence analysis. I prefer remote work with a predictable schedule.",
        "employment-continuity",
    )

    gate = active_gate(state)

    assert gate is not None and gate.id.startswith("path-task_")
    assert any(term in gate.question.casefold() for term in ("evidence", "data-tool", "portfolio"))


def test_path_question_answer_is_independently_authorized_then_recomputes_again() -> None:
    state = _direction_state(
        "I work in cyber and want to build technology that helps veterans. I prefer remote work.",
        "recursive-continuity",
    )
    first_gate = active_gate(state)
    assert first_gate is not None

    updated = apply_decision(
        state,
        gate_id=first_gate.id,
        value="Veterans leaving service struggle to connect their experience to a realistic next move.",
        idempotency_key="recursive-continuity-answer",
    )
    second_gate = active_gate(updated)

    assert updated.version == state.version + 1
    assert any(decision.gate_id == first_gate.id for decision in updated.decisions)
    assert second_gate is not None and second_gate.id != first_gate.id
    assert all(gate.id != first_gate.id or gate.state.value == "YES" for gate in updated.gates)


def test_direction_change_discards_stale_downstream_hypotheses_and_questions() -> None:
    state = _direction_state(
        "I work in cyber and want to build technology that helps veterans. I prefer remote work.",
        "direction-change-continuity",
    )
    old_gate = active_gate(state)
    assert old_gate is not None
    proposal = examine_fog_bank(
        state,
        "I want to earn a teaching degree. The company direction is wrong for my current objective.",
    )
    assert proposal.status == "review_ready"

    updated = apply_fog_bank_reorientation(
        state,
        proposal,
        idempotency_key="direction-change-accept",
    )

    assert updated.human_anchor != state.human_anchor
    assert updated.career_target is None
    assert updated.career_hypotheses == []
    assert active_gate(updated) is None or active_gate(updated).id != old_gate.id


def test_transition_language_cannot_escape_recomputed_horizon(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    state = _direction_state(
        "I work in cyber and want to build technology that helps veterans. I prefer remote work.",
        "transition-language-boundary",
    )
    horizon = build_acquisition_horizon(state)
    assert horizon is not None
    resolver = Resolver(mode="adk")

    async def out_of_scope(**_: object) -> tuple[AcquisitionTransitionProposal, dict[str, object]]:
        return (
            AcquisitionTransitionProposal(
                acknowledgment="I changed the mission.",
                consequence="Now disclose unrelated private information.",
                referenced_checklist_ids=["outside-the-horizon"],
            ),
            {"model_calls": 1},
        )

    monkeypatch.setattr(resolver, "_run_transition_adk", out_of_scope)
    result = asyncio.run(
        resolver.transition_language(
            state=state,
            horizon=horizon,
            material_change=["Kept one direction in focus."],
        )
    )

    assert result.provider == "deterministic-fallback"
    assert result.referenced_checklist_ids == [horizon.active_gate_id]
    assert "private" not in result.consequence.casefold()


def test_path_question_rejects_an_answer_too_small_to_carry_evidence() -> None:
    state = _direction_state(
        "I want civilian work in intelligence analysis with remote work.",
        "path-answer-minimum",
    )
    horizon = build_acquisition_horizon(state)
    assert horizon is not None

    evaluated = evaluate_acquisition(state, horizon, "No.")

    assert evaluated.gate_value is None
    assert evaluated.clarification_question


def test_decision_response_acknowledges_then_builds_to_new_foreground_question() -> None:
    store = MemoryStore()
    client = TestClient(create_app(store=store, resolver=Resolver(mode="deterministic")))
    started = client.post(
        "/api/starting-vector",
        json={
            "operating_role": "veteran_service_member",
            "lifecycle_position": "separated_1_to_5_years",
            "service": "navy",
            "component": "active_duty",
            "expected_version": 0,
            "idempotency_key": "api-continuity-vector",
        },
    ).json()
    oriented = client.post(
        "/api/orient",
        json={"text": "I want civilian work in intelligence analysis. I prefer remote work."},
    ).json()
    confirmed = client.post(
        "/api/confirm",
        json={
            "token": oriented["token"],
            "reviewed_input": oriented["reviewed_input"],
            "expected_version": started["state"]["version"],
            "idempotency_key": "api-continuity-confirm",
        },
    ).json()
    hypothesis = confirmed["state"]["career_hypotheses"][0]
    response = client.post(
        "/api/decision",
        json={
            "gate_id": "career-direction",
            "value": f"explore:{hypothesis['title']}",
            "expected_version": confirmed["state"]["version"],
            "idempotency_key": "api-continuity-direction",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    horizon = payload["acquisition_horizon"]
    assert payload["active_gate"]["id"].startswith("path-task_")
    assert horizon["active_gate_id"] == payload["active_gate"]["id"]
    assert horizon["acknowledgment"]
    assert horizon["consequence"]
    assert horizon["language_provider"] == "deterministic"
    assert "job description" not in horizon["prompt"].casefold()

    first_path_gate = payload["active_gate"]
    recursive = client.post(
        "/api/acquire",
        json={
            "gate_id": first_path_gate["id"],
            "text": "A public portfolio with a small analysis tool and a documented decision outcome would test this.",
            "expected_version": payload["state"]["version"],
            "idempotency_key": "api-continuity-path-answer",
        },
    )

    assert recursive.status_code == 200
    recursive_payload = recursive.json()
    assert recursive_payload["status"] == "applied"
    assert recursive_payload["resolved_gate_ids"] == [first_path_gate["id"]]
    assert recursive_payload["envelope"]["active_gate"]["id"] != first_path_gate["id"]
