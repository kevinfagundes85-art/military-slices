from __future__ import annotations

from copy import deepcopy

import pytest

from military_slices.adaptive_resolver_aperture import (
    ApertureReasonCode,
    ApertureRequest,
    ExecutionMode,
    select_adaptive_resolver_aperture,
)
from military_slices.engine import new_state
from military_slices.governance import bind_gate_contracts
from military_slices.models import (
    ActorProvenance,
    Authority,
    Fact,
    FreshnessStatus,
    Gate,
    GateState,
    ImpactItem,
    LifecyclePosition,
    LineageIntegrity,
    SliceName,
    SurfaceType,
)
from military_slices.state_bound_rejection import record_state_bound_rejection

VALIDITY = ("anchor", "path", "lifecycle", "time_validity", "authority", "effect_reachability")


def _state(count: int = 0, *, required: bool = False):  # type: ignore[no-untyped-def]
    state = new_state(f"h1-{count}-{required}")
    state.human_anchor = "Reach the authorized next outcome."
    state.path_target_state = "RESOLVE_CURRENT_GATE"
    facts = [
        Fact(
            id=f"fact-{index:03d}",
            statement=f"Governed condition {index}.",
            value=f"condition-{index}",
            authority=Authority.AUTHORITATIVE_SOURCE,
            affected_slices=[SliceName.CAREER],
            field_key=f"condition_{index}",
        )
        for index in range(count)
    ]
    state.facts.extend(facts)
    gate = Gate(
        id="gate-current",
        title="Resolve current governed decision",
        question="What does the governed evidence permit?",
        why="This is the current consequential Gate.",
        state=GateState.CONFLICTED if required else GateState.UNKNOWN,
        surface=SurfaceType.CONFLICT if required else SurfaceType.CONFIRM,
        affected_slices=[SliceName.CAREER],
        authority_required=Authority.HUMAN,
        authorized_scope=["slice:career"],
        required_evidence=[item.id for item in facts] if required else [],
    )
    state.gates.append(gate)
    state.latent_fact_count = len(facts)
    return bind_gate_contracts(state)


