from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any

from military_slices.models import (
    ActorProvenance,
    Authority,
    CanonicalState,
    CareerHypothesis,
    DerivedIndexRef,
    DomainPackRef,
    Gate,
    GovernorDecision,
    LineageIntegrity,
    LineageRecord,
    MigrationStatus,
    MutationEvent,
    ResolverTransitionProposal,
)


class GovernanceError(ValueError):
    pass


def _payload_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    return hashlib.sha256(encoded).hexdigest()


def resolver_nomination_ref(
    *,
    gate_id: str,
    source_state_version: int,
    hypotheses: list[CareerHypothesis],
) -> str:
    """Identify one bounded nomination without retaining model input or output text."""
    payload = {
        "gate_id": gate_id,
        "source_state_version": source_state_version,
        "hypotheses": [item.model_dump(mode="json") for item in hypotheses],
    }
    return f"resolver-proposal:sha256:{_payload_hash(payload)}"


def validate_resolver_nomination(
    *,
    proposal: ResolverTransitionProposal,
    hypotheses: list[CareerHypothesis],
) -> str:
    """Bind the Governor proposal to the exact candidate batch it is authorizing."""
    if proposal.effect != "nominate":
        raise GovernanceError("Resolver proposal integrity applies only to nominations.")
    expected = resolver_nomination_ref(
        gate_id=proposal.gate_id,
        source_state_version=proposal.source_state_version,
        hypotheses=hypotheses,
    )
    proposal_refs = [
        item for item in proposal.evidence_refs if item.startswith("resolver-proposal:sha256:")
    ]
    if proposal_refs != [expected]:
        raise GovernanceError("Resolver nomination does not match its bounded proposal identity.")
    return expected


def validate_domain_pack(reference: DomainPackRef, payload: dict[str, Any]) -> None:
    version = payload.get("version")
    if version != reference.version:
        raise GovernanceError("Domain Pack version does not match its governed reference.")
    if _payload_hash(payload) != reference.content_hash:
        raise GovernanceError("Domain Pack content hash does not match its governed reference.")


def reconstitute_governance(state: CanonicalState) -> CanonicalState:
    """Normalize additive governance metadata without manufacturing historical truth."""
    restored = deepcopy(state)
    if not restored.mutation_events and not restored.lineage:
        restored.migration_status = (
            MigrationStatus.LEGACY_VALID if restored.version == 0 else MigrationStatus.LINEAGE_INCOMPLETE
        )
        if restored.version > 0:
            # A pre-governance record may contain recomputable cached projections,
            # but it cannot prove which canonical version produced them.
            restored.derived_indexes = []
    return restored


def bind_gate_contracts(state: CanonicalState) -> CanonicalState:
    for gate in state.gates:
        gate.source_state_version = state.version
    state.derived_indexes = [
        DerivedIndexRef(
            name="gates",
            source_state_version=state.version,
            content_hash=_index_hash([gate.model_dump(mode="json") for gate in state.gates]),
        ),
        DerivedIndexRef(
            name="projections",
            source_state_version=state.version,
            content_hash=_index_hash([item.model_dump(mode="json") for item in state.projections]),
        ),
    ]
    return state


def _index_hash(payload: list[dict[str, Any]]) -> str:
    encoded = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    return hashlib.sha256(encoded).hexdigest()


def verify_derived_indexes(state: CanonicalState) -> None:
    if not state.derived_indexes:
        return
    expected: dict[str, str] = {
        "gates": _index_hash([gate.model_dump(mode="json") for gate in state.gates]),
        "projections": _index_hash([item.model_dump(mode="json") for item in state.projections]),
    }
    indexes: dict[str, DerivedIndexRef] = {item.name: item for item in state.derived_indexes}
    if set(indexes) != set(expected):
        raise GovernanceError("Required derived index is missing or unknown.")
    for name, expected_hash in expected.items():
        item = indexes[name]
        if item.source_state_version != state.version or item.content_hash != expected_hash:
            raise GovernanceError(f"Required derived index {name} is stale or unverifiable.")


def validate_gate_children(parent: Gate, children: list[Gate]) -> None:
    parent_scope = set(parent.authorized_scope)
    parent_authority = set(parent.authority_set)
    union_scope: set[str] = set()
    union_authority: set[Authority] = set()
    for child in children:
        if child.parent_gate_id != parent.id:
            raise GovernanceError("Child Gate is not bound to the declared parent.")
        child_scope = set(child.authorized_scope)
        child_authority = set(child.authority_set)
        if not child_scope.issubset(parent_scope):
            raise GovernanceError("Child Gate scope exceeds the parent Gate scope.")
        if not child_authority.issubset(parent_authority):
            raise GovernanceError("Child Gate authority exceeds the parent Gate authority.")
        union_scope.update(child_scope)
        union_authority.update(child_authority)
    if not union_scope.issubset(parent_scope) or not union_authority.issubset(parent_authority):
        raise GovernanceError("Factored Gate union exceeds the parent contract.")


def validate_gate_transition(gate: Gate, target_state: Any) -> None:
    legal = {
        "UNKNOWN": {"PARTIAL", "YES", "NO", "CONFLICTED"},
        "PARTIAL": {"PARTIAL", "YES", "NO", "CONFLICTED"},
        "CONFLICTED": {"PARTIAL", "YES", "NO"},
        "YES": set(),
        "NO": set(),
    }
    if str(target_state) not in legal[gate.state.value]:
        raise GovernanceError(
            f"Illegal Gate transition from {gate.state.value} to {target_state}."
        )


