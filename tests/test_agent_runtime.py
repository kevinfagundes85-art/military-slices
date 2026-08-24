from __future__ import annotations

import json

import pytest

from military_slices.agent_runtime import ResolverProposal, _extract_json


def test_governed_agent_json_accepts_fenced_final_response() -> None:
    raw = {
        "hypotheses": [
            {
                "title": "Maintenance Planner",
                "rationale": "Uses scheduling and inspection experience.",
                "evidence_family": "maintenance",
            }
        ],
        "machine_closed": ["occupational source located"],
        "remaining_uncertainty": "Needs a real posting.",
    }
    payload = _extract_json(f"```json\n{json.dumps(raw)}\n```")
    proposal = ResolverProposal.model_validate(payload)
    assert proposal.hypotheses[0].title == "Maintenance Planner"


def test_governed_agent_json_rejects_non_json_chatter() -> None:
    with pytest.raises(ValueError):
        _extract_json("I think you should be a project manager.")
