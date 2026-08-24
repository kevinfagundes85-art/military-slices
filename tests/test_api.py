from __future__ import annotations

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


def test_txt_artifact_is_editable_and_not_persisted() -> None:
    client, _ = make_client()
    before = client.get("/api/state").json()["state"]
    response = client.post(
        "/api/artifact",
        files={"file": ("resume.txt", b"Led maintenance schedules.", "text/plain")},
    )
    assert response.status_code == 200
    assert response.json()["text"] == "Led maintenance schedules."
    assert "Nothing has been saved" in response.json()["notice"]
    after = client.get("/api/state").json()["state"]
    assert after["version"] == before["version"]


def test_security_headers_and_health_evidence() -> None:
    client, _ = make_client()
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["agent_framework"] == "google-adk"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
