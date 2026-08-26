from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from dataclasses import replace
from pathlib import Path
from typing import Annotated, Any, cast

from fastapi import Cookie, FastAPI, File, Form, HTTPException, Request, Response, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from military_slices.acquisition import build_acquisition_horizon, evaluate_acquisition
from military_slices.agent_runtime import Resolver, ResolverResult
from military_slices.artifacts import ArtifactError, extract_artifact, multimodal_extract
from military_slices.control import create_what_if, history_entry, lens_projections, path_progress, promote_what_if
from military_slices.domain_pack import installed_domain_pack_ref
from military_slices.engine import (
    active_gate,
    apply_artifact_input,
    apply_confirmed_input,
    apply_decision,
    apply_fog_bank_reorientation,
    apply_hypotheses,
    apply_revalidation,
    apply_starting_vector,
    career_resolution_required,
    examine_fog_bank,
    orient,
    reconstitute_state,
)
from military_slices.governance import (
    AuthorityGovernor,
    GovernanceError,
    bind_gate_contracts,
    external_effects_enabled,
    probe_execution_enabled,
    resolver_nomination_ref,
    validate_resolver_nomination,
)
from military_slices.models import (
    AcquisitionRequest,
    ActorProvenance,
    Authority,
    ConfirmRequest,
    DecisionRequest,
    FogBankAcceptRequest,
    FogBankRequest,
    GateState,
    OrientRequest,
    ResolverTransitionProposal,
    RevalidationRequest,
    SliceName,
    StartingVectorRequest,
    StateEnvelope,
    WhatIfPromotionRequest,
    WhatIfRequest,
)
from military_slices.path_runtime import PACK_VERSION
from military_slices.security import (
    LocalRateLimiter,
    TokenError,
    issue_fog_bank,
    issue_orientation,
    issue_session,
    issue_what_if,
    verify_fog_bank,
    verify_orientation,
    verify_session,
    verify_what_if,
)
from military_slices.store import FirestoreStore, MemoryStore, StateStore, VersionConflictError
from military_slices.temporal import changed_fields, current_impact

LOGGER = logging.getLogger("military_slices")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(message)s")

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
COOKIE_NAME = "military_slices_session"


def _make_store() -> StateStore:
    if os.getenv("MILITARY_SLICES_STORE", "memory") == "firestore":
        return FirestoreStore(project=os.getenv("GOOGLE_CLOUD_PROJECT"))
    return MemoryStore()


