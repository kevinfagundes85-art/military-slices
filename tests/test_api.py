from __future__ import annotations

import io

from docx import Document
from fastapi.testclient import TestClient

from military_slices.agent_runtime import Resolver
from military_slices.app import create_app
from military_slices.store import MemoryStore


def make_client() -> tuple[TestClient, MemoryStore]:
    store = MemoryStore()
    app = create_app(store=store, resolver=Resolver(mode="deterministic"))
    return TestClient(app), store


def test_orientation_writes_nothing_until_confirmation() -> None:
    client, store = make_client()
    initial = client.get("/api/state").json()
    profile_cookie = client.cookies.get("military_slices_session")
    assert profile_cookie is not None
    profile_id = initial["state"]["profile_id"]
    result = client.post("/api/orient", json={"text": "I want remote work and will not relocate."})
    assert result.status_code == 200
    assert store.get(profile_id).version == 0


def test_full_feedback_cycle_persists_and_reconstitutes() -> None:
    client, _ = make_client()
    initial = client.get("/api/state").json()
    oriented = client.post(
        "/api/orient",
        json={"text": "I leave active service in March 2027 and need work near Tacoma."},
    ).json()
    confirmed = client.post(
        "/api/confirm",
        json={
            "token": oriented["token"],
            "reviewed_input": oriented["reviewed_input"],
            "expected_version": initial["state"]["version"],
            "idempotency_key": "confirm-api-0001",
        },
    )
    assert confirmed.status_code == 200
    payload = confirmed.json()
    assert payload["state"]["version"] == 1
    assert payload["what_changed"] is not None
    assert payload["state"]["telemetry"]["resolver_context_bytes"] > 0
    assert payload["state"]["telemetry"]["context_reduction_ratio"] >= 0
    reloaded = client.get("/api/state").json()
    assert reloaded["state"]["version"] == 1
    assert reloaded["state"]["facts"]


def test_second_browser_isolation() -> None:
    app = create_app(store=MemoryStore(), resolver=Resolver(mode="deterministic"))
    first = TestClient(app)
    second = TestClient(app)
    one = first.get("/api/state").json()["state"]["profile_id"]
    two = second.get("/api/state").json()["state"]["profile_id"]
    assert one != two


def test_stale_write_returns_409() -> None:
    client, _ = make_client()
    initial = client.get("/api/state").json()
    oriented = client.post("/api/orient", json={"text": "I want a civilian career."}).json()
    body = {
        "token": oriented["token"],
        "reviewed_input": oriented["reviewed_input"],
        "expected_version": initial["state"]["version"],
        "idempotency_key": "confirm-api-0002",
    }
    assert client.post("/api/confirm", json=body).status_code == 200
    body["idempotency_key"] = "confirm-api-0003"
    assert client.post("/api/confirm", json=body).status_code == 409


def test_lost_response_retry_returns_current_state_without_another_write() -> None:
    client, _ = make_client()
    initial = client.get("/api/state").json()
    oriented = client.post("/api/orient", json={"text": "I need stable civilian work."}).json()
    body = {
        "token": oriented["token"],
        "reviewed_input": oriented["reviewed_input"],
        "expected_version": initial["state"]["version"],
        "idempotency_key": "confirm-retry-0001",
    }
    first = client.post("/api/confirm", json=body)
    replay = client.post("/api/confirm", json=body)
    assert first.status_code == replay.status_code == 200
    assert first.json()["state"]["version"] == replay.json()["state"]["version"] == 1


def test_decision_retry_is_idempotent_across_http_boundary() -> None:
    client, _ = make_client()
    initial = client.get("/api/state").json()
    oriented = client.post("/api/orient", json={"text": "I need stable civilian work."}).json()
    confirmed = client.post(
        "/api/confirm",
        json={
            "token": oriented["token"],
            "reviewed_input": oriented["reviewed_input"],
            "expected_version": initial["state"]["version"],
            "idempotency_key": "decision-setup-0001",
        },
    ).json()
    body = {
        "gate_id": "planned-transition-date",
        "value": "2027-06-01",
        "expected_version": confirmed["state"]["version"],
        "idempotency_key": "decision-retry-0001",
    }
    first = client.post("/api/decision", json=body)
    replay = client.post("/api/decision", json=body)
    assert first.status_code == replay.status_code == 200
    assert first.json()["state"]["version"] == replay.json()["state"]["version"] == 2


def test_artifact_cancel_equivalent_creates_no_write() -> None:
    client, _ = make_client()
    before = client.get("/api/state").json()["state"]
    after = client.get("/api/state").json()["state"]
    assert before["version"] == after["version"] == 0


def test_deliberately_selected_artifact_updates_plan_without_second_confirmation() -> None:
    client, _ = make_client()
    before = client.get("/api/state").json()["state"]
    response = client.post(
        "/api/artifact",
        data={"expected_version": "0", "idempotency_key": "artifact-direct-0001"},
        files={
            "file": (
                "resume.txt",
                b"Kevin kevin@example.com. Led maintenance schedules and want remote work.",
                "text/plain",
            )
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["state"]["version"] == 1
    assert payload["state"]["facts"]
    assert payload["what_changed"]["headline"] == "Your document changed what comes next."
    serialized = response.text
    assert "kevin@example.com" not in serialized
    assert payload["state"]["original_intents"] == ["Shared a document to update my transition plan."]
    after = client.get("/api/state").json()["state"]
    assert after["version"] == before["version"] + 1


def test_resume_sized_docx_clears_artifact_gate_in_one_request() -> None:
    client, _ = make_client()
    document = Document()
    for index in range(55):
        document.add_paragraph(
            f"Experience {index}: led intelligence analysis, planning, and executive briefings for operational work."
        )
    output = io.BytesIO()
    document.save(output)
    response = client.post(
        "/api/artifact",
        data={"expected_version": "0", "idempotency_key": "artifact-docx-0001"},
        files={
            "file": (
                "resume.docx",
                output.getvalue(),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["state"]["version"] == 1
    assert len(payload["state"]["career_hypotheses"]) == 3
    assert payload["active_gate"]["id"] in {"planned-transition-date", "next-work-preferences"}


def test_artifact_retry_is_idempotent_and_stale_artifact_is_rejected() -> None:
    client, _ = make_client()
    body = {"expected_version": "0", "idempotency_key": "artifact-retry-0001"}
    upload = {"file": ("resume.txt", b"Led military logistics work.", "text/plain")}
    first = client.post("/api/artifact", data=body, files=upload)
    replay = client.post("/api/artifact", data=body, files=upload)
    assert first.status_code == replay.status_code == 200
    assert first.json()["state"]["version"] == replay.json()["state"]["version"] == 1
    stale = client.post(
        "/api/artifact",
        data={"expected_version": "0", "idempotency_key": "artifact-retry-0002"},
        files=upload,
    )
    assert stale.status_code == 409


def test_security_headers_and_health_evidence() -> None:
    client, _ = make_client()
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["agent_framework"] == "google-adk"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
    public_response = client.get("/api/health")
    assert public_response.status_code == 200
    assert public_response.json() == response.json()
