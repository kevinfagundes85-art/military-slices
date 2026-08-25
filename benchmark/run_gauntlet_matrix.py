from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

from run_gauntlet import Action, Scenario, run_scenario

SERVICES = ("Army", "Navy", "Marine Corps", "Air Force", "Space Force", "Coast Guard")
PERSONAS = ("separating member", "retiring member", "recent veteran", "military spouse")
STAGES = (">18 months", "12–18 months", "6–12 months", "90–180 days", "<90 days", "post-transition")
TARGETS = ("Logistics Manager", "Technical Program Manager", "Emergency Planning Coordinator", "Aviation Safety Manager", "Space Systems Analyst", "Maritime Compliance Manager")
DATES = ("December 2028", "June 2028", "December 2027", "January 2027", "November 2026", "recently")


def build_matrix() -> tuple[Scenario, ...]:
    scenarios = []
    for service_index, service in enumerate(SERVICES):
        target = TARGETS[service_index]
        date = DATES[service_index]
        scenarios.extend(
            (
                Scenario(
                    f"M{service_index + 1}1",
                    service,
                    PERSONAS[0],
                    STAGES[service_index],
                    "matrix-known-target-change",
                    (
                        Action("text", f"I am leaving the {service} in {date}. My career target is {target}. I will stay local and want predictable hours."),
                        Action("text", f"My career target is Senior {target}."),
                        Action("revalidate"),
                        Action("reload"),
                    ),
                    forbidden_slices=("Education",),
                    expected=("impact", "revalidation", "persistence", "task_bound"),
                ),
                Scenario(
                    f"M{service_index + 1}2",
                    service,
                    PERSONAS[1],
                    STAGES[(service_index + 1) % len(STAGES)],
                    "matrix-uncertain-career",
                    (Action("text", f"I am retiring from the {service} in {date}. I want meaningful civilian work with normal hours and limited travel, but I am uncertain which direction best fits my leadership and planning experience."), Action("reload")),
                    expected=("anchor", "persistence", "task_bound"),
                ),
                Scenario(
                    f"M{service_index + 1}3",
                    service,
                    PERSONAS[2],
                    STAGES[(service_index + 2) % len(STAGES)],
                    "matrix-resume-artifact",
                    (Action("text", f"I am a recently separated {service} veteran. My anchor is make my resume submission-ready for {target}."), Action("artifact", artifact_type=("txt", "docx", "pdf", "png")[service_index % 4]), Action("reload")),
                    forbidden_slices=("Education", "Location"),
                    expected=("persistence", "task_bound"),
                ),
                Scenario(
                    f"M{service_index + 1}4",
                    service,
                    PERSONAS[3],
                    "PCS-driven",
                    "matrix-spouse-pcs",
                    (Action("text", f"My spouse serves in the {service} and we PCS in about a year. My anchor is protect my career and our children's school stability while deciding where to live."), Action("reload")),
                    expected=("anchor", "persistence", "task_bound"),
                ),
            )
        )
    return tuple(scenarios)


MATRIX = build_matrix()


def main() -> None:
    started_at = datetime.now(UTC)
    started = time.perf_counter()
    results = []
    errors = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(run_scenario, scenario): scenario for scenario in MATRIX}
        for future in as_completed(futures):
            scenario = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:
                errors.append({"scenario_id": scenario.id, "error": f"{type(exc).__name__}: {exc}"})
    results.sort(key=lambda item: item["scenario_id"])
    payload = {
        "start_timestamp": started_at.isoformat(),
        "wall_seconds": round(time.perf_counter() - started, 3),
        "attempted": len(MATRIX),
        "completed": len(results),
        "driver_errors": errors,
        "model_calls": sum(item["model_calls"] for item in results),
        "tool_calls": sum(item["tool_calls"] for item in results),
        "input_tokens": sum(item["input_tokens"] for item in results),
        "output_tokens": sum(item["output_tokens"] for item in results),
        "estimated_cost": round(sum(item["estimated_cost"] for item in results), 6),
        "results": results,
    }
    output = Path(__file__).with_name("output") / f"gauntlet-matrix-{started_at.strftime('%Y%m%dT%H%M%SZ')}.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(output)
    print(json.dumps({key: payload[key] for key in ("wall_seconds", "attempted", "completed", "driver_errors", "model_calls", "tool_calls", "input_tokens", "output_tokens", "estimated_cost")}, indent=2))


if __name__ == "__main__":
    main()
