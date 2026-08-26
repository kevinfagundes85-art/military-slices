from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


def utc_now() -> datetime:
    return datetime.now(UTC)


class GateState(StrEnum):
    YES = "YES"
    NO = "NO"
    PARTIAL = "PARTIAL"
    UNKNOWN = "UNKNOWN"
    CONFLICTED = "CONFLICTED"


class ExecutionState(StrEnum):
    ACTIVE = "ACTIVE"
    PARALYZED = "PARALYZED"
    COMPLETE = "COMPLETE"


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


class PlanningActor(StrEnum):
    UNKNOWN = "unknown"
    SERVICE_MEMBER = "service_member"
    VETERAN = "veteran"
    MILITARY_SPOUSE = "military_spouse"
    COUNSELOR_SUPPORTER = "counselor_supporter"


class MilitaryStateSubject(StrEnum):
    UNKNOWN = "unknown"
    PLANNING_ACTOR = "planning_actor"
    PLANNING_ACTOR_SPOUSE = "planning_actor_spouse"
    SUPPORTED_PERSON = "supported_person"


class LifecyclePosition(StrEnum):
    UNKNOWN = "unknown"
    CURRENTLY_SERVING = "currently_serving"
    LEAVING_WITHIN_12_MONTHS = "leaving_within_12_months"
    SEPARATED_WITHIN_LAST_YEAR = "separated_within_last_year"
    SEPARATED_1_TO_5_YEARS = "separated_1_to_5_years"
    SEPARATED_MORE_THAN_5_YEARS = "separated_more_than_5_years"


class ServiceComponent(StrEnum):
    ACTIVE_DUTY = "active_duty"
    RESERVE = "reserve"
    NATIONAL_GUARD = "national_guard"


class StateCategory(StrEnum):
    CANONICAL = "canonical"
    HISTORICAL = "historical"
    HYPOTHETICAL = "hypothetical"
    LATENT = "latent"
    ACTIVE = "active"


class FreshnessStatus(StrEnum):
    VALID = "valid"
    STALE = "stale"


class FreshnessClass(StrEnum):
    STABLE = "stable"
    SLOW = "slow"
    VOLATILE = "volatile"
    EXTERNAL_EXPIRING = "external_expiring"


class DomainPackStatus(StrEnum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    RETIRED = "RETIRED"
    LEGACY_VALID = "LEGACY_VALID"


class MigrationStatus(StrEnum):
    LEGACY_VALID = "LEGACY_VALID"
    LINEAGE_ENRICHED = "LINEAGE_ENRICHED"
    LINEAGE_INCOMPLETE = "LINEAGE_INCOMPLETE"
    REVALIDATION_REQUIRED = "REVALIDATION_REQUIRED"


class LineageIntegrity(StrEnum):
    VERIFIED = "VERIFIED"
    INCOMPLETE = "INCOMPLETE"
    CONFLICTED = "CONFLICTED"


class DomainPackRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    domain_pack_id: str = Field(min_length=3, max_length=100)
    version: str = Field(min_length=1, max_length=100)
    content_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    helm_compatibility_version: str = "1.1"
    approval_event_id: str | None = None
    effective_date: str | None = None
    status: DomainPackStatus = DomainPackStatus.DRAFT

    @classmethod
    def for_payload(
        cls,
        *,
        domain_pack_id: str,
        version: str,
        payload: dict[str, Any],
        status: DomainPackStatus = DomainPackStatus.DRAFT,
        helm_compatibility_version: str = "1.1",
        approval_event_id: str | None = None,
        effective_date: str | None = None,
    ) -> DomainPackRef:
        encoded = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
        return cls(
            domain_pack_id=domain_pack_id,
            version=version,
            content_hash=hashlib.sha256(encoded).hexdigest(),
            helm_compatibility_version=helm_compatibility_version,
            approval_event_id=approval_event_id,
            effective_date=effective_date,
            status=status,
        )

    @model_validator(mode="after")
    def active_pack_requires_approval(self) -> DomainPackRef:
        if self.status == DomainPackStatus.ACTIVE and (
            not self.approval_event_id or not self.effective_date
        ):
            raise ValueError("An active Domain Pack requires approval and an effective date.")
        return self


def legacy_transition_pack_ref() -> DomainPackRef:
    legacy_identity = {
        "domain_pack_id": "military-transition",
        "version": "2026-08-24-v2-shadow-tested",
        "status": "legacy-unapproved-baseline",
    }
    return DomainPackRef.for_payload(
        domain_pack_id="military-transition",
        version="2026-08-24-v2-shadow-tested",
        payload=legacy_identity,
        status=DomainPackStatus.LEGACY_VALID,
    )


class ActorProvenance(BaseModel):
    model_config = ConfigDict(extra="forbid")

    actor_id: str
    actor_type: Literal["human", "system", "authoritative_source"]
    auth_context: str
    event_id: str = Field(min_length=8, max_length=160)
    timestamp: datetime = Field(default_factory=utc_now)
    integrity_ref: str
    source_system: str
    trusted: bool = False

    @classmethod
    def trusted_session(
        cls,
        *,
        profile_id: str,
        event_id: str,
        integrity_ref: str,
        source_system: str = "military-slices-web",
    ) -> ActorProvenance:
        return cls(
            actor_id=profile_id,
            actor_type="human",
            auth_context="signed_session",
            event_id=event_id,
            integrity_ref=integrity_ref,
            source_system=source_system,
            trusted=True,
        )


class MutationEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    idempotency_key: str
    actor: ActorProvenance
    expected_version: int = Field(ge=0)
    result_version: int = Field(ge=1)
    source_state_version: int = Field(ge=0)
    mutation_kind: str = Field(min_length=2, max_length=100)
    dependency_refs: list[str] = Field(default_factory=list)
    domain_pack: DomainPackRef
    occurred_at: datetime = Field(default_factory=utc_now)


class LineageRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subject_id: str
    depends_on: list[str] = Field(default_factory=list)
    valid_while: list[str] = Field(default_factory=list)
    invalidated_by: list[str] = Field(default_factory=list)
    source_state_version: int = Field(ge=0)
    authority_refs: list[str] = Field(default_factory=list)
    integrity: LineageIntegrity = LineageIntegrity.VERIFIED


class DerivedIndexRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Literal["gates", "projections"]
    source_state_version: int = Field(ge=0)
    content_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    integrity: LineageIntegrity = LineageIntegrity.VERIFIED


class ResolverTransitionProposal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    gate_id: str
    source_state_version: int = Field(ge=0)
    proposed_state: GateState
    proposed_value: str | None = None
    authority: Authority
    effect: Literal["nominate", "resolve"] = "resolve"
    scope: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)


class GovernorDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    authorized: bool
    reason_code: str
    gate_id: str
    source_state_version: int = Field(ge=0)
    effect: Literal["nominate", "resolve"]
    authority: Authority
    permitted_scope: list[str] = Field(default_factory=list)


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
    field_key: str = "general_context"
    status: FreshnessStatus = FreshnessStatus.VALID
    last_validated_at: datetime = Field(default_factory=utc_now)
    freshness_class: FreshnessClass = FreshnessClass.STABLE


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
    parent_gate_id: str | None = None
    authorized_scope: list[str] = Field(default_factory=list)
    authority_set: list[Authority] = Field(default_factory=list)
    construction_provenance: str = "deterministic:legacy-gate"
    source_state_version: int = Field(default=0, ge=0)
    required_evidence: list[str] = Field(default_factory=list)
    value_score: int = Field(ge=0, le=100, default=50)
    resolved_value: str | None = None
    updated_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def supply_legacy_bounds(self) -> Gate:
        if not self.authorized_scope:
            self.authorized_scope = [f"slice:{item.value}" for item in self.affected_slices]
        if not self.authority_set:
            self.authority_set = [self.authority_required]
        return self


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
    state_category: Literal[StateCategory.HYPOTHETICAL] = StateCategory.HYPOTHETICAL


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
    may_have_changed: bool = False


class ReceiptPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str
    operation: Literal["replace", "remove"] = "replace"
    value: str | None = None
    reason: str
    created_at: datetime = Field(default_factory=utc_now)


class ImpactItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    source_field: str
    dependent_field: str
    fact_id: str
    affected_slice: SliceName
    message: str
    question: str
    confirm_label: str
    update_label: str
    update_options: list[str] = Field(default_factory=list, max_length=4)
    blocking: bool = False
    created_at: datetime = Field(default_factory=utc_now)


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


class StartingVectorRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    operating_role: Literal["veteran_service_member", "spouse_partner", "counselor_supporter"]
    lifecycle_position: LifecyclePosition
    service: ServiceName
    component: ServiceComponent
    expected_version: int = Field(ge=0)
    idempotency_key: str = Field(min_length=8, max_length=128)


class FogBankRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=3, max_length=4_000)
    source_version: int = Field(ge=0)


class FogBankAcceptRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str
    expected_version: int = Field(ge=0)
    idempotency_key: str = Field(min_length=8, max_length=128)


