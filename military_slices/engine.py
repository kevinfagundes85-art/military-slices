from __future__ import annotations

import hashlib
import re
from copy import deepcopy
from datetime import UTC, date, datetime, timedelta

from military_slices.domain_pack import installed_domain_pack_ref
from military_slices.governance import (
    bind_gate_contracts,
    reconstitute_governance,
    verify_derived_indexes,
)
from military_slices.models import (
    Authority,
    CanonicalState,
    CareerHypothesis,
    Decision,
    Evidence,
    Fact,
    FeedbackEvent,
    FogBankChange,
    FogBankProposal,
    Gate,
    GateState,
    LifecyclePosition,
    MilitaryStateSubject,
    OrientationResult,
    OrientedStatement,
    PlanningActor,
    ServiceComponent,
    ServiceName,
    SliceName,
    SliceProjection,
    SurfaceType,
    utc_now,
)
from military_slices.path_runtime import (
    ANCHOR_OPTIONS,
    anchor_domain,
    derive_execution_state,
    detect_planning_parties,
    detect_separation_type,
    detect_service,
    normalize_service_choice,
    path_task_gate_id,
    refresh_path_state,
    resolve_human_anchor,
    resume_target_specificity,
)
from military_slices.temporal import (
    apply_revalidation_delta,
    evaluate_elapsed_freshness,
    fact_is_usable,
    infer_fact_metadata,
    propagate_temporal_changes,
)

ALL_SLICES = [
    SliceName.CAREER,
    SliceName.EDUCATION,
    SliceName.LOCATION,
    SliceName.RESUME,
]

MAX_ARTIFACT_FACTS = 24


def stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("\x1f".join(parts).encode()).hexdigest()[:16]
    return f"{prefix}_{digest}"


def _sentences(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text.strip())
    return [part.strip(" -\t") for part in re.split(r"(?<=[.!?])\s+|\n+", normalized) if part.strip()]


def _slice_hits(statement: str) -> list[SliceName]:
    value = statement.lower()
    hits: list[SliceName] = []
    keywords = {
        SliceName.CAREER: (
            "job",
            "career",
            "work",
            "position",
            "remote",
            "hybrid",
            "salary",
            "income",
            "employ",
            "role",
            "industry",
            "defense",
            "manager",
            "analyst",
            "build a company",
            "build something",
            "startup",
            "founder",
            "make an impact",
            "work with veterans",
        ),
        SliceName.EDUCATION: (
            "school",
            "degree",
            "college",
            "credential",
            "certif",
            "training",
            "education",
            "gi bill",
            "learn ai",
            "upskill",
        ),
        SliceName.LOCATION: (
            "relocat",
            "move",
            "location",
            "commute",
            "city",
            "state",
            "family",
            "stay near",
            "stay in",
            "stay local",
            "remain local",
            "near ",
        ),
        SliceName.RESUME: (
            "resume",
            "résumé",
            "cv",
            "mos",
            "rating",
            "afsc",
            "specialty",
            "experience",
            "duty",
            "led",
            "coordinated",
        ),
    }
    for slice_name, terms in keywords.items():
        if any(term in value for term in terms):
            hits.append(slice_name)
    return hits


def _statement_kind(statement: str) -> str:
    value = statement.lower()
    if any(term in value for term in ("don't know", "do not know", "not sure", "uncertain")):
        return "unknown"
    if any(term in value for term in ("can't", "cannot", "won't", "will not", "hate", "must not")):
        return "preference"
    if re.search(
        r"\b(20\d{2}-\d{2}-\d{2}|20\d{2}|january|february|march|april|may|june|july|august|september|october|november|december)\b",
        value,
    ):
        return "date"
    if any(term in value for term in ("want", "need", "goal", "plan", "hope")):
        return "goal"
    return "fact"


def _explicit_lifecycle_claim(text: str) -> LifecyclePosition | None:
    lower = text.casefold()
    if re.search(
        r"\b(?:left|separated|retired|got out)\b[^.!?]{0,50}"
        r"\b(?:[1-5]|one|two|three|four|five)\s+years?\s+ago\b",
        lower,
    ):
        return LifecyclePosition.SEPARATED_1_TO_5_YEARS
    if re.search(
        r"\b(?:left|separated|retired|got out)\b[^.!?]{0,50}"
        r"\b(?:months?|less than a year|last year)\b",
        lower,
    ):
        return LifecyclePosition.SEPARATED_WITHIN_LAST_YEAR
    if re.search(r"\b(?:left|separated|retired|got out)\b[^.!?]{0,50}\b(?:[6-9]|\d{2,})\s+years?\s+ago\b", lower):
        return LifecyclePosition.SEPARATED_MORE_THAN_5_YEARS
    if any(term in lower for term in ("currently serving", "still serving", "on active duty now")):
        return LifecyclePosition.CURRENTLY_SERVING
    if any(term in lower for term in ("leave active service", "separate next", "retire next", "getting out next")):
        return LifecyclePosition.LEAVING_WITHIN_12_MONTHS
    return None


def _orientation_conflicts(text: str, context: CanonicalState | None) -> list[str]:
    if context is None or context.lifecycle_position == LifecyclePosition.UNKNOWN:
        return []
    claimed = _explicit_lifecycle_claim(text)
    if claimed is None or claimed == context.lifecycle_position:
        return []
    established_past = context.lifecycle_position in {
        LifecyclePosition.SEPARATED_WITHIN_LAST_YEAR,
        LifecyclePosition.SEPARATED_1_TO_5_YEARS,
        LifecyclePosition.SEPARATED_MORE_THAN_5_YEARS,
    }
    claimed_past = claimed in {
        LifecyclePosition.SEPARATED_WITHIN_LAST_YEAR,
        LifecyclePosition.SEPARATED_1_TO_5_YEARS,
        LifecyclePosition.SEPARATED_MORE_THAN_5_YEARS,
    }
    if established_past != claimed_past:
        return ["This conflicts with the service timeline you established at the start."]
    return []


def orient(text: str, *, context: CanonicalState | None = None) -> OrientationResult:
    statements: list[OrientedStatement] = []
    affected: list[SliceName] = []
    for sentence in _sentences(text):
        hits = _slice_hits(sentence)
        for slice_name in hits:
            if slice_name not in affected:
                affected.append(slice_name)
        statements.append(
            OrientedStatement(
                text=sentence,
                kind=_statement_kind(sentence),
                affected_slices=hits,
            )
        )

    meaningful = [statement for statement in statements if statement.affected_slices]
    conflicts = _orientation_conflicts(text, context)
    sufficient = bool(meaningful) and not conflicts
    clarification: str | None = None
    if conflicts:
        clarification = "Which service timeline is current? Nothing will change until you resolve this difference."
    elif not sufficient:
        clarification = "What decision about your transition would you most like help with first?"
    elif SliceName.CAREER in affected and not any(
        term in text.lower() for term in ("want", "need", "prefer", "don't", "do not", "won't", "hate")
    ):
        clarification = "What would you like more or less of in your next work?"

    if meaningful:
        domains = ", ".join(_slice_label(item) for item in affected)
        summary = f"This could shape {domains}."
    else:
        summary = "There is not enough decision context to choose a useful starting point yet."

    return OrientationResult(
        reviewed_input=text.strip(),
        summary=summary,
        statements=statements,
        affected_slices=affected,
        clarification_question=clarification,
        conflicts=conflicts,
        sufficient=sufficient,
    )


