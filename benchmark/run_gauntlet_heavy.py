from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

from run_gauntlet import Action, Scenario, run_scenario

HEAVY_SCENARIOS = (
    Scenario(
        "H01",
        "Army",
        "separating member",
        "6–12 months",
        "heavy-career-resolution",
        (
            Action("text", "I separate from the Army in June 2027. I want stable civilian work with less travel and no shift work. I am unsure which career fits my logistics and operations background."),
            Action("artifact", artifact_type="docx"),
            Action("reload"),
        ),
        expected=("anchor", "task_bound", "persistence"),
    ),
    Scenario(
        "H02",
        "Navy",
        "retiring member",
        "6–12 months",
        "heavy-rejection-resolution",
        (
            Action("text", "I retire from the Navy in May 2027. I want analytical work with predictable hours and limited travel, but I am torn between operations analysis and project delivery."),
            Action("artifact", artifact_type="pdf"),
            Action("reject"),
            Action("reload"),
        ),
        expected=("anchor", "rejection", "persistence", "task_bound"),
    ),
    Scenario(
        "H03",
        "Coast Guard",
        "separating member",
        "90–180 days",
        "heavy-multimodal-resolution",
        (
            Action("text", "I leave the Coast Guard in January 2027. I want mission-driven civilian work near Portland with a steady schedule, but I do not know which direction fits."),
            Action("artifact", artifact_type="png"),
            Action("reload"),
        ),
        expected=("anchor", "persistence", "task_bound"),
    ),
    Scenario(
        "H04",
        "Air Force",
        "recent veteran",
        "post-transition",
        "job-posting-resolution",
        (
            Action("text", "I recently left the Air Force. I want to compare program delivery and customer success work, keep normal daytime hours, and use my training leadership experience."),
            Action("text", "A job posting asks for stakeholder coordination, delivery schedules, risk tracking, and executive briefings. Use it as evidence, not as permission to change my anchor."),
            Action("reload"),
        ),
        expected=("anchor", "persistence", "task_bound"),
    ),
)


def main() -> None:
    started_at = datetime.now(UTC)
    started = time.perf_counter()
    results = []
    errors = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(run_scenario, scenario): scenario for scenario in HEAVY_SCENARIOS}
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
        "attempted": len(HEAVY_SCENARIOS),
        "completed": len(results),
        "driver_errors": errors,
        "model_calls": sum(item["model_calls"] for item in results),
        "tool_calls": sum(item["tool_calls"] for item in results),
        "input_tokens": sum(item["input_tokens"] for item in results),
        "output_tokens": sum(item["output_tokens"] for item in results),
        "estimated_cost": round(sum(item["estimated_cost"] for item in results), 6),
        "results": results,
    }
    output = Path(__file__).with_name("output") / f"gauntlet-heavy-{started_at.strftime('%Y%m%dT%H%M%SZ')}.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(output)
    print(json.dumps({key: payload[key] for key in ("wall_seconds", "attempted", "completed", "driver_errors", "model_calls", "tool_calls", "input_tokens", "output_tokens", "estimated_cost")}, indent=2))


if __name__ == "__main__":
    main()
