"""Availability-only preflight for the frozen T1 provider configuration."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from google import genai

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "benchmark/output/adaptive-resolver-aperture-t1-provider-preflight-2026-08-28.json"
PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "veteran-pathfinder-kf-2026")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
MODEL = "gemini-3.7-flash"


def _hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, separators=(",", ":"), sort_keys=True, default=str).encode()).hexdigest()


def main() -> int:
    started = datetime.now(UTC)
    base: dict[str, Any] = {
        "provider": "Vertex AI",
        "project": PROJECT,
        "location": LOCATION,
        "requested_model": MODEL,
        "timestamp": started.isoformat(),
        "operation": "models.get",
        "benchmark_task_content_transmitted": False,
        "benchmark_calls": 0,
    }
    try:
        client = genai.Client(vertexai=True, project=PROJECT, location=LOCATION)
        model = client.models.get(model=MODEL)
        metadata = {
            "name": model.name,
            "display_name": model.display_name,
            "version": model.version,
        }
        result = {
            **base,
            "initialization_success": True,
            "model_metadata": metadata,
            "model_metadata_sha256": _hash(metadata),
            "error_class": None,
            "error": None,
        }
    except Exception as exc:  # provider failure is evidence, not a retry trigger
        result = {
            **base,
            "initialization_success": False,
            "model_metadata": None,
            "model_metadata_sha256": None,
            "error_class": type(exc).__name__,
            "error": str(exc),
        }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    attempts: list[dict[str, Any]] = []
    if OUT.exists():
        previous = json.loads(OUT.read_text(encoding="utf-8"))
        attempts = previous.get("attempts", [previous])
    attempts.append(result)
    ledger = {
        "contract": "adaptive-resolver-aperture-t1-provider-preflight-v1",
        "attempts": attempts,
        "final_status": "AVAILABLE" if result["initialization_success"] else "UNAVAILABLE",
    }
    OUT.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["initialization_success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
