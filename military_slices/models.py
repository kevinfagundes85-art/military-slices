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
    estimated_cost_usd: float = 0


class CanonicalState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile_id: str
    version: int = 0
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    original_intents: list[str] = Field(default_factory=list)
    current_goal: str | None = None
    transition_date: str | None = None
    stage: Literal["TODAY", "PREPARE", "SEPARATE", "TRANSITION", "STABILIZE"] = "TODAY"
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
    agent_run: dict[str, Any] | None = None
