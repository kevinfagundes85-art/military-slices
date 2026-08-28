"""Build compact, label-blind T1 scoring extracts from the committed raw ledger."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from benchmark.t1_runtime_contract import ReplacementT1PublicTask

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "benchmark" / "t1_runtime_r3"
RAW = ROOT / "benchmark" / "output" / "adaptive_resolver_aperture_t1_r3" / "provider_execution_raw.json"
OUT = ROOT / "benchmark" / "output" / "adaptive_resolver_aperture_t1_r3" / "scoring_extract"
SHARDS = tuple(sorted(PACKAGE.glob("helm_arav1_t1_r3_public_corpus_shard_*_of_6_2026-08-28.json")))

HARD_GATES = (
    "stale_suppression",
    "authority_violation",
    "improper_governance_bypass",
    "hidden_identity_miss",
    "model_selected_authority",
    "ungoverned_broad_context_exposure",
    "relevant_invalidation_bypass",
    "partial_coupled_adjudication",
    "unauthorized_canonical_mutation",
)


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def final_failure(call: dict[str, Any]) -> str | None:
    if call.get("valid") or not call.get("attempts"):
        return None
    attempt = call["attempts"][-1]
    return str(attempt.get("failure_class") or "provider_other")


def provider_metrics(call: dict[str, Any]) -> dict[str, Any]:
    attempts = call.get("attempts", [])
    return {
        "attempts": len(attempts),
        "input_tokens": sum(int(item.get("input_tokens", 0)) for item in attempts),
        "output_tokens": sum(int(item.get("output_tokens", 0)) for item in attempts),
        "thinking_tokens": sum(int(item.get("thinking_tokens", 0)) for item in attempts),
        "provider_cost_usd": sum(float(item.get("estimated_cost_usd", 0.0)) for item in attempts),
        "provider_failure_class": final_failure(call),
    }


def semantic_result(call: dict[str, Any], arm: str) -> tuple[str, list[str], str | None]:
    if not call.get("valid"):
        return "PROVIDER_FAILURE", [], None
    decision = call.get("decision") or {}
    if arm == "H1" and decision.get("type") == "DETERMINISTIC_GOVERNED_REUSE":
        return "DETERMINISTIC_REUSE", list(decision.get("reuse_fact_ids", [])), "governed_reuse"
    if arm == "H1" and "nomination" in decision:
        nomination = decision.get("nomination")
        outcome = "CANDIDATE_FOR_EXAMINATION" if nomination is not None else "NO_NOMINATION"
        receipt = call.get("selection_receipt") or {}
        return outcome, list(receipt.get("evidence_ids", [])), "probe_discovery"
    return (
        str(decision.get("outcome", "MISSING_OUTCOME")),
        list(decision.get("evidence_ids", [])),
        "governed_adjudication",
    )


def row(task_id: str, arm: str, call: dict[str, Any]) -> dict[str, Any]:
    outcome, evidence_ids, result_type = semantic_result(call, arm)
    receipt = call.get("selection_receipt") or {}
    metrics = provider_metrics(call)
    payload: dict[str, Any] = {
        "task_id": task_id,
        "arm": arm,
        "final_outcome": outcome,
        "semantic_result_type": result_type,
        "evidence_ids": json.dumps(evidence_ids, separators=(",", ":")),
        "selected_mode": receipt.get("selected_mode"),
        "mode_reason_code": receipt.get("reason_code"),
        **metrics,
        "human_examinations": 0,
        "authority_oracle_result": "null",
        "authority_lookup_performed": False,
    }
    payload.update({key: 0 for key in HARD_GATES})
    return payload


def main() -> int:
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] | None = None
    artifacts: list[dict[str, Any]] = []
    totals = {"H0": 0, "H1": 0, "B": 0}
    for shard_number, shard_path in enumerate(SHARDS, start=1):
        public = json.loads(shard_path.read_text(encoding="utf-8"))
        tasks = [ReplacementT1PublicTask.model_validate(item) for item in public["tasks"]]
        rows = [
            row(task.task_id, arm, raw["results"][arm][task.task_id])
            for task in tasks
            for arm in ("H0", "H1", "B")
        ]
        for item in rows:
            totals[item["arm"]] += 1
        if fieldnames is None:
            fieldnames = list(rows[0])
        path = OUT / f"t1_r3_scoring_extract_shard_{shard_number}_of_6.csv"
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        artifacts.append(
            {
                "name": path.name,
                "bytes": path.stat().st_size,
                "sha256": sha256_path(path),
                "rows": len(rows),
            }
        )

    results = raw["results"]
    h1_provider_calls = [item for item in results["H1"].values() if item.get("attempts")]
    summary = {
        "artifact": "T1 r3 compact scoring extract manifest",
        "source_raw_sha256": sha256_path(RAW),
        "source_execution_commit": "ed451fd4b532236d3c5cef003ccad0dbeff6550f",
        "row_count": sum(totals.values()),
        "rows_by_arm": totals,
        "h0": {
            "provider_valid": sum(bool(item.get("valid")) for item in results["H0"].values()),
            "provider_failures": sum(not bool(item.get("valid")) for item in results["H0"].values()),
        },
        "h1": {
            "provider_logical_calls": len(h1_provider_calls),
            "provider_valid": sum(bool(item.get("valid")) for item in h1_provider_calls),
            "provider_failures": sum(not bool(item.get("valid")) for item in h1_provider_calls),
            "zero_call_deterministic_reuse": sum(not item.get("attempts") for item in results["H1"].values()),
            "arm_task_results": len(results["H1"]),
        },
        "b": {
            "provider_valid": sum(bool(item.get("valid")) for item in results["B"].values()),
            "provider_failures": sum(not bool(item.get("valid")) for item in results["B"].values()),
        },
        "authority_oracle": {
            "requests_made_during_execution": 0,
            "result_for_every_task": "null",
            "retrospective_schedule_application_prohibited": True,
        },
        "hard_gate_counter_basis": (
            "read-only routing and non-authoritative model proposals; "
            "no Canonical mutation path executed"
        ),
        "artifacts": artifacts,
    }
    manifest_path = OUT / "t1_r3_scoring_extract_manifest.json"
    manifest_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"manifest_sha256={sha256_path(manifest_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