def _request(**changes: object) -> ApertureRequest:
    values: dict[str, object] = {
        "task_decision_id": "developer-fixture",
        "gate_id": "gate-current",
        "effect_dimension": "employment_authority",
    }
    values.update(changes)
    return ApertureRequest(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize("count", [3, 10, 25, 50, 100])
def test_declared_joint_surface_is_exact_and_read_only(count: int) -> None:
    state = _state(count, required=True)
    before = state.model_dump_json()

    selection = select_adaptive_resolver_aperture(state, _request())

    assert selection.receipt.selected_mode == ExecutionMode.WIDE_GOVERNED_APERTURE
    assert selection.receipt.reason_code == ApertureReasonCode.DECLARED_JOINT_REQUIREMENT
    assert selection.receipt.evidence_ids == [f"fact-{index:03d}" for index in range(count)]
    assert len(selection.payload) == count
    assert state.model_dump_json() == before


def test_wide_surface_excludes_neighboring_evidence() -> None:
    state = _state(3, required=True)
    state.facts.append(
        Fact(
            id="irrelevant-neighbor",
            statement="An irrelevant neighboring fact.",
            value="irrelevant",
            authority=Authority.AUTHORITATIVE_SOURCE,
            affected_slices=[SliceName.CAREER],
        )
    )
    selection = select_adaptive_resolver_aperture(state, _request())
    assert selection.receipt.evidence_ids == ["fact-000", "fact-001", "fact-002"]


@pytest.mark.parametrize(
    ("mutation", "reason"),
    [
        ("missing", ApertureReasonCode.FAIL_CLOSED_MISSING_REQUIRED_EVIDENCE),
        ("expired", ApertureReasonCode.FAIL_CLOSED_INVALID_FACT),
        ("stale_gate", ApertureReasonCode.FAIL_CLOSED_STALE_GATE),
        ("unauthorized", ApertureReasonCode.FAIL_CLOSED_UNAUTHORIZED_FACT),
    ],
)
def test_invalid_joint_surface_fails_closed(mutation: str, reason: ApertureReasonCode) -> None:
    state = _state(3, required=True)
    if mutation == "missing":
        state.facts.pop()
    elif mutation == "expired":
        state.facts[-1].status = FreshnessStatus.STALE
    elif mutation == "stale_gate":
        state.version += 1
    else:
        state.facts[-1].affected_slices = [SliceName.EDUCATION]

    selection = select_adaptive_resolver_aperture(state, _request())
    assert selection.receipt.selected_mode == ExecutionMode.FULL_GOVERNED_EXAMINATION
    assert selection.receipt.fail_closed_condition == reason
    assert not selection.payload


def test_real_blocking_impacts_declare_sparse_sequence() -> None:
    state = _state(3)
    for index, fact in enumerate(state.facts):
        state.impacts.append(
            ImpactItem(
                id=f"impact-{index}",
                source_field="governed_dependency",
                dependent_field=fact.field_key,
                fact_id=fact.id,
                affected_slice=SliceName.CAREER,
                message="Review the declared condition.",
                question="Does it remain material?",
                confirm_label="Confirm",
                update_label="Update",
                blocking=True,
            )
        )

    selection = select_adaptive_resolver_aperture(state, _request())
    assert selection.receipt.selected_mode == ExecutionMode.SPARSE_APERTURE
    assert selection.receipt.evidence_ids == ["fact-000"]


def test_apparent_decomposability_without_governed_declaration_fails_closed() -> None:
    state = _state(3)
    selection = select_adaptive_resolver_aperture(state, _request())
    assert selection.receipt.selected_mode == ExecutionMode.FULL_GOVERNED_EXAMINATION
    assert selection.receipt.reason_code == ApertureReasonCode.FAIL_CLOSED_AMBIGUOUS_MODE


def _recorded_rejection():  # type: ignore[no-untyped-def]
    state = _state(1)
    actor = ActorProvenance.trusted_session(
        profile_id=state.profile_id,
        event_id="h1-authorized-rejection",
        integrity_ref="developer-fixture",
    )
    state = record_state_bound_rejection(
        state,
        actor=actor,
        idempotency_key="h1-rejection-key",
        fact_ids=["fact-000"],
        effect_dimension="employment_authority",
        gate_id="gate-current",
        validity_dimensions=VALIDITY,
    )
    return state


def test_valid_governed_rejection_selects_reuse() -> None:
    state = _recorded_rejection()
    selection = select_adaptive_resolver_aperture(
        state,
        _request(reuse_fact_ids=("fact-000",), reuse_validity_dimensions=VALIDITY),
    )
    assert selection.receipt.selected_mode == ExecutionMode.DETERMINISTIC_REUSE
    assert selection.receipt.reason_code == ApertureReasonCode.VALID_DETERMINISTIC_REUSE
    assert not selection.payload


@pytest.mark.parametrize("change", ["authority", "lifecycle", "gate", "stale_lineage"])
def test_reuse_material_changes_never_bypass_examination(change: str) -> None:
    state = _recorded_rejection()
    if change == "authority":
        state.facts[0].authority = Authority.HUMAN
    elif change == "lifecycle":
        state.lifecycle_position = LifecyclePosition.SEPARATED_1_TO_5_YEARS
    elif change == "gate":
        state.gates[0].question = "A materially changed governed question?"
    else:
        state.lineage[-1].integrity = LineageIntegrity.INCOMPLETE
    selection = select_adaptive_resolver_aperture(
        state,
        _request(reuse_fact_ids=("fact-000",), reuse_validity_dimensions=VALIDITY),
    )
    assert selection.receipt.selected_mode != ExecutionMode.DETERMINISTIC_REUSE


def test_near_match_identity_does_not_suppress() -> None:
    state = _recorded_rejection()
    state.facts.append(state.facts[0].model_copy(update={"id": "fact-near", "value": "different"}))
    selection = select_adaptive_resolver_aperture(
        state,
        _request(reuse_fact_ids=("fact-near",), reuse_validity_dimensions=VALIDITY),
    )
    assert selection.receipt.selected_mode != ExecutionMode.DETERMINISTIC_REUSE


def test_protection_precedence_over_cheaper_paths() -> None:
    state = _recorded_rejection()
    state.conflicts.append("Authoritative conflict requires examination.")
    selection = select_adaptive_resolver_aperture(
        state,
        _request(reuse_fact_ids=("fact-000",), reuse_validity_dimensions=VALIDITY),
    )
    assert selection.receipt.selected_mode == ExecutionMode.FULL_GOVERNED_EXAMINATION
    assert selection.receipt.reason_code == ApertureReasonCode.FULL_EXAM_CONFLICT


@pytest.mark.parametrize(
    ("reason_code", "authority", "expected"),
    [
        ("lifecycle_boundary_crossed", None, ApertureReasonCode.FULL_EXAM_LIFECYCLE),
        ("authority_review_required", Authority.AUTHORITATIVE_SOURCE, ApertureReasonCode.FULL_EXAM_AUTHORITY),
        ("human_gate_required", Authority.HUMAN, ApertureReasonCode.FULL_EXAM_HUMAN_GATE),
    ],
)
def test_explicit_governed_protection_signals_select_full_examination(
    reason_code: str,
    authority: Authority | None,
    expected: ApertureReasonCode,
) -> None:
    state = _state(1)
    state.execution.reason_code = reason_code
    state.execution.blocking_gate_id = "gate-current" if authority is not None else None
    state.execution.resolving_authority = authority
    selection = select_adaptive_resolver_aperture(state, _request())
    assert selection.receipt.selected_mode == ExecutionMode.FULL_GOVERNED_EXAMINATION
    assert selection.receipt.reason_code == expected


def test_probe_requires_structural_eligibility_and_never_self_selects() -> None:
    state = _state(1)
    eligible = select_adaptive_resolver_aperture(
        state,
        _request(permitted_latent_fact_id="fact-000", probe_discovery_permitted=True),
    )
    disabled = select_adaptive_resolver_aperture(
        state,
        _request(permitted_latent_fact_id="fact-000", probe_discovery_permitted=False),
    )
    assert eligible.receipt.selected_mode == ExecutionMode.PROBE_DISCOVERY
    assert disabled.receipt.selected_mode == ExecutionMode.FULL_GOVERNED_EXAMINATION


def test_already_governed_relationship_is_not_probe_eligible() -> None:
    state = _recorded_rejection()
    selection = select_adaptive_resolver_aperture(
        state,
        _request(permitted_latent_fact_id="fact-000", probe_discovery_permitted=True),
    )
    assert selection.receipt.selected_mode != ExecutionMode.PROBE_DISCOVERY


def test_coupling_ratio_is_telemetry_only() -> None:
    state = _state(3, required=True)
    first = select_adaptive_resolver_aperture(state, _request())
    changed = deepcopy(state)
    for index in range(20):
        changed.facts.append(
            Fact(
                id=f"ratio-only-{index}",
                statement="Relevant but not required telemetry-only fact.",
                value=str(index),
                authority=Authority.AUTHORITATIVE_SOURCE,
                affected_slices=[SliceName.CAREER],
            )
        )
    second = select_adaptive_resolver_aperture(changed, _request())
    assert first.receipt.coupling_ratio.ratio != second.receipt.coupling_ratio.ratio
    assert first.receipt.selected_mode == second.receipt.selected_mode
    assert first.receipt.evidence_ids == second.receipt.evidence_ids
    assert first.receipt.coupling_ratio.telemetry_only is True