def validate_mutation_commit(
    *,
    previous: CanonicalState,
    updated: CanonicalState,
    expected_version: int,
) -> None:
    if previous.version != expected_version:
        raise GovernanceError("Mutation authorization is not bound to the stored canonical version.")
    if updated.version != expected_version + 1:
        raise GovernanceError("Governed persistence requires exactly one canonical version advance.")
    matching = [
        event
        for event in updated.mutation_events
        if event.expected_version == expected_version and event.result_version == updated.version
    ]
    if len(matching) != 1:
        raise GovernanceError("Governed persistence requires exactly one matching mutation event.")
    event = matching[0]
    if not event.actor.trusted or event.actor.actor_id != updated.profile_id:
        raise GovernanceError("Governed persistence requires trusted matching actor provenance.")
    if event.idempotency_key not in updated.processed_keys:
        raise GovernanceError("Mutation event and replay key are not atomically aligned.")
    if event.domain_pack != updated.domain_pack:
        raise GovernanceError("Mutation event Domain Pack does not match the governed state pin.")
    if not any(item.subject_id == f"mutation:{event.id}" for item in updated.lineage):
        raise GovernanceError("Governed persistence requires mutation lineage.")
    verify_derived_indexes(updated)


class AuthorityGovernor:
    def evaluate(
        self,
        *,
        state: CanonicalState,
        gate: Gate,
        proposal: ResolverTransitionProposal,
        actor: ActorProvenance | None = None,
    ) -> GovernorDecision:
        reason = self._reason(state=state, gate=gate, proposal=proposal, actor=actor)
        return GovernorDecision(
            authorized=reason == "authorized",
            reason_code=reason,
            gate_id=gate.id,
            source_state_version=proposal.source_state_version,
            effect=proposal.effect,
            authority=proposal.authority,
            permitted_scope=gate.authorized_scope if reason == "authorized" else [],
        )

    @staticmethod
    def _reason(
        *,
        state: CanonicalState,
        gate: Gate,
        proposal: ResolverTransitionProposal,
        actor: ActorProvenance | None,
    ) -> str:
        if proposal.gate_id != gate.id:
            return "gate_identity_mismatch"
        if proposal.source_state_version != state.version or gate.source_state_version != state.version:
            return "stale_source_state"
        if not set(proposal.scope).issubset(gate.authorized_scope):
            return "scope_exceeded"
        if proposal.effect == "nominate":
            if proposal.proposed_state != gate.state:
                return "nomination_cannot_change_gate_state"
            if proposal.authority not in gate.authority_set:
                return "authority_not_permitted"
            return "authorized"
        try:
            validate_gate_transition(gate, proposal.proposed_state.value)
        except GovernanceError:
            return "illegal_gate_transition"
        if gate.authority_required == Authority.HUMAN:
            if proposal.authority != Authority.HUMAN:
                return "human_authority_required"
            if actor is None or not actor.trusted or actor.actor_type != "human":
                return "untrusted_actor"
            if actor.actor_id != state.profile_id:
                return "actor_subject_mismatch"
        if proposal.authority not in gate.authority_set:
            return "authority_not_permitted"
        return "authorized"

    def record_human_mutation(
        self,
        *,
        state: CanonicalState,
        actor: ActorProvenance,
        idempotency_key: str,
        expected_version: int,
        result_version: int,
        dependency_refs: list[str],
        mutation_kind: str = "human_input",
    ) -> CanonicalState:
        if any(
            event.id == actor.event_id or event.idempotency_key == idempotency_key
            for event in state.mutation_events
        ):
            return state
        if not actor.trusted or actor.actor_type != "human" or actor.actor_id != state.profile_id:
            raise GovernanceError("A governed mutation requires a trusted matching human actor.")
        if result_version != expected_version + 1:
            raise GovernanceError("A governed mutation must advance exactly one canonical version.")
        if state.version not in (expected_version, result_version):
            raise GovernanceError("The mutation event is not bound to the current canonical version.")
        updated = deepcopy(state)
        updated.version = result_version
        updated.mutation_events.append(
            MutationEvent(
                id=actor.event_id,
                idempotency_key=idempotency_key,
                actor=actor,
                expected_version=expected_version,
                result_version=result_version,
                source_state_version=expected_version,
                mutation_kind=mutation_kind,
                dependency_refs=dependency_refs,
                domain_pack=updated.domain_pack,
            )
        )
        updated.lineage.append(
            LineageRecord(
                subject_id=f"mutation:{actor.event_id}",
                depends_on=dependency_refs,
                valid_while=[f"canonical-version:{result_version}"],
                invalidated_by=[f"superseding-mutation-after:{result_version}"],
                source_state_version=expected_version,
                authority_refs=[f"actor:{actor.event_id}", f"domain-pack:{updated.domain_pack.content_hash}"],
                integrity=LineageIntegrity.VERIFIED,
            )
        )
        if expected_version == 0 and len(updated.mutation_events) == 1:
            updated.migration_status = MigrationStatus.LINEAGE_ENRICHED
        return bind_gate_contracts(updated)


def external_effects_enabled() -> bool:
    return False


def probe_execution_enabled() -> bool:
    return False
