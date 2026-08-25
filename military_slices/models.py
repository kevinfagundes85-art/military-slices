from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


def utc_now() -> datetime:
    return datetime.now(UTC)


class GateState(StrEnum):
    YES = "YES"
    NO = "NO"
    PARTIAL = "PARTIAL"
    UNKNOWN = "UNKNOWN"
    CONFLICTED = "CONFLICTED"


class Authority(StrEnum):
    HUMAN = "human"
    AUTHORITATIVE_SOURCE = "authoritative_source"
    DETERMINISTIC_RULE = "deterministic_rule"
    BOUNDED_AGENT = "bounded_agent"


class SurfaceType(StrEnum):
    TEXT = "text"
    DATE = "date"
    CHOICE = "choice"
    MULTISELECT = "multiselect"
    COMPARE = "compare"
    UPLOAD = "upload"
    CONFIRM = "confirm"
    CONFLICT = "conflict"


class SliceName(StrEnum):
    CAREER = "career"
    EDUCATION = "education"
    LOCATION = "location"
    RESUME = "resume"


class ServiceName(StrEnum):
    ARMY = "army"
    NAVY = "navy"
    MARINE_CORPS = "marine_corps"
    AIR_FORCE = "air_force"
    SPACE_FORCE = "space_force"
    COAST_GUARD = "coast_guard"


class StateCategory(StrEnum):
    CANONICAL = "canonical"
    HISTORICAL = "historical"
    HYPOTHETICAL = "hypothetical"
    LATENT = "latent"
    ACTIVE = "active"


class Evidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    label: str
    source_uri: str | None = None
    authority: Authority
    captured_at: datetime = Field(default_factory=utc_now)
    purpose: str


class Fact(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    statement: str
    value: str
    authority: Authority
    evidence_ids: list[str] = Field(default_factory=list)
    effective_at: str | None = None
    affected_slices: list[SliceName] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1, default=1)


class Gate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    question: str
    why: str
    state: GateState
    surface: SurfaceType
    affected_slices: list[SliceName]
    authority_required: Authority
    options: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    value_score: int = Field(ge=0, le=100, default=50)
    resolved_value: str | None = None
    updated_at: datetime = Field(default_factory=utc_now)


class CareerHypothesis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    rationale: str
    evidence: list[str] = Field(default_factory=list)
    capability_matches: list[str] = Field(default_factory=list)
    possible_gaps: list[str] = Field(default_factory=list)
    next_step: str = "Compare this direction with a real civilian job description."
    confidence: Literal["explore", "promising", "strong"] = "explore"
    status: Literal["candidate", "accepted", "rejected"] = "candidate"


class SliceProjection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: SliceName
    label: str
    status: GateState = GateState.UNKNOWN
    summary: str
    changed: bool = False


class ActiveTask(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    reason: str
    source: str
    affected_slices: list[SliceName] = Field(default_factory=list)


class ProgressItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    label: str
    state: GateState


class PathProgress(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target: str
    closed: int = Field(ge=0)
    total: int = Field(ge=1)
    items: list[ProgressItem]


class LensProjection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: SliceName
    label: str
    path_relevant: bool
    fact_count: int = Field(ge=0)
    closed_gates: int = Field(ge=0)
    open_gates: int = Field(ge=0)
    conflicted_gates: int = Field(ge=0)
    latent_dependencies: int = Field(ge=0)
    summary: str
    facts: list[str] = Field(default_factory=list, max_length=6)
    decisions: list[str] = Field(default_factory=list, max_length=6)


class HistoryEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: int = Field(ge=0)
    recorded_at: datetime
    human_anchor: str | None
    path_target_state: str
    open_gates: list[str]
    closed_decisions: list[str]
    change_summary: str
    current: bool = False


class WhatIfRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=3, max_length=2_000)
    source_version: int | None = Field(default=None, ge=0)


class WhatIfPromotionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str
    expected_version: int = Field(ge=0)
    idempotency_key: str = Field(min_length=8, max_length=128)


class WhatIfBranch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    category: Literal[StateCategory.HYPOTHETICAL] = StateCategory.HYPOTHETICAL
    source_version: int = Field(ge=0)
    human_anchor: str | None
    path_target_state: str
    modification_kind: Literal["relocation_willingness", "education_priority", "transition_date"]
    modification_value: str
    statement: str
    affected_gates: list[str]
    affected_slices: list[SliceName]
    consequences: list[str]
    evidence_basis: list[str]
    uncertainty: list[str]
    conflicts: list[str]
    current_summary: list[str]
    hypothetical_summary: list[str]
    created_at: datetime = Field(default_factory=utc_now)
    token: str = ""


class Decision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    gate_id: str
    value: str
    authority: Authority = Authority.HUMAN
    decided_at: datetime = Field(default_factory=utc_now)


class FeedbackEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    headline: str
    consequences: list[str]
    created_at: datetime = Field(default_factory=utc_now)


class TelemetrySummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    tool_calls: int = 0
    agent_gates_closed: int = 0
    duplicate_questions_avoided: int = 0
    total_agent_latency_ms: int = 0
    resolver_context_bytes: int = 0
    state_bytes_avoided: int = 0
    context_reduction_ratio: float = 0
    estimated_cost_usd: float = 0


class CanonicalState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile_id: str
    version: int = 0
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    original_intents: list[str] = Field(default_factory=list)
    current_goal: str | None = None
    human_anchor: str | None = None
    service: ServiceName | None = None
    component_status: str | None = None
    separation_type: Literal["separation", "retirement"] | None = None
    transition_date: str | None = None
    stage: Literal["TODAY", "PREPARE", "SEPARATE", "TRANSITION", "STABILIZE"] = "TODAY"
    current_timeline_window: str = "PATH_IDENTITY"
    path_target_state: str = "PATH_IDENTIFIED"
    active_tasks: list[ActiveTask] = Field(default_factory=list)
    latent_fact_count: int = Field(default=0, ge=0)
    transition_pack_version: str = "2026-08-24-v2-shadow-tested"
    facts: list[Fact] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    gates: list[Gate] = Field(default_factory=list)
    decisions: list[Decision] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    career_hypotheses: list[CareerHypothesis] = Field(default_factory=list)
    rejected_roles: list[str] = Field(default_factory=list)
    projections: list[SliceProjection] = Field(default_factory=list)
    feedback: list[FeedbackEvent] = Field(default_factory=list)
    processed_keys: list[str] = Field(default_factory=list)
    telemetry: TelemetrySummary = Field(default_factory=TelemetrySummary)


class OrientedStatement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str
    kind: Literal["fact", "preference", "goal", "date", "unknown", "conflict"]
    affected_slices: list[SliceName]


class OrientationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reviewed_input: str
    summary: str
    statements: list[OrientedStatement]
    affected_slices: list[SliceName]
    clarification_question: str | None = None
    sufficient: bool
    token: str = ""


class OrientRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1, max_length=12_000)


class ConfirmRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str
    reviewed_input: str = Field(min_length=1, max_length=12_000)
    expected_version: int = Field(ge=0)
    idempotency_key: str = Field(min_length=8, max_length=128)


class DecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    gate_id: str
    value: str = Field(min_length=1, max_length=2_000)
    expected_version: int = Field(ge=0)
    idempotency_key: str = Field(min_length=8, max_length=128)


class StateEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    state: CanonicalState
    active_gate: Gate | None
    what_changed: FeedbackEvent | None
    progress: PathProgress
    lenses: list[LensProjection]
    agent_run: dict[str, Any] | None = None
