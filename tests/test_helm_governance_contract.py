from __future__ import annotations

from copy import deepcopy

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from military_slices.agent_runtime import Resolver, ResolverResult
from military_slices.app import create_app
from military_slices.domain_pack import installed_domain_pack_payload, installed_domain_pack_ref
from military_slices.engine import apply_confirmed_input, new_state, orient, reconstitute_state
from military_slices.governance import (
    AuthorityGovernor,
    GovernanceError,
    external_effects_enabled,
    probe_execution_enabled,
    reconstitute_governance,
    resolver_nomination_ref,
    validate_domain_pack,
    validate_gate_children,
    validate_resolver_nomination,
    verify_derived_indexes,
)
from military_slices.models import (
    ActorProvenance,
    Authority,
    CanonicalState,
    CareerHypothesis,
    DomainPackRef,
    DomainPackStatus,
    Gate,
    GateState,
    MigrationStatus,
    ResolverTransitionProposal,
    SliceName,
    SurfaceType,
)
from military_slices.slices import project_slice_context
from military_slices.store import MemoryStore


def _human_gate(**updates: object) -> Gate:
    values: dict[str, object] = {
        "id": "career-direction",
        "title": "Choose a direction",
        "question": "Which direction is worth testing?",
        "why": "A human must choose the direction.",
        "state": GateState.PARTIAL,
        "surface": SurfaceType.COMPARE,
        "affected_slices": [SliceName.CAREER],
        "authority_required": Authority.HUMAN,
        "authorized_scope": ["career:hypothesis-selection"],
        "authority_set": [Authority.HUMAN],
        "source_state_version": 3,
    }
    values.update(updates)
    return Gate.model_validate(values)


def test_legacy_profile_loads_without_invented_provenance() -> None:
    legacy = CanonicalState.model_validate({"profile_id": "ms-legacy"})

    restored = reconstitute_governance(legacy)

    assert restored.migration_status == MigrationStatus.LEGACY_VALID
    assert restored.domain_pack.status == DomainPackStatus.LEGACY_VALID
    assert restored.mutation_events == []
    assert restored.lineage == []


def test_domain_pack_payload_is_bound_to_exact_hash_and_version() -> None:
    payload = {"version": "2026-test.1", "rules": [{"id": "rule-one", "effect": "ask"}]}
    pack = DomainPackRef.for_payload(
        domain_pack_id="military-transition",
        version="2026-test.1",
        payload=payload,
    )
    validate_domain_pack(pack, payload)

    with pytest.raises(GovernanceError, match="content hash"):
        validate_domain_pack(pack, {**payload, "rules": [{"id": "rule-one", "effect": "approve"}]})

    with pytest.raises(GovernanceError, match="version"):
        validate_domain_pack(pack, {**payload, "version": "2026-test.2"})


def test_child_gate_cannot_expand_parent_scope_or_authority() -> None:
    parent = _human_gate()
    child = _human_gate(
        id="career-direction:child",
        parent_gate_id=parent.id,
        authorized_scope=["career:hypothesis-selection", "resume:publish"],
        authority_set=[Authority.HUMAN, Authority.BOUNDED_AGENT],
    )

    with pytest.raises(GovernanceError, match="scope"):
        validate_gate_children(parent, [child])


def test_resolver_cannot_close_a_human_gate_or_mutate_state() -> None:
    state = CanonicalState(profile_id="ms-governor", version=3)
    before = deepcopy(state)
    gate = _human_gate()
    proposal = ResolverTransitionProposal(
        gate_id=gate.id,
        source_state_version=3,
        proposed_state=GateState.YES,
        proposed_value="Project Manager",
        authority=Authority.BOUNDED_AGENT,
        scope=["career:hypothesis-selection"],
        evidence_refs=["onet:13-1082.00"],
    )

    decision = AuthorityGovernor().evaluate(state=state, gate=gate, proposal=proposal)

    assert decision.authorized is False
    assert decision.reason_code == "human_authority_required"
    assert state == before


