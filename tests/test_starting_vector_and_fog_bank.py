from __future__ import annotations

from fastapi.testclient import TestClient

from military_slices.agent_runtime import Resolver
from military_slices.app import create_app
from military_slices.control import lens_projections
from military_slices.engine import (
    active_gate,
    apply_confirmed_input,
    apply_decision,
    apply_fog_bank_reorientation,
    apply_starting_vector,
    examine_fog_bank,
    new_state,
    orient,
    reconstitute_state,
)
from military_slices.models import (
    LifecyclePosition,
    MilitaryStateSubject,
    PlanningActor,
    ServiceComponent,
    ServiceName,
    SliceName,
)
from military_slices.store import MemoryStore

ACCEPTANCE_INPUT = (
    "Left the military 3 years ago after 20 years working with difficult technology and cyber problems. "
    "I've been working as a cyber engineer but I want to build something cool with AI to make an "
    "impact on everyone possible."
)

FOG_INPUT = (
    "I already left the military three years ago. I'm already working as a cyber engineer. "
    "This isn't about finding my first civilian job; I'm trying to figure out what I should build or do next."
)

TARGET_RELATIVE_HYPOTHETICAL = (
    "What if I upskill with a home lab and build a usable website for veterans leaving the service?"
)


def _vector_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "operating_role": "veteran_service_member",
        "lifecycle_position": "separated_1_to_5_years",
        "service": "navy",
        "component": "active_duty",
        "expected_version": 0,
        "idempotency_key": "starting-vector-0001",
    }
    payload.update(overrides)
    return payload


def _started_state() -> object:
    return apply_starting_vector(
        new_state("ms-vector-test"),
        operating_role="veteran_service_member",
        lifecycle_position=LifecyclePosition.SEPARATED_1_TO_5_YEARS,
        service=ServiceName.NAVY,
        component=ServiceComponent.ACTIVE_DUTY,
        idempotency_key="starting-vector-0001",
    )


def _wrong_frame_state() -> object:
    state = apply_starting_vector(
        new_state("ms-fog-test"),
        operating_role="veteran_service_member",
        lifecycle_position=LifecyclePosition.LEAVING_WITHIN_12_MONTHS,
        service=ServiceName.NAVY,
        component=ServiceComponent.ACTIVE_DUTY,
        idempotency_key="wrong-vector-0001",
    )
    state = apply_confirmed_input(
        state,
        orient("I need civilian work.", context=state),
        idempotency_key="wrong-anchor-0001",
    )
    return apply_decision(
        state,
        gate_id="planned-transition-date",
        value="2027-06-01",
        idempotency_key="wrong-date-0001",
    )


def test_starting_vector_is_one_trusted_persistent_mutation() -> None:
    store = MemoryStore()
    client = TestClient(create_app(store=store))

    response = client.post("/api/starting-vector", json=_vector_payload())

    assert response.status_code == 200
    state = response.json()["state"]
    assert state["version"] == 1
    assert state["starting_vector_complete"] is True
    assert state["planning_actor"] == "veteran"
    assert state["military_state_subject"] == "planning_actor"
    assert state["lifecycle_position"] == "separated_1_to_5_years"
    assert state["service"] == "navy"
    assert state["component_status"] == "active_duty"
    assert state["mutation_events"][-1]["mutation_kind"] == "starting_vector"
    assert state["mutation_events"][-1]["actor"]["trusted"] is True


def test_role_mapping_preserves_planner_and_military_subject() -> None:
    spouse = apply_starting_vector(
        new_state("ms-spouse"),
        operating_role="spouse_partner",
        lifecycle_position=LifecyclePosition.CURRENTLY_SERVING,
        service=ServiceName.ARMY,
        component=ServiceComponent.ACTIVE_DUTY,
        idempotency_key="spouse-vector-0001",
    )
    counselor = apply_starting_vector(
        new_state("ms-counselor"),
        operating_role="counselor_supporter",
        lifecycle_position=LifecyclePosition.LEAVING_WITHIN_12_MONTHS,
        service=ServiceName.AIR_FORCE,
        component=ServiceComponent.RESERVE,
        idempotency_key="counselor-vector-0001",
    )

    assert spouse.planning_actor == PlanningActor.MILITARY_SPOUSE
    assert spouse.military_state_subject == MilitaryStateSubject.PLANNING_ACTOR_SPOUSE
    assert counselor.planning_actor == PlanningActor.COUNSELOR_SUPPORTER
    assert counselor.military_state_subject == MilitaryStateSubject.SUPPORTED_PERSON


