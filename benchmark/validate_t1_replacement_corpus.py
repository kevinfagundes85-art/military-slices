"""Validate the public replacement T1 corpus without reading sealed material."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from benchmark.t1_runtime_contract import ReplacementT1PublicTask
from military_slices.adaptive_resolver_aperture import select_adaptive_resolver_aperture
from military_slices.governance import verify_derived_indexes


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_tasks(paths: list[Path]) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    for path in paths:
        value = json.loads(path.read_text(encoding="utf-8"))
        records = value.get("tasks") if isinstance(value, dict) else value
        if not isinstance(records, list):
            raise ValueError(f"{path}: expected a task list")
        tasks.extend(records)
    return tasks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    raw_tasks = load_tasks(args.paths)
    task_ids: set[str] = set()
    mode_counts: Counter[str] = Counter()
    reason_counts: Counter[str] = Counter()
    failures: list[dict[str, str]] = []
    for raw in raw_tasks:
        task_id = str(raw.get("task_id", "UNKNOWN"))
        try:
            if task_id in task_ids:
                raise ValueError("duplicate task_id")
            task_ids.add(task_id)
            task = ReplacementT1PublicTask.model_validate(raw)
            state = task.runtime_state()
            verify_derived_indexes(state)
            selection = select_adaptive_resolver_aperture(state, task.aperture_request.to_runtime())
            mode_counts[selection.receipt.selected_mode.value] += 1
            reason_counts[selection.receipt.reason_code.value] += 1
        except Exception as exc:  # noqa: BLE001 - validation ledger preserves every failure
            failures.append({"task_id": task_id, "type": type(exc).__name__, "message": str(exc)})
    report = {
        "task_count": len(raw_tasks),
        "unique_task_ids": len(task_ids),
        "valid_count": len(raw_tasks) - len(failures),
        "failure_count": len(failures),
        "mode_counts": dict(sorted(mode_counts.items())),
        "reason_counts": dict(sorted(reason_counts.items())),
        "files": [
            {"path": str(path), "bytes": path.stat().st_size, "sha256": digest(path)}
            for path in args.paths
        ],
        "failures": failures,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
