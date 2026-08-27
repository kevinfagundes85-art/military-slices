from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import time
from copy import deepcopy
from pathlib import Path
from typing import Any

from benchmark.run_probe_decisive_falsification import ProbeHarness, sha256_json
from benchmark.run_state_bound_rejection_falsification import (
    actor,
    add_irrelevant_change,
    initial_state,
    provider_attempt,
)
from military_slices.domain_pack import installed_domain_pack_payload, installed_domain_pack_ref
from military_slices.governance import bind_gate_contracts
from military_slices.models import Authority, CanonicalState, Fact, FreshnessStatus
from military_slices.state_bound_rejection import (
    GovernedContentRejectionLookup,
    RejectionLookup,
    lookup_governed_content_rejection,
    lookup_state_bound_rejection,
    record_state_bound_rejection,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT / "benchmark/contracts/governed_identity_generalization_falsification_2026-08-27.json"
)
BASE_CONTRACT_PATH = ROOT / "benchmark/contracts/state_bound_rejection_falsification_2026-08-27.json"
RAW_PATH = ROOT / "benchmark/output/helm-governed-identity-generalization-raw-2026-08-27.json"
EXPECTED_CONTRACT_SHA256 = "aa9ecc972edb5df65eefcb8e19727a444aa59863a1182b93a298bb49f8eed779"
EXPECTED_BASE_CONTRACT_SHA256 = "c130b4abfbe048ae2e50fbeba4c31cd8adcbae6d3317ff390d8f9d3d85b37325"
VALIDITY_DIMENSIONS = [
    "anchor",
    "path",
    "lifecycle",
    "time_validity",
    "authority",
    "effect_reachability",
]


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def state_hash(state: CanonicalState) -> str:
    return sha256_json(state.model_dump(mode="json"))


def percentile_stats(values: list[float]) -> dict[str, float]:
    if not values:
        return {"mean": 0.0, "median": 0.0, "min": 0.0, "max": 0.0, "stdev": 0.0}
    return {
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "min": min(values),
        "max": max(values),
        "stdev": statistics.stdev(values) if len(values) > 1 else 0.0,
    }


def base_cases() -> dict[str, dict[str, Any]]:
    payload = json.loads(BASE_CONTRACT_PATH.read_text(encoding="utf-8"))
    return {item["id"]: item for item in payload["cases"]}


def governed_rejection_state(case: dict[str, Any]) -> CanonicalState:
    state = initial_state(case)
    return record_state_bound_rejection(
        state,
        actor=actor(state, f"event-generalized-rejection-{case['id']}"),
        idempotency_key=f"generalized-rejection-{case['id']}",
        fact_ids=case["source_fact_ids"],
        effect_dimension=case["effect_dimension"],
        gate_id=case["gate_id"],
        validity_dimensions=VALIDITY_DIMENSIONS,
    )


def append_candidate(
    state: CanonicalState,
    base_case: dict[str, Any],
    fixture: dict[str, Any],
) -> tuple[CanonicalState, str, str, str]:
    candidate = deepcopy(state)
    original = next(item for item in candidate.facts if item.id == base_case["source_fact_ids"][0])
    overrides = fixture.get("overrides", {})
    gate_id = str(overrides.get("gate_id", base_case["gate_id"]))
    effect_dimension = str(overrides.get("effect_dimension", base_case["effect_dimension"]))
    if gate_id != base_case["gate_id"]:
        original_gate = next(item for item in candidate.gates if item.id == base_case["gate_id"])
        alternative = original_gate.model_copy(deep=True)
        alternative.id = gate_id
        alternative.title = "Examine a different governed consequence"
        alternative.question = "Does this evidence change a different declared Gate consequence?"
        candidate.gates.append(alternative)
    gate_suffix = overrides.get("gate_question_suffix")
    if gate_suffix:
        gate = next(item for item in candidate.gates if item.id == gate_id)
        gate.question = gate.question + str(gate_suffix)
    lifecycle = overrides.get("lifecycle_position")
    if lifecycle:
        candidate.lifecycle_position = type(candidate.lifecycle_position)(lifecycle)
    authority = Authority(overrides.get("authority", original.authority.value))
    status = FreshnessStatus(overrides.get("status", original.status.value))
    candidate_fact = Fact(
        id=fixture["candidate_fact_id"],
        statement=fixture.get("candidate_statement", fixture["candidate_value"]),
        value=fixture["candidate_value"],
        authority=authority,
        evidence_ids=[f"reingested:{fixture['id']}"],
        effective_at=overrides.get("effective_at", original.effective_at),
        affected_slices=original.affected_slices,
        field_key=original.field_key,
        status=status,
        freshness_class=original.freshness_class,
    )
    candidate.facts.append(candidate_fact)
    return bind_gate_contracts(candidate), candidate_fact.id, effect_dimension, gate_id


