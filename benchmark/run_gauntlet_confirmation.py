from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

from run_gauntlet import Action, Scenario, run_scenario
from run_gauntlet_anchor_order import scenarios as anchor_order_scenarios

EXACT_MATRIX_FAILURES = (
    ("Army", "December 2028", "Logistics Manager", "Senior Logistics Manager"),
    ("Navy", "June 2028", "Technical Program Manager", "Senior Technical Program Manager"),
    ("Air Force", "January 2027", "Aviation Safety Manager", "Senior Aviation Safety Manager"),
    ("Space Force", "November 2026", "Space Systems Analyst", "Senior Space Systems Analyst"),
)


def confirmation_scenarios() -> tuple[Scenario, ...]:
    scenarios = list(anchor_order_scenarios())
    for index, (service, when, first_target, next_target) in enumerate(EXACT_MATRIX_FAILURES, start=1):
        scenarios.append(
            Scenario(
                f"C-M{index}",
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
                    Action("reload"),
                ),
                expected=("impact", "revalidation", "persistence", "active"),
            )
        )
    scenarios.extend(
        (
            Scenario(
                "C-R1",
                "Navy",
                "retiring member",
                "6–12 months",
                "resume-generic-target",
                (
                    Action(
                        "text",
                        "My anchor is make my resume submission-ready, but I have not named the target role yet.",
                    ),
                ),
                expected=("resume_target_gate", "active"),
            ),
            Scenario(
                "C-R2",
                "Marine Corps",
                "separating member",
                "<90 days",
                "resume-negated-target",
                (Action("text", "Make my résumé ready, but I don't have a target role yet."),),
                expected=("resume_target_gate", "active"),
            ),
            Scenario(
                "C-R3",
                "Army",
                "veteran",
                "post-transition",
                "resume-concrete-target",
                (Action("text", "Make my résumé submission-ready for Senior Program Manager."),),
                expected=("no_resume_target_gate", "active"),
            ),
            Scenario(
                "C-R4",
                "Air Force",
                "military spouse",
                "PCS-driven",
                "resume-posting-target",
                (Action("text", "Make my résumé ready for this uploaded job posting."),),
                expected=("no_resume_target_gate", "active"),
            ),
            Scenario(
                "C-R5",
                "Space Force",
                "separating member",
                ">18 months",
                "resume-target-cleared",
                (
                    Action("text", "Make my résumé submission-ready for Space Systems Analyst."),
                    Action("text", "Clear my target role; I have not chosen the specific role."),
                ),
                expected=("resume_target_gate", "active"),
            ),
            Scenario(
                "C-E1",
                "Coast Guard",
                "separating member",
                "90–180 days",
                "execution-active",
                (Action("text", "I want civilian work with predictable hours."),),
                expected=("active",),
            ),
            Scenario(
                "C-E2",
                "Army",
                "separating member",
                "12–18 months",
                "execution-paralyzed",
                (
                    Action("text", "I want civilian work with predictable hours."),
                    Action("text", "I need immediate income and full-time education in the same first six months."),
                ),
                expected=("conflict", "paralyzed"),
            ),
            Scenario(
                "C-E3",
                "Navy",
                "retiring member",
                "6–12 months",
                "execution-scoped-paralysis",
                (
                    Action("text", "I want civilian work with predictable hours."),
                    Action("text", "I need immediate income and full-time education in the same first six months."),
                    Action("text", "I led 20 people and managed operational schedules."),
                ),
                expected=("conflict", "paralyzed", "scoped_evidence"),
            ),
            Scenario(
                "C-E4",
                "Marine Corps",
                "separating member",
                "<90 days",
                "execution-clearance",
                (
                    Action("text", "I want civilian work with predictable hours."),
                    Action("text", "I need immediate income and full-time education in the same first six months."),
                    Action("decide", "Immediate income"),
                    Action("reload"),
                ),
                expected=("active", "persistence"),
            ),
            Scenario(
                "C-E5",
                "Air Force",
                "veteran",
                "post-transition",
                "execution-complete",
                (
                    Action("text", "I want civilian work with predictable hours."),
                    Action("text", "I accepted a civilian job as Program Manager. This goal is complete."),
                    Action("reload"),
                ),
                expected=("complete", "persistence"),
            ),
            Scenario(
                "C-A1",
                "Army",
                "separating member",
                "12–18 months",
                "artifact-txt",
                (Action("text", "My career target is Program Manager."), Action("artifact", artifact_type="txt")),
                expected=("active",),
            ),
            Scenario(
                "C-A2",
                "Navy",
                "retiring member",
                "6–12 months",
                "artifact-docx",
                (Action("text", "My career target is Program Manager."), Action("artifact", artifact_type="docx")),
                expected=("active",),
            ),
            Scenario(
                "C-A3",
                "Marine Corps",
                "separating member",
                "<90 days",
                "artifact-pdf",
                (Action("text", "My career target is Operations Manager."), Action("artifact", artifact_type="pdf")),
                expected=("active",),
            ),
            Scenario(
                "C-A4",
                "Coast Guard",
                "military spouse",
                "PCS-driven",
                "artifact-image",
                (
                    Action("text", "My career target is Emergency Planning Manager."),
                    Action("artifact", artifact_type="png"),
                ),
                expected=("active",),
            ),
        )
    )
    assert len(scenarios) == 30
    return tuple(scenarios)


def main() -> None:
    cases = confirmation_scenarios()
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
    elapsed = time.perf_counter() - started
    cost = round(sum(item["estimated_cost"] for item in results), 6)
    payload = {
        "start_timestamp": started_at.isoformat(),
        "wall_seconds": round(elapsed, 3),
        "time_rail_seconds": 900,
        "cost_rail_usd": 5.0,
        "attempted": len(cases),
        "completed": len(results),
        "invariant_clean": sum(not item["failure_codes"] for item in results),
        "driver_errors": errors,
        "within_time_rail": elapsed <= 900,
        "within_cost_rail": cost <= 5.0,
        "model_calls": sum(item["model_calls"] for item in results),
        "tool_calls": sum(item["tool_calls"] for item in results),
        "input_tokens": sum(item["input_tokens"] for item in results),
        "output_tokens": sum(item["output_tokens"] for item in results),
        "estimated_cost": cost,
        "results": results,
    }
    output = Path(__file__).with_name("output") / f"gauntlet-confirmation-{started_at.strftime('%Y%m%dT%H%M%SZ')}.json"
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
                    "within_time_rail",
                    "within_cost_rail",
                )
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
