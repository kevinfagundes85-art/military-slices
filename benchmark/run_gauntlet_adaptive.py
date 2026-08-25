from __future__ import annotations

import json
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

import httpx

from run_gauntlet import Action, BASE_URL, Scenario, run_scenario

ADAPTIVE_SCENARIOS = (
    Scenario("A01", "Army", "military spouse", "PCS-driven", "location-first-family", (Action("text", "My spouse is Army and our next PCS is to Fort Liberty in November 2027. My anchor is choose a neighborhood and school plan while keeping my remote job."), Action("reload")), expected=("anchor", "persistence", "task_bound")),
    Scenario("A02", "Navy", "separating member", "12–18 months", "education-benefit-first", (Action("text", "I separate from the Navy in February 2028. My anchor is choose a data analytics degree and verify the current education-benefit rules before committing."), Action("reload")), expected=("anchor", "persistence", "task_bound")),
    Scenario("A03", "Marine Corps", "separating member", "terminal period", "entrepreneurship-terminal", (Action("text", "I am on terminal leave from the Marine Corps. My anchor is launch a mobile equipment repair business; I do not want civilian job recommendations."),), forbidden_slices=("Education",), expected=("anchor", "task_bound")),
    Scenario("A04", "Air Force", "retiring member", "6–12 months", "irrelevant-evidence-control", (Action("text", "My anchor is make my resume ready for Aviation Safety Manager roles."), Action("artifact", artifact_type="docx"), Action("artifact", artifact_type="png"), Action("reload")), forbidden_slices=("Education", "Location"), expected=("persistence", "task_bound")),
    Scenario("A05", "Space Force", "separating member", ">18 months", "oconus-conus", (Action("text", "I leave the Space Force from an OCONUS assignment in August 2028. My career target is Space Systems Program Analyst, and I am open to relocating CONUS."),), expected=("target", "task_bound")),
    Scenario("A06", "Coast Guard", "recent veteran", "recently separated", "semantic-reentry", (Action("text", "I recently left the Coast Guard. I want steady emergency management work near Boston with minimal travel."), Action("text", "To restate it: steady emergency management work near Boston, and little travel."), Action("reload")), expected=("anchor", "persistence", "task_bound")),
    Scenario("A07", "Army", "separating member", "90–180 days", "compensation-family-conflict", (Action("text", "I separate from the Army in December 2026. I want work immediately, need at least 95000 dollars, cannot relocate because of shared custody, and prefer program operations."),), expected=("anchor", "task_bound")),
    Scenario("A08", "Navy", "retiring member", "6–12 months", "long-messy-bounded", (Action("text", "I retire from the Navy in July 2027 after a long technical career. I want meaningful civilian work with normal hours and less travel, my spouse has a local business, one child starts high school, I enjoy restoring motorcycles, and I cannot tell whether operations leadership or compliance work fits best."), Action("reload")), expected=("anchor", "persistence", "task_bound")),
    Scenario("A09", "Air Force", "military spouse", "PCS-driven", "licensed-spouse", (Action("text", "We PCS to California in nine months. I am a military spouse and licensed clinical social worker; my anchor is preserve my career through the licensing transfer and avoid an employment gap."),), expected=("anchor", "task_bound")),
    Scenario("A10", "Space Force", "dual-military household", "12–18 months", "dual-military-timing", (Action("text", "We are dual military. One Guardian separates in May 2028 while the other remains active. Our anchor is coordinate one civilian career start without disrupting the active-duty assignment or childcare."),), expected=("anchor", "task_bound")),
    Scenario("A11", "Coast Guard", "separating member", "6–12 months", "job-posting-evidence", (Action("text", "I leave the Coast Guard in June 2027. I want operations work with predictable hours and I am deciding between emergency planning and compliance."), Action("text", "A real posting requires exercise planning, regulatory documentation, incident coordination, and briefings. Treat this only as evidence for the current career decision."), Action("reload")), expected=("anchor", "persistence", "task_bound")),
    Scenario("A12", "Marine Corps", "veteran", "post-transition", "anchor-change", (Action("text", "My career target is Warehouse Operations Manager and I will stay local."), Action("text", "My anchor has changed: education comes first now, and I want a teaching credential before returning to full-time work."), Action("reload")), expected=("persistence", "task_bound")),
)


def orient_confirm(client: httpx.Client, text: str, version: int, key: str) -> dict:
    orientation = client.post("/api/orient", json={"text": text}).raise_for_status().json()
    return client.post("/api/confirm", json={"token": orientation["token"], "reviewed_input": orientation["reviewed_input"], "expected_version": version, "idempotency_key": key}).raise_for_status().json()


