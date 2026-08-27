from __future__ import annotations

import json

from benchmark.run_governed_identity_generalization_falsification import (
    CONTRACT_PATH,
    deterministic_matrix,
)


def test_frozen_identity_generalization_matrix_preserves_safety_boundary() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    result = deterministic_matrix(contract)
    i0 = result["identity_scoreboard"]["I0"]
    i1 = result["identity_scoreboard"]["I1"]

    assert i0["recognized_true_equivalents"] == 0
    assert i0["false_suppressions"] == 0
    assert i1["recognized_true_equivalents"] == 3
    assert i1["identity_misses"] == 3
    assert i1["recognition_recall"] == 0.5
    assert i1["suppression_precision"] == 1.0
    assert i1["false_suppressions"] == 0
    assert i1["stale_suppressions"] == 0
    assert i1["authority_violations"] == 0
    assert result["i2"]["status"] == "NOT EXPRESSIBLE IN FROZEN DOMAIN PACK"


def test_generalized_matches_survive_irrelevant_change_and_invalidate_materially() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    rows = deterministic_matrix(contract)["state_bound_invalidations"]

    assert len(rows) == 3
    for row in rows:
        assert row["irrelevant_canonical_change"]["suppressed"] is True
        assert row["material_source_or_evidence_change"]["suppressed"] is False
        assert row["gate_version_change"]["suppressed"] is False
        assert row["relevant_authority_change"]["suppressed"] is False
        assert row["relevant_time_or_lifecycle_change"]["suppressed"] is False
        assert row["stale_suppressions"] == 0
