from __future__ import annotations

from fastapi.testclient import TestClient

from military_slices.agent_runtime import Resolver
from military_slices.app import create_app
from military_slices.control import lens_projections, path_progress
from military_slices.engine import new_state, recompute_state
from military_slices.models import SliceName
from military_slices.store import MemoryStore


def make_client() -> tuple[TestClient, MemoryStore]:
    store = MemoryStore()
    app = create_app(store=store, resolver=Resolver(mode="deterministic"))
    return TestClient(app), store


def confirm(client: TestClient, text: str, key: str = "control-confirm-0001") -> dict[str, object]:
    initial = client.get("/api/state").json()
    oriented = client.post("/api/orient", json={"text": text}).json()
    response = client.post(
        "/api/confirm",
        json={
            "token": oriented["token"],
            "reviewed_input": oriented["reviewed_input"],
            "expected_version": initial["state"]["version"],
            "idempotency_key": key,
        },
    )
    assert response.status_code == 200
    return response.json()


def test_lenses_are_deterministic_read_only_projections() -> None:
    client, _ = make_client()
    confirmed = confirm(client, "I retire from the Navy in June 2027 and need civilian work without shift work.")
    before = client.get("/api/state").json()
    for name in ("career", "education", "location", "resume"):
        response = client.get(f"/api/lenses/{name}")
        assert response.status_code == 200
        assert response.json()["lens"]["name"] == name
    after = client.get("/api/state").json()
    assert after["state"]["version"] == before["state"]["version"] == confirmed["state"]["version"]
    assert after["state"]["telemetry"] == before["state"]["telemetry"]
    assert after["active_gate"] == before["active_gate"]
    assert after["state"]["active_tasks"] == before["state"]["active_tasks"]


def test_history_inspection_preserves_current_canonical_state() -> None:
    client, _ = make_client()
    confirmed = confirm(client, "I need civilian work after leaving the Army in June 2027.")
    current_before = client.get("/api/state").json()
    history = client.get("/api/history").json()
    assert [entry["version"] for entry in history["entries"]] == [0, confirmed["state"]["version"]]
    inspected = client.get("/api/history/0")
    assert inspected.status_code == 200
    assert inspected.json()["category"] == "historical"
    assert inspected.json()["entry"]["version"] == 0
    current_after = client.get("/api/state").json()
    assert current_after["state"] == current_before["state"]
    assert current_after["active_gate"] == current_before["active_gate"]


def test_what_if_is_isolated_until_explicit_promotion() -> None:
    client, _ = make_client()
    confirmed = confirm(
        client,
        "I retire from the Navy in June 2027, need civilian work, and will not relocate.",
    )
    before = client.get("/api/state").json()
    branch_response = client.post("/api/what-if", json={"text": "What if I were willing to relocate?"})
    assert branch_response.status_code == 200
    branch = branch_response.json()
    assert branch["category"] == "hypothetical"
    assert branch["source_version"] == confirmed["state"]["version"]
    assert branch["conflicts"]
    assert branch["affected_slices"] == ["location", "career"]
    unchanged = client.get("/api/state").json()
    assert unchanged["state"] == before["state"]
    assert unchanged["active_gate"] == before["active_gate"]

    promoted_response = client.post(
        "/api/what-if/promote",
        json={
            "token": branch["token"],
            "expected_version": before["state"]["version"],
            "idempotency_key": "promote-whatif-0001",
        },
    )
    assert promoted_response.status_code == 200
    promoted = promoted_response.json()
    assert promoted["state"]["version"] == before["state"]["version"] + 1
    assert any(item["gate_id"] == "what-if:relocation_willingness" for item in promoted["state"]["decisions"])
    assert promoted["what_changed"]["headline"] == "You made the explored change part of your current plan."
    assert all("will not relocate" not in fact["statement"].casefold() for fact in promoted["state"]["facts"])
    assert branch["conflicts"][0] not in promoted["state"]["conflicts"]
    replay = client.post(
        "/api/what-if/promote",
        json={
            "token": branch["token"],
            "expected_version": before["state"]["version"],
            "idempotency_key": "promote-whatif-0001",
        },
    )
    assert replay.status_code == 200
    assert replay.json()["state"]["version"] == promoted["state"]["version"]
    stale = client.post(
        "/api/what-if/promote",
        json={
            "token": branch["token"],
            "expected_version": before["state"]["version"],
            "idempotency_key": "promote-whatif-stale-0001",
        },
    )
    assert stale.status_code == 409
    history = client.get("/api/history").json()
    assert before["state"]["version"] in [entry["version"] for entry in history["entries"]]