def isolation_and_bounded_update() -> dict:
    started = time.perf_counter()
    with httpx.Client(base_url=BASE_URL, timeout=45) as owner, httpx.Client(base_url=BASE_URL, timeout=45) as other:
        owner_initial = owner.get("/api/state").raise_for_status().json()
        owner_state = orient_confirm(owner, "I separate from the Army in June 2027. My career target is Program Management. I will stay local.", 0, "iso-initial-" + uuid.uuid4().hex)
        owner_state = orient_confirm(owner, "My career target is National Defense Program Management.", owner_state["state"]["version"], "iso-target-" + uuid.uuid4().hex)
        impact = owner_state.get("impact")
        if not impact:
            raise RuntimeError("owner impact was not produced")
        update = owner.post("/api/revalidate", json={"impact_id": impact["id"], "action": "update", "value": "Open to relocating", "expected_version": owner_state["state"]["version"], "idempotency_key": "iso-update-" + uuid.uuid4().hex}).raise_for_status().json()
        replay = owner.get("/api/state").raise_for_status().json()
        other_initial = other.get("/api/state").raise_for_status().json()
        other_attempt = other.post("/api/revalidate", json={"impact_id": impact["id"], "action": "confirm", "expected_version": other_initial["state"]["version"], "idempotency_key": "iso-cross-" + uuid.uuid4().hex}).raise_for_status().json()
        fact = next(item for item in replay["state"]["facts"] if item.get("field_key") == "relocation_willingness")
        failures = []
        if fact.get("value") != "YES" or fact.get("status") != "valid" or replay.get("impact") is not None:
            failures.append("BAD_REVALIDATION")
        if other_attempt["state"]["version"] != 0 or other_attempt.get("impact") is not None:
            failures.append("ISOLATION_FAILURE")
        telemetry = replay["state"]["telemetry"]
        return {
            "scenario_id": "A13",
            "scenario_family": "bounded-update-second-user-isolation",
            "service": "Army",
            "persona_type": "separating member",
            "transition_stage": "6–12 months",
            "latency": round(time.perf_counter() - started, 4),
            "failure_codes": failures,
            "model_calls": telemetry.get("model_calls", 0),
            "tool_calls": telemetry.get("tool_calls", 0),
            "input_tokens": telemetry.get("input_tokens", 0),
            "output_tokens": telemetry.get("output_tokens", 0),
            "estimated_cost": 0,
            "state_versions": [0, owner_state["state"]["version"], update["state"]["version"], replay["state"]["version"]],
            "bounded_updates": telemetry.get("temporal_bounded_update_flows", 0),
            "freshness_model_calls": telemetry.get("temporal_freshness_model_calls", 0),
            "receipt_patch_bytes": telemetry.get("temporal_patch_bytes", 0),
            "receipt_patch_count": telemetry.get("temporal_patch_count", 0),
            "full_receipt_rebuilds": telemetry.get("temporal_full_rebuilds", 0),
            "owner_profile": owner_initial["state"]["profile_id"],
            "other_profile": other_initial["state"]["profile_id"],
        }


def main() -> None:
    started_at = datetime.now(UTC)
    started = time.perf_counter()
    results = []
    errors = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(run_scenario, scenario): scenario for scenario in ADAPTIVE_SCENARIOS}
        for future in as_completed(futures):
            scenario = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:
                errors.append({"scenario_id": scenario.id, "error": f"{type(exc).__name__}: {exc}"})
    try:
        results.append(isolation_and_bounded_update())
    except Exception as exc:
        errors.append({"scenario_id": "A13", "error": f"{type(exc).__name__}: {exc}"})
    results.sort(key=lambda item: item["scenario_id"])
    payload = {
        "start_timestamp": started_at.isoformat(),
        "wall_seconds": round(time.perf_counter() - started, 3),
        "attempted": len(ADAPTIVE_SCENARIOS) + 1,
        "completed": len(results),
        "driver_errors": errors,
        "model_calls": sum(item.get("model_calls", 0) for item in results),
        "tool_calls": sum(item.get("tool_calls", 0) for item in results),
        "input_tokens": sum(item.get("input_tokens", 0) for item in results),
        "output_tokens": sum(item.get("output_tokens", 0) for item in results),
        "estimated_cost": round(sum(item.get("estimated_cost", 0) for item in results), 6),
        "results": results,
    }
    output = Path(__file__).with_name("output") / f"gauntlet-adaptive-{started_at.strftime('%Y%m%dT%H%M%SZ')}.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(output)
    print(json.dumps({key: payload[key] for key in ("wall_seconds", "attempted", "completed", "driver_errors", "model_calls", "tool_calls", "input_tokens", "output_tokens", "estimated_cost")}, indent=2))


if __name__ == "__main__":
    main()
