from __future__ import annotations

import json
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

import httpx

from run_gauntlet import BASE_URL, INPUT_USD_PER_MILLION, OUTPUT_USD_PER_MILLION, TOOL_CALL_USD

CASES = (
    ("P01", "Marine Corps", "I am a Marine with broad experience, but I do not know what I want after service yet.", {"planned-transition-date": "2027-12-01", "service-path-identity": "Marine Corps", "transition-direction": "Civilian work", "next-work-preferences": "I want predictable daytime work with limited travel."}),
    ("P02", "Army", "I leave the Army in June 2027. I need immediate income and full-time education before I will accept work.", {"priority-first-six-months": "A staged combination"}),
    ("P03", "Air Force", "I leave the Air Force in September 2027. I want stable work with normal hours, limited travel, and a mission-driven team, but I do not know which civilian role fits.", {"career-direction": "first-candidate"}),
    ("P04", "Navy", "My anchor is make my resume submission-ready, but I have not named the target role yet.", {"resume-target-role": "Technical Program Manager"}),
    ("P05", "Space Force", "I leave the Space Force in May 2028. My anchor is choose education or training before employment.", {"education-outcome": "A graduate certificate that qualifies me for space systems program work."}),
    ("P06", "Coast Guard", "I leave the Coast Guard in March 2027. My anchor is decide where my family should live after service.", {"location-priority": "Stay within one hour of family and keep a reasonable commute."}),
)


def decide(client: httpx.Client, envelope: dict, value: str) -> tuple[dict, float]:
    gate = envelope["active_gate"]
    if value == "first-candidate":
        candidates = [item for item in envelope["state"].get("career_hypotheses", []) if item.get("status") == "candidate"]
        if not candidates:
            raise RuntimeError("career gate had no candidate")
        value = "explore:" + candidates[0]["title"]
    started = time.perf_counter()
    response = client.post("/api/decision", json={"gate_id": gate["id"], "value": value, "expected_version": envelope["state"]["version"], "idempotency_key": "progress-" + uuid.uuid4().hex})
    latency = time.perf_counter() - started
    response.raise_for_status()
    return response.json(), latency


def run_case(case: tuple[str, str, str, dict[str, str]]) -> dict:
    case_id, service, text, answers = case
    started = time.perf_counter()
    with httpx.Client(base_url=BASE_URL, timeout=45) as client:
        initial = client.get("/api/state").raise_for_status().json()
        orientation = client.post("/api/orient", json={"text": text}).raise_for_status().json()
        before_confirm = client.get("/api/state").raise_for_status().json()
        unauthorized_write = before_confirm["state"]["version"] != 0
        response = client.post("/api/confirm", json={"token": orientation["token"], "reviewed_input": orientation["reviewed_input"], "expected_version": 0, "idempotency_key": case_id.lower() + "-confirm-" + uuid.uuid4().hex}).raise_for_status().json()
        gate_sequence = []
        decision_latencies = []
        for _ in range(8):
            gate = response.get("active_gate")
            if not gate:
                break
            gate_sequence.append({"id": gate["id"], "state": gate["state"], "authority": gate["authority_required"], "surface": gate["surface"]})
            answer = answers.get(gate["id"])
            if answer is None:
                break
            response, latency = decide(client, response, answer)
            decision_latencies.append(latency)
        reloaded = client.get("/api/state").raise_for_status().json()
        state = reloaded["state"]
        telemetry = state["telemetry"]
        input_tokens = telemetry.get("input_tokens", 0)
        output_tokens = telemetry.get("output_tokens", 0)
        tool_calls = telemetry.get("tool_calls", 0)
        cost = input_tokens / 1_000_000 * INPUT_USD_PER_MILLION + output_tokens / 1_000_000 * OUTPUT_USD_PER_MILLION + tool_calls * TOOL_CALL_USD
        failures = []
        if unauthorized_write:
            failures.append("UNAUTHORIZED_MUTATION")
        if reloaded["state"]["version"] != response["state"]["version"]:
            failures.append("PERSISTENCE_FAILURE")
        if len(state.get("active_tasks", [])) > 3:
            failures.append("TASK_OVERFLOW")
        if telemetry.get("temporal_freshness_model_calls", 0):
            failures.append("MODEL_OVERUSE")
        if case_id == "P02" and state.get("conflicts"):
            failures.append("MISSED_CONFLICT")
        if case_id == "P03" and not state.get("career_target"):
            failures.append("OTHER")
        return {
            "scenario_id": case_id,
            "service": service,
            "scenario_family": "gate-progression",
            "human_anchor": state.get("human_anchor"),
            "gate_sequence": gate_sequence,
            "final_gate": reloaded.get("active_gate"),
            "state_versions": [initial["state"]["version"], state["version"]],
            "career_target": state.get("career_target"),
            "conflicts": state.get("conflicts", []),
            "active_tasks_max": len(state.get("active_tasks", [])),
            "model_calls": telemetry.get("model_calls", 0),
            "tool_calls": tool_calls,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "agent_gates_closed": telemetry.get("agent_gates_closed", 0),
            "estimated_cost": round(cost, 6),
            "decision_latencies": decision_latencies,
            "latency": round(time.perf_counter() - started, 4),
            "failure_codes": failures,
            "execution_state_present": state.get("execution", {}).get("state") in {"ACTIVE", "PARALYZED", "COMPLETE"},
            "execution_state": state.get("execution", {}).get("state"),
        }


def main() -> None:
    started_at = datetime.now(UTC)
    started = time.perf_counter()
    results = []
    errors = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(run_case, case): case[0] for case in CASES}
        for future in as_completed(futures):
            case_id = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:
                errors.append({"scenario_id": case_id, "error": f"{type(exc).__name__}: {exc}"})
    results.sort(key=lambda item: item["scenario_id"])
    payload = {
        "start_timestamp": started_at.isoformat(),
        "wall_seconds": round(time.perf_counter() - started, 3),
        "attempted": len(CASES),
        "completed": len(results),
        "driver_errors": errors,
        "model_calls": sum(item["model_calls"] for item in results),
        "tool_calls": sum(item["tool_calls"] for item in results),
        "input_tokens": sum(item["input_tokens"] for item in results),
        "output_tokens": sum(item["output_tokens"] for item in results),
        "estimated_cost": round(sum(item["estimated_cost"] for item in results), 6),
        "results": results,
    }
    output = Path(__file__).with_name("output") / f"gauntlet-progression-{started_at.strftime('%Y%m%dT%H%M%SZ')}.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(output)
    print(json.dumps({key: payload[key] for key in ("wall_seconds", "attempted", "completed", "driver_errors", "model_calls", "tool_calls", "input_tokens", "output_tokens", "estimated_cost")}, indent=2))


if __name__ == "__main__":
    main()