def _slice_label(slice_name: SliceName) -> str:
    return {
        SliceName.CAREER: "work",
        SliceName.EDUCATION: "education",
        SliceName.LOCATION: "location",
        SliceName.RESUME: "your experience story",
    }[slice_name]


def new_state(profile_id: str) -> CanonicalState:
    state = refresh_path_state(CanonicalState(profile_id=profile_id, projections=_build_projections(None)))
    state.domain_pack = installed_domain_pack_ref()
    state.gates = _recompute_gates(state)
    state.projections = _build_projections(state)
    return bind_gate_contracts(derive_execution_state(state))


def apply_starting_vector(
    current: CanonicalState,
    *,
    operating_role: str,
    lifecycle_position: LifecyclePosition,
    service: ServiceName,
    component: ServiceComponent,
    idempotency_key: str,
) -> CanonicalState:
    if idempotency_key in current.processed_keys:
        return current
    if current.starting_vector_complete:
        raise ValueError("The starting orientation is already established. Use Something doesn’t fit to reconsider it.")
    state = deepcopy(current)
    previous_execution = deepcopy(current.execution)
    if operating_role == "veteran_service_member":
        state.planning_actor = (
            PlanningActor.VETERAN
            if lifecycle_position
            in {
                LifecyclePosition.SEPARATED_WITHIN_LAST_YEAR,
                LifecyclePosition.SEPARATED_1_TO_5_YEARS,
                LifecyclePosition.SEPARATED_MORE_THAN_5_YEARS,
            }
            else PlanningActor.SERVICE_MEMBER
        )
        state.military_state_subject = MilitaryStateSubject.PLANNING_ACTOR
    elif operating_role == "spouse_partner":
        state.planning_actor = PlanningActor.MILITARY_SPOUSE
        state.military_state_subject = MilitaryStateSubject.PLANNING_ACTOR_SPOUSE
    elif operating_role == "counselor_supporter":
        state.planning_actor = PlanningActor.COUNSELOR_SUPPORTER
        state.military_state_subject = MilitaryStateSubject.SUPPORTED_PERSON
    else:
        raise ValueError("Choose who you are planning for.")
    state.lifecycle_position = lifecycle_position
    state.service = service
    state.component_status = component
    state.starting_vector_complete = True
    labels = {
        "veteran_service_member": "Veteran or service member",
        "spouse_partner": "Spouse or partner",
        "counselor_supporter": "Counselor or supporter",
    }
    state.decisions.append(
        Decision(
            id=stable_id("decision", state.profile_id, idempotency_key),
            gate_id="starting-vector",
            value=f"{labels[operating_role]} · {lifecycle_position.value} · {service.value} · {component.value}",
        )
    )
    state = refresh_path_state(state)
    state.gates = _recompute_gates(state)
    state.projections = _build_projections(state)
    state.feedback.append(
        FeedbackEvent(
            id=stable_id("feedback", state.profile_id, idempotency_key),
            headline="Your starting point is set.",
            consequences=["The next question will use this service and timeline context."],
        )
    )
    state.processed_keys.append(idempotency_key)
    state.updated_at = utc_now()
    state.version += 1
    return derive_execution_state(state, previous=previous_execution, resolving_authority=Authority.HUMAN)


def _already_civilian_employed(text: str) -> bool:
    lower = text.casefold()
    return bool(
        re.search(r"\b(?:already\s+)?(?:work(?:ing)?|employed)\s+as\s+(?:a|an)\b", lower)
        or any(term in lower for term in ("already have a civilian job", "already employed in civilian"))
    )


def examine_fog_bank(current: CanonicalState, text: str) -> FogBankProposal:
    reviewed = text.strip()
    oriented = orient(reviewed)
    changes: list[FogBankChange] = []
    conflicts: list[str] = []
    claimed_timeline = _explicit_lifecycle_claim(reviewed)
    if claimed_timeline and claimed_timeline != current.lifecycle_position:
        changes.append(
            FogBankChange(
                field="lifecycle_position",
                current_value=current.lifecycle_position.value,
                proposed_value=claimed_timeline.value,
                reason="Your new statement gives a different explicit service timeline.",
                affected_slices=ALL_SLICES,
            )
        )
        conflicts.append("The new service timeline differs from the current orientation.")
        if (
            claimed_timeline
            in {
                LifecyclePosition.SEPARATED_WITHIN_LAST_YEAR,
                LifecyclePosition.SEPARATED_1_TO_5_YEARS,
                LifecyclePosition.SEPARATED_MORE_THAN_5_YEARS,
            }
            and current.transition_date
        ):
            changes.append(
                FogBankChange(
                    field="transition_date",
                    current_value=current.transition_date,
                    proposed_value=None,
                    reason="A future separation date cannot remain active for an already-separated veteran.",
                    affected_slices=ALL_SLICES,
                )
            )

    anchor_resolution = resolve_human_anchor(oriented)
    proposed_anchor = anchor_resolution.anchor
    employment_disproves_first_job = (
        _already_civilian_employed(reviewed) and current.human_anchor == "Find civilian work"
    )
    if employment_disproves_first_job:
        conflicts.append("Existing civilian employment conflicts with the current first-job target.")
        if not proposed_anchor or proposed_anchor == "Find civilian work":
            next_clause = next(
                (
                    sentence
                    for sentence in _sentences(reviewed)
                    if any(
                        term in sentence.casefold()
                        for term in ("trying to figure out", "want to build", "what i should build", "do next")
                    )
                ),
                None,
            )
            proposed_anchor = next_clause
    if proposed_anchor and proposed_anchor != current.human_anchor:
        changes.append(
            FogBankChange(
                field="human_anchor",
                current_value=current.human_anchor,
                proposed_value=proposed_anchor,
                reason="The reviewed statement identifies a different outcome to examine next.",
                affected_slices=oriented.affected_slices or [SliceName.CAREER],
            )
        )

    affected = list(
        dict.fromkeys(
            [slice_name for change in changes for slice_name in change.affected_slices] + oriented.affected_slices
        )
    )
    if not changes:
        return FogBankProposal(
            source_version=current.version,
            reviewed_input=reviewed,
            status="clarification_needed",
            summary="There is not enough new context to propose a safe re-orientation yet.",
            clarification_question="What is the current plan getting wrong or leaving out?",
            statements=oriented.statements,
            conflicts=conflicts,
            affected_slices=affected,
        )
    return FogBankProposal(
        source_version=current.version,
        reviewed_input=reviewed,
        status="review_ready",
        summary="The current frame may need to change, but nothing has changed yet.",
        statements=oriented.statements,
        conflicts=conflicts,
        affected_slices=affected,
        changes=changes,
    )