def test_mutation_authority_is_bound_to_trusted_actor_and_state_version() -> None:
    state = CanonicalState(profile_id="ms-authority", version=4)
    gate = _human_gate(source_state_version=4)
    proposal = ResolverTransitionProposal(
        gate_id=gate.id,
        source_state_version=4,
        proposed_state=GateState.YES,
        proposed_value="Project Manager",
        authority=Authority.HUMAN,
        scope=["career:hypothesis-selection"],
    )
    untrusted = ActorProvenance(
        actor_id=state.profile_id,
        actor_type="human",
        auth_context="untrusted",
        event_id="event-authority-0001",
        integrity_ref="none",
        source_system="test",
        trusted=False,
    )

    denied = AuthorityGovernor().evaluate(state=state, gate=gate, proposal=proposal, actor=untrusted)
    assert denied.reason_code == "untrusted_actor"

    trusted = untrusted.model_copy(update={"trusted": True, "auth_context": "signed_session"})
    stale = proposal.model_copy(update={"source_state_version": 3})
    denied = AuthorityGovernor().evaluate(state=state, gate=gate, proposal=stale, actor=trusted)
    assert denied.reason_code == "stale_source_state"


def test_duplicate_mutation_event_cannot_create_a_second_version() -> None:
    state = reconstitute_governance(CanonicalState(profile_id="ms-replay", version=2))
    actor = ActorProvenance.trusted_session(
        profile_id=state.profile_id,
        event_id="event-replay-0001",
        integrity_ref="session:test",
    )

    first = AuthorityGovernor().record_human_mutation(
        state=state,
        actor=actor,
        idempotency_key="replay-contract-0001",
        expected_version=2,
        result_version=3,
        dependency_refs=["gate:career-direction"],
    )
    replay = AuthorityGovernor().record_human_mutation(
        state=first,
        actor=actor,
        idempotency_key="replay-contract-0001",
        expected_version=2,
        result_version=3,
        dependency_refs=["gate:career-direction"],
    )

    assert replay == first
    assert len(replay.mutation_events) == 1


def test_external_effects_and_autonomous_probe_are_disabled() -> None:
    assert external_effects_enabled() is False
    assert probe_execution_enabled() is False


def test_active_domain_pack_requires_authenticated_approval() -> None:
    payload = {"version": "2026-test.1", "rules": []}
    with pytest.raises(ValidationError, match="requires approval"):
        DomainPackRef.for_payload(
            domain_pack_id="military-transition",
            version="2026-test.1",
            payload=payload,
            status=DomainPackStatus.ACTIVE,
        )


def test_installed_domain_pack_has_reproducible_identity_but_no_invented_approval() -> None:
    reference = installed_domain_pack_ref()
    validate_domain_pack(reference, installed_domain_pack_payload())
    assert reference.status == DomainPackStatus.LEGACY_VALID
    assert reference.approval_event_id is None


def test_existing_versioned_profile_without_lineage_is_marked_incomplete() -> None:
    restored = reconstitute_governance(CanonicalState(profile_id="ms-old", version=4))
    assert restored.migration_status == MigrationStatus.LINEAGE_INCOMPLETE


def test_slice_projection_excludes_profile_audit_and_other_slice_context() -> None:
    state = new_state("ms-projection")
    state = state.model_copy(
        update={
            "original_intents": ["private raw ingress"],
            "current_goal": "internal duplicate",
            "facts": [
                *state.facts,
            ],
        }
    )
    state = apply_confirmed_input(
        state,
        orient("I want remote project work. I also want a university degree."),
        idempotency_key="slice-projection-0001",
    )

    career = project_slice_context(state, SliceName.CAREER)

    assert "profile_id" not in career
    assert "original_intents" not in career
    assert "mutation_events" not in career
    assert "domain_pack" not in career
    assert all("university degree" not in item.casefold() for item in career["confirmed_statements"])


def test_derived_index_tampering_fails_closed() -> None:
    state = new_state("ms-index")
    verify_derived_indexes(state)
    state.derived_indexes[0].content_hash = "0" * 64

    with pytest.raises(GovernanceError, match="stale or unverifiable"):
        reconstitute_state(state)


