from __future__ import annotations

import argparse
import hashlib
import json
import time
from collections.abc import Callable
from copy import deepcopy
from pathlib import Path
from typing import Any

from benchmark.run_capsule_scale_falsification import runtime_cost
from benchmark.run_probe_decisive_falsification import (
    MODEL,
    PROJECT,
    ProbeHarness,
    canonical_json,
    case_state,
    identity_bound_probe_schema,
    probe_payload,
    sha256_json,
)
from military_slices.governance import (
    AuthorityGovernor,
    bind_gate_contracts,
    reconstitute_governance,
    validate_mutation_commit,
)
from military_slices.models import (
    ActorProvenance,
    Authority,
    CanonicalState,
    Decision,
    Fact,
    FreshnessStatus,
    Gate,
    GateState,
    ImpactItem,
    LifecyclePosition,
    SliceName,
    SurfaceType,
)
from military_slices.state_bound_rejection import (
    lookup_state_bound_rejection,
    record_state_bound_rejection,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "benchmark/contracts/state_bound_rejection_falsification_2026-08-27.json"
RAW_PATH = ROOT / "benchmark/output/helm-state-bound-rejection-falsification-raw-2026-08-27.json"
EXPECTED_CONTRACT_SHA256 = "c130b4abfbe048ae2e50fbeba4c31cd8adcbae6d3317ff390d8f9d3d85b37325"
LOCATION = "global"
INTERRUPTED_PROVIDER_ATTEMPTS = [
    {
        "attempt_id": f"superseded-evidence:{phase}:1",
        "status": "provider-completed-evidence-write-failed",
        "failure_class": "HarnessCheckpointFailure",
        "failure": (
            "The provider call returned and the case completed in memory, but the elevated process "
            "could not run git rev-parse before the first checkpoint was written."
        ),
        "response_id": "NOT RETAINED",
        "payload_sha256": "NOT RETAINED",
        "raw_response_sha256": "NOT RETAINED",
        "schema_valid": "NOT MEASURED",
        "identity_valid": "NOT MEASURED",
        "input_tokens": "NOT MEASURED",
        "output_tokens": "NOT MEASURED",
        "total_tokens": "NOT MEASURED",
        "latency_ms": "NOT MEASURED",
        "estimated_cost_usd": "NOT MEASURED",
        "retried_silently": False,
        "included_in_scored_metrics": False,
    }
    for phase in ("A", "B2", "D")
]
SECOND_INTERRUPTED_PROVIDER_ATTEMPTS = [
    {
        "attempt_id": "superseded-evidence:A:scored-round-1",
        "status": "provider-completed-evidence-write-failed",
        "failure_class": "HarnessCaseCheckpointFailure",
        "failure": "The initial call completed, but its case checkpoint had not yet been written.",
        "response_id": "NOT RETAINED",
        "tokens": "NOT MEASURED",
        "latency_ms": "NOT MEASURED",
        "estimated_cost_usd": "NOT MEASURED",
        "retried_silently": False,
        "included_in_scored_metrics": False,
    },
    {
        "attempt_id": "superseded-evidence:B2:scored-round-1",
        "status": "provider-failed",
        "failure_class": "ClientError:429_RESOURCE_EXHAUSTED",
        "failure": "Vertex AI returned HTTP 429 after SDK-level transport handling.",
        "response_id": "NOT AVAILABLE",
        "tokens": "NOT MEASURED",
        "latency_ms": "NOT MEASURED",
        "estimated_cost_usd": "NOT MEASURED",
        "retried_silently": False,
        "included_in_scored_metrics": False,
    },
]
ALL_INTERRUPTED_PROVIDER_ATTEMPTS = (
    INTERRUPTED_PROVIDER_ATTEMPTS + SECOND_INTERRUPTED_PROVIDER_ATTEMPTS
)


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def state_hash(state: CanonicalState) -> str:
    return sha256_json(state.model_dump(mode="json"))


def validity_dimensions(case: dict[str, Any]) -> list[str]:
    triggers = set(case["relevant_invalidation"]["triggers"])
    dimensions = ["authority", "effect_reachability"]
    if "relevant_anchor_change" in triggers:
        dimensions.append("anchor")
    if "relevant_path_change" in triggers:
        dimensions.append("path")
    if "lifecycle_boundary_crossing" in triggers:
        dimensions.append("lifecycle")
    if "validity_expiration" in triggers:
        dimensions.append("time_validity")
    return sorted(dimensions)


def examination_gate(case: dict[str, Any]) -> Gate:
    contract = case["gate_contract"]
    return Gate(
        id=case["gate_id"],
        title=contract["title"],
        question=contract["question"],
        why=contract["why"],
        state=GateState.UNKNOWN,
        surface=SurfaceType.CONFIRM,
        affected_slices=[SliceName(item) for item in contract["affected_slices"]],
        authority_required=Authority(contract["authority_required"]),
        required_evidence=list(contract["required_evidence"]),
        authorized_scope=list(contract["authorized_scope"]),
    )


def initial_state(case: dict[str, Any]) -> CanonicalState:
    state = case_state(case)
    state.gates.append(examination_gate(case))
    return bind_gate_contracts(state)


def actor(state: CanonicalState, event_id: str) -> ActorProvenance:
    return ActorProvenance.trusted_session(
        profile_id=state.profile_id,
        event_id=event_id,
        integrity_ref=f"frozen-state-bound-rejection:{event_id}",
        source_system="synthetic-state-bound-rejection-human",
    )


def provider_attempt(
    harness: ProbeHarness,
    case: dict[str, Any],
    *,
    attempt_id: str,
) -> dict[str, Any]:
    try:
        result = harness.run_attempt(case)
    except Exception as exc:
        payload = probe_payload(case)
        return {
            "attempt_id": attempt_id,
            "expected_case_id": case["id"],
            "payload_sha256": sha256_json(payload),
            "response_id": None,
            "raw_response_sha256": None,
            "schema_valid": False,
            "identity_valid": False,
            "valid": False,
            "failure_class": type(exc).__name__,
            "failure": str(exc),
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "latency_ms": 0.0,
            "estimated_cost_usd": 0.0,
            "model_calls": 1,
            "nominated": None,
            "decision": None,
            "provider_model_version": None,
            "response_schema_sha256": sha256_json(identity_bound_probe_schema(case["id"])),
            "authority_violation": False,
        }
    return {
        "attempt_id": attempt_id,
        "expected_case_id": case["id"],
        "payload_sha256": result.get("payload_sha256"),
        "response_id": result.get("provider_response_id"),
        "raw_response_sha256": result.get("raw_response_sha256"),
        "schema_valid": result.get("schema_valid", False),
        "identity_valid": result.get("identity_valid", False),
        "valid": result.get("valid", False),
        "failure_class": result.get("error_class"),
        "failure": result.get("error"),
        "input_tokens": result.get("input_tokens", 0),
        "output_tokens": result.get("output_tokens", 0),
        "total_tokens": result.get("total_tokens", 0),
        "latency_ms": result.get("latency_ms", 0.0),
        "estimated_cost_usd": result.get("estimated_cost_usd", 0.0),
        "model_calls": result.get("model_calls", 1),
        "nominated": result.get("nominated"),
        "decision": result.get("decision"),
        "provider_model_version": result.get("provider_model_version"),
        "response_schema_sha256": result.get("response_schema_sha256"),
        "authority_violation": False,
    }


def governed_change(
    state: CanonicalState,
    *,
    key: str,
    dependency_refs: list[str],
    mutation_kind: str,
    mutate: Callable[[CanonicalState], None],
) -> CanonicalState:
    previous = deepcopy(state)
    working = deepcopy(state)
    mutate(working)
    working.processed_keys.append(key)
    governed = AuthorityGovernor().record_human_mutation(
        state=working,
        actor=actor(working, f"event-{key}"),
        idempotency_key=key,
        expected_version=previous.version,
        result_version=previous.version + 1,
        dependency_refs=dependency_refs,
        mutation_kind=mutation_kind,
    )
    validate_mutation_commit(previous=previous, updated=governed, expected_version=previous.version)
    return governed


def record_rejection(
    state: CanonicalState,
    case: dict[str, Any],
    *,
    key_suffix: str,
) -> CanonicalState:
    key = f"state-bound-rejection-{case['id']}-{key_suffix}"
    return record_state_bound_rejection(
        state,
        actor=actor(state, f"event-{key}"),
        idempotency_key=key,
        fact_ids=case["source_fact_ids"],
        effect_dimension=case["effect_dimension"],
        gate_id=case["gate_id"],
        validity_dimensions=validity_dimensions(case),
    )


def lookup(state: CanonicalState, case: dict[str, Any], fact_ids: list[str] | None = None) -> dict[str, Any]:
    result = lookup_state_bound_rejection(
        state,
        fact_ids=fact_ids or case["source_fact_ids"],
        effect_dimension=case["effect_dimension"],
        gate_id=case["gate_id"],
        validity_dimensions=validity_dimensions(case),
    )
    return {
        "status": result.status,
        "suppressed": result.suppress,
        "decision_id": result.decision_id,
        "scope_hash": result.identity.scope_hash,
        "identity_hash": result.identity.identity_hash,
        "gate_version": result.identity.gate_version,
        "evidence_lineage_hash": result.identity.evidence_lineage_hash,
        "invalidation_triggers": list(result.invalidation_triggers),
        "lookup_ms": result.lookup_ms,
        "estimated_deterministic_cost_usd": runtime_cost(result.lookup_ms),
    }


def add_irrelevant_change(state: CanonicalState, case: dict[str, Any]) -> CanonicalState:
    item = case["irrelevant_mutation"]

    def mutate(working: CanonicalState) -> None:
        working.facts.append(
            Fact(
                id=item["fact_id"],
                statement=item["statement"],
                value=item["statement"],
                authority=Authority.HUMAN,
                affected_slices=[SliceName.RESUME],
                field_key=item["field_key"],
            )
        )
        working.decisions.append(
            Decision(
                id=f"decision-{item['fact_id']}",
                gate_id="unrelated-profile-maintenance",
                value="unrelated_governed_change",
                authority=Authority.HUMAN,
            )
        )

    return governed_change(
        state,
        key=f"irrelevant-change-{case['id']}",
        dependency_refs=[f"fact:{item['fact_id']}", "scope:unrelated"],
        mutation_kind="unrelated_governed_change",
        mutate=mutate,
    )


def apply_relevant_invalidation(state: CanonicalState, case: dict[str, Any]) -> CanonicalState:
    change = case["relevant_invalidation"]

    def mutate(working: CanonicalState) -> None:
        fact = next(item for item in working.facts if item.id == case["source_fact_ids"][0])
        fact.statement = change["replacement_statement"]
        fact.value = change["replacement_statement"]
        if "replacement_status" in change:
            fact.status = FreshnessStatus(change["replacement_status"])
            working.lifecycle_position = LifecyclePosition.SEPARATED_1_TO_5_YEARS
        if "replacement_anchor" in change:
            working.human_anchor = change["replacement_anchor"]
        if "replacement_path" in change:
            working.path_target_state = change["replacement_path"]
        if "gate_question_suffix" in change:
            gate = next(item for item in working.gates if item.id == case["gate_id"])
            gate.question = gate.question + change["gate_question_suffix"]

    return governed_change(
        state,
        key=f"relevant-invalidation-{case['id']}",
        dependency_refs=[
            *(f"invalidation:{trigger}" for trigger in change["triggers"]),
            f"fact:{case['source_fact_ids'][0]}",
        ],
        mutation_kind="material_rejection_invalidation",
        mutate=mutate,
    )


def accept_after_invalidation(
    state: CanonicalState,
    case: dict[str, Any],
    attempt: dict[str, Any],
) -> CanonicalState:
    if not attempt["valid"] or not attempt["nominated"]:
        return state
    candidate = attempt["decision"]["nomination"]
    candidate_hash = sha256_json(candidate)

    def mutate(working: CanonicalState) -> None:
        fact = next(item for item in working.facts if item.id == case["source_fact_ids"][0])
        working.impacts.append(
            ImpactItem(
                id=f"impact-reconsidered-{case['id']}",
                source_field="governed_probe_examination",
                dependent_field=fact.field_key,
                fact_id=fact.id,
                affected_slice=fact.affected_slices[0],
                message="Authorized examination established a material relationship after invalidation.",
                question="Does this relationship change the current next move?",
                confirm_label="Confirm",
                update_label="Correct",
                blocking=True,
            )
        )
        working.decisions.append(
            Decision(
                id=f"decision-reconsidered-{case['id']}",
                gate_id=case["gate_id"],
                value="candidate_relationship_accepted_after_invalidation",
                authority=Authority.HUMAN,
            )
        )

    return governed_change(
        state,
        key=f"accepted-after-invalidation-{case['id']}",
        dependency_refs=[
            f"candidate-for-examination:sha256:{candidate_hash}",
            f"fact:{case['source_fact_ids'][0]}",
            f"gate:{case['gate_id']}",
        ],
        mutation_kind="probe_candidate_accepted_after_invalidation",
        mutate=mutate,
    )


def structural_variant_state(state: CanonicalState, case: dict[str, Any]) -> tuple[CanonicalState, dict[str, Any]]:
    variant = deepcopy(state)
    item = case["semantic_equivalent_structural_different"]
    original = next(fact for fact in variant.facts if fact.id == case["source_fact_ids"][0])
    variant.facts.append(
        Fact(
            id=item["fact_id"],
            statement=item["statement"],
            value=item["statement"],
            authority=original.authority,
            affected_slices=original.affected_slices,
            field_key=original.field_key,
            status=original.status,
        )
    )
    provider_case = {
        "id": f"{case['id']}-structural-different",
        "statement": item["statement"],
        "field_key": case["field_key"],
        "authority": case["authority"],
        "status": case["status"],
        "expected_material": False,
    }
    return variant, provider_case


def invalidated_provider_case(case: dict[str, Any]) -> dict[str, Any]:
    change = case["relevant_invalidation"]
    return {
        "id": f"{case['id']}-after-invalidation",
        "statement": change["replacement_statement"],
        "field_key": case["field_key"],
        "authority": case["authority"],
        "status": change.get("replacement_status", "valid"),
        "expected_material": True,
    }


def unavailable_attempt(case_id: str, phase: str) -> dict[str, Any]:
    return {
        "attempt_id": f"{case_id}:{phase}:not-repeated-after-interruption",
        "expected_case_id": case_id,
        "payload_sha256": None,
        "response_id": None,
        "raw_response_sha256": None,
        "schema_valid": False,
        "identity_valid": False,
        "valid": False,
        "failure_class": "PriorAttemptEvidenceUnavailable",
        "failure": "The completed or failed prior attempt was preserved and not repeated.",
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "latency_ms": 0.0,
        "estimated_cost_usd": 0.0,
        "model_calls": 0,
        "nominated": None,
        "decision": None,
        "provider_model_version": None,
        "response_schema_sha256": None,
        "authority_violation": False,
    }


def phase_case(
    harness: ProbeHarness | None,
    case: dict[str, Any],
    *,
    use_frozen_rejection_baseline: bool = True,
) -> dict[str, Any]:
    base = initial_state(case)
    base_hash = state_hash(base)
    initial_attempt = (
        provider_attempt(harness, case, attempt_id=f"{case['id']}:A:1")
        if harness is not None
        else unavailable_attempt(case["id"], "A")
    )
    initial_probe_zero_write = state_hash(base) == base_hash
    governed: CanonicalState | None = None
    if (initial_attempt["valid"] and initial_attempt["nominated"]) or use_frozen_rejection_baseline:
        governed = record_rejection(base, case, key_suffix="initial")

    if governed is None:
        b1 = {"status": "UNAVAILABLE", "reason": "Initial Probe did not yield a valid nomination."}
        structural_state = base
    else:
        b1 = lookup(governed, case)
        structural_state = governed

    variant_state, variant_case = structural_variant_state(structural_state, case)
    variant_fact_id = case["semantic_equivalent_structural_different"]["fact_id"]
    b2_lookup = lookup(variant_state, case, [variant_fact_id])
    b2_attempt = (
        provider_attempt(harness, variant_case, attempt_id=f"{case['id']}:B2:1")
        if harness is not None
        else unavailable_attempt(case["id"], "B2")
    )
    b2_human_examinations = int(bool(b2_attempt["valid"] and b2_attempt["nominated"]))
    if b2_human_examinations:
        variant_case_for_record = deepcopy(case)
        variant_case_for_record["source_fact_ids"] = [variant_fact_id]
        record_rejection(variant_state, variant_case_for_record, key_suffix="identity-miss")

    phase_c: dict[str, Any]
    if governed is None:
        phase_c = {"status": "UNAVAILABLE", "reason": "No governed initial rejection."}
        invalidation_base = base
    else:
        version_before = governed.version
        changed = add_irrelevant_change(governed, case)
        phase_c = {
            **lookup(changed, case),
            "canonical_version_before": version_before,
            "canonical_version_after": changed.version,
            "whole_state_changed": state_hash(governed) != state_hash(changed),
        }
        invalidation_base = changed

    phase_d_lookup: dict[str, Any]
    if governed is None:
        phase_d_lookup = {"status": "UNAVAILABLE", "reason": "No governed initial rejection."}
        invalidated = base
    else:
        invalidated = apply_relevant_invalidation(invalidation_base, case)
        phase_d_lookup = lookup(invalidated, case)
    d_attempt = (
        provider_attempt(
            harness,
            invalidated_provider_case(case),
            attempt_id=f"{case['id']}:D:1",
        )
        if harness is not None
        else unavailable_attempt(case["id"], "D")
    )
    accepted = accept_after_invalidation(invalidated, case, d_attempt)
    stale_suppression = int(phase_d_lookup.get("suppressed") is True)
    rejection_decisions = [
        item
        for item in (governed.decisions if governed else [])
        if item.value == "candidate_relationship_rejected"
    ]
    phase_a = {
        "provider": initial_attempt,
        "probe_zero_write": initial_probe_zero_write,
        "rejection_recorded": governed is not None,
        "authoritative_identity": b1.get("identity_hash") if governed else None,
        "scope_hash": b1.get("scope_hash") if governed else None,
        "rejection_decision_count": len(rejection_decisions),
        "rejection_provenance_recorded": bool(
            governed
            and any(
                item.subject_id.startswith("decision:decision-state-bound-rejection-")
                for item in governed.lineage
            )
        ),
        "latent_fact_available": bool(
            governed
            and any(fact.id == case["source_fact_ids"][0] for fact in governed.facts)
        ),
        "blocking_impacts": sum(item.blocking for item in governed.impacts) if governed else 0,
        "dependencies": sum(len(gate.dependencies) for gate in governed.gates) if governed else 0,
        "anchor_unchanged": bool(governed and governed.human_anchor == base.human_anchor),
        "path_unchanged": bool(governed and governed.path_target_state == base.path_target_state),
        "feasibility_unchanged": bool(governed and governed.execution == base.execution),
        "canonical_version_delta": governed.version - base.version if governed else 0,
    }
    return {
        "case_id": case["id"],
        "effect_dimension": case["effect_dimension"],
        "validity_dimensions": validity_dimensions(case),
        "phase_a_initial_rejection": phase_a,
        "phase_b1_exact_structural_repeat": {
            **b1,
            "probe_calls": 0,
            "model_calls": 0,
            "tokens": 0,
            "human_examinations": 0,
        },
        "phase_b2_semantic_equivalent_structural_different": {
            "semantic_relationship_equivalent": True,
            "structural_identity_match": b2_lookup["status"] == "SUPPRESSED",
            "classification": "IDENTITY MISS" if b2_lookup["status"] == "IDENTITY_MISS" else b2_lookup["status"],
            "lookup": b2_lookup,
            "provider": b2_attempt,
            "human_examinations": b2_human_examinations,
        },
        "phase_c_irrelevant_governed_change": {
            **phase_c,
            "probe_calls": 0,
            "model_calls": 0,
            "tokens": 0,
            "human_examinations": 0,
        },
        "phase_d_relevant_invalidation": {
            "declared_triggers": case["relevant_invalidation"]["triggers"],
            "lookup": phase_d_lookup,
            "provider": d_attempt,
            "human_examinations": int(bool(d_attempt["valid"] and d_attempt["nominated"])),
        },
        "phase_e_rejection_becomes_wrong": {
            "expected_now_material": True,
            "stale_suppression": stale_suppression,
            "candidate_reentered_examination": bool(d_attempt["valid"] and d_attempt["nominated"]),
            "accepted_governed_mutation": accepted.version > invalidated.version,
            "blocking_impact_after_authorized_acceptance": any(
                item.id == f"impact-reconsidered-{case['id']}" for item in accepted.impacts
            ),
            "state_hash_before_invalidation": state_hash(invalidation_base),
            "state_hash_after_invalidation": state_hash(invalidated),
            "state_hash_after_authorized_examination": state_hash(accepted),
        },
        "restart": {
            "state_hash_preserved": state_hash(
                reconstitute_governance(
                    CanonicalState.model_validate_json(governed.model_dump_json())
                )
            )
            == state_hash(governed)
            if governed
            else False,
            "suppression_after_restart": lookup(
                reconstitute_governance(CanonicalState.model_validate_json(governed.model_dump_json())),
                case,
            )["status"]
            if governed
            else "UNAVAILABLE",
        },
        "initial_rejection_basis": (
            "current_provider_nomination"
            if initial_attempt["valid"] and initial_attempt["nominated"]
            else "immutable_prior_governed_rejection_baseline"
        ),
    }


def aggregate(cases: list[dict[str, Any]]) -> dict[str, Any]:
    attempts = [
        row[phase]["provider"]
        for row in cases
        for phase in ("phase_a_initial_rejection", "phase_b2_semantic_equivalent_structural_different")
    ] + [row["phase_d_relevant_invalidation"]["provider"] for row in cases]
    exact = [row["phase_b1_exact_structural_repeat"] for row in cases]
    identity = [row["phase_b2_semantic_equivalent_structural_different"] for row in cases]
    irrelevant = [row["phase_c_irrelevant_governed_change"] for row in cases]
    invalidations = [row["phase_d_relevant_invalidation"] for row in cases]
    stale = sum(row["phase_e_rejection_becomes_wrong"]["stale_suppression"] for row in cases)
    authority_violations = sum(int(attempt["authority_violation"]) for attempt in attempts)
    improper_blocking = sum(row["phase_a_initial_rejection"]["blocking_impacts"] for row in cases)
    exact_cost_avoided = sum(
        row["phase_a_initial_rejection"]["provider"]["estimated_cost_usd"]
        for row in cases
        if row["phase_b1_exact_structural_repeat"].get("suppressed") is True
    )
    identity_miss_cost = sum(
        row["provider"]["estimated_cost_usd"]
        for row in identity
        if row["classification"] == "IDENTITY MISS"
    )
    return {
        "initial_rejections": sum(row["phase_a_initial_rejection"]["rejection_recorded"] for row in cases),
        "exact_repeat_count": len(exact),
        "exact_repeat_suppression_hits": sum(row.get("suppressed") is True for row in exact),
        "exact_repeat_suppression_misses": sum(row.get("suppressed") is not True for row in exact),
        "exact_repeat_probe_calls_avoided": sum(row.get("suppressed") is True for row in exact),
        "exact_repeat_examinations_avoided": sum(row.get("suppressed") is True for row in exact),
        "exact_repeat_estimated_model_cost_avoided_usd": exact_cost_avoided,
        "semantic_equivalent_structural_different_count": len(identity),
        "semantic_equivalent_structural_identity_matches": sum(row["structural_identity_match"] for row in identity),
        "identity_misses": sum(row["classification"] == "IDENTITY MISS" for row in identity),
        "identity_miss_probe_calls": sum(
            row["provider"]["model_calls"]
            for row in identity
            if row["classification"] == "IDENTITY MISS"
        ),
        "identity_miss_tokens": sum(
            row["provider"]["total_tokens"]
            for row in identity
            if row["classification"] == "IDENTITY MISS"
        ),
        "identity_miss_human_examinations": sum(
            row["human_examinations"]
            for row in identity
            if row["classification"] == "IDENTITY MISS"
        ),
        "identity_miss_estimated_cost_usd": identity_miss_cost,
        "irrelevant_change_suppression_hits": sum(row.get("suppressed") is True for row in irrelevant),
        "relevant_invalidations": sum(row["lookup"].get("status") == "INVALIDATED" for row in invalidations),
        "false_invalidations": sum(row.get("status") == "INVALIDATED" for row in irrelevant),
        "suppression_after_known_relevant_invalidation": sum(
            row["lookup"].get("suppressed") is True for row in invalidations
        ),
        "stale_suppressions": stale,
        "authority_violations": authority_violations,
        "improper_blocking_state_from_rejection": improper_blocking,
        "provider_calls": sum(attempt["model_calls"] for attempt in attempts),
        "provider_failures": sum(not attempt["valid"] for attempt in attempts),
        "provider_input_tokens": sum(attempt["input_tokens"] for attempt in attempts),
        "provider_output_tokens": sum(attempt["output_tokens"] for attempt in attempts),
        "provider_total_tokens": sum(attempt["total_tokens"] for attempt in attempts),
        "provider_estimated_cost_usd": sum(attempt["estimated_cost_usd"] for attempt in attempts),
        "provider_latency_ms": sum(attempt["latency_ms"] for attempt in attempts),
        "human_examinations": sum(
            row["phase_a_initial_rejection"]["rejection_recorded"]
            + row["phase_b2_semantic_equivalent_structural_different"]["human_examinations"]
            + row["phase_d_relevant_invalidation"]["human_examinations"]
            for row in cases
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=RAW_PATH)
    parser.add_argument("--implementation-commit", required=True)
    parser.add_argument(
        "--do-not-repeat-interrupted-case",
        action="store_true",
        help="Use immutable prior rejection evidence for superseded-evidence and make no new calls.",
    )
    args = parser.parse_args()
    contract_hash = sha256_path(CONTRACT_PATH)
    if contract_hash != EXPECTED_CONTRACT_SHA256:
        raise SystemExit(
            f"Frozen contract hash mismatch: expected {EXPECTED_CONTRACT_SHA256}, got {contract_hash}."
        )
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    harness = ProbeHarness()
    started = time.perf_counter()
    results: list[dict[str, Any]] = []
    for case in contract["cases"]:
        case_harness = (
            None
            if args.do_not_repeat_interrupted_case and case["id"] == "superseded-evidence"
            else harness
        )
        result = phase_case(case_harness, case)
        results.append(result)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(
                {
                    "status": "in_progress",
                    "contract_sha256": contract_hash,
                    "implementation_commit": args.implementation_commit,
                    "interrupted_provider_attempts": ALL_INTERRUPTED_PROVIDER_ATTEMPTS,
                    "completed_cases": results,
                },
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )
    summary = aggregate(results)
    safety_pass = (
        summary["stale_suppressions"] == 0
        and summary["authority_violations"] == 0
        and summary["improper_blocking_state_from_rejection"] == 0
        and summary["suppression_after_known_relevant_invalidation"] == 0
    )
    exact_supported = summary["exact_repeat_suppression_hits"] == summary["exact_repeat_count"]
    if not safety_pass or not exact_supported:
        disposition = "STATE-BOUND REJECTION FALSIFIED"
    elif summary["identity_misses"]:
        disposition = "STATE-BOUND REJECTION SAFE — ECONOMIC VALUE LIMITED BY IDENTITY"
    else:
        disposition = "STATE-BOUND REJECTION SUPPORTED IN FROZEN BATTERY"
    evidence = {
        "status": "completed",
        "experiment": contract["contract_id"],
        "execution_timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "duration_ms": (time.perf_counter() - started) * 1000,
        "contract_sha256": contract_hash,
        "implementation_commit": args.implementation_commit,
        "provider": "Vertex AI",
        "provider_project": PROJECT,
        "provider_location": LOCATION,
        "model": MODEL,
        "predetermined_provider_calls": contract["provider_attempts"]["total_predetermined_calls"],
        "interrupted_provider_attempts": ALL_INTERRUPTED_PROVIDER_ATTEMPTS,
        "total_provider_calls_including_interrupted": (
            summary["provider_calls"] + len(ALL_INTERRUPTED_PROVIDER_ATTEMPTS)
        ),
        "retry_policy": "zero retries",
        "architecture_classification": contract["architecture_classification"],
        "canonical_helm_amendment": False,
        "production_mutations": 0,
        "production_probe_enabled": False,
        "cases": results,
        "summary": summary,
        "safety_gates_pass": safety_pass,
        "engineering_disposition": disposition,
        "preserved_overall_helm_disposition": contract["governing_disposition"],
    }
    args.output.write_text(json.dumps(evidence, indent=2, sort_keys=True), encoding="utf-8")
    print(canonical_json({"output": str(args.output), "summary": summary, "disposition": disposition}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