def apply_fog_bank_reorientation(
    current: CanonicalState,
    proposal: FogBankProposal,
    *,
    idempotency_key: str,
) -> CanonicalState:
    if idempotency_key in current.processed_keys:
        return current
    if proposal.status != "review_ready" or not proposal.changes:
        raise ValueError("This Fog Bank exploration does not contain a reviewable change.")
    if proposal.source_version != current.version:
        raise ValueError("The plan changed after this exploration. Reconsider it from the current plan.")
    state = deepcopy(current)
    previous_execution = deepcopy(current.execution)
    for change in proposal.changes:
        if change.field == "lifecycle_position" and change.proposed_value:
            state.lifecycle_position = LifecyclePosition(change.proposed_value)
            if (
                state.lifecycle_position
                in {
                    LifecyclePosition.SEPARATED_WITHIN_LAST_YEAR,
                    LifecyclePosition.SEPARATED_1_TO_5_YEARS,
                    LifecyclePosition.SEPARATED_MORE_THAN_5_YEARS,
                }
                and state.planning_actor == PlanningActor.SERVICE_MEMBER
            ):
                state.planning_actor = PlanningActor.VETERAN
        elif change.field == "transition_date":
            state.transition_date = change.proposed_value
        elif change.field == "human_anchor":
            if change.proposed_value != state.human_anchor:
                state.career_target = None
                state.career_hypotheses = []
            state.human_anchor = change.proposed_value
            state.current_goal = change.proposed_value
    state.original_intents.append(proposal.reviewed_input)
    _merge_human_facts(
        state,
        orient(proposal.reviewed_input),
        evidence_label="Human-approved Fog Bank re-orientation",
    )
    state.decisions.append(
        Decision(
            id=stable_id("decision", state.profile_id, idempotency_key),
            gate_id="fog-bank-reorientation",
            value=proposal.reviewed_input,
        )
    )
    state = propagate_temporal_changes(current, state)
    state = refresh_path_state(state)
    state.gates = _recompute_gates(state)
    state.projections = _build_projections(state)
    state.feedback.append(
        FeedbackEvent(
            id=stable_id("feedback", state.profile_id, idempotency_key),
            headline="You changed how the plan is oriented.",
            consequences=[change.reason for change in proposal.changes[:3]],
        )
    )
    state.processed_keys.append(idempotency_key)
    state.updated_at = utc_now()
    state.version += 1
    return derive_execution_state(state, previous=previous_execution, resolving_authority=Authority.HUMAN)


def reconstitute_state(current: CanonicalState) -> CanonicalState:
    current = reconstitute_governance(current)
    verify_derived_indexes(current)
    previous_execution = deepcopy(current.execution)
    state = refresh_path_state(evaluate_elapsed_freshness(current))
    state.gates = _recompute_gates(state)
    state.projections = _build_projections(state)
    return bind_gate_contracts(derive_execution_state(state, previous=previous_execution))


def _extract_transition_date(text: str) -> str | None:
    iso = re.search(r"\b(20\d{2})-(0[1-9]|1[0-2])-([0-2]\d|3[01])\b", text)
    if iso:
        try:
            return date.fromisoformat(iso.group(0)).isoformat()
        except ValueError:
            return None
    months = {
        name.lower(): index
        for index, name in enumerate(
            (
                "",
                "January",
                "February",
                "March",
                "April",
                "May",
                "June",
                "July",
                "August",
                "September",
                "October",
                "November",
                "December",
            )
        )
        if name
    }
    month_year = re.search(r"\b(" + "|".join(months) + r")\s+(20\d{2})\b", text, flags=re.IGNORECASE)
    if month_year:
        return date(int(month_year.group(2)), months[month_year.group(1).lower()], 1).isoformat()
    return None


def _describes_household_relocation(text: str) -> bool:
    return bool(re.search(r"\b(?:pcs|move|moving|relocat(?:e|ion|ing))\b", text, flags=re.IGNORECASE))


