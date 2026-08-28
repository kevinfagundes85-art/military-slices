"""Executable, label-blind runtime contract for the replacement T1 corpus.

This module is benchmark infrastructure.  It adds no Canonical state and grants
no authority.  Public tasks carry exact serialized runtime objects so the
operator never invents a mapping after corpus seal.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from benchmark.t1_governed_resolver import GOVERNED_ADJUDICATION_SYSTEM_INSTRUCTION
from military_slices.adaptive_resolver_aperture import (
    ApertureRequest,
    ApertureSelection,
    ExecutionMode,
)
from military_slices.models import CanonicalState


class GovernedOutcome(StrEnum):
    PASS = "PASS"  # noqa: S105 - decision outcome, not a credential
    WAIT = "WAIT"
    HUMAN = "HUMAN"
    REANCHOR = "REANCHOR"
    TERMINATE = "TERMINATE"
    FAIL = "FAIL"


class GovernedAdjudicationDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: str
    outcome: GovernedOutcome
    evidence_ids: list[str]
    reason: str = Field(min_length=1)


class PublicApertureRequest(BaseModel):
    """Exact JSON representation of the ephemeral H1 request."""

    model_config = ConfigDict(extra="forbid")

    task_decision_id: str
    gate_id: str
    effect_dimension: str
    reuse_fact_ids: list[str] = Field(default_factory=list)
    reuse_validity_dimensions: list[str] = Field(default_factory=list)
    permitted_latent_fact_id: str | None = None
    probe_discovery_permitted: bool = False

    def to_runtime(self) -> ApertureRequest:
        return ApertureRequest(
            task_decision_id=self.task_decision_id,
            gate_id=self.gate_id,
            effect_dimension=self.effect_dimension,
            reuse_fact_ids=tuple(self.reuse_fact_ids),
            reuse_validity_dimensions=tuple(self.reuse_validity_dimensions),
            permitted_latent_fact_id=self.permitted_latent_fact_id,
            probe_discovery_permitted=self.probe_discovery_permitted,
        )


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


class ReplacementT1PublicTask(BaseModel):
    """Complete label-blind task handed to BHE after replacement seal."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str
    corpus_id: str
    task_id: str = Field(pattern=r"^t1r-[0-9a-f]{16}$")
    canonical_state: dict[str, Any]
    canonical_state_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    aperture_request: PublicApertureRequest
    decision_request: dict[str, Any]
    broad_context_case: dict[str, Any]
    authority_binding: dict[str, Any]
    public_metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_runtime_binding(self) -> ReplacementT1PublicTask:
        if sha256_json(self.canonical_state) != self.canonical_state_sha256:
            raise ValueError("canonical_state_sha256 mismatch")
        state = CanonicalState.model_validate(self.canonical_state)
        request = self.aperture_request.to_runtime()
        if request.task_decision_id != self.task_id:
            raise ValueError("ApertureRequest task identity mismatch")
        if not any(gate.id == request.gate_id for gate in state.gates):
            raise ValueError("ApertureRequest Gate does not resolve in CanonicalState")
        return self

    def runtime_state(self) -> CanonicalState:
        return CanonicalState.model_validate(self.canonical_state)


@dataclass(frozen=True)
class ProviderInvocation:
    system_instruction: str
    payload: dict[str, Any]
    response_schema: dict[str, Any]


def governed_resolver_invocation(
    task: ReplacementT1PublicTask,
    *,
    arm: str,
    selection: ApertureSelection | None,
) -> ProviderInvocation | None:
    """Bind H0/H1 to one non-authoritative generic Resolver call."""

    state = task.runtime_state()
    if arm == "H1" and selection is not None and selection.receipt.selected_mode == ExecutionMode.DETERMINISTIC_REUSE:
        return None

    if arm == "H1" and selection is not None and selection.receipt.selected_mode in {
        ExecutionMode.SPARSE_APERTURE,
        ExecutionMode.WIDE_GOVERNED_APERTURE,
    }:
        evidence = [fact.model_dump(mode="json") for fact in selection.payload]
        governed_surface: dict[str, Any] = {
            "anchor": state.human_anchor,
            "path": state.path_target_state,
            "gate": next(
                gate.model_dump(mode="json")
                for gate in state.gates
                if gate.id == task.aperture_request.gate_id
            ),
            "evidence": evidence,
        }
    else:
        governed_surface = state.model_dump(mode="json")

    payload = {
        "task_id": task.task_id,
        "arm": arm,
        "decision_request": task.decision_request,
        "governed_surface": governed_surface,
        "execution_receipt": selection.receipt.model_dump(mode="json") if selection is not None else None,
    }
    return ProviderInvocation(
        system_instruction=GOVERNED_ADJUDICATION_SYSTEM_INSTRUCTION,
        payload=payload,
        response_schema=GovernedAdjudicationDecision.model_json_schema(),
    )


def broad_context_invocation(task: ReplacementT1PublicTask, system_instruction: str) -> ProviderInvocation:
    return ProviderInvocation(
        system_instruction=system_instruction,
        payload={
            "task_id": task.task_id,
            "decision_request": task.decision_request,
            "case_file": task.broad_context_case,
        },
        response_schema=GovernedAdjudicationDecision.model_json_schema(),
    )