def test_acceptance_scenario_does_not_become_first_civilian_job_transition() -> None:
    started = _started_state()
    result = orient(ACCEPTANCE_INPUT, context=started)
    state = apply_confirmed_input(started, result, idempotency_key="acceptance-input-0001")

    assert state.human_anchor != "Find civilian work"
    assert state.lifecycle_position == LifecyclePosition.SEPARATED_1_TO_5_YEARS
    assert state.current_timeline_window == "H"
    assert state.stage == "STABILIZE"
    assert all(gate.id != "planned-transition-date" for gate in state.gates)
    assert active_gate(state) is not None
    assert active_gate(state).id == "career-direction"
    career = next(item for item in lens_projections(state) if item.name == SliceName.CAREER)
    assert "one date clarifies" not in career.summary.casefold()


def test_separated_undecided_veteran_gets_a_real_direction_choice_without_a_future_date() -> None:
    state = apply_decision(
        _started_state(),
        gate_id="transition-human-anchor",
        value="I am still deciding",
        idempotency_key="separated-undecided-0001",
    )
    gate = active_gate(state)

    assert state.transition_date is None
    assert gate is not None
    assert gate.id == "transition-direction"
    assert gate.options == [
        "Civilian work",
        "Education or training",
        "Location and family fit",
    ]
    assert state.feedback[-1].consequences == [
        "Kept work, education, and location open.",
        "Put one clear direction choice in front of you next.",
    ]

    advanced = apply_decision(
        state,
        gate_id="transition-direction",
        value="Civilian work",
        idempotency_key="separated-direction-0002",
    )
    assert advanced.human_anchor == "Find civilian work"
    assert active_gate(advanced) is None or active_gate(advanced).id != "transition-direction"


def test_remote_ai_position_is_work_context_not_a_location_fact() -> None:
    result = orient("I want to take a different route and slowly transition to a remote AI position.")

    assert result.sufficient is True
    assert result.affected_slices == [SliceName.CAREER]
    assert result.statements[0].affected_slices == [SliceName.CAREER]


def test_deterministic_timeline_cannot_be_silently_overridden_by_free_text() -> None:
    started = _started_state()

    result = orient("I expect to leave active service next spring for civilian work.", context=started)

    assert result.sufficient is False
    assert result.conflicts
    assert "timeline" in result.clarification_question.casefold()
    assert started.lifecycle_position == LifecyclePosition.SEPARATED_1_TO_5_YEARS
    assert started.version == 1


def test_what_if_accepts_a_target_relative_experiment_without_writing_truth() -> None:
    store = MemoryStore()
    client = TestClient(create_app(store=store, resolver=Resolver(mode="deterministic")))
    client.get("/api/state")
    vector = client.post("/api/starting-vector", json=_vector_payload()).json()
    oriented = client.post("/api/orient", json={"text": ACCEPTANCE_INPUT}).json()
    confirmed = client.post(
        "/api/confirm",
        json={
            "token": oriented["token"],
            "reviewed_input": oriented["reviewed_input"],
            "expected_version": vector["state"]["version"],
            "idempotency_key": "target-relative-confirm-0001",
        },
    ).json()
    before = client.get("/api/state").json()

    response = client.post("/api/what-if", json={"text": TARGET_RELATIVE_HYPOTHETICAL})

    assert response.status_code == 200
    branch = response.json()
    assert branch["modification_kind"] == "target_experiment"
    assert branch["modification_value"] == TARGET_RELATIVE_HYPOTHETICAL.removeprefix("What if ")
    assert branch["affected_gates"] == ["career-direction"]
    assert branch["affected_slices"] == ["career", "resume"]
    assert confirmed["state"]["human_anchor"] in branch["consequences"][0]
    assert "current goal" in branch["evidence_basis"][0].casefold()
    assert client.get("/api/state").json() == before


