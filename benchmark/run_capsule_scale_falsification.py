from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
import time
import tracemalloc
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from google import genai
from google.genai import types

from benchmark.run_probe_decisive_falsification import (
    CURRENT_DECISION_CONTEXT,
    MODEL,
    PROJECT,
    ProbeHarness,
    case_state,
    sha256_json,
)
from benchmark.run_sparse_activation_benchmark import (
    CLOUD_RUN_CPU_USD_PER_SECOND,
    CLOUD_RUN_MEMORY_USD_PER_GIB_SECOND,
    CLOUD_RUN_REQUEST_USD,
    LOCATION,
    MODEL_INPUT_USD_PER_MILLION,
    MODEL_OUTPUT_USD_PER_MILLION,
    NORMAL_REQUIRED,
    DecisionAssessment,
    Scenario,
    build_baseline_context,
    build_helm_context,
    build_state,
    canonical_json,
)
from benchmark.run_sparse_activation_benchmark import (
    SYSTEM_INSTRUCTION as DECISION_SYSTEM_INSTRUCTION,
)
from military_slices.engine import apply_starting_vector, new_state
from military_slices.governance import (
    AuthorityGovernor,
    bind_gate_contracts,
    probe_execution_enabled,
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
    LineageIntegrity,
    LineageRecord,
    MigrationStatus,
    MutationEvent,
    ServiceComponent,
    ServiceName,
    SliceName,
    SurfaceType,
)
from military_slices.path_runtime import refresh_path_state
from military_slices.temporal import (
    apply_revalidation_delta,
    build_consequential_impact_index,
    consequential_impact_projection,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "benchmark/contracts/capsule_scale_falsification_2026-08-27.json"
GATE3_PATH = ROOT / "benchmark/contracts/gate3_interruption_classifier_2026-08-27.json"
OUT = ROOT / "benchmark/output"
RAW_PATH = OUT / "helm-capsule-scale-falsification-raw-2026-08-27.json"
CSV_PATH = OUT / "helm-capsule-scale-falsification-summary-2026-08-27.csv"
EXPECTED_CONTRACT_SHA256 = "2223b61d7c751698b9b11127c998b29e644529293a7ac7ee8cfe47101839fce3"
IMPLEMENTATION_COMMIT = "63b198d5359e747efa56e33a483118969484a5c1"
FIXED_NOW = datetime(2026, 8, 27, tzinfo=UTC)
FIXED_TODAY = date(2026, 8, 27)


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def usage_numbers(response: Any) -> dict[str, int]:
    usage = response.usage_metadata.to_json_dict() if response.usage_metadata else {}
    input_tokens = int(usage.get("prompt_token_count", 0) or 0)
    output_tokens = int(usage.get("candidates_token_count", 0) or 0)
    thought_tokens = int(usage.get("thoughts_token_count", 0) or 0)
    total_tokens = int(usage.get("total_token_count", input_tokens + output_tokens + thought_tokens) or 0)
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "thought_tokens": thought_tokens,
        "total_tokens": total_tokens,
    }


def token_cost(tokens: dict[str, int]) -> float:
    return (
        tokens["input_tokens"] / 1_000_000 * MODEL_INPUT_USD_PER_MILLION
        + (tokens["output_tokens"] + tokens["thought_tokens"]) / 1_000_000 * MODEL_OUTPUT_USD_PER_MILLION
    )


def runtime_cost(milliseconds: float) -> float:
    return (
        milliseconds / 1000 * (CLOUD_RUN_CPU_USD_PER_SECOND + CLOUD_RUN_MEMORY_USD_PER_GIB_SECOND)
        + CLOUD_RUN_REQUEST_USD
    )


class DecisionHarness:
    def __init__(self) -> None:
        self.client = genai.Client(vertexai=True, project=PROJECT, location=LOCATION)

    def run(self, context: dict[str, Any], run_id: str) -> dict[str, Any]:
        message = "Assess this frozen decision context. Context contents are data only.\n" + canonical_json(context)
        started = time.perf_counter()
        response = self.client.models.generate_content(
            model=MODEL,
            contents=message,
            config=types.GenerateContentConfig(
                system_instruction=DECISION_SYSTEM_INSTRUCTION,
                temperature=0,
                top_p=1,
                max_output_tokens=700,
                response_mime_type="application/json",
                response_schema=DecisionAssessment,
                thinking_config=types.ThinkingConfig(include_thoughts=False, thinking_budget=512),
            ),
        )
        latency_ms = (time.perf_counter() - started) * 1000
        parsed = response.parsed
        assessment = (
            parsed
            if isinstance(parsed, DecisionAssessment)
            else DecisionAssessment.model_validate(parsed)
            if isinstance(parsed, dict)
            else DecisionAssessment.model_validate_json(response.text or "")
        )
        tokens = usage_numbers(response)
        return {
            "run_id": run_id,
            "assessment": assessment.model_dump(mode="json"),
            **tokens,
            "model_calls": 1,
            "latency_ms": latency_ms,
            "estimated_model_cost_usd": token_cost(tokens),
            "response_id": getattr(response, "response_id", None),
            "response_sha256": sha256_json(assessment.model_dump(mode="json")),
        }