def _extract_career_target(text: str) -> str | None:
    match = re.search(
        r"\b(?:career target|target role|job target|change (?:my )?(?:career|role))\s*(?:is|to|:)\s*([^.!?\n]{3,120})",
        text,
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    target = match.group(1).strip()
    return target if resume_target_specificity(f"résumé ready for {target}") == "concrete" else None


def _clears_career_target(text: str) -> bool:
    lower = text.casefold()
    return any(
        term in lower
        for term in (
            "remove my target role",
            "clear my target role",
            "i don't have a target role",
            "i do not have a target role",
            "i haven't chosen the specific role",
            "i have not chosen the specific role",
            "target role is not named",
        )
    )


def _set_explicit_career_target(state: CanonicalState, target: str) -> None:
    state.career_target = target
    state.rejected_roles = [item for item in state.rejected_roles if item.casefold() != target.casefold()]
    selected = next(
        (item for item in state.career_hypotheses if item.title.casefold() == target.casefold()),
        None,
    )
    for hypothesis in state.career_hypotheses:
        if hypothesis.status == "accepted":
            hypothesis.status = "candidate"
    if selected is None:
        selected = CareerHypothesis(
            id=stable_id("career", state.profile_id, target.casefold()),
            title=target,
            rationale="This is the direction you explicitly chose to test.",
            evidence=["Your confirmed career target"],
            capability_matches=["Your explicitly confirmed direction"],
            possible_gaps=_role_gaps(target),
            questions_to_test=_role_questions(target),
            first_experiment=_role_first_experiment(target),
            next_step="Run the first bounded experiment and add what you learn.",
            status="accepted",
        )
        state.career_hypotheses.insert(0, selected)
    else:
        selected.status = "accepted"
    state.career_hypotheses = [
        selected,
        *(item for item in state.career_hypotheses if item.id != selected.id),
    ][:3]


def _has_income_education_conflict(text: str) -> bool:
    lower = text.lower()
    income = any(term in lower for term in ("immediate income", "need income", "job immediately", "work right away"))
    school = any(term in lower for term in ("full-time school", "school full time", "full-time education"))
    return income and school


def _fact_kind(statement: OrientedStatement) -> str:
    if statement.kind == "preference":
        return "preference"
    if statement.kind == "goal":
        return "goal"
    if statement.kind == "date":
        return "time_anchor"
    return "human_context"


def _merge_human_facts(
    state: CanonicalState,
    orientation: OrientationResult,
    *,
    evidence_label: str = "Confirmed transition statement",
    max_new_facts: int | None = None,
) -> list[str]:
    added: list[str] = []
    statements = [statement for statement in orientation.statements if statement.affected_slices]
    if max_new_facts is not None:
        priority = {"preference": 0, "goal": 0, "date": 0, "conflict": 0, "unknown": 1, "fact": 2}
        statements = [
            statement
            for _, statement in sorted(
                enumerate(statements),
                key=lambda item: (
                    priority[item[1].kind],
                    -len(item[1].affected_slices),
                    item[0],
                ),
            )[:max_new_facts]
        ]
    for statement in statements:
        fact_id = stable_id("fact", _fact_kind(statement), statement.text.casefold())
        if any(existing.id == fact_id for existing in state.facts):
            state.telemetry.duplicate_questions_avoided += 1
            continue
        evidence_id = stable_id("evidence", state.profile_id, statement.text.casefold())
        state.evidence.append(
            Evidence(
                id=evidence_id,
                label=evidence_label,
                authority=Authority.HUMAN,
                purpose="transition planning",
            )
        )
        state.facts.append(
            Fact(
                id=fact_id,
                statement=statement.text,
                value=statement.text,
                authority=Authority.HUMAN,
                evidence_ids=[evidence_id],
                affected_slices=statement.affected_slices,
                field_key=infer_fact_metadata(statement.text, statement.affected_slices, statement.kind)[0],
                freshness_class=infer_fact_metadata(statement.text, statement.affected_slices, statement.kind)[1],
            )
        )
        added.append(statement.text)
    return added


def apply_confirmed_input(
    current: CanonicalState,
    orientation: OrientationResult,
    *,
    idempotency_key: str,
) -> CanonicalState:
    if idempotency_key in current.processed_keys:
        return current
    state = deepcopy(current)
    previous_execution = deepcopy(current.execution)
    state.original_intents.append(orientation.reviewed_input)
    anchor_resolution = resolve_human_anchor(orientation)
    state.telemetry.anchor_candidates += anchor_resolution.candidate_count
    state.telemetry.selected_anchor_class = anchor_resolution.selected_class
    state.telemetry.anchor_selection_reason_code = anchor_resolution.reason_code
    if anchor_resolution.anchor and (not state.human_anchor or current.execution.state.value == "COMPLETE"):
        state.human_anchor = anchor_resolution.anchor
    detected_actor, detected_subject = detect_planning_parties(orientation.reviewed_input)
    if state.planning_actor == PlanningActor.UNKNOWN and detected_actor != PlanningActor.UNKNOWN:
        state.planning_actor = detected_actor
    if (
        state.military_state_subject == MilitaryStateSubject.UNKNOWN
        and detected_subject != MilitaryStateSubject.UNKNOWN
    ):
        state.military_state_subject = detected_subject
    state.service = state.service or detect_service(orientation.reviewed_input)
    detected_type = detect_separation_type(orientation.reviewed_input)
    if state.separation_type is None and detected_type in ("separation", "retirement"):
        state.separation_type = detected_type
    added = _merge_human_facts(state, orientation)
    extracted_date = _extract_transition_date(orientation.reviewed_input)
    if extracted_date:
        if (
            state.military_state_subject == MilitaryStateSubject.PLANNING_ACTOR_SPOUSE
            and _describes_household_relocation(orientation.reviewed_input)
        ):
            state.pcs_relocation_date = extracted_date
        elif (
            state.military_state_subject != MilitaryStateSubject.PLANNING_ACTOR_SPOUSE
            and state.lifecycle_position
            not in {
                LifecyclePosition.SEPARATED_WITHIN_LAST_YEAR,
                LifecyclePosition.SEPARATED_1_TO_5_YEARS,
                LifecyclePosition.SEPARATED_MORE_THAN_5_YEARS,
            }
        ):
            state.transition_date = extracted_date
    explicit_target = _extract_career_target(orientation.reviewed_input)
    if _clears_career_target(orientation.reviewed_input):
        state.career_target = None
        for hypothesis in state.career_hypotheses:
            if hypothesis.status == "accepted":
                hypothesis.status = "candidate"
        if anchor_domain(state.human_anchor) == "resume":
            state.human_anchor = "Make my résumé ready for a specific target"
    elif explicit_target:
        _set_explicit_career_target(state, explicit_target)

    if _has_income_education_conflict(orientation.reviewed_input):
        conflict = "Immediate income and full-time education overlap in the first transition period."
        if conflict not in state.conflicts:
            state.conflicts.append(conflict)

    state = propagate_temporal_changes(current, state)
    state = refresh_path_state(state)
    state.gates = _recompute_gates(state)
    state.projections = _build_projections(state)
    consequences = _consequences_for_input(state, orientation, extracted_date)
    headline = "Your plan has a clearer starting point." if added else "Your existing plan was reused."
    state.feedback.append(
        FeedbackEvent(
            id=stable_id("feedback", state.profile_id, idempotency_key),
            headline=headline,
            consequences=consequences,
        )
    )
    state.processed_keys.append(idempotency_key)
    state.updated_at = utc_now()
    state.version += 1
    state.telemetry.resume_target_specificity = resume_target_specificity(state.human_anchor or "")
    return derive_execution_state(
        state,
        previous=previous_execution,
        resolving_authority=Authority.HUMAN,
    )


def apply_artifact_input(
    current: CanonicalState,
    orientation: OrientationResult,
    *,
    idempotency_key: str,
) -> CanonicalState:
    """Apply a deliberately supplied artifact without a redundant confirmation.

    Selecting a file is the human authorization to use it for this decision.
    Only decision-relevant statements survive orientation; raw bytes, contact-only
    text, and the full extracted document are not persisted.
    """
    if idempotency_key in current.processed_keys:
        return current
    state = deepcopy(current)
    previous_execution = deepcopy(current.execution)
    state.original_intents.append("Shared a document to update my transition plan.")
    added = _merge_human_facts(
        state,
        orientation,
        evidence_label="Statement from a deliberately submitted artifact",
        max_new_facts=MAX_ARTIFACT_FACTS,
    )
    detected_actor, detected_subject = detect_planning_parties(orientation.reviewed_input)
    if state.planning_actor == PlanningActor.UNKNOWN and detected_actor != PlanningActor.UNKNOWN:
        state.planning_actor = detected_actor
    if (
        state.military_state_subject == MilitaryStateSubject.UNKNOWN
        and detected_subject != MilitaryStateSubject.UNKNOWN
    ):
        state.military_state_subject = detected_subject
    state.service = state.service or detect_service(orientation.reviewed_input)
    detected_type = detect_separation_type(orientation.reviewed_input)
    if state.separation_type is None and detected_type in ("separation", "retirement"):
        state.separation_type = detected_type
    extracted_date = _extract_transition_date(orientation.reviewed_input)
    if extracted_date:
        if (
            state.military_state_subject == MilitaryStateSubject.PLANNING_ACTOR_SPOUSE
            and _describes_household_relocation(orientation.reviewed_input)
        ):
            state.pcs_relocation_date = extracted_date
        elif (
            state.military_state_subject != MilitaryStateSubject.PLANNING_ACTOR_SPOUSE
            and state.lifecycle_position
            not in {
                LifecyclePosition.SEPARATED_WITHIN_LAST_YEAR,
                LifecyclePosition.SEPARATED_1_TO_5_YEARS,
                LifecyclePosition.SEPARATED_MORE_THAN_5_YEARS,
            }
        ):
            state.transition_date = extracted_date
    explicit_target = _extract_career_target(orientation.reviewed_input)
    if explicit_target:
        _set_explicit_career_target(state, explicit_target)
    if _has_income_education_conflict(orientation.reviewed_input):
        conflict = "Immediate income and full-time education overlap in the first transition period."
        if conflict not in state.conflicts:
            state.conflicts.append(conflict)

    state = propagate_temporal_changes(current, state)
    state = refresh_path_state(state)
    state.gates = _recompute_gates(state)
    state.projections = _build_projections(state)
    consequences = _consequences_for_input(state, orientation, extracted_date)
    state.feedback.append(
        FeedbackEvent(
            id=stable_id("feedback", state.profile_id, idempotency_key),
            headline="Your document changed what comes next." if added else "Your existing plan was reused.",
            consequences=consequences,
        )
    )
    state.processed_keys.append(idempotency_key)
    state.updated_at = utc_now()
    state.version += 1
    state.telemetry.resume_target_specificity = resume_target_specificity(state.human_anchor or "")
    return derive_execution_state(state, previous=previous_execution, resolving_authority=Authority.HUMAN)


def _recompute_gates(state: CanonicalState) -> list[Gate]:
    existing = {gate.id: gate for gate in state.gates}
    gates: list[Gate] = []
    if state.conflicts:
        gate = Gate(
            id="priority-first-six-months",
            title="Choose what must lead first",
            question="Which must govern your first six months after separation?",
            why="Income and full-time education both require the same time and attention.",
            state=GateState.CONFLICTED,
            surface=SurfaceType.CONFLICT,
            affected_slices=[SliceName.CAREER, SliceName.EDUCATION],
            authority_required=Authority.HUMAN,
            options=["Immediate income", "Full-time education", "A staged combination"],
            value_score=100,
        )
        gates.append(_preserve_resolution(gate, existing))

    domain = anchor_domain(state.human_anchor)
    if not state.human_anchor:
        gate = Gate(
            id="transition-human-anchor",
            title="Choose the outcome that should lead",
            question="What should this transition plan help you accomplish next?",
            why="One outcome keeps useful information from turning into unrelated work.",
            state=GateState.UNKNOWN,
            surface=SurfaceType.CHOICE,
            affected_slices=ALL_SLICES,
            authority_required=Authority.HUMAN,
            options=list(ANCHOR_OPTIONS),
            value_score=100,
        )
        gates.append(_preserve_resolution(gate, existing))
    elif domain == "resume" and state.active_tasks and state.active_tasks[0].title.startswith("Name the role"):
        gate = Gate(
            id="resume-target-role",
            title="Bound the résumé work",
            question="What role or specific use should this résumé support?",
            why="The target determines which evidence matters and keeps unrelated career ideas latent.",
            state=GateState.PARTIAL,
            surface=SurfaceType.TEXT,
            affected_slices=[SliceName.RESUME, SliceName.CAREER],
            authority_required=Authority.HUMAN,
            value_score=99,
        )
        gates.append(_preserve_resolution(gate, existing))
    elif (
        domain != "resume"
        and not state.transition_date
        and state.military_state_subject != MilitaryStateSubject.PLANNING_ACTOR_SPOUSE
        and state.lifecycle_position
        in {
            LifecyclePosition.UNKNOWN,
            LifecyclePosition.LEAVING_WITHIN_12_MONTHS,
        }
    ):
        gate = Gate(
            id="planned-transition-date",
            title="Anchor the timing",
            question="When do you expect to leave active service?",
            why="One date clarifies application, education, relocation, and résumé timing.",
            state=GateState.UNKNOWN,
            surface=SurfaceType.DATE,
            affected_slices=ALL_SLICES,
            authority_required=Authority.HUMAN,
            value_score=95,
        )
        gates.append(_preserve_resolution(gate, existing))

    if (
        domain not in (None, "resume")
        and state.transition_date
        and not state.service
        and state.military_state_subject != MilitaryStateSubject.PLANNING_ACTOR_SPOUSE
    ):
        gate = Gate(
            id="service-path-identity",
            title="Use the right service path",
            question="Which service transition path applies to you?",
            why="The underlying decision stays common, but timing and terminology differ by service.",
            state=GateState.UNKNOWN,
            surface=SurfaceType.CHOICE,
            affected_slices=ALL_SLICES,
            authority_required=Authority.HUMAN,
            options=["Army", "Navy", "Marine Corps", "Air Force", "Space Force", "Coast Guard"],
            value_score=90,
        )
        gates.append(_preserve_resolution(gate, existing))

    preferences = [
        fact
        for fact in state.facts
        if fact_is_usable(fact)
        and any(
            term in fact.statement.lower()
            for term in (
                "want",
                "prefer",
                "hate",
                "won't",
                "will not",
                "don't",
                "do not",
                "remote",
                "hybrid",
                "schedule",
                "travel",
                "commute",
                "shift work",
            )
        )
    ]
    if domain == "employment" and not preferences:
        gate = Gate(
            id="next-work-preferences",
            title="Shape the work around you",
            question="What would you like more or less of in your next work?",
            why=(
                "Your preferences prevent the system from recommending the closest title "
                "instead of the right direction."
            ),
            state=GateState.PARTIAL if state.current_goal else GateState.UNKNOWN,
            surface=SurfaceType.TEXT,
            affected_slices=[SliceName.CAREER, SliceName.EDUCATION, SliceName.LOCATION],
            authority_required=Authority.HUMAN,
            value_score=85,
        )
        gates.append(_preserve_resolution(gate, existing))

    if domain == "employment" and preferences and not any(h.status == "accepted" for h in state.career_hypotheses):
        gate = Gate(
            id="career-direction",
            title="Choose a direction to test",
            question="Which direction is worth testing first?",
            why=(
                "A direction lets the system compare real roles, evidence, and gaps instead "
                "of guessing from a military title."
            ),
            state=GateState.PARTIAL if state.career_hypotheses else GateState.UNKNOWN,
            surface=SurfaceType.COMPARE if state.career_hypotheses else SurfaceType.TEXT,
            affected_slices=[SliceName.CAREER, SliceName.EDUCATION, SliceName.RESUME],
            authority_required=Authority.HUMAN,
            authorized_scope=["career:hypothesis-nomination", "career:hypothesis-selection"],
            authority_set=[Authority.HUMAN, Authority.BOUNDED_AGENT],
            options=[h.title for h in state.career_hypotheses if h.status == "candidate"],
            value_score=75,
        )
        gates.append(_preserve_resolution(gate, existing))

    if domain == "education" and not any(
        any(term in fact.statement.casefold() for term in ("degree", "program", "school", "credential", "training"))
        for fact in state.facts
    ):
        gate = Gate(
            id="education-outcome",
            title="Define the education outcome",
            question="What should education or training make possible after service?",
            why="The outcome is needed before comparing programs, timing, or funding routes.",
            state=GateState.PARTIAL,
            surface=SurfaceType.TEXT,
            affected_slices=[SliceName.EDUCATION],
            authority_required=Authority.HUMAN,
            value_score=80,
        )
        gates.append(_preserve_resolution(gate, existing))

    if domain == "location" and not any(SliceName.LOCATION in fact.affected_slices for fact in state.facts):
        gate = Gate(
            id="location-priority",
            title="Define the location decision",
            question="What location condition must the next plan respect?",
            why="A single governing condition is enough to evaluate the next location decision.",
            state=GateState.PARTIAL,
            surface=SurfaceType.TEXT,
            affected_slices=[SliceName.LOCATION],
            authority_required=Authority.HUMAN,
            value_score=80,
        )
        gates.append(_preserve_resolution(gate, existing))

    separated_lifecycle = state.lifecycle_position in {
        LifecyclePosition.SEPARATED_WITHIN_LAST_YEAR,
        LifecyclePosition.SEPARATED_1_TO_5_YEARS,
        LifecyclePosition.SEPARATED_MORE_THAN_5_YEARS,
    }
    if domain == "undecided" and state.service and (state.transition_date or separated_lifecycle):
        gate = Gate(
            id="transition-direction",
            title="Choose one direction to examine",
            question="Which direction is worth examining first?",
            why="This is exploration, not a permanent commitment, and it keeps the next step bounded.",
            state=GateState.PARTIAL,
            surface=SurfaceType.CHOICE,
            affected_slices=[SliceName.CAREER, SliceName.EDUCATION, SliceName.LOCATION],
            authority_required=Authority.HUMAN,
            options=["Civilian work", "Education or training", "Location and family fit"],
            value_score=80,
        )
        gates.append(_preserve_resolution(gate, existing))

    if domain != "resume" and state.human_anchor and state.active_tasks and not any(
        gate.state not in (GateState.YES, GateState.NO) for gate in gates
    ):
        completed_gate_ids = {decision.gate_id for decision in state.decisions}
        for task in state.active_tasks:
            task_gate_id = path_task_gate_id(task)
            if task_gate_id in completed_gate_ids:
                continue
            task_title = task.title.strip().rstrip(".")
            question = (
                task.title.strip()
                if task.title.strip().endswith("?")
                else f"What have you learned—or what still needs to be tested—about: {task_title}?"
            )
            gate = Gate(
                id=task_gate_id,
                title="Resolve the next material uncertainty",
                question=question,
                why=task.reason,
                state=GateState.PARTIAL,
                surface=SurfaceType.TEXT,
                affected_slices=task.affected_slices or ALL_SLICES,
                authority_required=Authority.HUMAN,
                authorized_scope=["path:task-evidence"],
                authority_set=[Authority.HUMAN],
                value_score=60,
            )
            gates.append(_preserve_resolution(gate, existing))
            break
    return sorted(gates, key=lambda item: item.value_score, reverse=True)


def _preserve_resolution(gate: Gate, existing: dict[str, Gate]) -> Gate:
    previous = existing.get(gate.id)
    if previous:
        gate.updated_at = previous.updated_at
        if previous.state in (GateState.YES, GateState.NO):
            gate.state = previous.state
            gate.resolved_value = previous.resolved_value
    return gate


def active_gate(state: CanonicalState) -> Gate | None:
    unresolved = [gate for gate in state.gates if gate.state not in (GateState.YES, GateState.NO)]
    return max(unresolved, key=lambda item: item.value_score, default=None)


def apply_decision(
    current: CanonicalState,
    *,
    gate_id: str,
    value: str,
    idempotency_key: str,
    source_text: str | None = None,
) -> CanonicalState:
    if idempotency_key in current.processed_keys:
        return current
    state = deepcopy(current)
    previous_execution = deepcopy(current.execution)
    matching = next((gate for gate in state.gates if gate.id == gate_id), None)
    if matching is None:
        raise ValueError("That decision is no longer active. Refresh to continue from current state.")
    if matching.state in (GateState.YES, GateState.NO):
        raise ValueError("That decision is already resolved.")

    normalized = value.strip()
    previous_date = state.transition_date
    collateral_added: list[str] = []
    if source_text and source_text.strip().casefold() != normalized.casefold():
        source_orientation = orient(source_text, context=current)
        if source_orientation.conflicts:
            raise ValueError(source_orientation.clarification_question or "Resolve the conflicting information first.")
        collateral_added = _merge_human_facts(
            state,
            source_orientation,
            evidence_label="Direct answer in the active conversation",
        )
    if gate_id == "planned-transition-date":
        parsed = _extract_transition_date(normalized)
        if parsed is None:
            raise ValueError("Enter a valid transition date.")
        state.transition_date = parsed
        normalized = parsed
    elif gate_id == "transition-human-anchor":
        if normalized not in ANCHOR_OPTIONS:
            raise ValueError("Choose one of the listed transition outcomes.")
        state.human_anchor = ANCHOR_OPTIONS[normalized]
        if source_text:
            source_anchor = resolve_human_anchor(orient(source_text, context=current)).anchor
            if source_anchor:
                state.human_anchor = source_anchor
        state.current_goal = state.human_anchor
    elif gate_id == "service-path-identity":
        state.service = normalize_service_choice(normalized)
    elif gate_id == "resume-target-role":
        if resume_target_specificity(f"résumé ready for {normalized}") != "concrete":
            raise ValueError("Name a specific role or provide a specific job posting.")
        state.human_anchor = f"Make my résumé submission-ready for {normalized}"
        state.current_goal = state.human_anchor
    elif gate_id == "transition-direction":
        state.human_anchor = {
            "Civilian work": "Find civilian work",
            "Education or training": "Choose an education or training path",
            "Location and family fit": "Make a post-service location decision",
        }.get(normalized)
        if state.human_anchor is None:
            raise ValueError("Choose one of the listed directions.")
        if normalized == "Civilian work" and source_text:
            source_anchor = resolve_human_anchor(orient(source_text, context=current)).anchor
            if source_anchor and anchor_domain(source_anchor) == "employment":
                state.human_anchor = source_anchor
        state.current_goal = state.human_anchor
    elif gate_id == "next-work-preferences":
        orientation = orient(normalized)
        _merge_human_facts(state, orientation)
    elif gate_id in ("education-outcome", "location-priority"):
        orientation = orient(normalized)
        _merge_human_facts(state, orientation)
    elif gate_id == "priority-first-six-months":
        state.conflicts = [item for item in state.conflicts if "Immediate income and full-time education" not in item]
    elif gate_id == "career-direction":
        rejecting = normalized.casefold().startswith("reject:")
        chosen = normalized.split(":", 1)[1].strip() if ":" in normalized else normalized
        matched = False
        for hypothesis in state.career_hypotheses:
            if hypothesis.title.casefold() != chosen.casefold():
                continue
            matched = True
            if rejecting:
                hypothesis.status = "rejected"
                if hypothesis.title not in state.rejected_roles:
                    state.rejected_roles.append(hypothesis.title)
            else:
                hypothesis.status = "accepted"
                state.career_target = hypothesis.title
        if not matched:
            raise ValueError("That direction is no longer available. Refresh to see current options.")
        normalized = ("Not for me: " if rejecting else "Explore: ") + chosen
    elif gate_id.startswith("path-task_"):
        orientation = orient(normalized, context=current)
        for statement in orientation.statements:
            if not statement.affected_slices:
                statement.affected_slices = list(matching.affected_slices)
        _merge_human_facts(
            state,
            orientation,
            evidence_label="Direct answer to the current path question",
        )

    rejecting_career = gate_id == "career-direction" and normalized.startswith("Not for me:")
    matching.state = GateState.PARTIAL if rejecting_career else GateState.YES
    matching.resolved_value = normalized
    matching.updated_at = utc_now()
    state.decisions.append(
        Decision(
            id=stable_id("decision", state.profile_id, gate_id, idempotency_key),
            gate_id=gate_id,
            value=normalized,
        )
    )
    consequences = _decision_consequences(gate_id, previous_date, state.transition_date, normalized)
    if collateral_added:
        consequences.append(
            "Carried forward the other relevant details in your answer so they do not need to be asked again."
        )
    state.feedback.append(
        FeedbackEvent(
            id=stable_id("feedback", state.profile_id, idempotency_key),
            headline="That decision changed what comes next.",
            consequences=consequences,
        )
    )
    if rejecting_career:
        state.career_hypotheses = [item for item in state.career_hypotheses if item.status != "rejected"]
        replacements = deterministic_hypotheses(" ".join(fact.statement for fact in state.facts), state.rejected_roles)
        known = {item.title for item in state.career_hypotheses}
        state.career_hypotheses.extend(item for item in replacements if item.title not in known)
        state.career_hypotheses = state.career_hypotheses[:3]
    state = propagate_temporal_changes(current, state)
    state = refresh_path_state(state)
    state.gates = _recompute_gates(state)
    state.projections = _build_projections(state)
    state.processed_keys.append(idempotency_key)
    state.updated_at = utc_now()
    state.version += 1
    state.telemetry.resume_target_specificity = resume_target_specificity(state.human_anchor or "")
    return derive_execution_state(state, previous=previous_execution, resolving_authority=Authority.HUMAN)


def career_resolution_required(state: CanonicalState) -> bool:
    gate = active_gate(state)
    return bool(
        anchor_domain(state.human_anchor) == "employment"
        and gate
        and gate.id == "career-direction"
        and not any(item.status == "candidate" for item in state.career_hypotheses)
    )


def recompute_state(state: CanonicalState) -> CanonicalState:
    """Recompute deterministic path projections without persistence or model work."""
    previous_execution = deepcopy(state.execution)
    state = refresh_path_state(state)
    state.gates = _recompute_gates(state)
    state.projections = _build_projections(state)
    state.telemetry.resume_target_specificity = resume_target_specificity(state.human_anchor or "")
    return derive_execution_state(state, previous=previous_execution)


def apply_revalidation(
    current: CanonicalState,
    *,
    impact_id: str,
    action: str,
    value: str | None,
    idempotency_key: str,
) -> tuple[CanonicalState, bool]:
    state, changed = apply_revalidation_delta(
        current,
        impact_id=impact_id,
        action=action,
        value=value,
        idempotency_key=idempotency_key,
    )
    if not changed:
        return state, False
    previous_execution = deepcopy(current.execution)
    state = recompute_state(state)
    state = derive_execution_state(state, previous=previous_execution, resolving_authority=Authority.HUMAN)
    return state, True


def _build_projections(state: CanonicalState | None) -> list[SliceProjection]:
    if state is None:
        return [
            SliceProjection(name=SliceName.CAREER, label="Work", summary="Ready when you are."),
            SliceProjection(name=SliceName.EDUCATION, label="Education", summary="Ready when it matters."),
            SliceProjection(name=SliceName.LOCATION, label="Location", summary="Ready when it matters."),
            SliceProjection(name=SliceName.RESUME, label="Your story", summary="Ready when you share it."),
        ]
    projections: list[SliceProjection] = []
    for name, label in (
        (SliceName.CAREER, "Work"),
        (SliceName.EDUCATION, "Education"),
        (SliceName.LOCATION, "Location"),
        (SliceName.RESUME, "Your story"),
    ):
        facts = [fact for fact in state.facts if name in fact.affected_slices]
        unresolved = [
            gate
            for gate in state.gates
            if name in gate.affected_slices and gate.state not in (GateState.YES, GateState.NO)
        ]
        if any(gate.state == GateState.CONFLICTED for gate in unresolved):
            status = GateState.CONFLICTED
            summary = "A priority needs your decision."
        elif name == SliceName.CAREER and any(item.status == "accepted" for item in state.career_hypotheses):
            accepted = next(item for item in state.career_hypotheses if item.status == "accepted")
            status = GateState.YES
            summary = f"Exploring {accepted.title}."
        elif name == SliceName.CAREER and state.career_hypotheses:
            status = GateState.PARTIAL
            summary = "Civilian directions are ready to compare."
        elif facts:
            status = GateState.PARTIAL if unresolved else GateState.YES
            summary = {
                SliceName.CAREER: "Your work preferences are shaping the search.",
                SliceName.EDUCATION: "Credential timing is included in the plan.",
                SliceName.LOCATION: "Your location constraints are included.",
                SliceName.RESUME: "Your experience is ready to translate.",
            }[name]
        else:
            status = GateState.UNKNOWN
            summary = "Not affecting this decision."
        projections.append(SliceProjection(name=name, label=label, status=status, summary=summary))
    return projections


def _consequences_for_input(
    state: CanonicalState,
    orientation: OrientationResult,
    transition_date: str | None,
) -> list[str]:
    consequences = [f"Connected your input to {_slice_label(item)}." for item in orientation.affected_slices]
    if transition_date:
        consequences.append("Anchored application, education, relocation, and résumé timing to one date.")
    if state.conflicts:
        consequences.append("Surfaced a priority conflict instead of silently averaging it.")
    if not consequences:
        consequences.append("Preserved your words and reduced the next question to one clarification.")
    return consequences[:4]


def _decision_consequences(
    gate_id: str,
    previous_date: str | None,
    current_date: str | None,
    decision_value: str,
) -> list[str]:
    if gate_id == "planned-transition-date":
        if previous_date and previous_date != current_date:
            return [
                "Reopened only the timing-sensitive work.",
                "Preserved preferences and decisions that the date did not change.",
            ]
        return [
            "Clarified when to begin applications.",
            "Clarified whether education can finish before separation.",
            "Clarified when relocation and résumé work become urgent.",
        ]
    if gate_id == "priority-first-six-months":
        return [
            "Resolved the conflict across work and education.",
            "Made the selected priority govern the first six months.",
        ]
    if gate_id == "career-direction":
        if decision_value.startswith("Not for me:"):
            return ["Removed that direction from future suggestions.", "Kept the remaining options in view."]
        return ["Kept one direction in focus.", "Left the other directions available for later review."]
    if gate_id == "transition-human-anchor":
        if decision_value == "I am still deciding":
            return [
                "Kept work, education, and location open.",
                "Put one clear direction choice in front of you next.",
            ]
        return [f"Made {decision_value.lower()} the focus of the plan."]
    if gate_id == "transition-direction":
        return [
            "Put the direction you chose first for exploration.",
            "Kept the other directions available without treating this as permanent.",
        ]
    if gate_id == "next-work-preferences":
        return [
            "Used this preference to shape the directions you see next.",
            "Did not require you to explain why the condition matters.",
        ]
    if gate_id == "resume-target-role":
        return [f"Bound the résumé work to {decision_value}."]
    if gate_id == "education-outcome":
        return ["Made the education outcome—not the program list—the next planning constraint."]
    if gate_id == "location-priority":
        return ["Made this location condition part of the active decision."]
    if gate_id.startswith("path-task_"):
        return [
            "Used what you learned to retire this uncertainty.",
            "Recomputed the next question from the updated plan.",
        ]
    return [
        "Used that answer to determine the next useful question.",
    ]


def deterministic_hypotheses(text: str, rejected: list[str]) -> list[CareerHypothesis]:
    lower = text.lower()
    families: list[tuple[str, str, list[str]]] = []
    if any(
        term in lower
        for term in ("build a company", "start a company", "startup", "founder", "build something")
    ):
        families.extend(
            [
                (
                    "Veteran-focused AI product builder",
                    "Tests a product-building route around the veteran problem and impact you named.",
                    ["O*NET 15-1252.00", "U.S. Small Business Administration business guide"],
                ),
                (
                    "AI product management",
                    "Tests product discovery and delivery inside an existing organization before or "
                    "alongside a venture.",
                    ["O*NET 13-1082.00", "BLS Occupational Outlook Handbook"],
                ),
                (
                    "Veteran technology program lead",
                    "Tests mission-driven program ownership using your technical and military-connected context.",
                    ["O*NET 13-1082.00", "BLS Occupational Outlook Handbook"],
                ),
            ]
        )
    elif any(term in lower for term in ("intelligence", "analysis", "brief", "research")):
        families.extend(
            [
                (
                    "Operations Research Analyst",
                    "Uses structured analysis and decision support without requiring a defense setting.",
                    ["O*NET 15-2031.00", "BLS Occupational Outlook Handbook"],
                ),
                (
                    "Business Intelligence Analyst",
                    "Translates complex information into decisions for civilian organizations.",
                    ["O*NET 15-2051.01"],
                ),
                (
                    "Program Management Analyst",
                    "Combines planning, stakeholder coordination, and executive communication.",
                    ["O*NET 13-1111.00"],
                ),
            ]
        )
    elif any(term in lower for term in ("logistics", "supply", "warehouse", "transport")):
        families.extend(
            [
                ("Logistics Analyst", "Builds on supply, movement, and readiness coordination.", ["O*NET 13-1081.02"]),
                (
                    "Supply Chain Planner",
                    "Applies operational planning to civilian inventory and distribution.",
                    ["O*NET 13-1081.00"],
                ),
                ("Operations Manager", "Transfers team, schedule, and resource responsibility.", ["O*NET 11-1021.00"]),
            ]
        )
    elif any(term in lower for term in ("maintenance", "mechanic", "equipment", "aviation")):
        families.extend(
            [
                (
                    "Maintenance Planner",
                    "Uses readiness, scheduling, and equipment history to reduce downtime.",
                    ["O*NET 49-1011.00"],
                ),
                (
                    "Field Service Manager",
                    "Transfers technical leadership and customer-facing troubleshooting.",
                    ["O*NET 49-1011.00"],
                ),
                (
                    "Quality Assurance Specialist",
                    "Applies inspection, procedure, and risk-control experience.",
                    ["O*NET 13-1199.00"],
                ),
            ]
        )
    else:
        families.extend(
            [
                (
                    "Operations Coordinator",
                    "Tests how planning, execution, and cross-team coordination translate.",
                    ["O*NET 13-1082.00"],
                ),
                (
                    "Project Coordinator",
                    "Tests schedule, stakeholder, and delivery responsibility in a new setting.",
                    ["O*NET 13-1082.00"],
                ),
                (
                    "Customer Success Specialist",
                    "Tests coaching, problem-solving, and relationship skills outside defense.",
                    ["O*NET 13-1161.00"],
                ),
            ]
        )
    return [
        CareerHypothesis(
            id=stable_id("career", title),
            title=title,
            rationale=rationale,
            evidence=evidence,
            capability_matches=_role_capabilities(title),
            possible_gaps=_role_gaps(title),
            questions_to_test=_role_questions(title),
            first_experiment=_role_first_experiment(title),
            next_step="Run the first bounded experiment and add what you learn.",
        )
        for title, rationale, evidence in families
        if title not in rejected
    ][:3]


def _role_capabilities(title: str) -> list[str]:
    lower = title.casefold()
    if any(term in lower for term in ("maintenance", "field service", "quality")):
        return ["Operational scheduling", "Inspection and risk control", "Team coordination"]
    if any(term in lower for term in ("analyst", "intelligence", "research")):
        return ["Structured analysis", "Decision support", "Executive communication"]
    if any(term in lower for term in ("logistics", "supply", "operations")):
        return ["Resource planning", "Cross-team coordination", "Operational execution"]
    return ["Planning", "Stakeholder coordination", "Problem solving"]


def _role_gaps(title: str) -> list[str]:
    lower = title.casefold()
    if any(term in lower for term in ("founder", "business principal", "product builder")):
        return [
            "A specific user problem worth owning",
            "Evidence that a small useful solution changes something for that user",
        ]
    if "maintenance" in lower or "field service" in lower:
        return ["Civilian maintenance-system terminology", "Evidence from comparable job postings"]
    if "quality" in lower:
        return ["Industry-specific quality standards", "Civilian examples with measurable outcomes"]
    if "analyst" in lower:
        return ["Civilian data-tool evidence", "Portfolio examples without protected information"]
    return ["Civilian job-title calibration", "Evidence matched to a real posting"]


def _role_questions(title: str) -> list[str]:
    return [
        f"What evidence would confirm or change this assumption: {gap}?"
        for gap in _role_gaps(title)[:3]
    ]


def _role_first_experiment(title: str) -> str:
    first_gap = _role_gaps(title)[0]
    return (
        f"Choose the smallest real example, conversation, work sample, or comparison that could test: "
        f"{first_gap}. Capture what the evidence confirms, changes, or leaves unanswered."
    )


def apply_hypotheses(state: CanonicalState, hypotheses: list[CareerHypothesis]) -> CanonicalState:
    updated = deepcopy(state)
    accepted = [item for item in updated.career_hypotheses if item.status == "accepted"]
    updated.career_hypotheses = accepted + hypotheses
    updated.gates = _recompute_gates(updated)
    updated.projections = _build_projections(updated)
    return bind_gate_contracts(updated)


def transition_window(separation_date: str) -> dict[str, str]:
    parsed = date.fromisoformat(separation_date)
    return {
        "resume_ready_by": (parsed - timedelta(days=180)).isoformat(),
        "applications_begin_by": (parsed - timedelta(days=150)).isoformat(),
        "relocation_decision_by": (parsed - timedelta(days=120)).isoformat(),
        "separation_date": parsed.isoformat(),
    }


def state_age_seconds(state: CanonicalState) -> int:
    return max(0, int((datetime.now(UTC) - state.updated_at).total_seconds()))
