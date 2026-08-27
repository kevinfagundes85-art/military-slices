from __future__ import annotations

from benchmark.run_sparse_activation_benchmark import (
    ADVERSARIAL,
    EXPECTED_NORMAL_DECISION,
    EXPECTED_NORMAL_GATE,
    NORMAL_REQUIRED,
    Scenario,
    build_baseline_context,
    build_helm_context,
    build_state,
    canonical_json,
    dataset_manifest,
    sha256_text,
)

BENCHMARK_1_DATASET_SHA256 = "4d89fbb0cfb6ed8588ec414b05d68b3e79cd0a404c25ef2be28da9f31e8f7437"


def _normal(scale: int) -> Scenario:
    return Scenario(
        f"normal-{scale}",
        f"Normal {scale}",
        scale,
        EXPECTED_NORMAL_GATE,
        EXPECTED_NORMAL_DECISION,
        NORMAL_REQUIRED,
    )


def _adversarial(scenario_id: str) -> Scenario:
    return next(item for item in ADVERSARIAL if item.id == scenario_id)


def test_benchmark_2_preserves_benchmark_1_ground_truth_manifest() -> None:
    normal = [_normal(scale) for scale in (10, 100, 1_000, 10_000, 100_000)]

    assert sha256_text(canonical_json(dataset_manifest([*normal, *ADVERSARIAL]))) == (
        BENCHMARK_1_DATASET_SHA256
    )


def test_scale_generator_is_exact_and_reproducible() -> None:
    first = build_state(_normal(100))
    second = build_state(_normal(100))

    assert len(first.facts) == 100
    assert [fact.id for fact in first.facts] == [fact.id for fact in second.facts]
    assert first.human_anchor == second.human_anchor
    assert len(first.active_tasks) == 1


def test_competent_baseline_includes_ground_truth_and_excludes_clear_noise() -> None:
    state = build_state(_normal(100))
    context, metrics = build_baseline_context(state)
    ids = {item["id"] for item in context["facts"]}
    clear_noise_ids = {fact.id for fact in state.facts if not fact.affected_slices}

    assert set(NORMAL_REQUIRED).issubset(ids)
    assert ids.isdisjoint(clear_noise_ids)
    assert metrics["active_fact_count"] < len(state.facts)


def test_sparse_projection_activates_one_task_and_bounded_evidence() -> None:
    state = build_state(_normal(10_000))
    context, metrics = build_helm_context(state)
    ids = {item["id"] for item in context["permitted_governed_evidence"]}

    assert metrics["active_task_count"] == 1
    assert metrics["horizon_size"] >= 1
    assert metrics["active_fact_count"] <= 8
    assert set(NORMAL_REQUIRED).issubset(ids)
    assert metrics["latent_fact_count"] >= 9_992


def test_hidden_dependency_forces_bounded_re_evaluation_without_broadening_context() -> None:
    state = build_state(_adversarial("hidden-dependency"))
    baseline, _ = build_baseline_context(state)
    helm, metrics = build_helm_context(state)
    baseline_ids = {item["id"] for item in baseline["facts"]}
    helm_ids = {item["id"] for item in helm["permitted_governed_evidence"]}

    assert "adv-employment-restriction" in baseline_ids
    assert helm_ids == {"adv-employment-restriction"}
    assert metrics["impact_forced_re_evaluation"] is True
    assert metrics["active_fact_count"] == 1
    assert metrics["probe_calls"] == 0


def test_cross_domain_and_temporal_impacts_force_the_same_bounded_projection() -> None:
    expected = {
        "cross-domain-collision": "adv-location-deadline",
        "temporal-activation": "adv-expiring-certification",
    }
    for scenario_id, fact_id in expected.items():
        context, metrics = build_helm_context(build_state(_adversarial(scenario_id)))
        ids = {item["id"] for item in context["permitted_governed_evidence"]}

        assert ids == {fact_id}
        assert metrics["impact_forced_re_evaluation"] is True
        assert metrics["active_fact_count"] == 1
        assert metrics["probe_calls"] == 0


def test_conflict_supersedes_normal_frontier_but_does_not_invent_evidence() -> None:
    state = build_state(_adversarial("conflict"))
    context, metrics = build_helm_context(state)
    ids = {item["id"] for item in context["permitted_governed_evidence"]}

    assert context["enforced_frontier"]["benchmark_gate_key"] == "authority-conflict"
    assert metrics["active_gate"] == "benchmark-authority-conflict"
    assert metrics["active_task_count"] == 1
    assert ids == {"adv-authority-conflict"}
    assert metrics["impact_forced_re_evaluation"] is True


def test_normal_frontier_packet_does_not_widen_after_impact_fix() -> None:
    context, metrics = build_helm_context(build_state(_normal(100_000)))
    ids = {item["id"] for item in context["permitted_governed_evidence"]}

    assert metrics["impact_forced_re_evaluation"] is False
    assert metrics["active_fact_count"] == 8
    assert set(NORMAL_REQUIRED).issubset(ids)
    assert context["enforced_frontier"]["benchmark_gate_key"] == EXPECTED_NORMAL_GATE
    assert metrics["probe_calls"] == 0


def test_baseline_context_is_model_safe_capped_at_large_scale() -> None:
    state = build_state(_normal(10_000))
    context, metrics = build_baseline_context(state)

    assert metrics["active_fact_count"] <= 384
    assert metrics["context_bytes"] < 180_000
    assert context["retrieval_contract"]["truncated"] is True