def test_target_relative_what_if_requires_human_promotion_and_preserves_target() -> None:
    store = MemoryStore()
    client = TestClient(create_app(store=store, resolver=Resolver(mode="deterministic")))
    client.get("/api/state")
    vector = client.post("/api/starting-vector", json=_vector_payload()).json()
    oriented = client.post("/api/orient", json={"text": ACCEPTANCE_INPUT}).json()
    confirmed = client.post(
        "/api/confirm",
        json={
            "token": oriented["token"],
            "reviewed_input": oriented["reviewed_input"],
            "expected_version": vector["state"]["version"],
            "idempotency_key": "target-promotion-confirm-0001",
        },
    ).json()
    branch = client.post("/api/what-if", json={"text": TARGET_RELATIVE_HYPOTHETICAL}).json()
    before = client.get("/api/state").json()["state"]

    promoted = client.post(
        "/api/what-if/promote",
        json={
            "token": branch["token"],
            "expected_version": before["version"],
            "idempotency_key": "target-experiment-promote-0001",
        },
    )

    assert promoted.status_code == 200
    state = promoted.json()["state"]
    assert state["human_anchor"] == confirmed["state"]["human_anchor"]
    assert state["version"] == before["version"] + 1
    assert any(item["gate_id"] == "what-if:target_experiment" for item in state["decisions"])
    assert any(
        fact["field_key"] == "target_experiment" and "home lab" in fact["statement"].casefold()
        for fact in state["facts"]
    )


def test_target_relative_what_if_cannot_expand_before_a_target_exists() -> None:
    client = TestClient(create_app(store=MemoryStore(), resolver=Resolver(mode="deterministic")))

    response = client.post("/api/what-if", json={"text": TARGET_RELATIVE_HYPOTHETICAL})

    assert response.status_code == 400
    assert "what matters now" in response.json()["detail"].casefold()


def test_currently_serving_without_departure_does_not_manufacture_a_separation_gate() -> None:
    state = apply_starting_vector(
        new_state("ms-serving"),
        operating_role="veteran_service_member",
        lifecycle_position=LifecyclePosition.CURRENTLY_SERVING,
        service=ServiceName.COAST_GUARD,
        component=ServiceComponent.ACTIVE_DUTY,
        idempotency_key="serving-vector-0001",
    )
    state = apply_confirmed_input(
        state,
        orient("I want to decide what kind of AI product to build next.", context=state),
        idempotency_key="serving-input-0001",
    )

    assert all(gate.id != "planned-transition-date" for gate in state.gates)


def test_fog_bank_examination_and_cancellation_write_nothing() -> None:
    current = _wrong_frame_state()
    before = current.model_dump(mode="json")

    proposal = examine_fog_bank(current, FOG_INPUT)

    assert proposal.status == "review_ready"
    assert proposal.changes
    assert current.model_dump(mode="json") == before
    assert current.human_anchor == "Find civilian work"
    assert {change.field for change in proposal.changes} == {
        "human_anchor",
        "lifecycle_position",
        "transition_date",
    }
    assert set(proposal.affected_slices) == set(SliceName)


def test_fog_bank_acceptance_uses_normal_version_lineage_and_replay_contract() -> None:
    current = _wrong_frame_state()
    proposal = examine_fog_bank(current, FOG_INPUT)

    updated = apply_fog_bank_reorientation(current, proposal, idempotency_key="fog-accept-0001")
    replay = apply_fog_bank_reorientation(updated, proposal, idempotency_key="fog-accept-0001")

    assert updated.version == current.version + 1
    assert updated.human_anchor != "Find civilian work"
    assert updated.lifecycle_position == LifecyclePosition.SEPARATED_1_TO_5_YEARS
    assert updated.transition_date is None
    assert all(gate.id != "planned-transition-date" for gate in updated.gates)
    assert any(decision.gate_id == "fog-bank-reorientation" for decision in updated.decisions)
    assert replay.version == updated.version
    assert reconstitute_state(updated).human_anchor == updated.human_anchor


