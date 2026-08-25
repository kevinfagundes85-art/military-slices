from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

from run_gauntlet import Action, Scenario, run_scenario
from run_gauntlet_anchor_order import scenarios as anchor_order_scenarios
from run_gauntlet_confirmation import EXACT_MATRIX_FAILURES


def replay_scenarios() -> tuple[Scenario, ...]:
    cases = list(anchor_order_scenarios())
    for index, (service, when, first_target, next_target) in enumerate(EXACT_MATRIX_FAILURES, start=1):
        cases.append(
            Scenario(
                f"X-M{index}",
                service,
                "separating member",
                "mixed",
                "exact-frozen-matrix-failure",
                (
                    Action(
                        "text",
                        f"I am leaving the {service} in {when}. My career target is {first_target}. "
                        "I will stay local and want predictable hours.",
                    ),
                    Action("text", f"My career target is {next_target}."),
                    Action("revalidate"),
                ),
                expected=("impact", "revalidation", "active"),
            )
        )
    cases.extend(
        (
            Scenario(
                "X-R1",
                "Navy",
                "retiring member",
                "6-12 months",
                "exact-resume-stop-condition",
                (Action("text", "My anchor is make my resume submission-ready, but I have not named the target role yet."),),
                expected=("resume_target_gate", "active"),
            ),
            Scenario(
                "X-E1",
                "Army",
                "separating member",
                "12-18 months",
                "execution-contract",
                (
                    Action("text", "I want civilian work with predictable hours."),
                    Action("text", "I need immediate income and full-time education in the same first six months."),
                ),
                expected=("conflict", "paralyzed"),
            ),
        )
    )
    return tuple(cases)


def main() -> None:
    cases = replay_scenarios()
    started_at = datetime.now(UTC)
    started = time.perf_counter()
    results = []
    errors = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(run_scenario, scenario): scenario for scenario in cases}
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
        "attempted": len(cases),
        "completed": len(results),
        "invariant_clean": sum(not item["failure_codes"] for item in results),
        "driver_errors": errors,
        "model_calls": sum(item["model_calls"] for item in results),
        "tool_calls": sum(item["tool_calls"] for item in results),
        "input_tokens": sum(item["input_tokens"] for item in results),
        "output_tokens": sum(item["output_tokens"] for item in results),
        "estimated_cost": round(sum(item["estimated_cost"] for item in results), 6),
        "results": results,
    }
    output = Path(__file__).with_name("output") / f"gauntlet-exact-replay-{started_at.strftime('%Y%m%dT%H%M%SZ')}.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(output)
    print(
        json.dumps(
            {
                key: payload[key]
                for key in (
                    "wall_seconds",
                    "attempted",
                    "completed",
                    "invariant_clean",
                    "driver_errors",
                    "model_calls",
                    "tool_calls",
                    "estimated_cost",
                )
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
