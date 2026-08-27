from __future__ import annotations

import json
from copy import deepcopy

from benchmark.run_probe_decisive_falsification import (
    CONTRACT,
    EXPECTED_CONTRACT_SHA256,
    LEXICAL_FALSE_NEGATIVES,
    authority_audit,
    case_state,
    graduate,
    probe_payload,
    sha256_path,
)
from military_slices.governance import probe_execution_enabled


def test_frozen_probe_contract_is_exact() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    assert sha256_path(CONTRACT) == EXPECTED_CONTRACT_SHA256
    assert len(contract["cases"]) == 15
    assert {
        case["id"] for case in contract["cases"] if case["id"] in LEXICAL_FALSE_NEGATIVES
    } == LEXICAL_FALSE_NEGATIVES


def test_probe_payload_never_contains_expected_label() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    for case in contract["cases"]:
        payload = probe_payload(case)
        assert "expected_material" not in json.dumps(payload)


def test_nomination_is_zero_write_and_production_probe_stays_disabled() -> None:
    case = json.loads(CONTRACT.read_text(encoding="utf-8"))["cases"][0]
    state = case_state(case)
    before = deepcopy(state)
    result = {
        "decision": {
            "case_id": case["id"],
            "nomination": {
                "kind": "CandidateForExamination",
                "effect": "DISCOVER_WAKE_ONLY",
                "possible_relationship": "This may constrain the current move.",
                "why_examine": "The relationship is plausible but not governed truth.",
                "examination_question": "Does the agreement apply to this work?",
            },
            "no_nomination_reason": None,
        }
    }

    audit = authority_audit(before, state, result)

    assert audit["violation"] is False
    assert audit["canonical_unchanged"] is True
    assert probe_execution_enabled() is False


def test_authorized_graduation_reuses_existing_structures_and_skips_second_probe() -> None:
    case = json.loads(CONTRACT.read_text(encoding="utf-8"))["cases"][0]
    state = case_state(case)
    result = {
        "decision": {
            "case_id": case["id"],
            "nomination": {
                "kind": "CandidateForExamination",
                "effect": "DISCOVER_WAKE_ONLY",
                "possible_relationship": "This may constrain the current move.",
                "why_examine": "The relationship is plausible but requires human examination.",
                "examination_question": "Does the agreement apply to the proposed venture?",
            },
            "no_nomination_reason": None,
        }
    }

    trace = graduate(case, state, result)

    assert trace["governance_validated"] is True
    assert trace["version_delta"] == 1
    assert trace["second_pass"]["probe_calls"] == 0
    assert trace["second_pass"]["model_calls"] == 0
    assert trace["second_pass"]["correct_consequential_handling"] is True
    assert trace["persisted_structures"] == [
        "Fact",
        "ImpactItem",
        "Decision",
        "MutationEvent",
        "LineageRecord",
    ]
