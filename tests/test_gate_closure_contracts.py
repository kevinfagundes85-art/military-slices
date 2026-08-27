from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from benchmark.run_sparse_activation_benchmark import ADVERSARIAL, build_state
from military_slices.engine import apply_confirmed_input, apply_starting_vector, new_state, orient
from military_slices.models import ExecutionState, LifecyclePosition, ServiceComponent, ServiceName
from military_slices.path_runtime import refresh_path_state
from military_slices.temporal import apply_revalidation_delta, consequential_impact_projection

ROOT = Path(__file__).resolve().parents[1]


def test_gate1_dense_contract_is_frozen_and_preserves_benchmark_ground_truth() -> None:
    contract = json.loads((ROOT / "benchmark/contracts/gate1_dense_iterative_2026-08-27.json").read_text())
    assert contract["immutable_dependencies"] == [
        "adv-employment-restriction",
        "adv-location-deadline",
        "adv-expiring-certification",
    ]
    assert contract["first_expected_dependency"] == "adv-employment-restriction"
    assert contract["sparse_packet_max_dependency_facts"] == 1
    assert contract["pass_conditions"]["unique_human_decisions"] == 3


def test_gate3_classifier_contract_was_frozen_without_a_post_hoc_threshold() -> None:
    contract = json.loads((ROOT / "benchmark/contracts/gate3_interruption_classifier_2026-08-27.json").read_text())
    assert contract["frozen_before_execution"] is True
    assert contract["no_post_hoc_vocabulary_tuning"] is True
    assert len(contract["cases"]) == 15
    assert {case["expected_material"] for case in contract["cases"]} == {True, False}


def test_gate6_probe_contract_is_discover_wake_only_and_frozen() -> None:
    contract = json.loads((ROOT / "benchmark/contracts/gate6_probe_2026-08-27.json").read_text())
    assert contract["production_probe_enabled"] is False
    assert contract["authority"] == "DISCOVER / WAKE only"
    assert "mutate canonical" in contract["prohibited"]
    assert len(contract["cases"]) == 5


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
    assert {decision.gate_id for decision in state.decisions if decision.gate_id.startswith("revalidate:")} == {
        "revalidate:external_employment_restriction",
        "revalidate:relocation_timing",
        "revalidate:program_eligibility",
    }


def _lifecycle_state(position: LifecyclePosition, month: str | None, profile: str) -> object:
    return apply_starting_vector(
        new_state(profile),
        operating_role="veteran_service_member",
        lifecycle_position=position,
        service=ServiceName.NAVY,
        component=ServiceComponent.ACTIVE_DUTY,
        transition_month=month,
        idempotency_key=f"{profile}-vector",
    )


def test_month_granularity_lifecycle_eliminates_ineligible_path_work_before_model_reasoning() -> None:
    eighteen = _lifecycle_state(LifecyclePosition.CURRENTLY_SERVING, "2028-02", "life-18")
    forty_five = _lifecycle_state(LifecyclePosition.LEAVING_WITHIN_12_MONTHS, "2026-10", "life-45")
    recent = _lifecycle_state(LifecyclePosition.SEPARATED_WITHIN_LAST_YEAR, "2026-03", "life-recent")
    three_year = _lifecycle_state(LifecyclePosition.SEPARATED_1_TO_5_YEARS, None, "life-three")
    long_term = _lifecycle_state(LifecyclePosition.SEPARATED_MORE_THAN_5_YEARS, None, "life-long")
    unknown = _lifecycle_state(LifecyclePosition.CURRENTLY_SERVING, None, "life-unknown")

    eighteen = refresh_path_state(eighteen, today=date(2026, 8, 27))
    forty_five = refresh_path_state(forty_five, today=date(2026, 8, 27))
    recent = refresh_path_state(recent, today=date(2026, 8, 27))
    assert eighteen.current_timeline_window in {"A", "B"}
    assert forty_five.current_timeline_window in {"E", "F"}
    assert recent.current_timeline_window == "H"
    assert three_year.current_timeline_window == "H"
    assert long_term.current_timeline_window == "H"
    assert unknown.current_timeline_window == "PATH_IDENTITY"
    for separated in (recent, three_year, long_term):
        assert all("leave active service" not in task.title.casefold() for task in separated.active_tasks)


def test_complete_stops_and_new_human_intent_opens_a_new_governed_lifecycle() -> None:
    state = apply_confirmed_input(
        new_state("closure-new-anchor"),
        orient("I want civilian work with predictable hours."),
        idempotency_key="closure-anchor-1",
    )
    state = apply_confirmed_input(
        state,
        orient("I accepted a civilian job as a Program Manager. This goal is complete."),
        idempotency_key="closure-complete-2",
    )
    prior_anchor = state.human_anchor
    prior_fact_ids = {fact.id for fact in state.facts}
    assert state.execution.state == ExecutionState.COMPLETE
    assert state.active_tasks == []

    reopened = apply_confirmed_input(
        state,
        orient("Now I want to choose an education path for applied AI."),
        idempotency_key="closure-new-anchor-3",
    )
    assert reopened.execution.state == ExecutionState.ACTIVE
    assert reopened.human_anchor != prior_anchor
    assert prior_fact_ids.issubset({fact.id for fact in reopened.facts})
    assert reopened.version == state.version + 1