def test_http_mutation_persists_trusted_provenance_lineage_and_pack_pin() -> None:
    store = MemoryStore()
    client = TestClient(create_app(store=store))
    orientation = client.post("/api/orient", json={"text": "I want civilian project work."}).json()
    before = client.get("/api/state").json()["state"]

    response = client.post(
        "/api/confirm",
        json={
            "token": orientation["token"],
            "reviewed_input": orientation["reviewed_input"],
            "expected_version": before["version"],
            "idempotency_key": "governed-http-0001",
        },
    )

    assert response.status_code == 200
    state = response.json()["state"]
    assert state["version"] == 1
    assert len(state["mutation_events"]) == 1
    event = state["mutation_events"][0]
    assert event["actor"]["trusted"] is True
    assert event["actor"]["auth_context"] == "signed_session"
    assert event["expected_version"] == 0
    assert event["result_version"] == 1
    assert event["domain_pack"]["content_hash"] == installed_domain_pack_ref().content_hash
    assert state["lineage"][0]["source_state_version"] == 0
    assert all(item["source_state_version"] == 1 for item in state["derived_indexes"])


def test_governed_store_rejects_version_advance_without_event_lineage() -> None:
    store = MemoryStore()
    state = store.get("ms-no-event")
    state.version = 1

    with pytest.raises(GovernanceError, match="mutation event"):
        store.save_governed(state, expected_version=0)

    assert store.get("ms-no-event").version == 0


def test_terminal_gate_cannot_be_resolved_again_through_governor() -> None:
    state = CanonicalState(profile_id="ms-terminal", version=3)
    gate = _human_gate(state=GateState.YES, resolved_value="Project Manager")
    actor = ActorProvenance.trusted_session(
        profile_id=state.profile_id,
        event_id="event-terminal-0001",
        integrity_ref="session:test",
    )
    proposal = ResolverTransitionProposal(
        gate_id=gate.id,
        source_state_version=3,
        proposed_state=GateState.NO,
        proposed_value="No",
        authority=Authority.HUMAN,
        scope=gate.authorized_scope,
    )

    decision = AuthorityGovernor().evaluate(state=state, gate=gate, proposal=proposal, actor=actor)

    assert decision.authorized is False
    assert decision.reason_code == "illegal_gate_transition"


def test_governed_state_restarts_with_same_pack_event_lineage_and_gate_version() -> None:
    store = MemoryStore()
    client = TestClient(create_app(store=store))
    orientation = client.post("/api/orient", json={"text": "I want civilian logistics work."}).json()
    response = client.post(
        "/api/confirm",
        json={
            "token": orientation["token"],
            "reviewed_input": orientation["reviewed_input"],
            "expected_version": 0,
            "idempotency_key": "restart-governed-0001",
        },
    )
    assert response.status_code == 200
    stored = response.json()["state"]

    restarted = reconstitute_state(CanonicalState.model_validate(stored))

    assert restarted.domain_pack.content_hash == stored["domain_pack"]["content_hash"]
    assert [item.model_dump(mode="json") for item in restarted.mutation_events] == stored["mutation_events"]
    assert [item.model_dump(mode="json") for item in restarted.lineage] == stored["lineage"]
    assert all(gate.source_state_version == restarted.version for gate in restarted.gates)
    verify_derived_indexes(restarted)


def test_historical_pack_pin_is_not_silently_replaced_on_reconstitution() -> None:
    payload = {"version": "2025-retired", "rules": []}
    retired = DomainPackRef.for_payload(
        domain_pack_id="military-transition",
        version="2025-retired",
        payload=payload,
        status=DomainPackStatus.RETIRED,
    )
    legacy = CanonicalState(
        profile_id="ms-retired-pack",
        version=5,
        transition_pack_version="2025-retired",
        domain_pack=retired,
    )

    restored = reconstitute_state(legacy)

    assert restored.domain_pack == retired
    assert restored.domain_pack != installed_domain_pack_ref()
    assert restored.migration_status == MigrationStatus.LINEAGE_INCOMPLETE


def test_disabled_capabilities_cannot_be_enabled_by_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MILITARY_SLICES_EXTERNAL_EFFECTS", "true")
    monkeypatch.setenv("MILITARY_SLICES_AUTONOMOUS_PROBE", "true")

    assert external_effects_enabled() is False
    assert probe_execution_enabled() is False