def create_app(*, store: StateStore | None = None, resolver: Resolver | None = None) -> FastAPI:
    application = FastAPI(
        title="Military SLICES",
        version="0.1.0",
        docs_url=None if os.getenv("MILITARY_SLICES_ENV") == "production" else "/docs",
        redoc_url=None,
    )
    application.state.store = store or _make_store()
    application.state.resolver = resolver or Resolver()
    application.state.limiter = LocalRateLimiter()
    application.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @application.middleware("http")
    async def security_headers(request: Request, call_next: Any) -> Response:
        response = cast(Response, await call_next(request))
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
            "connect-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'"
        )
        return response

    @application.exception_handler(VersionConflictError)
    async def version_conflict(_: Request, exc: VersionConflictError) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @application.exception_handler(GovernanceError)
    async def governance_conflict(_: Request, exc: GovernanceError) -> JSONResponse:
        LOGGER.warning("governance_block reason=%s", str(exc)[:240])
        return JSONResponse(
            status_code=409,
            content={"detail": "This plan needs governed revalidation before that change can continue."},
        )

    @application.get("/api/health")
    @application.get("/healthz")
    async def health() -> dict[str, str]:
        pack = installed_domain_pack_ref()
        return {
            "status": "ok",
            "service": "military-slices",
            "model": os.getenv("MILITARY_SLICES_MODEL", "gemini-3.7-flash"),
            "agent_framework": "google-adk",
            "transition_pack": PACK_VERSION,
            "domain_pack_hash": pack.content_hash,
            "domain_pack_status": pack.status.value,
            "external_effects": "disabled" if not external_effects_enabled() else "enabled",
            "autonomous_probe": "disabled" if not probe_execution_enabled() else "enabled",
        }

    @application.get("/api/state", response_model=StateEnvelope)
    async def get_state(
        response: Response,
        military_slices_session: Annotated[str | None, Cookie()] = None,
    ) -> StateEnvelope:
        profile_id = _profile(response, military_slices_session)
        state = reconstitute_state(application.state.store.get(profile_id))
        return _envelope(state)

    @application.get("/api/lenses")
    async def lenses(
        response: Response,
        military_slices_session: Annotated[str | None, Cookie()] = None,
    ) -> dict[str, Any]:
        profile_id = _profile(response, military_slices_session)
        state = reconstitute_state(application.state.store.get(profile_id))
        return {"version": state.version, "lenses": [item.model_dump(mode="json") for item in lens_projections(state)]}

    @application.get("/api/lenses/{slice_name}")
    async def lens_detail(
        slice_name: SliceName,
        response: Response,
        military_slices_session: Annotated[str | None, Cookie()] = None,
    ) -> dict[str, Any]:
        profile_id = _profile(response, military_slices_session)
        state = reconstitute_state(application.state.store.get(profile_id))
        lens = next(item for item in lens_projections(state) if item.name == slice_name)
        return {"version": state.version, "lens": lens.model_dump(mode="json")}

    @application.get("/api/history")
    async def history(
        response: Response,
        military_slices_session: Annotated[str | None, Cookie()] = None,
    ) -> dict[str, Any]:
        profile_id = _profile(response, military_slices_session)
        states = application.state.store.history(profile_id)
        current_version = states[-1].version
        return {
            "category": "historical",
            "current_version": current_version,
            "entries": [
                history_entry(state, current=state.version == current_version).model_dump(mode="json")
                for state in states
            ],
        }

    @application.get("/api/history/{version}")
    async def history_version(
        version: int,
        response: Response,
        military_slices_session: Annotated[str | None, Cookie()] = None,
    ) -> dict[str, Any]:
        profile_id = _profile(response, military_slices_session)
        state = application.state.store.get_version(profile_id, version)
        if state is None:
            raise HTTPException(status_code=404, detail="That earlier version is not available.")
        return {
            "category": "historical",
            "entry": history_entry(state).model_dump(mode="json"),
            "progress": path_progress(state).model_dump(mode="json"),
            "lenses": [item.model_dump(mode="json") for item in lens_projections(state)],
        }

    @application.post("/api/what-if")
    async def what_if(
        payload: WhatIfRequest,
        request: Request,
        response: Response,
        military_slices_session: Annotated[str | None, Cookie()] = None,
    ) -> dict[str, Any]:
        profile_id = _profile(response, military_slices_session)
        _rate_limit(application, profile_id)
        current = application.state.store.get(profile_id)
        source_version = current.version if payload.source_version is None else payload.source_version
        source = application.state.store.get_version(profile_id, source_version)
        if source is None:
            raise HTTPException(status_code=404, detail="That source version is not available.")
        try:
            branch = create_what_if(source, payload.text)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        branch.token = issue_what_if(
            profile_id=profile_id,
            source_version=branch.source_version,
            modification_kind=branch.modification_kind,
            modification_value=branch.modification_value,
            statement=branch.statement,
        )
        _event(
            "what_if_created",
            profile_id,
            request,
            source_version=source_version,
            modification=branch.modification_kind,
            model_calls=0,
            production_mutations=0,
        )
        return branch.model_dump(mode="json")

    @application.post("/api/what-if/promote", response_model=StateEnvelope)
    async def promote_branch(
        payload: WhatIfPromotionRequest,
        request: Request,
        response: Response,
        military_slices_session: Annotated[str | None, Cookie()] = None,
    ) -> StateEnvelope:
        profile_id = _profile(response, military_slices_session)
        _rate_limit(application, profile_id)
        try:
            token_payload = verify_what_if(payload.token, profile_id=profile_id)
        except TokenError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        current = reconstitute_state(application.state.store.get(profile_id))
        if payload.idempotency_key in current.processed_keys:
            return _envelope(current)
        if current.version != payload.expected_version:
            raise VersionConflictError(
                "Your plan changed after this exploration. Explore it again from the current plan."
            )
        source = application.state.store.get_version(profile_id, int(token_payload["source_version"]))
        if source is None:
            raise HTTPException(status_code=404, detail="The source version for that exploration is unavailable.")
        try:
            branch = create_what_if(source, str(token_payload["statement"]))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if (
            branch.modification_kind != token_payload["modification_kind"]
            or branch.modification_value != token_payload["modification_value"]
        ):
            raise HTTPException(status_code=400, detail="That hypothetical branch failed integrity validation.")
        updated = promote_what_if(current, branch, idempotency_key=payload.idempotency_key)
        updated, agent_result = await _resolve_current_gate(application, updated)
        updated = _record_governed_mutation(
            current=current,
            updated=updated,
            profile_id=profile_id,
            idempotency_key=payload.idempotency_key,
            mutation_kind="what_if_promotion",
            dependency_refs=[
                f"hypothetical:{branch.id}",
                f"canonical-version:{branch.source_version}",
                *_agent_dependency_refs(agent_result),
            ],
        )
        saved = application.state.store.save_governed(updated, expected_version=current.version)
        _event(
            "what_if_promoted",
            profile_id,
            request,
            source_version=branch.source_version,
            version=saved.version,
            modification=branch.modification_kind,
            agent_provider=agent_result.provider if agent_result else "not-required",
            **_temporal_delta(current, saved),
        )
        return _envelope(saved, agent_run=_agent_run(agent_result))

    @application.post("/api/orient")
    async def orientation(
        payload: OrientRequest,
        request: Request,
        response: Response,
        military_slices_session: Annotated[str | None, Cookie()] = None,
    ) -> dict[str, Any]:
        profile_id = _profile(response, military_slices_session)
        _rate_limit(application, profile_id)
        started = time.perf_counter()
        current = reconstitute_state(application.state.store.get(profile_id))
        result = orient(payload.text, context=current if current.starting_vector_complete else None)
        result.token = issue_orientation(result.reviewed_input)
        _event(
            "orientation",
            profile_id,
            request,
            latency_ms=int((time.perf_counter() - started) * 1000),
            input_bytes=len(payload.text.encode()),
            statements=len(result.statements),
            sufficient=result.sufficient,
        )
        return result.model_dump(mode="json")

    @application.post("/api/confirm", response_model=StateEnvelope)
    async def confirm(
        payload: ConfirmRequest,
        request: Request,
        response: Response,
        military_slices_session: Annotated[str | None, Cookie()] = None,
    ) -> StateEnvelope:
        profile_id = _profile(response, military_slices_session)
        _rate_limit(application, profile_id)
        try:
            verify_orientation(payload.token, payload.reviewed_input)
        except TokenError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        current = reconstitute_state(application.state.store.get(profile_id))
        if payload.idempotency_key in current.processed_keys:
            return _envelope(current)
        if current.version != payload.expected_version:
            raise VersionConflictError("Your plan changed in another tab. Refresh to continue.")
        oriented = orient(
            payload.reviewed_input,
            context=current if current.starting_vector_complete else None,
        )
        if not oriented.sufficient:
            raise HTTPException(
                status_code=400,
                detail=oriented.clarification_question
                or "Add one decision-relevant detail before using this in your plan.",
            )
        updated = apply_confirmed_input(
            current,
            oriented,
            idempotency_key=payload.idempotency_key,
        )
        updated, agent_result = await _resolve_current_gate(application, updated)
        agent_telemetry = agent_result.telemetry if agent_result else {}
        updated = _record_governed_mutation(
            current=current,
            updated=updated,
            profile_id=profile_id,
            idempotency_key=payload.idempotency_key,
            mutation_kind="confirmed_input",
            dependency_refs=[
                "reviewed-orientation",
                f"canonical-version:{current.version}",
                *_agent_dependency_refs(agent_result),
            ],
        )
        saved = application.state.store.save_governed(updated, expected_version=current.version)
        current_gate = active_gate(saved)
        _event(
            "confirmed_input",
            profile_id,
            request,
            version=saved.version,
            agent_provider=agent_result.provider if agent_result else "not-required",
            model_calls=agent_telemetry.get("model_calls", 0),
            tool_calls=agent_telemetry.get("tool_calls", 0),
            input_tokens=agent_telemetry.get("input_tokens", 0),
            output_tokens=agent_telemetry.get("output_tokens", 0),
            latency_ms=agent_telemetry.get("latency_ms", 0),
            context_reduction_ratio=agent_telemetry.get("context_reduction_ratio", 0),
            agent_gates_closed=agent_telemetry.get("agent_gates_closed", 0),
            human_gate=current_gate.id if current_gate else None,
            **_temporal_delta(current, saved),
        )
        return _envelope(saved, agent_run=_agent_run(agent_result))

    @application.post("/api/starting-vector", response_model=StateEnvelope)
    async def starting_vector(
        payload: StartingVectorRequest,
        request: Request,
        response: Response,
        military_slices_session: Annotated[str | None, Cookie()] = None,
    ) -> StateEnvelope:
        profile_id = _profile(response, military_slices_session)
        _rate_limit(application, profile_id)
        current = reconstitute_state(application.state.store.get(profile_id))
        if payload.idempotency_key in current.processed_keys:
            return _envelope(current)
        if current.version != payload.expected_version:
            raise VersionConflictError("Your plan changed in another tab. Refresh to continue.")
        try:
            updated = apply_starting_vector(
                current,
                operating_role=payload.operating_role,
                lifecycle_position=payload.lifecycle_position,
                service=payload.service,
                component=payload.component,
                idempotency_key=payload.idempotency_key,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        updated = _record_governed_mutation(
            current=current,
            updated=updated,
            profile_id=profile_id,
            idempotency_key=payload.idempotency_key,
            mutation_kind="starting_vector",
            dependency_refs=["human-starting-vector", f"canonical-version:{current.version}"],
        )
        saved = application.state.store.save_governed(updated, expected_version=current.version)
        _event(
            "starting_vector_confirmed",
            profile_id,
            request,
            version=saved.version,
            operating_role=payload.operating_role,
            lifecycle_position=payload.lifecycle_position.value,
            service=payload.service.value,
            component=payload.component.value,
        )
        return _envelope(saved)

    @application.post("/api/fog-bank")
    async def fog_bank(
        payload: FogBankRequest,
        request: Request,
        response: Response,
        military_slices_session: Annotated[str | None, Cookie()] = None,
    ) -> dict[str, Any]:
        profile_id = _profile(response, military_slices_session)
        _rate_limit(application, profile_id)
        current = reconstitute_state(application.state.store.get(profile_id))
        if current.version != payload.source_version:
            raise VersionConflictError("Your plan changed. Reconsider this from the current plan.")
        proposal = examine_fog_bank(current, payload.text)
        if proposal.status == "review_ready":
            proposal.token = issue_fog_bank(
                profile_id=profile_id,
                source_version=current.version,
                reviewed_input=proposal.reviewed_input,
            )
        _event(
            "fog_bank_examined",
            profile_id,
            request,
            source_version=current.version,
            status=proposal.status,
            changes=len(proposal.changes),
            production_mutations=0,
        )
        return proposal.model_dump(mode="json")

    @application.post("/api/fog-bank/accept", response_model=StateEnvelope)
    async def accept_fog_bank(
        payload: FogBankAcceptRequest,
        request: Request,
        response: Response,
        military_slices_session: Annotated[str | None, Cookie()] = None,
    ) -> StateEnvelope:
        profile_id = _profile(response, military_slices_session)
        _rate_limit(application, profile_id)
        current = reconstitute_state(application.state.store.get(profile_id))
        if payload.idempotency_key in current.processed_keys:
            return _envelope(current)
        if current.version != payload.expected_version:
            raise VersionConflictError("Your plan changed. Reconsider this from the current plan.")
        try:
            token_payload = verify_fog_bank(payload.token, profile_id=profile_id)
        except TokenError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if int(token_payload["source_version"]) != current.version:
            raise VersionConflictError("Your plan changed. Reconsider this from the current plan.")
        proposal = examine_fog_bank(current, str(token_payload["reviewed_input"]))
        try:
            updated = apply_fog_bank_reorientation(
                current,
                proposal,
                idempotency_key=payload.idempotency_key,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        updated, agent_result = await _resolve_current_gate(application, updated)
        updated = _record_governed_mutation(
            current=current,
            updated=updated,
            profile_id=profile_id,
            idempotency_key=payload.idempotency_key,
            mutation_kind="fog_bank_reorientation",
            dependency_refs=[
                "human-reviewed-fog-bank",
                f"canonical-version:{current.version}",
                *_agent_dependency_refs(agent_result),
            ],
        )
        saved = application.state.store.save_governed(updated, expected_version=current.version)
        _event(
            "fog_bank_accepted",
            profile_id,
            request,
            version=saved.version,
            changes=len(proposal.changes),
        )
        return _envelope(saved, agent_run=_agent_run(agent_result))

    @application.post("/api/decision", response_model=StateEnvelope)
    async def decision(
        payload: DecisionRequest,
        request: Request,
        response: Response,
        military_slices_session: Annotated[str | None, Cookie()] = None,
    ) -> StateEnvelope:
        profile_id = _profile(response, military_slices_session)
        _rate_limit(application, profile_id)
        current = reconstitute_state(application.state.store.get(profile_id))
        if payload.idempotency_key in current.processed_keys:
            return _envelope(current)
        if current.version != payload.expected_version:
            raise VersionConflictError("Your plan changed in another tab. Refresh to continue.")
        matching_gate = next((gate for gate in current.gates if gate.id == payload.gate_id), None)
        if matching_gate is None:
            raise HTTPException(status_code=400, detail="That decision is no longer active. Refresh to continue.")
        actor = _trusted_actor(profile_id, payload.idempotency_key)
        governor_decision = AuthorityGovernor().evaluate(
            state=current,
            gate=matching_gate,
            proposal=ResolverTransitionProposal(
                gate_id=matching_gate.id,
                source_state_version=current.version,
                proposed_state=(
                    matching_gate.state
                    if payload.value.strip().casefold().startswith("reject:")
                    else GateState.YES
                ),
                proposed_value=payload.value,
                authority=Authority.HUMAN,
                scope=matching_gate.authorized_scope,
            ),
            actor=actor,
        )
        if not governor_decision.authorized:
            raise HTTPException(status_code=409, detail=f"Decision blocked: {governor_decision.reason_code}.")
        try:
            updated = apply_decision(
                current,
                gate_id=payload.gate_id,
                value=payload.value,
                idempotency_key=payload.idempotency_key,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        updated.governor_decisions.append(governor_decision)
        updated, agent_result = await _resolve_current_gate(application, updated)
        updated = _record_governed_mutation(
            current=current,
            updated=updated,
            profile_id=profile_id,
            idempotency_key=payload.idempotency_key,
            mutation_kind="human_decision",
            dependency_refs=[
                f"gate:{payload.gate_id}",
                f"canonical-version:{current.version}",
                *_agent_dependency_refs(agent_result),
            ],
        )
        saved = application.state.store.save_governed(updated, expected_version=current.version)
        _event(
            "human_decision",
            profile_id,
            request,
            version=saved.version,
            decision=payload.gate_id,
            agent_provider=agent_result.provider if agent_result else "not-required",
            **_temporal_delta(current, saved),
        )
        return _envelope(saved, agent_run=_agent_run(agent_result))

    @application.post("/api/acquire")
    async def acquire(
        payload: AcquisitionRequest,
        request: Request,
        response: Response,
        military_slices_session: Annotated[str | None, Cookie()] = None,
    ) -> dict[str, Any]:
        """Accept a natural answer without giving the conversational layer write authority."""
        profile_id = _profile(response, military_slices_session)
        _rate_limit(application, profile_id)
        current = reconstitute_state(application.state.store.get(profile_id))
        if payload.idempotency_key in current.processed_keys:
            return {
                "status": "applied",
                "message": "That answer was already used.",
                "matched_checklist_ids": [],
                "resolved_gate_ids": [],
                "envelope": _envelope(current).model_dump(mode="json"),
            }
        if current.version != payload.expected_version:
            raise VersionConflictError("Your plan changed in another tab. Refresh to continue.")
        gate = active_gate(current)
        horizon = build_acquisition_horizon(current)
        if gate is None or horizon is None or gate.id != payload.gate_id:
            raise HTTPException(status_code=409, detail="That question is no longer active. Refresh to continue.")
        evaluated = evaluate_acquisition(current, horizon, payload.text)
        if evaluated.gate_value is None:
            deterministic_question = evaluated.clarification_question or (
                "Add one detail that answers the question in front of you."
            )
            language = await application.state.resolver.acquisition_language(
                state=current,
                horizon=horizon,
                human_text=payload.text,
                deterministic_clarification=deterministic_question,
            )
            _event(
                "bounded_acquisition_clarification",
                profile_id,
                request,
                source_version=current.version,
                horizon_items=len(horizon.checklist),
                matched_items=len(evaluated.matched_checklist_ids),
                language_provider=language.provider,
                model_calls=language.telemetry.get("model_calls", 0),
                production_mutations=0,
            )
            return {
                "status": "clarification_needed",
                "message": language.clarification_question or deterministic_question,
                "reply": language.reply,
                "carry_forward": payload.text,
                "matched_checklist_ids": evaluated.matched_checklist_ids,
                "candidates": [item.model_dump(mode="json") for item in evaluated.candidates],
                "horizon": horizon.model_dump(mode="json"),
                "writes": 0,
                "language_provider": language.provider,
            }
        actor = _trusted_actor(profile_id, payload.idempotency_key)
        governor_decision = AuthorityGovernor().evaluate(
            state=current,
            gate=gate,
            proposal=ResolverTransitionProposal(
                gate_id=gate.id,
                source_state_version=current.version,
                proposed_state=GateState.YES,
                proposed_value=evaluated.gate_value,
                authority=Authority.HUMAN,
                scope=gate.authorized_scope,
                evidence_refs=[f"acquisition-horizon:sha256:{horizon.receipt_hash}"],
            ),
            actor=actor,
        )
        if not governor_decision.authorized:
            raise HTTPException(status_code=409, detail=f"Decision blocked: {governor_decision.reason_code}.")
        try:
            updated = apply_decision(
                current,
                gate_id=gate.id,
                value=evaluated.gate_value,
                source_text=payload.text,
                idempotency_key=payload.idempotency_key,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        updated.governor_decisions.append(governor_decision)
        updated, agent_result = await _resolve_current_gate(application, updated)
        updated = _record_governed_mutation(
            current=current,
            updated=updated,
            profile_id=profile_id,
            idempotency_key=payload.idempotency_key,
            mutation_kind="bounded_acquisition",
            dependency_refs=[
                f"gate:{gate.id}",
                f"acquisition-horizon:sha256:{horizon.receipt_hash}",
                f"canonical-version:{current.version}",
                *_agent_dependency_refs(agent_result),
            ],
        )
        saved = application.state.store.save_governed(updated, expected_version=current.version)
        _event(
            "bounded_acquisition_applied",
            profile_id,
            request,
            source_version=current.version,
            version=saved.version,
            horizon_items=len(horizon.checklist),
            matched_items=len(evaluated.matched_checklist_ids),
            resolved_gate=gate.id,
            agent_provider=agent_result.provider if agent_result else "not-required",
        )
        return {
            "status": "applied",
            "message": "Your answer changed what comes next.",
            "matched_checklist_ids": evaluated.matched_checklist_ids,
            "resolved_gate_ids": [gate.id],
            "envelope": _envelope(saved, agent_run=_agent_run(agent_result)).model_dump(mode="json"),
        }

    @application.post("/api/revalidate", response_model=StateEnvelope)
    async def revalidate(
        payload: RevalidationRequest,
        request: Request,
        response: Response,
        military_slices_session: Annotated[str | None, Cookie()] = None,
    ) -> StateEnvelope:
        profile_id = _profile(response, military_slices_session)
        _rate_limit(application, profile_id)
        current = reconstitute_state(application.state.store.get(profile_id))
        if payload.idempotency_key in current.processed_keys:
            return _envelope(current)
        if current.version != payload.expected_version:
            raise VersionConflictError("Your plan changed in another tab. Refresh to continue.")
        impact = next((item for item in current.impacts if item.id == payload.impact_id), None)
        try:
            updated, changed = apply_revalidation(
                current,
                impact_id=payload.impact_id,
                action=payload.action,
                value=payload.value,
                idempotency_key=payload.idempotency_key,
            )
        except ValueError as exc:
            _event(
                "temporal_revalidation_failed",
                profile_id,
                request,
                version=current.version,
                impact_id=payload.impact_id,
                action=payload.action,
                temporal_errors=1,
            )
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if not changed:
            return _envelope(current)
        updated = _record_governed_mutation(
            current=current,
            updated=updated,
            profile_id=profile_id,
            idempotency_key=payload.idempotency_key,
            mutation_kind="temporal_revalidation",
            dependency_refs=[f"impact:{payload.impact_id}", f"canonical-version:{current.version}"],
        )
        saved = application.state.store.save_governed(updated, expected_version=current.version)
        _event(
            "temporal_revalidation",
            profile_id,
            request,
            version=saved.version,
            canonical_field=impact.dependent_field if impact else None,
            action=payload.action,
            dependencies_evaluated=(
                saved.telemetry.temporal_dependencies_evaluated
                - current.telemetry.temporal_dependencies_evaluated
            ),
            fields_marked_stale=(
                saved.telemetry.temporal_fields_marked_stale
                - current.telemetry.temporal_fields_marked_stale
            ),
            silently_refreshed=(
                saved.telemetry.temporal_fields_silently_refreshed
                - current.telemetry.temporal_fields_silently_refreshed
            ),
            human_prompts=(
                saved.telemetry.temporal_human_prompts - current.telemetry.temporal_human_prompts
            ),
            receipt_patch_bytes=(
                saved.telemetry.temporal_patch_bytes - current.telemetry.temporal_patch_bytes
            ),
            freshness_model_calls=0,
            full_receipt_rebuilds=0,
        )
        return _envelope(saved)

    @application.post("/api/artifact")
    async def artifact(
        request: Request,
        response: Response,
        file: Annotated[UploadFile, File()],
        expected_version: Annotated[int, Form()],
        idempotency_key: Annotated[str, Form(min_length=8, max_length=128)],
        military_slices_session: Annotated[str | None, Cookie()] = None,
    ) -> StateEnvelope:
        profile_id = _profile(response, military_slices_session)
        _rate_limit(application, profile_id)
        current = reconstitute_state(application.state.store.get(profile_id))
        if idempotency_key in current.processed_keys:
            return _envelope(current)
        if current.version != expected_version:
            raise VersionConflictError("Your plan changed in another tab. Refresh to continue.")
        data = await file.read(5 * 1024 * 1024 + 1)
        try:
            extracted = extract_artifact(file.filename or "artifact", data, file.content_type)
            text = extracted.text
            if extracted.requires_multimodal:
                if os.getenv("MILITARY_SLICES_AGENT", "deterministic") != "adk":
                    raise ArtifactError("Image extraction is available in the deployed Gemini candidate.")
                text = await multimodal_extract(extracted)
        except ArtifactError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        finally:
            data = b""
        oriented = orient(text, context=current if current.starting_vector_complete else None)
        updated = apply_artifact_input(
            current,
            oriented,
            idempotency_key=idempotency_key,
        )
        updated, agent_result = await _resolve_current_gate(application, updated)
        agent_telemetry = agent_result.telemetry if agent_result else {}
        updated = _record_governed_mutation(
            current=current,
            updated=updated,
            profile_id=profile_id,
            idempotency_key=idempotency_key,
            mutation_kind="artifact_input",
            dependency_refs=[
                "deliberately-supplied-artifact",
                f"canonical-version:{current.version}",
                *_agent_dependency_refs(agent_result),
            ],
        )
        saved = application.state.store.save_governed(updated, expected_version=current.version)
        current_gate = active_gate(saved)
        _event(
            "artifact_applied",
            profile_id,
            request,
            version=saved.version,
            media_type=extracted.media_type,
            method=extracted.method,
            output_characters=len(text),
            agent_provider=agent_result.provider if agent_result else "not-required",
            model_calls=agent_telemetry.get("model_calls", 0),
            tool_calls=agent_telemetry.get("tool_calls", 0),
            latency_ms=agent_telemetry.get("latency_ms", 0),
            human_gate=current_gate.id if current_gate else None,
            **_temporal_delta(current, saved),
        )
        return _envelope(saved, agent_run=_agent_run(agent_result))

    @application.get("/")
    async def root() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @application.get("/{path:path}")
    async def spa(path: str) -> FileResponse:
        if path.startswith("api/"):
            raise HTTPException(status_code=404)
        return FileResponse(STATIC_DIR / "index.html")

    return application


def _profile(response: Response, token: str | None) -> str:
    profile_id = verify_session(token)
    if profile_id is None:
        profile_id, signed = issue_session()
        response.set_cookie(
            COOKIE_NAME,
            signed,
            httponly=True,
            secure=os.getenv("MILITARY_SLICES_COOKIE_SECURE", "false").lower() == "true",
            samesite="lax",
            max_age=60 * 60 * 24 * 180,
            path="/",
        )
    return profile_id


def _rate_limit(application: FastAPI, profile_id: str) -> None:
    if not application.state.limiter.allow(profile_id):
        raise HTTPException(status_code=429, detail="Please wait a moment before trying again.")


def _envelope(state: Any, agent_run: dict[str, Any] | None = None) -> StateEnvelope:
    return StateEnvelope(
        state=state,
        active_gate=active_gate(state),
        what_changed=state.feedback[-1] if state.feedback else None,
        progress=path_progress(state),
        lenses=lens_projections(state),
        impact=current_impact(state),
        agent_run=agent_run,
        acquisition_horizon=build_acquisition_horizon(state),
    )


def _apply_agent_result(state: Any, agent_result: Any) -> Any:
    state = apply_hypotheses(state, agent_result.hypotheses)
    state.telemetry.model_calls += int(agent_result.telemetry.get("model_calls", 0))
    state.telemetry.tool_calls += int(agent_result.telemetry.get("tool_calls", 0))
    state.telemetry.input_tokens += int(agent_result.telemetry.get("input_tokens", 0))
    state.telemetry.output_tokens += int(agent_result.telemetry.get("output_tokens", 0))
    state.telemetry.agent_gates_closed += int(agent_result.telemetry.get("agent_gates_closed", 0))
    state.telemetry.total_agent_latency_ms += int(agent_result.telemetry.get("latency_ms", 0))
    state.telemetry.resolver_context_bytes = int(agent_result.telemetry.get("resolver_context_bytes", 0))
    state.telemetry.state_bytes_avoided += int(agent_result.telemetry.get("state_bytes_avoided", 0))
    state.telemetry.context_reduction_ratio = float(
        agent_result.telemetry.get("context_reduction_ratio", 0)
    )
    if state.feedback and agent_result.hypotheses:
        consequence = (
            "New directions are ready to explore based on the experience and preferences you confirmed."
        )
        if consequence not in state.feedback[-1].consequences:
            state.feedback[-1].consequences.append(consequence)
    return state


async def _resolve_current_gate(
    application: FastAPI,
    state: Any,
) -> tuple[Any, ResolverResult | None]:
    state = bind_gate_contracts(state)
    if not career_resolution_required(state):
        return state, None
    agent_result = await application.state.resolver.resolve(state)
    gate = active_gate(state)
    if gate is None:
        return state, None
    proposal_ref = resolver_nomination_ref(
        gate_id=gate.id,
        source_state_version=state.version,
        hypotheses=agent_result.hypotheses,
    )
    proposal = ResolverTransitionProposal(
        gate_id=gate.id,
        source_state_version=state.version,
        proposed_state=gate.state,
        authority=Authority.BOUNDED_AGENT,
        effect="nominate",
        scope=["career:hypothesis-nomination"],
        evidence_refs=[
            proposal_ref,
            *[evidence for item in agent_result.hypotheses for evidence in item.evidence],
        ],
    )
    validate_resolver_nomination(proposal=proposal, hypotheses=agent_result.hypotheses)
    nomination = AuthorityGovernor().evaluate(
        state=state,
        gate=gate,
        proposal=proposal,
    )
    if not nomination.authorized:
        LOGGER.warning(
            "resolver_nomination_blocked reason=%s profile=%s",
            nomination.reason_code,
            state.profile_id[-12:],
        )
        return state, agent_result
    state.governor_decisions.append(nomination)
    agent_result = replace(agent_result, proposal_ref=proposal_ref)
    return _apply_agent_result(state, agent_result), agent_result


def _agent_dependency_refs(agent_result: ResolverResult | None) -> list[str]:
    if agent_result is None:
        return []
    return [agent_result.proposal_ref] if agent_result.proposal_ref else []


def _trusted_actor(profile_id: str, idempotency_key: str) -> ActorProvenance:
    digest = hashlib.sha256(f"{profile_id}:{idempotency_key}".encode()).hexdigest()
    return ActorProvenance.trusted_session(
        profile_id=profile_id,
        event_id=f"mutation-{digest[:32]}",
        integrity_ref=f"signed-session:{hashlib.sha256(profile_id.encode()).hexdigest()}",
    )


def _record_governed_mutation(
    *,
    current: Any,
    updated: Any,
    profile_id: str,
    idempotency_key: str,
    mutation_kind: str,
    dependency_refs: list[str],
) -> Any:
    return AuthorityGovernor().record_human_mutation(
        state=updated,
        actor=_trusted_actor(profile_id, idempotency_key),
        idempotency_key=idempotency_key,
        expected_version=current.version,
        result_version=updated.version,
        dependency_refs=dependency_refs,
        mutation_kind=mutation_kind,
    )


def _agent_run(agent_result: ResolverResult | None) -> dict[str, Any] | None:
    if agent_result is None:
        return None
    return {
        "provider": agent_result.provider,
        "latency_ms": agent_result.telemetry.get("latency_ms", 0),
        "tool_calls": agent_result.telemetry.get("tool_calls", 0),
        "fallback": agent_result.telemetry.get("fallback", False),
    }


def _temporal_delta(before: Any, after: Any) -> dict[str, Any]:
    return {
        "canonical_fields_changed": sorted(changed_fields(before, after)),
        "dependencies_evaluated": (
            after.telemetry.temporal_dependencies_evaluated
            - before.telemetry.temporal_dependencies_evaluated
        ),
        "fields_marked_stale": (
            after.telemetry.temporal_fields_marked_stale
            - before.telemetry.temporal_fields_marked_stale
        ),
        "fields_silently_refreshed": (
            after.telemetry.temporal_fields_silently_refreshed
            - before.telemetry.temporal_fields_silently_refreshed
        ),
        "human_revalidation_prompts": (
            after.telemetry.temporal_human_prompts - before.telemetry.temporal_human_prompts
        ),
        "freshness_model_calls": 0,
        "receipt_patch_bytes": (
            after.telemetry.temporal_patch_bytes - before.telemetry.temporal_patch_bytes
        ),
        "full_receipt_rebuilds": 0,
    }


def _event(name: str, profile_id: str, request: Request, **values: Any) -> None:
    payload = {
        "event": name,
        "profile_hash": profile_id[-12:],
        "path": request.url.path,
        **values,
    }
    LOGGER.info(json.dumps(payload, separators=(",", ":"), sort_keys=True))


app = create_app()
