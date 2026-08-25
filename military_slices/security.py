from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
import uuid
from dataclasses import dataclass
from typing import Any


class TokenError(ValueError):
    pass


def _secret() -> bytes:
    value = os.getenv("MILITARY_SLICES_SESSION_SECRET", "development-only-secret-change-me")
    if os.getenv("MILITARY_SLICES_ENV") == "production" and len(value) < 32:
        raise RuntimeError("MILITARY_SLICES_SESSION_SECRET must be at least 32 characters.")
    return value.encode()


def _encode(payload: dict[str, Any]) -> str:
    body = (
        base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode())
        .decode()
        .rstrip("=")
    )
    signature = hmac.new(_secret(), body.encode(), hashlib.sha256).hexdigest()
    return f"{body}.{signature}"


def _decode(token: str) -> dict[str, Any]:
    try:
        body, signature = token.rsplit(".", 1)
    except ValueError as exc:
        raise TokenError("Invalid token.") from exc
    expected = hmac.new(_secret(), body.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected):
        raise TokenError("Invalid token.")
    try:
        padding = "=" * (-len(body) % 4)
        payload = json.loads(base64.urlsafe_b64decode(body + padding))
    except (ValueError, json.JSONDecodeError) as exc:
        raise TokenError("Invalid token.") from exc
    if not isinstance(payload, dict):
        raise TokenError("Invalid token.")
    return payload


def issue_session(profile_id: str | None = None) -> tuple[str, str]:
    identifier = profile_id or f"ms-{uuid.uuid4().hex}"
    return identifier, _encode({"sub": identifier, "kind": "session", "iat": int(time.time())})


def verify_session(token: str | None) -> str | None:
    if not token:
        return None
    try:
        payload = _decode(token)
    except TokenError:
        return None
    if payload.get("kind") != "session" or not isinstance(payload.get("sub"), str):
        return None
    if not payload["sub"].startswith("ms-"):
        return None
    return str(payload["sub"])


def issue_orientation(text: str, ttl_seconds: int = 900) -> str:
    return _encode(
        {
            "kind": "orientation",
            "sha256": hashlib.sha256(text.encode()).hexdigest(),
            "exp": int(time.time()) + ttl_seconds,
        }
    )


def verify_orientation(token: str, text: str) -> None:
    payload = _decode(token)
    if payload.get("kind") != "orientation":
        raise TokenError("Invalid orientation token.")
    if int(payload.get("exp", 0)) < int(time.time()):
        raise TokenError("That review expired. Please orient the text again.")
    expected = hashlib.sha256(text.encode()).hexdigest()
    if not hmac.compare_digest(str(payload.get("sha256", "")), expected):
        raise TokenError("The reviewed text changed. Orient it again before confirming.")


def issue_what_if(
    *,
    profile_id: str,
    source_version: int,
    modification_kind: str,
    modification_value: str,
    statement: str,
    ttl_seconds: int = 1800,
) -> str:
    return _encode(
        {
            "kind": "what-if",
            "sub": profile_id,
            "source_version": source_version,
            "modification_kind": modification_kind,
            "modification_value": modification_value,
            "statement": statement,
            "exp": int(time.time()) + ttl_seconds,
        }
    )


def verify_what_if(token: str, *, profile_id: str) -> dict[str, Any]:
    payload = _decode(token)
    if payload.get("kind") != "what-if" or payload.get("sub") != profile_id:
        raise TokenError("That hypothetical branch does not belong to this plan.")
    if int(payload.get("exp", 0)) < int(time.time()):
        raise TokenError("That hypothetical branch expired. Explore it again before using it.")
    required = ("source_version", "modification_kind", "modification_value", "statement")
    if any(key not in payload for key in required):
        raise TokenError("Invalid hypothetical branch token.")
    return payload


@dataclass
class RateBucket:
    window_started: float
    count: int


class LocalRateLimiter:
    def __init__(self, limit: int = 30, window_seconds: int = 60) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._buckets: dict[str, RateBucket] = {}

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        bucket = self._buckets.get(key)
        if bucket is None or now - bucket.window_started >= self.window_seconds:
            self._buckets[key] = RateBucket(window_started=now, count=1)
            return True
        if bucket.count >= self.limit:
            return False
        bucket.count += 1
        return True
