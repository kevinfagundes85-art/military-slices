"""Stateless execution steering over existing HELM governance contracts.

Adaptive Resolver Aperture is deliberately not Canonical state.  It derives a
non-authoritative receipt from the current governed snapshot and dispatches only
to execution paths that the snapshot already makes eligible.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from military_slices.governance import GovernanceError, verify_derived_indexes
from military_slices.models import (
    Authority,
    CanonicalState,
    Fact,
    FreshnessStatus,
    Gate,
    LineageIntegrity,
)
from military_slices.state_bound_rejection import (
    GovernedContentRejectionLookup,
    RejectionLookup,
    lookup_governed_content_rejection,
    lookup_state_bound_rejection,
)


class ExecutionMode(StrEnum):
    DETERMINISTIC_REUSE = "A_DETERMINISTIC_REUSE"
    SPARSE_APERTURE = "B_SPARSE_APERTURE"
    WIDE_GOVERNED_APERTURE = "C_WIDE_GOVERNED_APERTURE"
    FULL_GOVERNED_EXAMINATION = "D_FULL_GOVERNED_EXAMINATION"
    PROBE_DISCOVERY = "E_PROBE_DISCOVERY"


class ApertureReasonCode(StrEnum):
    VALID_DETERMINISTIC_REUSE = "VALID_DETERMINISTIC_REUSE"
    DECLARED_DECOMPOSABLE = "DECLARED_DECOMPOSABLE"
    DECLARED_JOINT_REQUIREMENT = "DECLARED_JOINT_REQUIREMENT"
    FULL_EXAM_CONFLICT = "FULL_EXAM_CONFLICT"
    FULL_EXAM_INVALIDATION = "FULL_EXAM_INVALIDATION"
    FULL_EXAM_AUTHORITY = "FULL_EXAM_AUTHORITY"
    FULL_EXAM_LIFECYCLE = "FULL_EXAM_LIFECYCLE"
    FULL_EXAM_HUMAN_GATE = "FULL_EXAM_HUMAN_GATE"
    PROBE_STRUCTURALLY_ELIGIBLE = "PROBE_STRUCTURALLY_ELIGIBLE"
    FAIL_CLOSED_MISSING_REQUIRED_EVIDENCE = "FAIL_CLOSED_MISSING_REQUIRED_EVIDENCE"
    FAIL_CLOSED_STALE_GATE = "FAIL_CLOSED_STALE_GATE"
    FAIL_CLOSED_INVALID_FACT = "FAIL_CLOSED_INVALID_FACT"
    FAIL_CLOSED_UNAUTHORIZED_FACT = "FAIL_CLOSED_UNAUTHORIZED_FACT"
    FAIL_CLOSED_AMBIGUOUS_MODE = "FAIL_CLOSED_AMBIGUOUS_MODE"
    FAIL_CLOSED_UNKNOWN_RELATIONSHIP = "FAIL_CLOSED_UNKNOWN_RELATIONSHIP"


class RejectedMode(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    mode: ExecutionMode
    reason: str


class CouplingRatioTelemetry(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    jointly_required: int = Field(ge=0)
    relevant_available: int = Field(ge=0)
    ratio: float | None
    telemetry_only: bool = True


class ExecutionReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    task_decision_id: str
    governed_snapshot_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    gate_id: str
    gate_version: int = Field(ge=0)
    selected_mode: ExecutionMode
    reason_code: ApertureReasonCode
    evidence_ids: list[str]
    payload_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    rejected_alternatives: list[RejectedMode]
    coupling_ratio: CouplingRatioTelemetry
    fail_closed_condition: ApertureReasonCode | None = None


@dataclass(frozen=True)
class ApertureRequest:
    """Ephemeral execution inputs; none are persisted or authoritative."""

    task_decision_id: str
    gate_id: str
    effect_dimension: str
    reuse_fact_ids: tuple[str, ...] = ()
    reuse_validity_dimensions: tuple[str, ...] = ()
    permitted_latent_fact_id: str | None = None
    probe_discovery_permitted: bool = False


@dataclass(frozen=True)
class ApertureSelection:
    receipt: ExecutionReceipt
    payload: tuple[Fact, ...]


def _hash(value: Any) -> str:
    encoded = json.dumps(value, separators=(",", ":"), sort_keys=True, default=str).encode()
    return hashlib.sha256(encoded).hexdigest()


def _snapshot_hash(state: CanonicalState) -> str:
    return _hash(state.model_dump(mode="json"))


def _gate(state: CanonicalState, gate_id: str) -> Gate | None:
    matches = [item for item in state.gates if item.id == gate_id]
    return matches[0] if len(matches) == 1 else None


def _scope_allows(gate: Gate, fact: Fact) -> bool:
    allowed = {item.removeprefix("slice:") for item in gate.authorized_scope if item.startswith("slice:")}
    return bool(fact.affected_slices) and all(item.value in allowed for item in fact.affected_slices)


def _payload_hash(facts: tuple[Fact, ...]) -> str:
    return _hash([item.model_dump(mode="json") for item in facts])


def _ratio(gate: Gate | None, state: CanonicalState) -> CouplingRatioTelemetry:
    if gate is None:
        return CouplingRatioTelemetry(jointly_required=0, relevant_available=0, ratio=None)
    jointly_required = len(gate.required_evidence)
    relevant_available = sum(bool(set(fact.affected_slices).intersection(gate.affected_slices)) for fact in state.facts)
    ratio = jointly_required / relevant_available if relevant_available else None
    return CouplingRatioTelemetry(
        jointly_required=jointly_required,
        relevant_available=relevant_available,
        ratio=ratio,
    )


def _receipt(
    state: CanonicalState,
    request: ApertureRequest,
    gate: Gate | None,
    mode: ExecutionMode,
    reason: ApertureReasonCode,
    payload: tuple[Fact, ...],
    *,
    fail_closed: ApertureReasonCode | None = None,
) -> ApertureSelection:
    rejected = [
        RejectedMode(mode=item, reason="not selected by deterministic precedence")
        for item in ExecutionMode
        if item != mode
    ]
    receipt = ExecutionReceipt(
        task_decision_id=request.task_decision_id,
        governed_snapshot_hash=_snapshot_hash(state),
        gate_id=gate.id if gate is not None else request.gate_id,
        gate_version=gate.source_state_version if gate is not None else 0,
        selected_mode=mode,
        reason_code=reason,
        evidence_ids=[item.id for item in payload],
        payload_hash=_payload_hash(payload),
        rejected_alternatives=rejected,
        coupling_ratio=_ratio(gate, state),
        fail_closed_condition=fail_closed,
    )
    return ApertureSelection(receipt=receipt, payload=payload)


def _full(
    state: CanonicalState,
    request: ApertureRequest,
    gate: Gate | None,
    reason: ApertureReasonCode,
) -> ApertureSelection:
    return _receipt(
        state,
        request,
        gate,
        ExecutionMode.FULL_GOVERNED_EXAMINATION,
        reason,
        (),
        fail_closed=reason if reason.value.startswith("FAIL_CLOSED_") else None,
    )


def _reuse_lookup(
    state: CanonicalState,
    request: ApertureRequest,
) -> tuple[RejectionLookup | None, GovernedContentRejectionLookup | None]:
    if not request.reuse_fact_ids:
        return None, None
    exact = lookup_state_bound_rejection(
        state,
        fact_ids=request.reuse_fact_ids,
        effect_dimension=request.effect_dimension,
        gate_id=request.gate_id,
        validity_dimensions=request.reuse_validity_dimensions,
    )
    content = lookup_governed_content_rejection(
        state,
        fact_ids=request.reuse_fact_ids,
        effect_dimension=request.effect_dimension,
        gate_id=request.gate_id,
        validity_dimensions=request.reuse_validity_dimensions,
    )
    return exact, content


def _structurally_eligible_probe_fact(
    state: CanonicalState,
    gate: Gate,
    request: ApertureRequest,
) -> Fact | None:
    if not request.probe_discovery_permitted or request.permitted_latent_fact_id is None:
        return None
    if state.latent_fact_count < 1:
        return None
    fact = next((item for item in state.facts if item.id == request.permitted_latent_fact_id), None)
    if fact is None or fact.status != FreshnessStatus.VALID or not _scope_allows(gate, fact):
        return None
    represented = set(gate.required_evidence) | set(gate.dependencies)
    represented.update(item.fact_id for item in state.impacts)
    represented.update(
        ref.removeprefix("input-fact:")
        for item in state.lineage
        for ref in item.depends_on
        if ref.startswith("input-fact:")
    )
    return None if fact.id in represented else fact


def select_adaptive_resolver_aperture(
    state: CanonicalState,
    request: ApertureRequest,
) -> ApertureSelection:
    """Select one existing execution topology without changing governed state."""

    gate = _gate(state, request.gate_id)
    if gate is None:
        return _full(state, request, None, ApertureReasonCode.FAIL_CLOSED_AMBIGUOUS_MODE)

    # Protection always wins.  These are governed signals, never model judgments.
    if state.conflicts:
        return _full(state, request, gate, ApertureReasonCode.FULL_EXAM_CONFLICT)
    reason = (state.execution.reason_code or "").casefold()
    if reason.startswith("lifecycle_") or reason.startswith("temporal_boundary_"):
        return _full(state, request, gate, ApertureReasonCode.FULL_EXAM_LIFECYCLE)
    if state.execution.blocking_gate_id == gate.id and state.execution.resolving_authority == Authority.HUMAN:
        return _full(state, request, gate, ApertureReasonCode.FULL_EXAM_HUMAN_GATE)
    if state.execution.blocking_gate_id == gate.id and state.execution.resolving_authority is not None:
        return _full(state, request, gate, ApertureReasonCode.FULL_EXAM_AUTHORITY)

    exact, content = _reuse_lookup(state, request)
    if request.reuse_fact_ids:
        rejection_lineage = [item for item in state.lineage if "state-bound-rejection:v1" in item.depends_on]
        if any(item.integrity != LineageIntegrity.VERIFIED for item in rejection_lineage):
            return _full(state, request, gate, ApertureReasonCode.FULL_EXAM_INVALIDATION)
        try:
            verify_derived_indexes(state)
        except GovernanceError:
            return _full(state, request, gate, ApertureReasonCode.FULL_EXAM_INVALIDATION)
    if (exact is not None and exact.status == "INVALIDATED") or (
        content is not None and content.status == "INVALIDATED"
    ):
        return _full(state, request, gate, ApertureReasonCode.FULL_EXAM_INVALIDATION)
    if (exact is not None and exact.suppress) or (content is not None and content.suppress):
        return _receipt(
            state,
            request,
            gate,
            ExecutionMode.DETERMINISTIC_REUSE,
            ApertureReasonCode.VALID_DETERMINISTIC_REUSE,
            (),
        )

    # A declared joint surface is exact: no partial or neighboring evidence is allowed.
    if gate.required_evidence:
        if gate.source_state_version != state.version:
            return _full(state, request, gate, ApertureReasonCode.FAIL_CLOSED_STALE_GATE)
        if len(gate.required_evidence) != len(set(gate.required_evidence)):
            return _full(state, request, gate, ApertureReasonCode.FAIL_CLOSED_AMBIGUOUS_MODE)
        by_id = {item.id: item for item in state.facts}
        if any(item not in by_id for item in gate.required_evidence):
            return _full(
                state,
                request,
                gate,
                ApertureReasonCode.FAIL_CLOSED_MISSING_REQUIRED_EVIDENCE,
            )
        payload = tuple(by_id[item] for item in gate.required_evidence)
        if any(item.status != FreshnessStatus.VALID for item in payload):
            return _full(state, request, gate, ApertureReasonCode.FAIL_CLOSED_INVALID_FACT)
        if any(not _scope_allows(gate, item) for item in payload):
            return _full(state, request, gate, ApertureReasonCode.FAIL_CLOSED_UNAUTHORIZED_FACT)
        return _receipt(
            state,
            request,
            gate,
            ExecutionMode.WIDE_GOVERNED_APERTURE,
            ApertureReasonCode.DECLARED_JOINT_REQUIREMENT,
            payload,
        )

    # Existing blocking Impacts are HELM's governed sequential/decomposable representation.
    blocking = sorted(
        (item for item in state.impacts if item.blocking and item.affected_slice in gate.affected_slices),
        key=lambda item: (item.created_at, item.id),
    )
    if blocking:
        fact = next((item for item in state.facts if item.id == blocking[0].fact_id), None)
        if fact is None:
            return _full(
                state,
                request,
                gate,
                ApertureReasonCode.FAIL_CLOSED_MISSING_REQUIRED_EVIDENCE,
            )
        if fact.status != FreshnessStatus.VALID:
            return _full(state, request, gate, ApertureReasonCode.FAIL_CLOSED_INVALID_FACT)
        if not _scope_allows(gate, fact):
            return _full(state, request, gate, ApertureReasonCode.FAIL_CLOSED_UNAUTHORIZED_FACT)
        return _receipt(
            state,
            request,
            gate,
            ExecutionMode.SPARSE_APERTURE,
            ApertureReasonCode.DECLARED_DECOMPOSABLE,
            (fact,),
        )

    probe_fact = _structurally_eligible_probe_fact(state, gate, request)
    if probe_fact is not None:
        return _receipt(
            state,
            request,
            gate,
            ExecutionMode.PROBE_DISCOVERY,
            ApertureReasonCode.PROBE_STRUCTURALLY_ELIGIBLE,
            (probe_fact,),
        )
    if request.permitted_latent_fact_id is not None:
        return _full(state, request, gate, ApertureReasonCode.FAIL_CLOSED_UNKNOWN_RELATIONSHIP)
    return _full(state, request, gate, ApertureReasonCode.FAIL_CLOSED_AMBIGUOUS_MODE)