def test_discarded_what_if_and_cross_user_token_leave_truth_untouched() -> None:
    owner, _ = make_client()
    other, _ = make_client()
    confirm(owner, "I leave the Coast Guard in June 2027 and plan to remain local.")
    before = owner.get("/api/state").json()
    branch = owner.post("/api/what-if", json={"text": "What if I were willing to relocate?"}).json()
    assert owner.get("/api/state").json()["state"] == before["state"]
    denied = other.post(
        "/api/what-if/promote",
        json={
            "token": branch["token"],
            "expected_version": 0,
            "idempotency_key": "cross-user-promote-0001",
        },
    )
    assert denied.status_code == 400
    assert other.get("/api/state").json()["state"]["version"] == 0
    assert owner.get("/api/state").json()["state"] == before["state"]


def test_resume_target_keeps_unrelated_career_context_latent_when_inspected() -> None:
    client, _ = make_client()
    uploaded = client.post(
        "/api/artifact",
        data={"expected_version": "0", "idempotency_key": "control-resume-0001"},
        files={
            "file": (
                "resume.txt",
                b"Navy cyber analyst. Led intelligence teams and program delivery.",
                "text/plain",
            )
        },
    ).json()
    anchor = client.post(
        "/api/decision",
        json={
            "gate_id": "transition-human-anchor",
            "value": "Improve a résumé for a specific goal",
            "expected_version": uploaded["state"]["version"],
            "idempotency_key": "control-resume-0002",
        },
    ).json()
    targeted = client.post(
        "/api/decision",
        json={
            "gate_id": "resume-target-role",
            "value": "Program management roles",
            "expected_version": anchor["state"]["version"],
            "idempotency_key": "control-resume-0003",
        },
    ).json()
    before_version = targeted["state"]["version"]
    career = client.get("/api/lenses/career").json()["lens"]
    assert career["fact_count"] >= 1
    assert targeted["state"]["career_hypotheses"] == []
    after = client.get("/api/state").json()
    assert after["state"]["version"] == before_version
    assert after["state"]["career_hypotheses"] == []


def test_progress_denominator_tracks_only_the_active_objective() -> None:
    state = new_state("ms-progress")
    assert path_progress(state).total == 1

    state.human_anchor = "Make my résumé ready for a specific target"
    resume = path_progress(recompute_state(state))
    assert [item.id for item in resume.items] == ["human-anchor", "resume-target", "resume-evidence"]

    state.human_anchor = "Find civilian work"
    employment = path_progress(recompute_state(state))
    assert [item.id for item in employment.items] == [
        "human-anchor",
        "transition-date",
        "service-path",
        "work-preferences",
        "career-direction",
    ]
    assert all("education" not in item.id and "location" not in item.id for item in employment.items)


def test_lens_projection_exposes_latent_context_without_activation() -> None:
    state = new_state("ms-latent")
    state.human_anchor = "Make my résumé submission-ready for Program Manager"
    state = recompute_state(state)
    career = next(item for item in lens_projections(state) if item.name == SliceName.CAREER)
    assert career.path_relevant
    assert len(state.active_tasks) <= 3


def test_lens_projection_cannot_mutate_state_or_model_telemetry() -> None:
    state = new_state("ms-projection-pure")
    state.human_anchor = "Find civilian work after leaving the Navy"
    state.transition_date = "2027-06-01"
    state = recompute_state(state)
    before = state.model_dump(mode="json")

    first = lens_projections(state)
    second = lens_projections(state)

    assert [item.model_dump(mode="json") for item in first] == [
        item.model_dump(mode="json") for item in second
    ]
    assert state.model_dump(mode="json") == before
    assert state.telemetry.model_calls == 0
