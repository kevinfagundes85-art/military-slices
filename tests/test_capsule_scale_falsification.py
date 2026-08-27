from __future__ import annotations

import json

from benchmark.run_capsule_scale_falsification import (
    CONTRACT_PATH,
    EXPECTED_CONTRACT_SHA256,
    dependency_density_axis,
    lifecycle_history_state,
    multiple_slices_axis,
    sha256_path,
)
from military_slices.governance import probe_execution_enabled


def contract() -> dict[str, object]:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_capsule_scale_contract_is_frozen() -> None:
    payload = contract()

    assert sha256_path(CONTRACT_PATH) == EXPECTED_CONTRACT_SHA256
    assert payload["state_width"]["facts"] == [10, 100, 1000, 10000, 100000]  # type: ignore[index]
    assert payload["dependency_density"]["counts"] == [0, 1, 3, 10, 25, 50, 100]  # type: ignore[index]


def test_decomposable_density_resolves_while_coupled_density_fails_visibly() -> None:
    result = dependency_density_axis(contract())
    decomposable = next(
        row for row in result["rows"] if row["class"] == "decomposable" and row["dependency_count"] == 3
    )
    coupled = next(row for row in result["rows"] if row["class"] == "coupled" and row["dependency_count"] == 3)

    assert decomposable["all_dependencies_accounted"] is True
    assert decomposable["actual_visible_dependency_count"] == 1
    assert coupled["all_dependencies_accounted"] is False
    assert coupled["simultaneous_dependency_count"] == 3
    assert coupled["unsafe_intermediate_states"] == 1


def test_long_history_does_not_activate_historical_decisions() -> None:
    state = lifecycle_history_state(1000)

    assert state.version == 1000
    assert len(state.decisions) == 1000
    assert len(state.mutation_events) == 1000
    assert len(state.lineage) == 1000
    assert all(not task.id.startswith("historical-") for task in state.active_tasks)


def test_multiple_slices_preserve_one_active_gate_and_probe_stays_disabled() -> None:
    result = multiple_slices_axis(contract())

    assert all(row["actual_active_gate_count"] == 1 for row in result["rows"])
    assert probe_execution_enabled() is False