class FogBankChange(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: Literal["human_anchor", "lifecycle_position", "transition_date"]
    current_value: str | None = None
    proposed_value: str | None = None
    reason: str
    affected_slices: list[SliceName] = Field(default_factory=list)


class RevalidationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    impact_id: str
    action: Literal["confirm", "update", "dismiss"]
    value: str | None = Field(default=None, max_length=2_000)
    expected_version: int = Field(ge=0)
    idempotency_key: str = Field(min_length=8, max_length=128)


class WhatIfBranch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    category: Literal[StateCategory.HYPOTHETICAL] = StateCategory.HYPOTHETICAL
    source_version: int = Field(ge=0)
    human_anchor: str | None
    path_target_state: str
    modification_kind: Literal[
        "relocation_willingness",
        "education_priority",
        "transition_date",
        "target_experiment",
    ]
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
    temporal_dependencies_evaluated: int = 0
    temporal_fields_marked_stale: int = 0
    temporal_fields_silently_refreshed: int = 0
    temporal_human_prompts: int = 0
    temporal_one_tap_confirmations: int = 0
    temporal_bounded_update_flows: int = 0
    temporal_freshness_model_calls: int = 0
    temporal_patch_bytes: int = 0
    temporal_patch_count: int = 0
    temporal_full_rebuilds: int = 0
    temporal_latency_ms: int = 0
    temporal_errors: int = 0
    anchor_candidates: int = 0
    selected_anchor_class: str | None = None
    anchor_selection_reason_code: str | None = None
    execution_state_before: ExecutionState | None = None
    execution_state_after: ExecutionState | None = None
    blocked_transition: str | None = None
    blocking_gate_id: str | None = None
    resume_target_specificity: Literal["concrete", "generic", "negated", "absent"] = "absent"


class ExecutionStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    state: ExecutionState = ExecutionState.ACTIVE
    blocked_transition: str | None = None
    blocking_gate_id: str | None = None
    reason_code: str | None = "anchor_or_next_transition_available"
    derived_from_version: int = Field(default=0, ge=0)
    anchor_fingerprint: str | None = None
    resolving_authority: Authority | None = None
    updated_at: datetime = Field(default_factory=utc_now)


class CanonicalState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile_id: str
    version: int = 0
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    original_intents: list[str] = Field(default_factory=list)
    current_goal: str | None = None
    human_anchor: str | None = None
    career_target: str | None = None
    planning_actor: PlanningActor = PlanningActor.UNKNOWN
    military_state_subject: MilitaryStateSubject = MilitaryStateSubject.UNKNOWN
    starting_vector_complete: bool = False
    lifecycle_position: LifecyclePosition = LifecyclePosition.UNKNOWN
    service: ServiceName | None = None
    component_status: str | None = None
    separation_type: Literal["separation", "retirement"] | None = None
    transition_date: str | None = None
    pcs_relocation_date: str | None = None
    stage: Literal["TODAY", "PREPARE", "SEPARATE", "TRANSITION", "STABILIZE"] = "TODAY"
    current_timeline_window: str = "PATH_IDENTITY"
    path_target_state: str = "PATH_IDENTIFIED"
    execution: ExecutionStatus = Field(default_factory=ExecutionStatus)
    active_tasks: list[ActiveTask] = Field(default_factory=list)
    latent_fact_count: int = Field(default=0, ge=0)
    transition_pack_version: str = "2026-08-24-v2-shadow-tested"
    domain_pack: DomainPackRef = Field(default_factory=legacy_transition_pack_ref)
    migration_status: MigrationStatus = MigrationStatus.LEGACY_VALID
    facts: list[Fact] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    gates: list[Gate] = Field(default_factory=list)
    decisions: list[Decision] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    career_hypotheses: list[CareerHypothesis] = Field(default_factory=list)
    rejected_roles: list[str] = Field(default_factory=list)
    projections: list[SliceProjection] = Field(default_factory=list)
    feedback: list[FeedbackEvent] = Field(default_factory=list)
    impacts: list[ImpactItem] = Field(default_factory=list)
    receipt_deltas: list[ReceiptPatch] = Field(default_factory=list)
    processed_keys: list[str] = Field(default_factory=list)
    mutation_events: list[MutationEvent] = Field(default_factory=list)
    governor_decisions: list[GovernorDecision] = Field(default_factory=list)
    lineage: list[LineageRecord] = Field(default_factory=list)
    derived_indexes: list[DerivedIndexRef] = Field(default_factory=list)
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
    conflicts: list[str] = Field(default_factory=list)
    sufficient: bool
    token: str = ""


class FogBankProposal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_version: int = Field(ge=0)
    reviewed_input: str
    status: Literal["clarification_needed", "review_ready"]
    summary: str
    clarification_question: str | None = None
    statements: list[OrientedStatement] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    affected_slices: list[SliceName] = Field(default_factory=list)
    changes: list[FogBankChange] = Field(default_factory=list)
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
    impact: ImpactItem | None = None
    agent_run: dict[str, Any] | None = None
