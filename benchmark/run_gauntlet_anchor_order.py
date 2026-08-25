from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

from run_gauntlet import Action, Scenario, run_scenario

SERVICES = ("Army", "Navy", "Marine Corps", "Air Force", "Space Force", "Coast Guard")


def scenarios() -> tuple[Scenario, ...]:
    output = []
    for index, service in enumerate(SERVICES, start=1):
        output.append(
            Scenario(
                f"O{index}A",
                service,
                "separating member",
                "6–12 months",
                "anchor-order-preference-last",
                (
                    Action("text", f"I leave the {service} in June 2027. My career target is Program Manager. I will stay local and want predictable hours."),
                    Action("text", "My career target is Defense Program Manager."),
                    Action("revalidate"),
                ),
                expected=("impact", "revalidation"),
            )
        )
        output.append(
            Scenario(
                f"O{index}B",
                service,
                "separating member",
                "6–12 months",
                "anchor-order-employment-first",
                (
                    Action("text", f"I leave the {service} in June 2027. I want civilian work with predictable hours. My career target is Program Manager. I will stay local."),
                    Action("text", "My career target is Defense Program Manager."),
                    Action("revalidate"),
                ),
                expected=("impact", "revalidation"),
            )
        )
    return tuple(output)


CASES = scenarios()


def main() -> None:
    started_at = datetime.now(UTC)
    started = time.perf_counter()
    results = []
    errors = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(run_scenario, scenario): scenario for scenario in CASES}
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
        "attempted": len(CASES),
        "completed": len(results),
        "driver_errors": errors,
        "failed": sum(bool(item["failure_codes"]) for item in results),
        "model_calls": sum(item["model_calls"] for item in results),
        "tool_calls": sum(item["tool_calls"] for item in results),
        "input_tokens": sum(item["input_tokens"] for item in results),
        "output_tokens": sum(item["output_tokens"] for item in results),
        "estimated_cost": round(sum(item["estimated_cost"] for item in results), 6),
        "results": results,
    }
    output = Path(__file__).with_name("output") / f"gauntlet-anchor-order-{started_at.strftime('%Y%m%dT%H%M%SZ')}.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(output)
    print(json.dumps({key: payload[key] for key in ("wall_seconds", "attempted", "completed", "driver_errors", "failed", "model_calls", "tool_calls", "estimated_cost")}, indent=2))


if __name__ == "__main__":
    main()
