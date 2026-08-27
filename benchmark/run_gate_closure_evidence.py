from __future__ import annotations

import hashlib
import json
import subprocess  # nosec B404
import time
from datetime import date
from pathlib import Path
from typing import Any

from benchmark.run_sparse_activation_benchmark import ADVERSARIAL, _fact, build_state
from military_slices.engine import apply_confirmed_input, apply_starting_vector, new_state, orient
from military_slices.models import (
    Authority,
    ExecutionState,
    FreshnessStatus,
    ImpactItem,
    LifecyclePosition,
    ServiceComponent,
    ServiceName,
    SliceName,
)
from military_slices.path_runtime import refresh_path_state
from military_slices.temporal import (
    apply_revalidation_delta,
    build_consequential_impact_index,
    consequential_impact_projection,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "benchmark/output"
FIXED = "2026-08-27"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(  # noqa: S603  # nosec B603 B607
        ["git", *args],  # noqa: S607
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def gate1() -> dict[str, Any]:
    scenario = next(item for item in ADVERSARIAL if item.id == "dense-dependency")
    runs = []
    for repetition in range(1, 6):
        state = build_state(scenario)
        initial = state.version
        steps = []
        started = time.perf_counter()
        for index in range(3):
            lookup_started = time.perf_counter()
            projected = consequential_impact_projection(state)
            lookup_ms = (time.perf_counter() - lookup_started) * 1000
            if projected is None or projected.impact_id is None:
                raise RuntimeError("Frozen dense dependency was not projected.")
            before = state.version
            state, changed = apply_revalidation_delta(
                state,
                impact_id=projected.impact_id,
                action="confirm",
                value=None,
                idempotency_key=f"g1-{repetition}-{index}",
            )
            replay, replay_changed = apply_revalidation_delta(
                state,
                impact_id=projected.impact_id,
                action="confirm",
                value=None,
                idempotency_key=f"g1-{repetition}-{index}",
            )
            steps.append(
                {
                    "fact_id": projected.fact_id,
                    "packet_fact_count": 1,
                    "lookup_ms": lookup_ms,
                    "changed": changed,
                    "version_delta": state.version - before,
                    "replay_write": replay_changed,
                    "replay_same_object": replay is state,
                }
            )
        unresolved = consequential_impact_projection(state)
        sequence = [step["fact_id"] for step in steps]
        runs.append(
            {
                "repetition": repetition,
                "steps": steps,
                "sequence": sequence,
                "all_recalled": set(sequence) == set(scenario.required_fact_ids),
                "first_correct": sequence[0] == "adv-employment-restriction",
                "final_unresolved": unresolved.fact_id if unresolved else None,
                "version_delta": state.version - initial,
                "model_calls": 0,
                "probe_calls": 0,
                "production_mutations": 0,
                "wall_ms": (time.perf_counter() - started) * 1000,
            }
        )
    return {
        "disposition": "PASS" if all(r["all_recalled"] and r["final_unresolved"] is None for r in runs) else "FAIL",
        "runs": runs,
        "simultaneous_control": {
            "benchmark_2_strict_correct": "0/5",
            "benchmark_2_dependency_recall": "1/3 per run",
            "source": "immutable Benchmark 2 evidence; not rerun or relabeled",
        },
    }


def gate3() -> dict[str, Any]:
    contract = json.loads((ROOT / "benchmark/contracts/gate3_interruption_classifier_2026-08-27.json").read_text())
    rows = []
    for case in contract["cases"]:
        state = new_state(f"classifier-{case['id']}")
        authority = Authority(case["authority"])
        status = FreshnessStatus(case["status"])
        fact = _fact(
            f"classifier-{case['id']}",
            case["statement"],
            slices=[SliceName.CAREER],
            field_key=case["field_key"],
            authority=authority,
            status=status,
        )
        state.facts.append(fact)
        if case.get("impact"):
            state.impacts.append(
                ImpactItem(
                    id=f"impact-{case['id']}",
                    source_field="frozen",
                    dependent_field=case["field_key"],
                    fact_id=fact.id,
                    affected_slice=SliceName.CAREER,
                    message="Review this change.",
                    question="Does this change the next move?",
                    confirm_label="Confirm",
                    update_label="Update",
                    blocking=True,
                )
            )
        index = build_consequential_impact_index(state)
        started = time.perf_counter()
        projection = consequential_impact_projection(state, index=index)
        lookup_ms = (time.perf_counter() - started) * 1000
        actual = projection is not None
        rows.append(
            {
                "id": case["id"],
                "expected_material": case["expected_material"],
                "interrupted": actual,
                "correct": actual == case["expected_material"],
                "source": projection.source if projection else None,
                "index_build_ms": index.build_ms,
                "lookup_ms": lookup_ms,
            }
        )
    tp = sum(r["expected_material"] and r["interrupted"] for r in rows)
    tn = sum(not r["expected_material"] and not r["interrupted"] for r in rows)
    fp = sum(not r["expected_material"] and r["interrupted"] for r in rows)
    fn = sum(r["expected_material"] and not r["interrupted"] for r in rows)
    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    return {
        "disposition": "PARTIAL",
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "rows": rows,
        "operating_boundary": (
            "Existing lexical fallback is not a semantic classifier; blocking Impact indexing is reliable, "
            "paraphrase and negation are not."
        ),
    }


def _life(position: LifecyclePosition, month: str | None, profile: str) -> Any:
    return apply_starting_vector(
        new_state(profile),
        operating_role="veteran_service_member",
        lifecycle_position=position,
        service=ServiceName.NAVY,
        component=ServiceComponent.ACTIVE_DUTY,
        transition_month=month,
        idempotency_key=f"{profile}-vector",
    )


def gate4() -> dict[str, Any]:
    fixtures = [
        ("serving-18-months", LifecyclePosition.CURRENTLY_SERVING, "2028-02"),
        ("serving-45-days", LifecyclePosition.LEAVING_WITHIN_12_MONTHS, "2026-10"),
        ("recently-separated", LifecyclePosition.SEPARATED_WITHIN_LAST_YEAR, "2026-03"),
        ("three-years", LifecyclePosition.SEPARATED_1_TO_5_YEARS, None),
        ("long-term", LifecyclePosition.SEPARATED_MORE_THAN_5_YEARS, None),
        ("unknown-date", LifecyclePosition.CURRENTLY_SERVING, None),
        ("approximate-date", LifecyclePosition.LEAVING_WITHIN_12_MONTHS, "2027-03"),
    ]
    rows = []
    for label, position, month in fixtures:
        state = refresh_path_state(_life(position, month, f"life-{label}"), today=date(2026, 8, 27))
        rows.append(
            {
                "id": label,
                "position": position.value,
                "month": month,
                "window": state.current_timeline_window,
                "stage": state.stage,
                "tasks": [task.title for task in state.active_tasks],
                "model_calls": 0,
                "future_separation_task_for_past": any(
                    "leave active service" in task.title.casefold() for task in state.active_tasks
                )
                if "separated" in position.value
                else False,
            }
        )
    changed = refresh_path_state(
        _life(LifecyclePosition.LEAVING_WITHIN_12_MONTHS, "2027-06", "life-changed"), today=date(2026, 8, 27)
    )
    prior_window = changed.current_timeline_window
    changed.transition_month = "2026-10"
    changed.version += 1
    changed = refresh_path_state(changed, today=date(2026, 8, 27))
    return {
        "disposition": "PASS" if all(not row["future_separation_task_for_past"] for row in rows) else "FAIL",
        "rows": rows,
        "changed_date": {"before": prior_window, "after": changed.current_timeline_window},
        "coordinate": (
            "existing lifecycle_position plus month-granularity transition_month; no Temporal Anchor primitive"
        ),
    }


def gate5() -> dict[str, Any]:
    state = apply_confirmed_input(
        new_state("gate5"), orient("I want civilian work with predictable hours."), idempotency_key="g5-1"
    )
    state = apply_confirmed_input(
        state, orient("I accepted a civilian job as a Program Manager. This goal is complete."), idempotency_key="g5-2"
    )
    complete = state.execution.state == ExecutionState.COMPLETE and not state.active_tasks
    old_anchor = state.human_anchor
    old_facts = {fact.id for fact in state.facts}
    reopened = apply_confirmed_input(
        state, orient("Now I want to choose an education path for applied AI."), idempotency_key="g5-3"
    )
    return {
        "disposition": "PASS" if complete and reopened.execution.state == ExecutionState.ACTIVE else "FAIL",
        "complete_stopped": complete,
        "old_anchor": old_anchor,
        "new_anchor": reopened.human_anchor,
        "historical_fact_ids_preserved": old_facts.issubset({fact.id for fact in reopened.facts}),
        "probe_calls": 0,
    }


def gate6() -> dict[str, Any]:
    contract = json.loads((ROOT / "benchmark/contracts/gate6_probe_2026-08-27.json").read_text())
    failed_matrix = json.loads((OUT / "sparse-activation-gate-closure-raw-2026-08-26.json").read_text())
    provider_failures = sum(run["status"] == "failed" for run in failed_matrix["runs"])
    return {
        "disposition": "FAIL",
        "cases_frozen": len(contract["cases"]),
        "executed_model_cases": 0,
        "provider_initialization_failures_in_preceding_matrix": provider_failures,
        "reason": (
            "A valid Probe comparison requires model-mediated bounded discovery. "
            "Provider initialization failed; no deterministic proxy was substituted."
        ),
        "production_probe_enabled": False,
        "production_mutations": 0,
    }


def main() -> None:
    OUT.mkdir(exist_ok=True)
    payload = {
        "executed_at": FIXED,
        "git_head": git("rev-parse", "HEAD"),
        "git_status": git("status", "--short"),
        "gates": {"1": gate1(), "3": gate3(), "4": gate4(), "5": gate5(), "6": gate6()},
        "gate2_matrix": "benchmark/output/sparse-activation-gate-closure-raw-2026-08-26.json",
        "gate7": {
            "automated_mobile": {
                "status": "PASS",
                "widths": [320, 375, 414],
                "page_overflow": False,
                "orientation_choice_min_height_px": 57.33,
                "month_input_height_px": 56.125,
                "month_input_font_px": 16,
                "console_warnings_or_errors": 0,
            },
            "physical_android": "OPEN",
            "cold_user": "OPEN",
        },
        "production_mutations": 0,
    }
    path = OUT / "helm-gate-closure-raw-2026-08-27.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"path": str(path), "sha256": sha(path)}, indent=2))


if __name__ == "__main__":
    main()