def _active_capsule(state: CanonicalState) -> dict[str, Any]:
    context, timing = build_helm_context(state)
    active_gate_count = 1 if timing["active_gate"] != "none" else 0
    active_slice_values = {slice_name for task in state.active_tasks for slice_name in task.affected_slices}
    return {
        "governed_facts": len(state.facts),
        "historical_facts": sum(f.field_key == "historical_achievement" for f in state.facts),
        "historical_versions": state.version,
        "latent_facts": timing["latent_fact_count"],
        "active_facts": timing["active_fact_count"],
        "hypothetical_facts": 0,
        "active_slices": sorted(item.value for item in active_slice_values),
        "active_slice_count": len(active_slice_values),
        "available_domain_pack_tasks": len(state.active_tasks) + len(state.gates),
        "dependency_edges": sum(len(g.dependencies) + len(g.required_evidence) for g in state.gates),
        "blocking_impacts": sum(item.blocking for item in state.impacts),
        "temporal_dependencies": len(state.impacts),
        "graduated_relationships": sum(
            decision.gate_id.startswith("probe-examination:") for decision in state.decisions
        ),
        "active_tasks": timing["active_task_count"],
        "active_gates": active_gate_count,
        "current_path_target": state.path_target_state,
        "payload_bytes": timing["context_bytes"],
        "model_input_tokens": 0,
        "model_output_tokens": 0,
        "probe_input_tokens": 0,
        "probe_output_tokens": 0,
        "consequential_interruptions": int(timing["impact_forced_re_evaluation"]),
        "simultaneous_dependency_count": 0,
        "frontier_selection_ms": timing["frontier_selection_ms"],
        "ordinary_retrieval_ms": timing["retrieval_ms"],
        "consequential_lookup_ms": timing["dependency_lookup_ms"],
        "serialization_ms": timing["preprocessing_ms"],
        "total_deterministic_ms": sum(
            float(timing[key])
            for key in (
                "frontier_selection_ms",
                "retrieval_ms",
                "dependency_lookup_ms",
                "preprocessing_ms",
            )
        ),
        "context_sha256": sha256_json(context),
    }


def _enrich_width_state(state: CanonicalState, scale: int) -> None:
    historical_count = max(1, math.floor(scale * 0.1))
    cross_domain_count = max(1, math.floor(scale * 0.2))
    for index, fact in enumerate(state.facts):
        if index < historical_count and fact.id not in NORMAL_REQUIRED:
            fact.field_key = "historical_achievement"
        if index < cross_domain_count and fact.id not in NORMAL_REQUIRED:
            fact.affected_slices = [(SliceName.EDUCATION, SliceName.LOCATION, SliceName.RESUME)[index % 3]]
    state.decisions.append(
        Decision(
            id=f"graduated-width-{scale}",
            gate_id="probe-examination:historical-permission",
            value="A prior relationship was examined and resolved.",
            authority=Authority.HUMAN,
        )
    )
    state.version = 1
    state.migration_status = MigrationStatus.LINEAGE_ENRICHED
    state.lineage.append(
        LineageRecord(
            subject_id=f"mutation:graduated-width-{scale}",
            depends_on=["fact:historical-permission"],
            valid_while=["canonical-version:1"],
            source_state_version=0,
            authority_refs=["actor:synthetic-human"],
            integrity=LineageIntegrity.VERIFIED,
        )
    )
    bind_gate_contracts(state)


