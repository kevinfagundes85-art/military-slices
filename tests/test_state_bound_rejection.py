from __future__ import annotations

from copy import deepcopy

from military_slices.engine import new_state
from military_slices.governance import AuthorityGovernor, bind_gate_contracts, reconstitute_governance
from military_slices.models import (
    ActorProvenance,
    Authority,
    CanonicalState,
    Decision,
    Fact,
    Gate,
    GateState,
    SliceName,
    SurfaceType,
)
from military_slices.state_bound_rejection import (
    REJECTION_VALUE,
    lookup_state_bound_rejection,
    record_state_bound_rejection,
)


def _state() -> tuple[CanonicalState, str, str]:
    state = new_state("state-bound-rejection-test")
    state.human_anchor = "Validate a permitted outside-work plan."
    state.path_target_state = "Resolve the next outside-work move."
    fact_id = "fact-outside-work"
    gate_id = "probe-examination:outside-work-authority"
    state.facts.append(
        Fact(
            id=fact_id,
            statement="The signed agreement permits this project.",
            value="permitted",
            authority=Authority.AUTHORITATIVE_SOURCE,
            affected_slices=[SliceName.CAREER],
            field_key="outside_work_terms",
        )
    )
    state.gates.append(
        Gate(
            id=gate_id,
            title="Examine outside-work authority",
            question="Does governed authority restrict this plan?",
            why="Only a material authority restriction interrupts the plan.",
            state=GateState.UNKNOWN,
            surface=SurfaceType.CONFIRM,
            affected_slices=[SliceName.CAREER],
            authority_required=Authority.HUMAN,
            required_evidence=["outside_work_terms"],
            authorized_scope=["effect:outside_work_authority_constraint"],
        )
    )
    return bind_gate_contracts(state), fact_id, gate_id


def _actor(state: CanonicalState, suffix: str) -> ActorProvenance:
    profile_id = state.profile_id
    return ActorProvenance.trusted_session(
        profile_id=profile_id,
        event_id=f"event-state-bound-{suffix}",
        integrity_ref=f"test:{suffix}",
        source_system="state-bound-rejection-test",
    )


def _recorded() -> tuple[CanonicalState, str, str]:
    state, fact_id, gate_id = _state()
    governed = record_state_bound_rejection(
        state,
        actor=_actor(state, "reject"),
        idempotency_key="state-bound-reject",
        fact_ids=[fact_id],
        effect_dimension="outside_work_authority_constraint",
        gate_id=gate_id,
        validity_dimensions=["anchor", "path", "authority", "effect_reachability"],
    )
    return governed, fact_id, gate_id


def _lookup(state: CanonicalState, fact_id: str, gate_id: str):  # type: ignore[no-untyped-def]
    return lookup_state_bound_rejection(
        state,
        fact_ids=[fact_id],
        effect_dimension="outside_work_authority_constraint",
        gate_id=gate_id,
        validity_dimensions=["anchor", "path", "authority", "effect_reachability"],
    )


def test_exact_repeat_is_suppressed_without_blocking_state() -> None:
    governed, fact_id, gate_id = _recorded()
    result = _lookup(governed, fact_id, gate_id)

    assert result.status == "SUPPRESSED"
    assert result.suppress is True
    assert len(governed.impacts) == 0
    assert sum(len(gate.dependencies) for gate in governed.gates) == 0
    assert [item.value for item in governed.decisions] == [REJECTION_VALUE]


def test_unrelated_governed_change_does_not_invalidate() -> None:
    governed, fact_id, gate_id = _recorded()
    previous = deepcopy(governed)
    governed.facts.append(
        Fact(
            id="fact-unrelated",
            statement="An unrelated profile fact changed.",
            value="unrelated",
            authority=Authority.HUMAN,
            affected_slices=[SliceName.EDUCATION],
        )
    )
    key = "state-bound-unrelated-change"
    governed.processed_keys.append(key)
    governed.decisions.append(
        Decision(
            id="decision-unrelated",
            gate_id="unrelated",
            value="unrelated_change",
            authority=Authority.HUMAN,
        )
    )
    governed = AuthorityGovernor().record_human_mutation(
        state=governed,
        actor=_actor(governed, "unrelated"),
        idempotency_key=key,
        expected_version=previous.version,
        result_version=previous.version + 1,
        dependency_refs=["fact:fact-unrelated"],
        mutation_kind="unrelated_human_change",
    )

    assert governed.version == previous.version + 1
    assert _lookup(governed, fact_id, gate_id).status == "SUPPRESSED"


def test_bound_fact_change_invalidates_and_never_stale_suppresses() -> None:
    governed, fact_id, gate_id = _recorded()
    fact = next(item for item in governed.facts if item.id == fact_id)
    fact.statement = "A new signed addendum prohibits this project."
    fact.value = fact.statement

    result = _lookup(governed, fact_id, gate_id)

    assert result.status == "INVALIDATED"
    assert result.suppress is False
    assert "evidence_lineage_changed" in result.invalidation_triggers


def test_semantically_equivalent_new_fact_id_is_an_identity_miss() -> None:
    governed, _, gate_id = _recorded()
    governed.facts.append(
        Fact(
            id="fact-outside-work-reingested",
            statement="The agreement allows this same project.",
            value="permitted",
            authority=Authority.AUTHORITATIVE_SOURCE,
            affected_slices=[SliceName.CAREER],
            field_key="outside_work_terms",
        )
    )

    result = _lookup(governed, "fact-outside-work-reingested", gate_id)

    assert result.status == "IDENTITY_MISS"
    assert result.suppress is False


def test_rejection_lookup_survives_restart() -> None:
    governed, fact_id, gate_id = _recorded()
    restarted = reconstitute_governance(type(governed).model_validate_json(governed.model_dump_json()))

    assert _lookup(restarted, fact_id, gate_id).status == "SUPPRESSED"