def serialize_i0(result: RejectionLookup, unchanged: bool) -> dict[str, Any]:
    return {
        "status": result.status,
        "suppressed": result.suppress,
        "identity_match": result.suppress,
        "decision_id": result.decision_id,
        "invalidation_triggers": list(result.invalidation_triggers),
        "lookup_ms": result.lookup_ms,
        "read_only": unchanged,
    }


def serialize_i1(result: GovernedContentRejectionLookup, unchanged: bool) -> dict[str, Any]:
    return {
        "status": result.status,
        "suppressed": result.suppress,
        "content_identity_match": result.content_identity_match,
        "decision_id": result.decision_id,
        "content_hash": result.identity.content_hash,
        "identity_hash": result.identity.identity_hash,
        "gate_version": result.identity.gate_version,
        "identity_construction_ms": result.identity.construction_ms,
        "lookup_ms": result.lookup_ms,
        "invalidation_triggers": list(result.invalidation_triggers),
        "read_only": unchanged,
    }


def identity_results(
    state: CanonicalState,
    *,
    fact_id: str,
    effect_dimension: str,
    gate_id: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    before = state_hash(state)
    i0 = lookup_state_bound_rejection(
        state,
        fact_ids=[fact_id],
        effect_dimension=effect_dimension,
        gate_id=gate_id,
        validity_dimensions=VALIDITY_DIMENSIONS,
    )
    after_i0 = state_hash(state)
    i1 = lookup_governed_content_rejection(
        state,
        fact_ids=[fact_id],
        effect_dimension=effect_dimension,
        gate_id=gate_id,
        validity_dimensions=VALIDITY_DIMENSIONS,
    )
    after_i1 = state_hash(state)
    return serialize_i0(i0, before == after_i0), serialize_i1(i1, before == after_i1)


def true_equivalent_rows(
    contract: dict[str, Any],
    cases: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for fixture in contract["true_equivalents"]:
        base = cases[fixture["base_case_id"]]
        governed = governed_rejection_state(base)
        candidate, fact_id, effect, gate_id = append_candidate(governed, base, fixture)
        i0, i1 = identity_results(
            candidate,
            fact_id=fact_id,
            effect_dimension=effect,
            gate_id=gate_id,
        )
        rows.append(
            {
                "fixture_id": fixture["id"],
                "base_case_id": fixture["base_case_id"],
                "variant": fixture["variant"],
                "semantic_relationship_equivalent": True,
                "candidate_fact_id": fact_id,
                "expected_i0_match": fixture["expected_i0_match"],
                "expected_i1_match": fixture["expected_i1_match"],
                "i0": i0,
                "i1": i1,
            }
        )
    return rows


def near_miss_rows(
    contract: dict[str, Any],
    cases: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for fixture in contract["near_misses"]:
        base = cases[fixture["base_case_id"]]
        governed = governed_rejection_state(base)
        candidate, fact_id, effect, gate_id = append_candidate(governed, base, fixture)
        i0, i1 = identity_results(
            candidate,
            fact_id=fact_id,
            effect_dimension=effect,
            gate_id=gate_id,
        )
        rows.append(
            {
                "fixture_id": fixture["id"],
                "base_case_id": fixture["base_case_id"],
                "expected_preventer": fixture["expected_preventer"],
                "must_suppress": False,
                "i0": i0,
                "i1": i1,
                "false_suppression_i0": i0["suppressed"],
                "false_suppression_i1": i1["suppressed"],
            }
        )
    return rows


def mutate_candidate_value(state: CanonicalState, fact_id: str) -> None:
    fact = next(item for item in state.facts if item.id == fact_id)
    fact.value = fact.value + " materially changed"


def mutate_gate_version(state: CanonicalState, gate_id: str) -> None:
    gate = next(item for item in state.gates if item.id == gate_id)
    gate.question = gate.question + " under changed governed requirements"
    bind_gate_contracts(state)


def mutate_candidate_authority(state: CanonicalState, fact_id: str) -> None:
    fact = next(item for item in state.facts if item.id == fact_id)
    fact.authority = Authority.HUMAN


def mutate_candidate_time(state: CanonicalState, fact_id: str) -> None:
    fact = next(item for item in state.facts if item.id == fact_id)
    fact.status = FreshnessStatus.STALE
    state.lifecycle_position = type(state.lifecycle_position)("currently_serving")


def invalidation_rows(
    contract: dict[str, Any],
    cases: dict[str, dict[str, Any]],
    equivalents: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    fixtures = {item["id"]: item for item in contract["true_equivalents"]}
    rows: list[dict[str, Any]] = []
    for result in equivalents:
        if not result["i1"]["suppressed"]:
            continue
        fixture = fixtures[result["fixture_id"]]
        base = cases[fixture["base_case_id"]]
        governed = governed_rejection_state(base)
        candidate, fact_id, effect, gate_id = append_candidate(governed, base, fixture)
        irrelevant = add_irrelevant_change(candidate, base)
        irrelevant_result = identity_results(
            irrelevant,
            fact_id=fact_id,
            effect_dimension=effect,
            gate_id=gate_id,
        )[1]
        mutation_results: dict[str, dict[str, Any]] = {}
        mutation_names = (
            "material_source_or_evidence_change",
            "gate_version_change",
            "relevant_authority_change",
            "relevant_time_or_lifecycle_change",
        )
        for name in mutation_names:
            changed = deepcopy(candidate)
            if name == "material_source_or_evidence_change":
                mutate_candidate_value(changed, fact_id)
            elif name == "gate_version_change":
                mutate_gate_version(changed, gate_id)
            elif name == "relevant_authority_change":
                mutate_candidate_authority(changed, fact_id)
            else:
                mutate_candidate_time(changed, fact_id)
            mutation_results[name] = identity_results(
                changed,
                fact_id=fact_id,
                effect_dimension=effect,
                gate_id=gate_id,
            )[1]
        rows.append(
            {
                "fixture_id": fixture["id"],
                "irrelevant_canonical_change": irrelevant_result,
                **mutation_results,
                "stale_suppressions": sum(
                    item["suppressed"] for item in mutation_results.values()
                ),
            }
        )
    return rows


def pack_i2_status() -> dict[str, Any]:
    payload = installed_domain_pack_payload()
    serialized = json.dumps(payload, separators=(",", ":"), sort_keys=True).casefold()
    declared_markers = (
        '"relationships"',
        '"relationship_id"',
        '"effect_identities"',
        '"declared_effect_identity"',
    )
    expressible = any(marker in serialized for marker in declared_markers)
    return {
        "status": "EXPRESSIBLE" if expressible else "NOT EXPRESSIBLE IN FROZEN DOMAIN PACK",
        "executed": expressible,
        "domain_pack_id": installed_domain_pack_ref().domain_pack_id,
        "domain_pack_version": installed_domain_pack_ref().version,
        "domain_pack_hash": installed_domain_pack_ref().content_hash,
        "reason": (
            "A frozen structural relationship/effect identity was found."
            if expressible
            else (
                "The installed pack contains service-path boundaries and source provenance, "
                "not a declared relationship/effect identity."
            )
        ),
    }


def scoreboard(
    equivalents: list[dict[str, Any]],
    near_misses: list[dict[str, Any]],
    invalidations: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    scores: dict[str, dict[str, Any]] = {}
    for level in ("i0", "i1"):
        match_key = "identity_match" if level == "i0" else "content_identity_match"
        recognized = sum(item[level]["suppressed"] for item in equivalents)
        false_suppressions = sum(item[level]["suppressed"] for item in near_misses)
        all_suppressions = recognized + false_suppressions
        construction = [
            item[level].get("identity_construction_ms", 0.0)
            for item in equivalents + near_misses
        ]
        lookups = [item[level]["lookup_ms"] for item in equivalents + near_misses]
        scores[level.upper()] = {
            "true_equivalent_cases": len(equivalents),
            "recognized_true_equivalents": recognized,
            "identity_misses": len(equivalents) - recognized,
            "near_miss_cases": len(near_misses),
            "correctly_not_suppressed_near_misses": len(near_misses) - false_suppressions,
            "false_matches": sum(
                item[level][match_key] and not item[level]["suppressed"]
                for item in near_misses
            ),
            "false_suppressions": false_suppressions,
            "stale_suppressions": (
                sum(item["stale_suppressions"] for item in invalidations) if level == "i1" else 0
            ),
            "authority_violations": sum(
                not item[level]["read_only"] for item in equivalents + near_misses
            ),
            "recognition_recall": recognized / len(equivalents),
            "suppression_precision": recognized / all_suppressions if all_suppressions else None,
            "identity_construction_ms": percentile_stats(construction),
            "lookup_ms": percentile_stats(lookups),
        }
    return scores


def deterministic_matrix(contract: dict[str, Any]) -> dict[str, Any]:
    cases = base_cases()
    equivalents = true_equivalent_rows(contract, cases)
    near_misses = near_miss_rows(contract, cases)
    invalidations = invalidation_rows(contract, cases, equivalents)
    scores = scoreboard(equivalents, near_misses, invalidations)
    return {
        "true_equivalents": equivalents,
        "near_misses": near_misses,
        "state_bound_invalidations": invalidations,
        "identity_scoreboard": scores,
        "i2": pack_i2_status(),
    }


def provider_case(fixture: dict[str, Any], base: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": fixture["id"],
        "statement": fixture["candidate_statement"],
        "field_key": base["field_key"],
        "authority": base["authority"],
        "status": base["status"],
        "expected_material": False,
    }


def provider_economics(
    *,
    contract: dict[str, Any],
    deterministic: dict[str, Any],
    harness: ProbeHarness,
    output_path: Path,
    implementation_commit: str,
) -> dict[str, Any]:
    cases = base_cases()
    result_by_id = {item["fixture_id"]: item for item in deterministic["true_equivalents"]}
    attempts: list[dict[str, Any]] = []
    for ordinal, fixture in enumerate(contract["true_equivalents"], start=1):
        attempt = provider_attempt(
            harness,
            provider_case(fixture, cases[fixture["base_case_id"]]),
            attempt_id=f"identity-generalization:{ordinal}:{fixture['id']}",
        )
        row = result_by_id[fixture["id"]]
        attempt["fixture_id"] = fixture["id"]
        attempt["i0_call_incurred"] = True
        attempt["i1_call_avoided"] = row["i1"]["suppressed"]
        attempt["i1_call_incurred"] = not row["i1"]["suppressed"]
        attempt["human_examination_if_incurred"] = int(
            bool(attempt["valid"] and attempt["nominated"])
        )
        attempts.append(attempt)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(
                {
                    "status": "provider_in_progress",
                    "implementation_commit": implementation_commit,
                    "contract_sha256": EXPECTED_CONTRACT_SHA256,
                    "deterministic": deterministic,
                    "provider_attempts": attempts,
                },
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )
    valid_attempts = [item for item in attempts if item["valid"]]
    avoided = [item for item in valid_attempts if item["i1_call_avoided"]]
    incurred = [item for item in valid_attempts if item["i1_call_incurred"]]
    return {
        "attempt_contract": contract["provider_attempt_contract"],
        "attempts": attempts,
        "calls": len(attempts),
        "valid_calls": len(valid_attempts),
        "provider_failures": len(attempts) - len(valid_attempts),
        "total_measured_tokens": sum(item["total_tokens"] for item in valid_attempts),
        "total_measured_cost_usd": sum(item["estimated_cost_usd"] for item in valid_attempts),
        "i1_safely_avoided_calls": len(avoided),
        "i1_safely_avoided_measured_tokens": sum(item["total_tokens"] for item in avoided),
        "i1_safely_avoided_measured_cost_usd": sum(
            item["estimated_cost_usd"] for item in avoided
        ),
        "i1_incurred_calls": len(incurred),
        "i1_incurred_measured_tokens": sum(item["total_tokens"] for item in incurred),
        "i1_incurred_measured_cost_usd": sum(
            item["estimated_cost_usd"] for item in incurred
        ),
        "i1_human_examinations_avoided": sum(
            item["human_examination_if_incurred"] for item in avoided
        ),
        "i1_human_examinations_incurred": sum(
            item["human_examination_if_incurred"] for item in incurred
        ),
        "economic_completeness": "COMPLETE" if len(valid_attempts) == len(attempts) else "INCOMPLETE",
    }


def disposition(deterministic: dict[str, Any]) -> str:
    i1 = deterministic["identity_scoreboard"]["I1"]
    if i1["false_suppressions"] or i1["stale_suppressions"] or i1["authority_violations"]:
        return "GOVERNED IDENTITY GENERALIZATION FALSIFIED"
    if i1["recognized_true_equivalents"] == 0:
        return "DETERMINISTIC IDENTITY BOUNDARY REACHED"
    if i1["recognition_recall"] < 1:
        return "GOVERNED IDENTITY GENERALIZATION SAFE — LIMITED RECOGNITION"
    return "GOVERNED IDENTITY GENERALIZATION SUPPORTED IN FROZEN BATTERY"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=RAW_PATH)
    parser.add_argument("--implementation-commit", required=True)
    parser.add_argument("--skip-provider", action="store_true")
    args = parser.parse_args()
    contract_hash = sha256_path(CONTRACT_PATH)
    base_hash = sha256_path(BASE_CONTRACT_PATH)
    if contract_hash != EXPECTED_CONTRACT_SHA256:
        raise SystemExit(f"Frozen contract hash mismatch: {contract_hash}")
    if base_hash != EXPECTED_BASE_CONTRACT_SHA256:
        raise SystemExit(f"Frozen State-Bound contract hash mismatch: {base_hash}")
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    started = time.perf_counter()
    deterministic = deterministic_matrix(contract)
    provider = (
        {"status": "SKIPPED", "reason": "--skip-provider"}
        if args.skip_provider
        else provider_economics(
            contract=contract,
            deterministic=deterministic,
            harness=ProbeHarness(),
            output_path=args.output,
            implementation_commit=args.implementation_commit,
        )
    )
    result = {
        "status": "completed",
        "contract_id": contract["contract_id"],
        "contract_sha256": contract_hash,
        "base_contract_sha256": base_hash,
        "implementation_commit": args.implementation_commit,
        "execution_timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "duration_ms": (time.perf_counter() - started) * 1000,
        "architecture_classification": contract["architecture_classification"],
        "prohibited_mechanisms_used": [],
        "deterministic": deterministic,
        "provider": provider,
        "engineering_disposition": disposition(deterministic),
        "overall_helm_disposition_preserved": contract["governing_disposition"],
        "canonical_helm_amendment": False,
        "production_mutations": 0,
        "production_probe_enabled": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "disposition": result["engineering_disposition"],
                "scoreboard": deterministic["identity_scoreboard"],
                "provider": provider,
            },
            separators=(",", ":"),
            default=str,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
