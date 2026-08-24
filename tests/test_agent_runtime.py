from __future__ import annotations

import asyncio
import json

import pytest

from military_slices.agent_runtime import Resolver, ResolverProposal, _extract_json
from military_slices.engine import new_state


def test_governed_agent_json_accepts_fenced_final_response() -> None:
    raw = {
        "hypotheses": [
            {
                "title": "Maintenance Planner",
                "rationale": "Uses scheduling and inspection experience.",
                "evidence_family": "maintenance",
                "capability_matches": ["Scheduling experience"],
                "possible_gaps": ["Civilian maintenance terminology"],
            }
        ],
        "machine_closed": ["occupational source located"],
        "remaining_uncertainty": "Needs a real posting.",
    }
    payload = _extract_json(f"```json\n{json.dumps(raw)}\n```")
    proposal = ResolverProposal.model_validate(payload)
    assert proposal.hypotheses[0].title == "Maintenance Planner"
    assert proposal.hypotheses[0].capability_matches == ["Scheduling experience"]


def test_governed_agent_json_rejects_non_json_chatter() -> None:
    with pytest.raises(ValueError):
        _extract_json("I think you should be a project manager.")


def test_resolver_timeout_falls_back_instead_of_spinning(monkeypatch: pytest.MonkeyPatch) -> None:
    resolver = Resolver(mode="adk", timeout_seconds=0.01, max_llm_calls=3)

    async def never_finishes(_state: object) -> object:
        await asyncio.sleep(10)
        raise AssertionError("unreachable")

    monkeypatch.setattr(resolver, "_run_adk", never_finishes)
    result = asyncio.run(resolver.resolve(new_state("ms-timeout")))
    assert result.provider == "deterministic-fallback"
    assert result.telemetry["fallback"] is True
    assert result.telemetry["error_class"] == "TimeoutError"
    assert result.hypotheses
