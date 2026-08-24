from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Annotated, Any, cast

from fastapi import Cookie, FastAPI, File, HTTPException, Request, Response, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from military_slices.agent_runtime import Resolver
from military_slices.artifacts import ArtifactError, extract_artifact, multimodal_extract
from military_slices.engine import (
    active_gate,
    apply_confirmed_input,
    apply_decision,
    apply_hypotheses,
    orient,
)
from military_slices.models import (
    ConfirmRequest,
    DecisionRequest,
    OrientRequest,
    StateEnvelope,
)
from military_slices.security import (
    LocalRateLimiter,
    TokenError,
    issue_orientation,
    issue_session,
    verify_orientation,
    verify_session,
)
from military_slices.store import FirestoreStore, MemoryStore, StateStore, VersionConflictError

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

    @application.get("/healthz")
    async def health() -> dict[str, str]:
        return {
            "status": "ok",
            "service": "military-slices",
            "model": os.getenv("MILITARY_SLICES_MODEL", "gemini-3.7-flash"),
            "agent_framework": "google-adk",
        }

    @application.get("/api/state", response_model=StateEnvelope)
    async def get_state(
        response: Response,
        military_slices_session: Annotated[str | None, Cookie()] = None,
    ) -> StateEnvelope:
        profile_id = _profile(response, military_slices_session)
        state = application.state.store.get(profile_id)
        return _envelope(state)

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
        current = application.state.store.get(profile_id)
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
        agent_result = await application.state.resolver.resolve(updated)
        updated = apply_hypotheses(updated, agent_result.hypotheses)
        updated.telemetry.model_calls += int(agent_result.telemetry.get("model_calls", 0))
        updated.telemetry.tool_calls += int(agent_result.telemetry.get("tool_calls", 0))
        updated.telemetry.input_tokens += int(agent_result.telemetry.get("input_tokens", 0))
        updated.telemetry.output_tokens += int(agent_result.telemetry.get("output_tokens", 0))
        saved = application.state.store.save(updated, expected_version=current.version)
        _event(
            "confirmed_input",
            profile_id,
            request,
            version=saved.version,
            agent_provider=agent_result.provider,
            model_calls=agent_result.telemetry.get("model_calls", 0),
            tool_calls=agent_result.telemetry.get("tool_calls", 0),
        )
        return _envelope(
            saved,
            agent_run={
                "provider": agent_result.provider,
                "latency_ms": agent_result.telemetry.get("latency_ms", 0),
                "tool_calls": agent_result.telemetry.get("tool_calls", 0),
                "fallback": agent_result.telemetry.get("fallback", False),
            },
        )

    @application.post("/api/decision", response_model=StateEnvelope)
    async def decision(
        payload: DecisionRequest,
        request: Request,
        response: Response,
        military_slices_session: Annotated[str | None, Cookie()] = None,
    ) -> StateEnvelope:
        profile_id = _profile(response, military_slices_session)
        _rate_limit(application, profile_id)
        current = application.state.store.get(profile_id)
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
        saved = application.state.store.save(updated, expected_version=current.version)
        _event("human_decision", profile_id, request, version=saved.version, decision=payload.gate_id)
        return _envelope(saved)

    @application.post("/api/artifact")
    async def artifact(
        request: Request,
        response: Response,
        file: Annotated[UploadFile, File()],
        military_slices_session: Annotated[str | None, Cookie()] = None,
    ) -> dict[str, Any]:
        profile_id = _profile(response, military_slices_session)
        _rate_limit(application, profile_id)
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
        _event(
            "artifact_extracted",
            profile_id,
            request,
            media_type=extracted.media_type,
            method=extracted.method,
            output_characters=len(text),
        )
        return {
            "filename": extracted.filename,
            "text": text,
            "method": extracted.method,
            "notice": "Review and edit this text. Nothing has been saved yet.",
        }

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
        agent_run=agent_run,
    )


def _event(name: str, profile_id: str, request: Request, **values: Any) -> None:
    payload = {
        "event": name,
        "profile_hash": profile_id[-12:],
        "path": request.url.path,
        **values,
    }
    LOGGER.info(json.dumps(payload, separators=(",", ":"), sort_keys=True))


app = create_app()
