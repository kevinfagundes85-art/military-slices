from __future__ import annotations

import json
from pathlib import Path

from benchmark.run_sparse_activation_benchmark import ADVERSARIAL, build_state
from military_slices.temporal import apply_revalidation_delta, consequential_impact_projection


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


def test_gate3_classifier_contract_was_frozen_without_a_post_hoc_threshold() -> None:
    contract = json.loads(
        (ROOT / "benchmark/contracts/gate3_interruption_classifier_2026-08-27.json").read_text()
    )
    assert contract["frozen_before_execution"] is True
    assert contract["no_post_hoc_vocabulary_tuning"] is True
    assert len(contract["cases"]) == 15
    assert {case["expected_material"] for case in contract["cases"]} == {True, False}


def test_dense_dependencies_resolve_iteratively_without_widening_sparse_projection() -> None:
    scenario = next(item for item in ADVERSARIAL if item.id == "dense-dependency")
    state = build_state(scenario)
    initial_version = state.version
    sequence: list[str] = []

    for step in range(3):
        projection = consequential_impact_projection(state)
        assert projection is not None
        assert projection.impact_id is not None
        sequence.append(projection.fact_id)
        state, changed = apply_revalidation_delta(
            state,
            impact_id=projection.impact_id,
            action="confirm",
            value=None,
            idempotency_key=f"dense-step-{step}",
        )
        assert changed is True
        replay, replay_changed = apply_revalidation_delta(
            state,
            impact_id=projection.impact_id,
            action="confirm",
            value=None,
            idempotency_key=f"dense-step-{step}",
        )
        assert replay is state
        assert replay_changed is False

    assert sequence[0] == "adv-employment-restriction"
    assert set(sequence) == set(scenario.required_fact_ids)
    assert state.version == initial_version + 3
    assert consequential_impact_projection(state) is None
    assert {
        decision.gate_id for decision in state.decisions if decision.gate_id.startswith("revalidate:")
    } == {
        "revalidate:external_employment_restriction",
        "revalidate:relocation_timing",
        "revalidate:program_eligibility",
    }
