from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Annotated, Any, cast

from fastapi import Cookie, FastAPI, File, Form, HTTPException, Request, Response, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from military_slices.agent_runtime import Resolver, ResolverResult
from military_slices.artifacts import ArtifactError, extract_artifact, multimodal_extract
from military_slices.control import create_what_if, history_entry, lens_projections, path_progress, promote_what_if
from military_slices.engine import (
    active_gate,
    apply_artifact_input,
    apply_confirmed_input,
    apply_decision,
    apply_hypotheses,
    apply_revalidation,
    career_resolution_required,
    orient,
    reconstitute_state,
)
from military_slices.models import (
    ConfirmRequest,
    DecisionRequest,
    OrientRequest,
    RevalidationRequest,
    SliceName,
    StateEnvelope,
    WhatIfPromotionRequest,
    WhatIfRequest,
)
from military_slices.path_runtime import PACK_VERSION
from military_slices.security import (
    LocalRateLimiter,
    TokenError,
    issue_orientation,
    issue_session,
    issue_what_if,
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

    @application.get("/api/health")
    @application.get("/healthz")
    async def health() -> dict[str, str]:
        return {
            "status": "ok",
            "service": "military-slices",
            "model": os.getenv("MILITARY_SLICES_MODEL", "gemini-3.7-flash"),
            "agent_framework": "google-adk",
            "transition_pack": PACK_VERSION,
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
        saved = application.state.store.save(updated, expected_version=current.version)
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
        result = orient(payload.text)
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
        oriented = orient(payload.reviewed_input)
        updated = apply_confirmed_input(
            current,
            oriented,
            idempotency_key=payload.idempotency_key,
        )
        updated, agent_result = await _resolve_current_gate(application, updated)
        agent_telemetry = agent_result.telemetry if agent_result else {}
        saved = application.state.store.save(updated, expected_version=current.version)
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
        try:
            updated = apply_decision(
                current,
                gate_id=payload.gate_id,
                value=payload.value,
                idempotency_key=payload.idempotency_key,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        updated, agent_result = await _resolve_current_gate(application, updated)
        saved = application.state.store.save(updated, expected_version=current.version)
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
        saved = application.state.store.save(updated, expected_version=current.version)
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
        oriented = orient(text)
        updated = apply_artifact_input(
            current,
            oriented,
            idempotency_key=idempotency_key,
        )
        updated, agent_result = await _resolve_current_gate(application, updated)
        agent_telemetry = agent_result.telemetry if agent_result else {}
        saved = application.state.store.save(updated, expected_version=current.version)
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
    return state


async def _resolve_current_gate(
    application: FastAPI,
    state: Any,
) -> tuple[Any, ResolverResult | None]:
    if not career_resolution_required(state):
        return state, None
    agent_result = await application.state.resolver.resolve(state)
    return _apply_agent_result(state, agent_result), agent_result


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