def test_application_has_no_external_dispatch_or_autonomous_probe_route() -> None:
    app = create_app(store=MemoryStore())
    paths = {route.path for route in app.routes}

    assert all("dispatch" not in path for path in paths)
    assert all("external-effect" not in path for path in paths)
    assert all("probe" not in path for path in paths)


def test_resolver_nomination_is_audited_but_does_not_close_human_gate() -> None:
    class CountingResolver(Resolver):
        def __init__(self) -> None:
            super().__init__(mode="deterministic")
            self.calls = 0

        async def resolve(self, state: CanonicalState) -> ResolverResult:
            self.calls += 1
            return await super().resolve(state)

    resolver = CountingResolver()
    client = TestClient(create_app(store=MemoryStore(), resolver=resolver))
    text = "I leave the Navy in June 2027. I want civilian work with predictable daytime hours."
    orientation = client.post("/api/orient", json={"text": text}).json()
    body = {
        "token": orientation["token"],
        "reviewed_input": orientation["reviewed_input"],
        "expected_version": 0,
        "idempotency_key": "nomination-audit-0001",
    }
    starting_response = client.post(
        "/api/confirm",
        json=body,
    )

    assert starting_response.status_code == 200
    starting_payload = starting_response.json()
    assert starting_payload["active_gate"]["id"] == "career-direction"
    assert starting_payload["active_gate"]["surface"] == "text"
    assert resolver.calls == 0

    direction_text = "I want predictable daytime operations work that uses planning and coordination."
    direction_orientation = client.post("/api/orient", json={"text": direction_text}).json()
    direction_body = {
        "token": direction_orientation["token"],
        "reviewed_input": direction_orientation["reviewed_input"],
        "expected_version": starting_payload["state"]["version"],
        "idempotency_key": "nomination-audit-direction-0001",
    }
    response = client.post("/api/confirm", json=direction_body)

    assert response.status_code == 200
    state = response.json()["state"]
    nomination = state["governor_decisions"][-1]
    assert nomination["authorized"] is True
    assert nomination["effect"] == "nominate"
    assert nomination["authority"] == "bounded_agent"
    assert response.json()["active_gate"]["id"] == "career-direction"
    assert response.json()["active_gate"]["state"] == "PARTIAL"
    proposal_refs = [
        item
        for item in state["mutation_events"][-1]["dependency_refs"]
        if item.startswith("resolver-proposal:sha256:")
    ]
    assert len(proposal_refs) == 1
    assert proposal_refs[0] in state["lineage"][-1]["depends_on"]
    receipt = " ".join(response.json()["what_changed"]["consequences"])
    assert "ready to explore" in receipt
    assert not any(term in receipt.casefold() for term in ("helm", "adk", "gemini", "resolver", "governor"))
    replay = client.post("/api/confirm", json=direction_body)
    assert replay.status_code == 200
    assert replay.json()["state"]["version"] == state["version"]
    assert resolver.calls == 1


def test_resolver_nomination_identity_rejects_a_tampered_hypothesis_batch() -> None:
    original = [
        CareerHypothesis(
            id="career_original",
            title="Operations Analyst",
            rationale="A bounded direction grounded in the supplied planning evidence.",
            evidence=["O*NET 15-2031.00"],
            capability_matches=["Structured analysis"],
            possible_gaps=["Civilian data-tool evidence"],
        )
    ]
    reference = resolver_nomination_ref(
        gate_id="career-direction",
        source_state_version=4,
        hypotheses=original,
    )
    proposal = ResolverTransitionProposal(
        gate_id="career-direction",
        source_state_version=4,
        proposed_state=GateState.PARTIAL,
        authority=Authority.BOUNDED_AGENT,
        effect="nominate",
        scope=["career:hypothesis-nomination"],
        evidence_refs=[reference],
    )
    validate_resolver_nomination(proposal=proposal, hypotheses=original)
    tampered = [original[0].model_copy(update={"title": "Unbound Different Role"})]

    with pytest.raises(GovernanceError, match="proposal identity"):
        validate_resolver_nomination(proposal=proposal, hypotheses=tampered)
