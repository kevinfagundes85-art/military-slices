from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_gate1_dense_contract_is_frozen_and_preserves_benchmark_ground_truth() -> None:
    contract = json.loads(
        (ROOT / "benchmark/contracts/gate1_dense_iterative_2026-08-27.json").read_text()
    )
    assert contract["immutable_dependencies"] == [
        "adv-employment-restriction",
        "adv-location-deadline",
        "adv-expiring-certification",
    ]
    assert contract["first_expected_dependency"] == "adv-employment-restriction"
    assert contract["sparse_packet_max_dependency_facts"] == 1
    assert contract["pass_conditions"]["unique_human_decisions"] == 3