def test_fog_bank_api_enforces_zero_write_stale_replay_and_cross_user_isolation() -> None:
    store = MemoryStore()
    app = create_app(store=store)
    owner = TestClient(app)
    other = TestClient(app)
    owner.post("/api/starting-vector", json=_vector_payload())
    orientation = owner.post("/api/orient", json={"text": "I need civilian work."}).json()
    owner.post(
        "/api/confirm",
        json={
            "token": orientation["token"],
            "reviewed_input": orientation["reviewed_input"],
            "expected_version": 1,
            "idempotency_key": "wrong-frame-api-0001",
        },
    )
    before = owner.get("/api/state").json()["state"]

    examined = owner.post(
        "/api/fog-bank",
        json={"text": FOG_INPUT, "source_version": before["version"]},
    )
    assert examined.status_code == 200
    assert owner.get("/api/state").json()["state"]["version"] == before["version"]
    proposal = examined.json()

    cross_user = other.post(
        "/api/fog-bank/accept",
        json={
            "token": proposal["token"],
            "expected_version": 0,
            "idempotency_key": "fog-cross-user-0001",
        },
    )
    assert cross_user.status_code == 400

    accepted = owner.post(
        "/api/fog-bank/accept",
        json={
            "token": proposal["token"],
            "expected_version": before["version"],
            "idempotency_key": "fog-api-accept-0001",
        },
    )
    assert accepted.status_code == 200
    accepted_state = accepted.json()["state"]
    assert accepted_state["mutation_events"][-1]["mutation_kind"] == "fog_bank_reorientation"
    assert accepted_state["lineage"][-1]["authority_refs"]

    replay = owner.post(
        "/api/fog-bank/accept",
        json={
            "token": proposal["token"],
            "expected_version": before["version"],
            "idempotency_key": "fog-api-accept-0001",
        },
    )
    assert replay.status_code == 200
    assert replay.json()["state"]["version"] == accepted_state["version"]


def test_insufficient_fog_bank_context_requests_one_detail_and_writes_nothing() -> None:
    state = _started_state()
    proposal = examine_fog_bank(state, "Something feels wrong.")

    assert proposal.status == "clarification_needed"
    assert proposal.clarification_question
    assert proposal.token == ""
    assert active_gate(state) is not None


def test_fog_bank_recognizes_a_human_declared_ai_product_direction() -> None:
    current = _wrong_frame_state()
    text = "Change my career plan and focus on building AI tools for veterans."

    proposal = examine_fog_bank(current, text)

    assert proposal.status == "review_ready"
    anchor_change = next(change for change in proposal.changes if change.field == "human_anchor")
    assert anchor_change.proposed_value == "focus on building AI tools for veterans"

    updated = apply_fog_bank_reorientation(current, proposal, idempotency_key="fog-ai-tools-0001")
    assert updated.human_anchor == "focus on building AI tools for veterans"
    assert updated.current_goal == updated.human_anchor
    assert updated.career_hypotheses == []


def test_fog_bank_corrects_service_branch_without_changing_the_plan_goal() -> None:
    current = _wrong_frame_state()
    current.service = ServiceName.AIR_FORCE
    original_anchor = current.human_anchor

    proposal = examine_fog_bank(
        current,
        "The service branch is wrong. I served in the Navy, not the Air Force.",
    )

    assert proposal.status == "review_ready"
    service_change = next(change for change in proposal.changes if change.field == "service")
    assert service_change.current_value == ServiceName.AIR_FORCE.value
    assert service_change.proposed_value == ServiceName.NAVY.value

    updated = apply_fog_bank_reorientation(current, proposal, idempotency_key="fog-service-0001")
    assert updated.service == ServiceName.NAVY
    assert updated.human_anchor == original_anchor


def test_fog_bank_reversal_keeps_the_positive_specific_role_goal() -> None:
    current = _wrong_frame_state()
    text = "I changed my mind. I no longer want to build a product; I want a stable cybersecurity analyst role."

    proposal = examine_fog_bank(current, text)

    anchor_change = next(change for change in proposal.changes if change.field == "human_anchor")
    assert anchor_change.proposed_value == "I want a stable cybersecurity analyst role"


def test_fog_bank_acceptance_rejects_a_stale_source_version() -> None:
    state = _wrong_frame_state()
    proposal = examine_fog_bank(state, FOG_INPUT)
    newer = apply_confirmed_input(
        state,
        orient("I prefer predictable hours.", context=state),
        idempotency_key="intervening-write-0001",
    )

    try:
        apply_fog_bank_reorientation(newer, proposal, idempotency_key="stale-fog-0001")
    except ValueError as exc:
        assert "changed during this review" in str(exc)
    else:
        raise AssertionError("A stale Fog Bank proposal must not mutate newer state.")
