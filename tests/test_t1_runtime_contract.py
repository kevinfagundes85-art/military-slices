from __future__ import annotations

from benchmark.t1_runtime_contract import (
    ReplacementT1PublicTask,
    governed_resolver_invocation,
    sha256_json,
)
from military_slices.adaptive_resolver_aperture import (
    ApertureRequest,
    ExecutionMode,
    select_adaptive_resolver_aperture,
)
from tests.test_adaptive_resolver_aperture import VALIDITY, _recorded_rejection, _request, _state


def _task(state, request: ApertureRequest) -> ReplacementT1PublicTask:  # type: ignore[no-untyped-def]
    state_json = state.model_dump(mode="json")
    return ReplacementT1PublicTask.model_validate(
        {
            "schema_version": "t1.replacement.public-task/1.0.0",
            "corpus_id": "replacement-fixture",
            "task_id": "t1r-0000000000000001",
            "canonical_state": state_json,
            "canonical_state_sha256": sha256_json(state_json),
            "aperture_request": {
                "task_decision_id": "t1r-0000000000000001",
                "gate_id": request.gate_id,
                "effect_dimension": request.effect_dimension,
                "reuse_fact_ids": list(request.reuse_fact_ids),
                "reuse_validity_dimensions": list(request.reuse_validity_dimensions),
                "permitted_latent_fact_id": request.permitted_latent_fact_id,
                "probe_discovery_permitted": request.probe_discovery_permitted,
            },
            "decision_request": {"question": "What does governed evidence permit?"},
            "broad_context_case": {"facts": state_json["facts"]},
            "authority_binding": {"request_event_type": "GATE_EVALUATION"},
        }
    )


def test_replacement_task_is_exact_runtime_input() -> None:
    state = _state(3, required=True)
    task = _task(state, _request())
    selection = select_adaptive_resolver_aperture(task.runtime_state(), task.aperture_request.to_runtime())
    assert selection.receipt.selected_mode == ExecutionMode.WIDE_GOVERNED_APERTURE
    assert selection.receipt.evidence_ids == ["fact-000", "fact-001", "fact-002"]


def test_mode_a_uses_real_rejection_and_bypasses_provider() -> None:
    state = _recorded_rejection()
    request = _request(reuse_fact_ids=("fact-000",), reuse_validity_dimensions=VALIDITY)
    task = _task(state, request)
    selection = select_adaptive_resolver_aperture(task.runtime_state(), task.aperture_request.to_runtime())
    assert selection.receipt.selected_mode == ExecutionMode.DETERMINISTIC_REUSE
    assert governed_resolver_invocation(task, arm="H1", selection=selection) is None


def test_mode_e_requires_explicit_public_structural_binding() -> None:
    state = _state(1)
    request = _request(permitted_latent_fact_id="fact-000", probe_discovery_permitted=True)
    task = _task(state, request)
    selection = select_adaptive_resolver_aperture(task.runtime_state(), task.aperture_request.to_runtime())
    assert selection.receipt.selected_mode == ExecutionMode.PROBE_DISCOVERY


def test_sparse_and_wide_payloads_are_exact() -> None:
    state = _state(10, required=True)
    task = _task(state, _request())
    selection = select_adaptive_resolver_aperture(task.runtime_state(), task.aperture_request.to_runtime())
    invocation = governed_resolver_invocation(task, arm="H1", selection=selection)
    assert invocation is not None
    evidence = invocation.payload["governed_surface"]["evidence"]
    assert [item["id"] for item in evidence] == [f"fact-{index:03d}" for index in range(10)]


def test_h0_uses_full_state() -> None:
    state = _state(3, required=True)
    task = _task(state, _request())
    invocation = governed_resolver_invocation(task, arm="H0", selection=None)
    assert invocation is not None
    assert invocation.payload["governed_surface"] == state.model_dump(mode="json")