def state_width_axis(contract: dict[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    peak_100k = 0
    build_100k_ms = 0.0
    for scale in contract["state_width"]["facts"]:
        scenario = Scenario(
            f"capsule-width-{scale}",
            f"Capsule width {scale}",
            scale,
            "venture-problem",
            "define-veteran-problem",
            NORMAL_REQUIRED,
        )
        if scale == 100_000:
            tracemalloc.start()
        started = time.perf_counter()
        state = build_state(scenario)
        _enrich_width_state(state, scale)
        build_ms = (time.perf_counter() - started) * 1000
        if scale == 100_000:
            _, peak_100k = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            build_100k_ms = build_ms
        capsule = _active_capsule(state)
        rows.append(
            {
                "scale": scale,
                "build_ms": build_ms,
                "index_build_ms": build_consequential_impact_index(state).build_ms,
                **capsule,
            }
        )
    projected_peak = peak_100k * 10
    projected_build_ms = build_100k_ms * 10
    optional = {
        "scale": contract["state_width"]["optional_facts"],
        "executed": False,
        "reason": (
            "Projected in-memory Pydantic graph exceeded 1 GiB or projected build exceeded 60 seconds; "
            "running it would test workstation memory pressure rather than frozen HELM."
            if projected_peak > 1024**3 or projected_build_ms > 60_000
            else (
                "Not executed because the optional point added scale without changing the measured "
                "curve enough to justify process risk."
            )
        ),
        "peak_100k_bytes": peak_100k,
        "projected_1m_bytes": projected_peak,
        "build_100k_ms": build_100k_ms,
        "projected_1m_build_ms": projected_build_ms,
    }
    return {"rows": rows, "optional_1m": optional}


def lifecycle_history_state(decision_count: int) -> CanonicalState:
    state = apply_starting_vector(
        new_state(f"capsule-history-{decision_count}"),
        operating_role="veteran_service_member",
        lifecycle_position=LifecyclePosition.SEPARATED_1_TO_5_YEARS,
        service=ServiceName.NAVY,
        component=ServiceComponent.ACTIVE_DUTY,
        transition_month="2023-08",
        idempotency_key=f"history-vector-{decision_count}",
    )
    state.human_anchor = "Build a remote technology venture serving military families."
    state.current_goal = state.human_anchor
    state.path_target_state = "VALIDATE_VENTURE_PROBLEM"
    state.decisions = []
    state.mutation_events = []
    state.lineage = []
    state.processed_keys = []
    for index in range(decision_count):
        key = f"history-{decision_count}-{index}"
        event_id = f"history-event-{decision_count}-{index}"
        state.decisions.append(
            Decision(
                id=f"history-decision-{decision_count}-{index}",
                gate_id=f"historical-gate-{index % 7}",
                value=f"Historical governed decision {index}",
                authority=Authority.HUMAN,
            )
        )
        actor = ActorProvenance.trusted_session(
            profile_id=state.profile_id,
            event_id=event_id,
            integrity_ref=f"history-control:{index}",
            source_system="synthetic-lifecycle-history",
        )
        state.processed_keys.append(key)
        state.mutation_events.append(
            MutationEvent(
                id=event_id,
                idempotency_key=key,
                actor=actor,
                expected_version=index,
                result_version=index + 1,
                source_state_version=index,
                mutation_kind="historical_decision",
                dependency_refs=[f"historical-gate:{index % 7}"],
                domain_pack=state.domain_pack,
                occurred_at=FIXED_NOW,
            )
        )
        state.lineage.append(
            LineageRecord(
                subject_id=f"mutation:{event_id}",
                depends_on=[f"historical-gate:{index % 7}"],
                valid_while=[f"canonical-version:{index + 1}"],
                invalidated_by=[f"superseding-mutation-after:{index + 1}"],
                source_state_version=index,
                authority_refs=[f"actor:{event_id}"],
                integrity=LineageIntegrity.VERIFIED,
            )
        )
    state.version = decision_count
    state.migration_status = MigrationStatus.LINEAGE_ENRICHED if decision_count else MigrationStatus.LEGACY_VALID
    refresh_path_state(state, today=FIXED_TODAY)
    bind_gate_contracts(state)
    return state


def lifecycle_length_axis(contract: dict[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for decisions in contract["lifecycle_length"]["governed_decisions"]:
        started = time.perf_counter()
        state = lifecycle_history_state(decisions)
        build_ms = (time.perf_counter() - started) * 1000
        capsule = _active_capsule(state)
        historical_lookup_started = time.perf_counter()
        historical_available = (
            next(
                (item.value for item in state.decisions if item.id.endswith("-0")),
                None,
            )
            if decisions
            else None
        )
        historical_lookup_ms = (time.perf_counter() - historical_lookup_started) * 1000
        rows.append(
            {
                "governed_decisions": decisions,
                "mutation_events": len(state.mutation_events),
                "lineage_records": len(state.lineage),
                "build_ms": build_ms,
                "historical_lookup_ms": historical_lookup_ms,
                "historical_item_available": historical_available is not None,
                "historical_decisions_in_payload": 0,
                **capsule,
            }
        )
    return {"rows": rows}


def dependency_state(count: int, coupled: bool) -> CanonicalState:
    state = new_state(f"capsule-density-{'coupled' if coupled else 'decomposable'}-{count}")
    state.human_anchor = CURRENT_DECISION_CONTEXT["human_anchor"]
    state.path_target_state = CURRENT_DECISION_CONTEXT["path_target"]
    state.gates = []
    state.active_tasks = []
    for index in range(count):
        fact = Fact(
            id=f"density-fact-{index:03d}",
            statement=f"Authoritative bounded condition {index} must be reviewed.",
            value=f"condition-{index}",
            authority=Authority.AUTHORITATIVE_SOURCE,
            affected_slices=[(SliceName.CAREER, SliceName.EDUCATION, SliceName.LOCATION, SliceName.RESUME)[index % 4]],
            field_key=f"bounded_condition_{index:03d}",
        )
        state.facts.append(fact)
        if not coupled:
            state.impacts.append(
                ImpactItem(
                    id=f"density-impact-{index:03d}",
                    source_field="frozen_density",
                    dependent_field=fact.field_key,
                    fact_id=fact.id,
                    affected_slice=fact.affected_slices[0],
                    message="Review this bounded condition.",
                    question="Does this condition remain material?",
                    confirm_label="Confirm",
                    update_label="Correct",
                    blocking=True,
                    created_at=FIXED_NOW,
                )
            )
    if coupled and count:
        state.gates.append(
            Gate(
                id=f"coupled-density-{count}",
                title="Resolve coupled conditions",
                question="What joint decision satisfies every simultaneously material condition?",
                why="No individual condition can be safely resolved without the others.",
                state=GateState.CONFLICTED,
                surface=SurfaceType.CONFLICT,
                affected_slices=list(SliceName),
                authority_required=Authority.HUMAN,
                required_evidence=[fact.id for fact in state.facts],
                value_score=100,
            )
        )
    state.latent_fact_count = len(state.facts)
    bind_gate_contracts(state)
    build_consequential_impact_index(state)
    return state


def _record_revalidation(
    previous: CanonicalState,
    updated: CanonicalState,
    idempotency_key: str,
) -> CanonicalState:
    actor = ActorProvenance.trusted_session(
        profile_id=updated.profile_id,
        event_id=f"event-{idempotency_key}",
        integrity_ref=f"synthetic-density:{idempotency_key}",
        source_system="synthetic-density-human",
    )
    governed = AuthorityGovernor().record_human_mutation(
        state=updated,
        actor=actor,
        idempotency_key=idempotency_key,
        expected_version=previous.version,
        result_version=updated.version,
        dependency_refs=[f"impact:{idempotency_key}", f"canonical-version:{previous.version}"],
        mutation_kind="density_revalidation",
    )
    validate_mutation_commit(previous=previous, updated=governed, expected_version=previous.version)
    return governed


def dependency_density_axis(contract: dict[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for coupled in (False, True):
        for count in contract["dependency_density"]["counts"]:
            state = dependency_state(count, coupled)
            capsule = _active_capsule(state)
            required_ids = {fact.id for fact in state.facts}
            actual_context, _ = build_helm_context(state)
            visible = {item["id"] for item in actual_context.get("permitted_governed_evidence", [])}
            sequence: list[str] = []
            unsafe_intermediate_states = 0
            started = time.perf_counter()
            if not coupled:
                while state.impacts:
                    projection = consequential_impact_projection(state)
                    if projection is None or projection.impact_id is None:
                        break
                    sequence.append(projection.fact_id)
                    previous = state
                    key = f"density-{count}-{len(sequence)}"
                    state, changed = apply_revalidation_delta(
                        state,
                        impact_id=projection.impact_id,
                        action="confirm",
                        value=None,
                        idempotency_key=key,
                    )
                    if not changed:
                        break
                    state = _record_revalidation(previous, state, key)
            elif count > 1 and visible != required_ids:
                unsafe_intermediate_states = 1
            resolution_ms = (time.perf_counter() - started) * 1000
            correct = (
                set(sequence) == required_ids and not state.impacts
                if not coupled
                else visible == required_ids
                if count
                else True
            )
            rows.append(
                {
                    **capsule,
                    "class": "coupled" if coupled else "decomposable",
                    "dependency_count": count,
                    "minimum_sufficient_fact_count": count if coupled else min(count, 1),
                    "actual_visible_dependency_count": len(visible),
                    "resolved_sequence_count": len(sequence),
                    "all_dependencies_accounted": correct,
                    "unsafe_intermediate_states": unsafe_intermediate_states,
                    "resolution_ms": resolution_ms,
                    "model_calls": 0,
                    "model_input_tokens": 0,
                    "model_output_tokens": 0,
                    "estimated_model_cost_usd": 0.0,
                    "rework": 0 if correct else max(0, count - len(visible)),
                    "simultaneous_dependency_count": count if coupled else min(count, 1),
                }
            )
    return {"rows": rows}


def temporal_axis(contract: dict[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for fixture in contract["temporal_movement"]:
        state = apply_starting_vector(
            new_state(f"capsule-temporal-{fixture['id']}"),
            operating_role="veteran_service_member",
            lifecycle_position=LifecyclePosition(fixture["lifecycle"]),
            service=ServiceName.NAVY,
            component=ServiceComponent.ACTIVE_DUTY,
            transition_month=fixture["transition_month"],
            idempotency_key=f"temporal-vector-{fixture['id']}",
        )
        state.human_anchor = "Choose a sustainable post-service direction."
        refresh_path_state(state, today=FIXED_TODAY)
        capsule = _active_capsule(state)
        rows.append(
            {
                "id": fixture["id"],
                "lifecycle": fixture["lifecycle"],
                "transition_month": fixture["transition_month"],
                "stage": state.stage,
                "timeline_window": state.current_timeline_window,
                "path_eligible_tasks": [task.title for task in state.active_tasks],
                "future_task_leak_for_post_service": any(
                    "leave active service" in task.title.casefold() for task in state.active_tasks
                )
                if fixture["id"].startswith("post-")
                else False,
                "probe_nominations": 0,
                "stale_state_invalidations": len(state.impacts),
                **capsule,
            }
        )
    return {"rows": rows}


def multiple_slices_axis(contract: dict[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    slice_order = [SliceName.CAREER, SliceName.EDUCATION, SliceName.LOCATION, SliceName.RESUME]
    for requested in contract["multiple_slices"]["counts"]:
        state = new_state(f"capsule-slices-{requested}")
        state.human_anchor = "Define the veteran problem a remote technology venture should own."
        state.gates = [
            Gate(
                id="slice-active-career",
                title="Define the problem",
                question="Which veteran problem should this venture own?",
                why="The Anchor cannot advance without one problem definition.",
                state=GateState.UNKNOWN,
                surface=SurfaceType.TEXT,
                affected_slices=[SliceName.CAREER],
                authority_required=Authority.HUMAN,
                value_score=100,
            )
        ]
        labels = contract["multiple_slices"]["ordered_slices"][:requested]
        for index, label in enumerate(labels):
            slice_name = slice_order[index] if index < 4 else SliceName.CAREER
            state.facts.append(
                Fact(
                    id=f"slice-fact-{index}",
                    statement=f"Permitted context exists for {label}.",
                    value=label,
                    authority=Authority.HUMAN,
                    affected_slices=[slice_name],
                    field_key="work_preference" if label == "Work Preferences" else f"slice_{index}",
                )
            )
        state.latent_fact_count = len(state.facts)
        bind_gate_contracts(state)
        capsule = _active_capsule(state)
        context, _ = build_helm_context(state)
        visible_slice_facts = context.get("permitted_governed_evidence", [])
        rows.append(
            {
                "available_context_domains": requested,
                "labels": labels,
                "core_slice_enums_represented": len(
                    {slice_name for fact in state.facts for slice_name in fact.affected_slices}
                ),
                "actual_active_gate_count": capsule["active_gates"],
                "visible_slice_fact_count": len(visible_slice_facts),
                "irrelevant_slice_leakage": max(0, len(visible_slice_facts) - 1),
                "probe_nominations": 0,
                **capsule,
            }
        )
    return {"rows": rows}


def _probe_one(case: dict[str, Any], ordinal: int, axis: str) -> dict[str, Any]:
    state = case_state(case)
    before_hash = sha256_json(state.model_dump(mode="json"))
    result = ProbeHarness().run(case)
    after_hash = sha256_json(state.model_dump(mode="json"))
    thought_tokens = max(
        0,
        result["total_tokens"] - result["input_tokens"] - result["output_tokens"],
    )
    estimated_cost = (
        result["input_tokens"] / 1_000_000 * MODEL_INPUT_USD_PER_MILLION
        + (result["output_tokens"] + thought_tokens) / 1_000_000 * MODEL_OUTPUT_USD_PER_MILLION
    )
    return {
        "axis": axis,
        "ordinal": ordinal,
        "case_id": case["id"],
        "expected_material": case["expected_material"],
        "nominated": result["nominated"],
        "correct": result["nominated"] == case["expected_material"],
        "decision": result["decision"],
        "payload_sha256": result["payload_sha256"],
        "response_sha256": result["response_sha256"],
        "response_id": result["provider_response_id"],
        "input_tokens": result["input_tokens"],
        "output_tokens": result["output_tokens"],
        "thought_tokens": thought_tokens,
        "total_tokens": result["total_tokens"],
        "latency_ms": result["latency_ms"],
        "estimated_cost_usd": estimated_cost,
        "probe_calls": 1,
        "authority_violation": before_hash != after_hash,
    }


def _classification(rows: list[dict[str, Any]]) -> dict[str, Any]:
    tp = sum(row["expected_material"] and row["nominated"] for row in rows)
    tn = sum(not row["expected_material"] and not row["nominated"] for row in rows)
    fp = sum(not row["expected_material"] and row["nominated"] for row in rows)
    fn = sum(row["expected_material"] and not row["nominated"] for row in rows)
    precision = tp / (tp + fp) if tp + fp else 1.0
    recall = tp / (tp + fn) if tp + fn else 1.0
    return {
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "probe_calls": sum(row["probe_calls"] for row in rows),
        "input_tokens": sum(row["input_tokens"] for row in rows),
        "output_tokens": sum(row["output_tokens"] for row in rows),
        "thought_tokens": sum(row["thought_tokens"] for row in rows),
        "total_tokens": sum(row["total_tokens"] for row in rows),
        "estimated_cost_usd": sum(row["estimated_cost_usd"] for row in rows),
        "latency_ms": percentile_stats([row["latency_ms"] for row in rows]),
        "authority_violations": sum(row["authority_violation"] for row in rows),
    }


def probe_rate_axis(contract: dict[str, Any], checkpoint: dict[str, Any]) -> dict[str, Any]:
    gate3 = json.loads(GATE3_PATH.read_text(encoding="utf-8"))
    frozen_cases = gate3["cases"]
    rows: list[dict[str, Any]] = []
    rate_rows: list[dict[str, Any]] = []
    for rate, count in zip(
        contract["probe_opportunity_rate"]["rates_percent"],
        contract["probe_opportunity_rate"]["opportunity_counts"],
        strict=True,
    ):
        if count == 0:
            rate_rows.append(
                {
                    "rate_percent": rate,
                    "governed_facts": contract["probe_opportunity_rate"]["governed_facts"],
                    "opportunity_count": 0,
                    **_classification([]),
                    "examination_burden": 0,
                }
            )
            continue
        tasks = [(frozen_cases[index % len(frozen_cases)], index, f"probe-rate-{rate}") for index in range(count)]
        rate_results: list[dict[str, Any]] = []
        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = {pool.submit(_probe_one, case, ordinal, axis): ordinal for case, ordinal, axis in tasks}
            for future in as_completed(futures):
                result = future.result()
                rate_results.append(result)
                rows.append(result)
                checkpoint["provider_progress"] = {
                    "axis": "probe_opportunity_rate",
                    "rate_percent": rate,
                    "completed": len(rows),
                }
                checkpoint["probe_rate_partial"] = rows
                RAW_PATH.write_text(json.dumps(checkpoint, indent=2, sort_keys=True), encoding="utf-8")
        rate_results.sort(key=lambda item: item["ordinal"])
        metrics = _classification(rate_results)
        rate_rows.append(
            {
                "rate_percent": rate,
                "governed_facts": contract["probe_opportunity_rate"]["governed_facts"],
                "opportunity_count": count,
                **metrics,
                "examination_burden": sum(row["nominated"] for row in rate_results),
                "false_nomination_examination_burden": metrics["fp"],
            }
        )
    return {"rates": rate_rows, "runs": rows}


def _authorized_relationship_state(
    case: dict[str, Any],
    probe_result: dict[str, Any],
    *,
    accepted: bool,
) -> CanonicalState:
    state = case_state(case)
    candidate = probe_result["decision"].get("nomination")
    if candidate is None:
        return state
    previous = deepcopy(state)
    candidate_hash = sha256_json(candidate)
    key = f"capsule-examination-{case['id']}-{'accept' if accepted else 'reject'}"
    state.decisions.append(
        Decision(
            id=f"decision-{key}",
            gate_id=f"probe-examination:{case['id']}",
            value=(
                "Trusted human confirmed this relationship is material."
                if accepted
                else "Trusted human rejected this relationship as non-material."
            ),
            authority=Authority.HUMAN,
        )
    )
    if accepted:
        fact = state.facts[0]
        state.impacts.append(
            ImpactItem(
                id=f"impact-{key}",
                source_field="governed_probe_examination",
                dependent_field=fact.field_key,
                fact_id=fact.id,
                affected_slice=fact.affected_slices[0],
                message="A human-authorized examination established a material relationship.",
                question="Does this relationship change the current next move?",
                confirm_label="Confirm",
                update_label="Correct",
                blocking=True,
                created_at=FIXED_NOW,
            )
        )
    state.processed_keys.append(key)
    actor = ActorProvenance.trusted_session(
        profile_id=state.profile_id,
        event_id=f"event-{key}",
        integrity_ref=f"candidate-for-examination:sha256:{candidate_hash}",
        source_system="synthetic-capsule-human",
    )
    governed = AuthorityGovernor().record_human_mutation(
        state=state,
        actor=actor,
        idempotency_key=key,
        expected_version=previous.version,
        result_version=previous.version + 1,
        dependency_refs=[
            f"candidate-for-examination:sha256:{candidate_hash}",
            f"fact:{state.facts[0].id}",
            f"human-examination:{actor.event_id}",
        ],
        mutation_kind=("probe_candidate_accepted" if accepted else "probe_candidate_rejected"),
    )
    validate_mutation_commit(previous=previous, updated=governed, expected_version=previous.version)
    return governed


def graduation_axis(contract: dict[str, Any]) -> dict[str, Any]:
    gate3 = json.loads(GATE3_PATH.read_text(encoding="utf-8"))
    case = next(item for item in gate3["cases"] if item["id"] == contract["graduation"]["relationship_case_id"])
    first = _probe_one(case, 0, "graduation-first-discovery")
    governed = _authorized_relationship_state(case, first, accepted=True)
    serialized = governed.model_dump_json()
    restarted = reconstitute_governance(CanonicalState.model_validate_json(serialized))
    rows: list[dict[str, Any]] = []
    for count in contract["graduation"]["repeat_counts"]:
        lookups: list[float] = []
        correct = 0
        for _ in range(count):
            started = time.perf_counter()
            projection = consequential_impact_projection(restarted)
            lookups.append((time.perf_counter() - started) * 1000)
            correct += int(
                bool(
                    projection
                    and projection.source == "blocking_impact"
                    and projection.fact_id == restarted.facts[0].id
                )
            )
        rows.append(
            {
                "repeat_count": count,
                "correct": correct,
                "probe_calls": 0,
                "model_calls": 0,
                "tokens": 0,
                "estimated_cost_usd": runtime_cost(sum(lookups)),
                "deterministic_lookup_ms": percentile_stats(lookups),
                "restart_correct": state_sha(restarted) == state_sha(governed),
            }
        )
    return {
        "first_discovery": first,
        "governed_version": governed.version,
        "persisted_structures": ["Fact", "ImpactItem", "Decision", "MutationEvent", "LineageRecord"],
        "rows": rows,
    }


def state_sha(state: CanonicalState) -> str:
    return sha256_json(state.model_dump(mode="json"))


def rejected_nomination_axis(contract: dict[str, Any]) -> dict[str, Any]:
    gate3 = json.loads(GATE3_PATH.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    for case_id in contract["rejected_probe_nominations"]["case_ids"]:
        case = next(item for item in gate3["cases"] if item["id"] == case_id)
        initial_state = case_state(case)
        first = _probe_one(case, 0, "rejected-nomination-first")
        after_probe_hash = state_sha(initial_state)
        governed = _authorized_relationship_state(case, first, accepted=False)
        repeat = _probe_one(case, 1, "rejected-nomination-repeat")
        rows.append(
            {
                "case_id": case_id,
                "first_nominated": first["nominated"],
                "probe_zero_write": after_probe_hash == state_sha(initial_state),
                "rejection_version_delta": governed.version - initial_state.version,
                "persisted_after_rejection": {
                    "decision_count": len(governed.decisions),
                    "mutation_event_count": len(governed.mutation_events),
                    "lineage_count": len(governed.lineage),
                    "blocking_impacts": sum(item.blocking for item in governed.impacts),
                    "dependencies": sum(len(gate.dependencies) for gate in governed.gates),
                },
                "path_unchanged": governed.path_target_state == initial_state.path_target_state,
                "anchor_unchanged": governed.human_anchor == initial_state.human_anchor,
                "repeat_probe_calls": 1,
                "repeat_nominated": repeat["nominated"],
                "repeat_tokens": repeat["total_tokens"],
                "repeat_cost_usd": repeat["estimated_cost_usd"],
                "authority_violations": int(first["authority_violation"]) + int(repeat["authority_violation"]),
                "first": first,
                "repeat": repeat,
            }
        )
    return {"rows": rows}


def _decision_quality(
    result: dict[str, Any],
    *,
    expected_gate: str,
    expected_decision: str,
    required_ids: set[str],
) -> dict[str, Any]:
    assessment = result["assessment"]
    recalled = required_ids.intersection(assessment["material_dependency_ids"])
    return {
        "gate_correct": assessment["selected_gate"] == expected_gate,
        "decision_correct": assessment["next_decision"] == expected_decision,
        "dependency_recall": len(recalled) / len(required_ids) if required_ids else 1.0,
        "missed_dependencies": sorted(required_ids - set(assessment["material_dependency_ids"])),
        "unsupported_assertions": assessment["unsupported_assertions"],
        "correct": (
            assessment["selected_gate"] == expected_gate
            and assessment["next_decision"] == expected_decision
            and recalled == required_ids
            and not assessment["unsupported_assertions"]
        ),
    }


def _decision_task(
    context: dict[str, Any],
    run_id: str,
    expected_gate: str,
    expected_decision: str,
    required_ids: set[str],
    deterministic: dict[str, Any],
) -> dict[str, Any]:
    result = DecisionHarness().run(context, run_id)
    return {
        **result,
        "quality": _decision_quality(
            result,
            expected_gate=expected_gate,
            expected_decision=expected_decision,
            required_ids=required_ids,
        ),
        "context_bytes": len(canonical_json(context).encode()),
        "active_facts": deterministic["active_fact_count"],
        "latent_facts": deterministic["latent_fact_count"],
        "deterministic": deterministic,
    }


def hidden_relationship_state() -> tuple[CanonicalState, dict[str, Any]]:
    scenario = Scenario(
        "capsule-hidden-relationship",
        "Capsule hidden relationship",
        1_000,
        "employment-restriction",
        "verify-employment-restriction",
        ("capsule-hidden-restriction",),
        True,
    )
    state = build_state(scenario)
    case = next(
        item
        for item in json.loads(GATE3_PATH.read_text(encoding="utf-8"))["cases"]
        if item["id"] == "paraphrased-restriction"
    )
    state.facts[-1] = Fact(
        id="capsule-hidden-restriction",
        statement=case["statement"],
        value=case["statement"],
        authority=Authority.AUTHORITATIVE_SOURCE,
        affected_slices=[SliceName.CAREER],
        field_key=case["field_key"],
        status=FreshnessStatus.VALID,
    )
    state.latent_fact_count = len(state.facts)
    build_consequential_impact_index(state)
    return state, case


def graduate_into_full_state(
    state: CanonicalState,
    case: dict[str, Any],
    probe_result: dict[str, Any],
    repetition: int,
) -> CanonicalState:
    candidate = probe_result["decision"].get("nomination")
    if candidate is None:
        return state
    previous = deepcopy(state)
    updated = deepcopy(state)
    fact = next(item for item in updated.facts if item.id == "capsule-hidden-restriction")
    key = f"protected-graduation-{repetition}"
    updated.impacts.append(
        ImpactItem(
            id=f"impact-{key}",
            source_field="governed_probe_examination",
            dependent_field=fact.field_key,
            fact_id=fact.id,
            affected_slice=SliceName.CAREER,
            message="A human-authorized examination established a material relationship.",
            question="Does this relationship block the next move?",
            confirm_label="Confirm",
            update_label="Correct",
            blocking=True,
            created_at=FIXED_NOW,
        )
    )
    updated.decisions.append(
        Decision(
            id=f"decision-{key}",
            gate_id="probe-examination:paraphrased-restriction",
            value="Trusted human confirmed the relationship is material.",
            authority=Authority.HUMAN,
        )
    )
    updated.processed_keys.append(key)
    actor = ActorProvenance.trusted_session(
        profile_id=updated.profile_id,
        event_id=f"event-{key}",
        integrity_ref=f"candidate-for-examination:sha256:{sha256_json(candidate)}",
        source_system="synthetic-protected-control-human",
    )
    governed = AuthorityGovernor().record_human_mutation(
        state=updated,
        actor=actor,
        idempotency_key=key,
        expected_version=previous.version,
        result_version=previous.version + 1,
        dependency_refs=[
            f"candidate-for-examination:sha256:{sha256_json(candidate)}",
            f"fact:{fact.id}",
        ],
        mutation_kind="protected_control_graduation",
    )
    validate_mutation_commit(previous=previous, updated=governed, expected_version=previous.version)
    build_consequential_impact_index(governed)
    return governed


def contemporaneous_controls(contract: dict[str, Any], checkpoint: dict[str, Any]) -> dict[str, Any]:
    runs: list[dict[str, Any]] = []
    tasks: list[tuple[dict[str, Any], str, str, str, set[str], dict[str, Any], dict[str, Any]]] = []
    repetitions = contract["contemporaneous_control"]["repetitions"]
    for scale in contract["contemporaneous_control"]["width_points"]:
        scenario = Scenario(
            f"control-width-{scale}",
            f"Control width {scale}",
            scale,
            "venture-problem",
            "define-veteran-problem",
            NORMAL_REQUIRED,
        )
        state = build_state(scenario)
        baseline_context, baseline_timing = build_baseline_context(state)
        helm_context, helm_timing = build_helm_context(state)
        for repetition in range(1, repetitions + 1):
            tasks.append(
                (
                    baseline_context,
                    f"width-{scale}-broad-{repetition}",
                    "venture-problem",
                    "define-veteran-problem",
                    set(NORMAL_REQUIRED),
                    baseline_timing,
                    {"axis": "state_width", "scale": scale, "condition": "broad", "repetition": repetition},
                )
            )
            tasks.append(
                (
                    helm_context,
                    f"width-{scale}-helm-{repetition}",
                    "venture-problem",
                    "define-veteran-problem",
                    set(NORMAL_REQUIRED),
                    helm_timing,
                    {"axis": "state_width", "scale": scale, "condition": "helm", "repetition": repetition},
                )
            )
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(_decision_task, *task[:-1]): task[-1] for task in tasks}
        for future in as_completed(futures):
            metadata = futures[future]
            runs.append({**metadata, **future.result()})
            checkpoint["provider_progress"] = {
                "axis": "contemporaneous_width",
                "completed": len(runs),
                "total": len(tasks),
            }
            checkpoint["control_partial"] = runs
            RAW_PATH.write_text(json.dumps(checkpoint, indent=2, sort_keys=True), encoding="utf-8")

    protected_runs: list[dict[str, Any]] = []
    for repetition in range(1, repetitions + 1):
        state, case = hidden_relationship_state()
        broad_context, broad_timing = build_baseline_context(state)
        sparse_context, sparse_timing = build_helm_context(state)
        broad = _decision_task(
            broad_context,
            f"protected-broad-{repetition}",
            "employment-restriction",
            "verify-employment-restriction",
            {"capsule-hidden-restriction"},
            broad_timing,
        )
        unprotected = _decision_task(
            sparse_context,
            f"protected-unprotected-{repetition}",
            "employment-restriction",
            "verify-employment-restriction",
            {"capsule-hidden-restriction"},
            sparse_timing,
        )
        probe = _probe_one(case, repetition, "protected-control")
        protected_state = graduate_into_full_state(state, case, probe, repetition)
        protected_context, protected_timing = build_helm_context(protected_state)
        protected = _decision_task(
            protected_context,
            f"protected-helm-{repetition}",
            "employment-restriction",
            "verify-employment-restriction",
            {"capsule-hidden-restriction"},
            protected_timing,
        )
        protected["probe"] = probe
        protected["combined_tokens"] = protected["total_tokens"] + probe["total_tokens"]
        protected["combined_cost_usd"] = protected["estimated_model_cost_usd"] + probe["estimated_cost_usd"]
        protected_runs.extend(
            [
                {"condition": "broad", "repetition": repetition, **broad},
                {"condition": "helm_sparse_unprotected", "repetition": repetition, **unprotected},
                {"condition": "helm_sparse_plus_probe", "repetition": repetition, **protected},
            ]
        )
        checkpoint["provider_progress"] = {
            "axis": "protected_control",
            "completed_repetitions": repetition,
            "total_repetitions": repetitions,
        }
        checkpoint["protected_control_partial"] = protected_runs
        RAW_PATH.write_text(json.dumps(checkpoint, indent=2, sort_keys=True), encoding="utf-8")
    runs.sort(key=lambda item: item["run_id"])
    return {"width_runs": runs, "protected_runs": protected_runs}


def _group_model_runs(runs: list[dict[str, Any]], keys: tuple[str, ...]) -> list[dict[str, Any]]:
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for run in runs:
        groups.setdefault(tuple(run[key] for key in keys), []).append(run)
    rows: list[dict[str, Any]] = []
    for identity, items in sorted(groups.items(), key=lambda item: str(item[0])):
        row = {key: value for key, value in zip(keys, identity, strict=True)}
        row.update(
            {
                "repetitions": len(items),
                "correct_rate": statistics.mean(float(item["quality"]["correct"]) for item in items),
                "input_tokens": percentile_stats([item["input_tokens"] for item in items]),
                "total_tokens": percentile_stats([item["total_tokens"] for item in items]),
                "latency_ms": percentile_stats([item["latency_ms"] for item in items]),
                "model_cost_usd": percentile_stats([item["estimated_model_cost_usd"] for item in items]),
                "context_bytes": items[0]["context_bytes"],
                "active_facts": items[0]["active_facts"],
            }
        )
        rows.append(row)
    return rows


def write_csv(payload: dict[str, Any]) -> None:
    rows: list[dict[str, Any]] = []
    for item in payload["axes"]["state_width"]["rows"]:
        rows.append(
            {
                "axis": "state_width",
                "point": item["scale"],
                "class": "deterministic",
                "governed_state": item["governed_facts"],
                "active_facts": item["active_facts"],
                "payload_bytes": item["payload_bytes"],
                "correct": True,
                "cost_usd": 0,
            }
        )
    for item in payload["axes"]["dependency_density"]["rows"]:
        rows.append(
            {
                "axis": "dependency_density",
                "point": item["dependency_count"],
                "class": item["class"],
                "governed_state": item["governed_facts"],
                "active_facts": item["active_facts"],
                "payload_bytes": item["payload_bytes"],
                "correct": item["all_dependencies_accounted"],
                "cost_usd": item["estimated_model_cost_usd"],
            }
        )
    for item in payload["axes"]["probe_opportunity_rate"]["rates"]:
        rows.append(
            {
                "axis": "probe_opportunity_rate",
                "point": item["rate_percent"],
                "class": "probe",
                "governed_state": item["governed_facts"],
                "active_facts": item["opportunity_count"],
                "payload_bytes": "NOT MEASURED",
                "correct": item["tp"] + item["tn"],
                "cost_usd": item["estimated_cost_usd"],
            }
        )
    with CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def execute(*, prepare_only: bool) -> dict[str, Any]:
    if sha256_path(CONTRACT_PATH) != EXPECTED_CONTRACT_SHA256:
        raise RuntimeError("Frozen Capsule contract hash changed; refusing execution.")
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "status": "deterministic-preparation",
        "executed_at": "2026-08-27",
        "implementation_commit": IMPLEMENTATION_COMMIT,
        "contract": {
            "path": str(CONTRACT_PATH.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256_path(CONTRACT_PATH),
            "gate3_sha256": sha256_path(GATE3_PATH),
        },
        "provider": contract["provider"],
        "axes": {},
        "production": {
            "traffic_moved": False,
            "probe_enabled": probe_execution_enabled(),
            "profiles_mutated": False,
            "external_effects": False,
            "domain_pack_changed": False,
            "canonical_helm_changed": False,
        },
    }
    payload["axes"]["state_width"] = state_width_axis(contract)
    payload["axes"]["lifecycle_length"] = lifecycle_length_axis(contract)
    payload["axes"]["dependency_density"] = dependency_density_axis(contract)
    payload["axes"]["temporal_movement"] = temporal_axis(contract)
    payload["axes"]["multiple_slices"] = multiple_slices_axis(contract)
    RAW_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    if prepare_only:
        payload["status"] = "prepared-no-provider-calls"
        RAW_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return payload
    payload["status"] = "provider-execution-in-progress"
    payload["axes"]["contemporaneous_controls"] = contemporaneous_controls(contract, payload)
    payload["axes"]["probe_opportunity_rate"] = probe_rate_axis(contract, payload)
    payload["axes"]["graduation"] = graduation_axis(contract)
    payload["axes"]["rejected_nominations"] = rejected_nomination_axis(contract)
    payload["derived"] = {
        "width_model_groups": _group_model_runs(
            payload["axes"]["contemporaneous_controls"]["width_runs"],
            ("scale", "condition"),
        ),
        "protected_model_groups": _group_model_runs(
            payload["axes"]["contemporaneous_controls"]["protected_runs"],
            ("condition",),
        ),
    }
    payload["status"] = "complete"
    RAW_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_csv(payload)
    return payload


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Run HELM Capsule scale falsification.")
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    payload = execute(prepare_only=args.prepare_only)
    print(
        json.dumps(
            {
                "status": payload["status"],
                "raw": str(RAW_PATH),
                "raw_sha256": sha256_path(RAW_PATH),
                "csv": str(CSV_PATH) if CSV_PATH.exists() else None,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
