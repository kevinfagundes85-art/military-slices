from __future__ import annotations

import pytest

from benchmark.run_capsule_scale_falsification import dependency_density_axis, dependency_state, state_sha
from benchmark.run_coupled_capsule_and_graduation_gate import gate_2_disposition
from benchmark.run_sparse_activation_benchmark import build_helm_context
from military_slices.agent_runtime import _minimal_context
from military_slices.engine import active_gate
from military_slices.governance import bind_gate_contracts
from military_slices.temporal import (
    build_consequential_impact_index,
    consequential_impact_index,
    consequential_impact_projection,
    minimum_sufficient_evidence,
)


@pytest.mark.parametrize("count", [3, 10, 25, 50, 100])
def test_coupled_gate_projects_exact_minimum_sufficient_surface(count: int) -> None:
    state = dependency_state(count, coupled=True)
    before = state_sha(state)

    context, metrics = build_helm_context(state)
    expected = [fact.id for fact in state.facts]
    actual = [fact["id"] for fact in context["permitted_governed_evidence"]]
    runtime = _minimal_context(state)
    runtime_actual = [fact["id"] for fact in runtime["minimum_sufficient_evidence"]]

    assert actual == expected
    assert runtime_actual == expected
    assert metrics["minimum_sufficient_evidence_count"] == count
    assert context["acquisition_horizon"] is None
    assert context["enforced_frontier"]["minimum_sufficient_evidence"] == {
        "required_count": count,
        "required_ids": expected,
        "selection_authority": "current Gate.required_evidence",
    }
    assert state_sha(state) == before


def test_decomposable_dependencies_remain_sparse_and_sequential() -> None:
    contract = {
        "dependency_density": {"counts": [1, 3, 10, 25, 50, 100]},
    }
    result = dependency_density_axis(contract)
    rows = [row for row in result["rows"] if row["class"] == "decomposable"]

    assert all(row["actual_visible_dependency_count"] == 1 for row in rows)
    assert all(row["all_dependencies_accounted"] is True for row in rows)
    assert all(row["resolved_sequence_count"] == row["dependency_count"] for row in rows)


def test_coupled_surface_excludes_irrelevant_governed_fact() -> None:
    state = dependency_state(3, coupled=True)
    irrelevant = state.facts[0].model_copy(
        update={"id": "irrelevant-extra", "statement": "An unrelated archival detail."}
    )
    state.facts.append(irrelevant)
    state.latent_fact_count = len(state.facts)
    bind_gate_contracts(state)
    build_consequential_impact_index(state)

    context, _ = build_helm_context(state)
    actual = {fact["id"] for fact in context["permitted_governed_evidence"]}

    assert actual == {"density-fact-000", "density-fact-001", "density-fact-002"}
    assert "irrelevant-extra" not in actual


def test_missing_required_evidence_fails_closed() -> None:
    state = dependency_state(3, coupled=True)
    state.facts.pop()
    index = build_consequential_impact_index(state)
    gate = active_gate(state)
    interruption = consequential_impact_projection(state, index=index)

    with pytest.raises(ValueError, match="missing declared required evidence"):
        minimum_sufficient_evidence(state, gate=gate, interruption=interruption, index=index)


def test_stale_gate_binding_fails_closed() -> None:
    state = dependency_state(3, coupled=True)
    state.version += 1
    index = build_consequential_impact_index(state)

    with pytest.raises(ValueError, match="bound to Canonical version"):
        minimum_sufficient_evidence(
            state,
            gate=active_gate(state),
            interruption=consequential_impact_projection(state, index=index),
            index=index,
        )


def test_duplicate_required_evidence_fails_closed() -> None:
    state = dependency_state(3, coupled=True)
    gate = active_gate(state)
    assert gate is not None
    gate.required_evidence.append(gate.required_evidence[0])
    index = consequential_impact_index(state)

    with pytest.raises(ValueError, match="duplicate required evidence"):
        minimum_sufficient_evidence(
            state,
            gate=gate,
            interruption=consequential_impact_projection(state, index=index),
            index=index,
        )


def test_graduation_gate_requires_five_valid_fully_governed_attempts() -> None:
    valid = {
        "valid": True,
        "semantic_valid": True,
        "graduation_success": True,
        "restart_survival": True,
        "second_pass_probe_calls": 0,
        "second_pass_model_calls": 0,
        "second_pass_tokens": 0,
        "authority_violation": False,
    }
    failed_provider = {**valid, "valid": False, "semantic_valid": False, "graduation_success": False}

    disposition, metrics = gate_2_disposition([valid] * 5 + [failed_provider] * 5, minimum_valid=5)

    assert disposition == "PASS"
    assert metrics == {
        "attempts": 10,
        "valid_attempts": 5,
        "successful_graduations": 5,
        "provider_or_contract_failures": 5,
        "authority_violations": 0,
    }
