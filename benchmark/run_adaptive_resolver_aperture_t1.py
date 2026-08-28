"""Execute the sealed, label-blind Adaptive Resolver Aperture T1 arms.

This runner consumes only the public r3 package.  It never loads ground truth,
expected modes, harms, scoring, or the hidden authority schedule.  Every
provider attempt is retained and the checkpoint is rewritten after each
logical call completes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from benchmark.run_probe_decisive_falsification import (
    SYSTEM_INSTRUCTION as PROBE_SYSTEM_INSTRUCTION,
)
from benchmark.run_probe_decisive_falsification import (
    ProbeDecision,
    identity_bound_probe_schema,
)
from benchmark.t1_runtime_contract import (
    GovernedAdjudicationDecision,
    ProviderInvocation,
    ReplacementT1PublicTask,
    broad_context_invocation,
    governed_resolver_invocation,
)
from military_slices.adaptive_resolver_aperture import (
    ExecutionMode,
    select_adaptive_resolver_aperture,
)

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "benchmark" / "t1_runtime_r3"
OUTPUT = ROOT / "benchmark" / "output" / "adaptive_resolver_aperture_t1_r3"
CHECKPOINT = OUTPUT / "provider_execution_checkpoint.json"
RAW_OUTPUT = OUTPUT / "provider_execution_raw.json"
MANIFEST = PACKAGE / "helm_arav1_t1_r3_public_manifest_2026-08-28.json"
HARNESS_CONFIG = PACKAGE / "helm_arav1_t1_r3_public_harness_config_2026-08-28.json"
PROVIDER_CONFIG = PACKAGE / "helm_arav1_t1_r3_public_provider_config_2026-08-28.json"
ARM_B_PROMPT = ROOT / "benchmark" / "whole_lifecycle_frozen" / "arm_b_system_prompt_2026-08-27.md"
SHARDS = tuple(sorted(PACKAGE.glob("helm_arav1_t1_r3_public_corpus_shard_*_of_6_2026-08-28.json")))


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, default=str)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_json(value: Any) -> str:
    return sha256_bytes(canonical_json(value).encode("utf-8"))


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def identity_bound_schema(model: type[BaseModel], field: str, identity: str) -> dict[str, Any]:
    schema = deepcopy(model.model_json_schema())
    schema["properties"][field] = {"type": "string", "enum": [identity]}
    stack: list[Any] = [schema]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            if "const" in current:
                current["enum"] = [current.pop("const")]
            stack.extend(current.values())
        elif isinstance(current, list):
            stack.extend(current)
    return schema


def usage_int(usage: dict[str, Any], key: str) -> int:
    value = usage.get(key, 0)
    return value if isinstance(value, int) else 0


class Provider:
    def __init__(self, config: dict[str, Any]) -> None:
        from google import genai
        from google.genai import types

        self.config = config
        self.types = types
        self.client = genai.Client(
            vertexai=True,
            project="veteran-pathfinder-kf-2026",
            location=config["location"],
            http_options=types.HttpOptions(timeout=config["timeout_ms"]),
        )

    def attempt(
        self,
        *,
        logical_call_id: str,
        attempt_number: int,
        invocation: ProviderInvocation,
        parse_model: type[BaseModel],
        response_schema: dict[str, Any],
    ) -> dict[str, Any]:
        config = self.config
        request = {
            "logical_call_id": logical_call_id,
            "attempt_number": attempt_number,
            "model": config["model"],
            "system_instruction": invocation.system_instruction,
            "payload": invocation.payload,
            "response_schema": response_schema,
            "temperature": config["temperature"],
            "top_p": config["top_p"],
            "thinking_budget": config["thinking_budget"],
            "max_output_tokens": config["max_output_tokens"],
        }
        started = time.perf_counter()
        try:
            response = self.client.models.generate_content(
                model=config["model"],
                contents=canonical_json(invocation.payload),
                config=self.types.GenerateContentConfig(
                    system_instruction=invocation.system_instruction,
                    temperature=config["temperature"],
                    top_p=config["top_p"],
                    max_output_tokens=config["max_output_tokens"],
                    response_mime_type="application/json",
                    response_json_schema=response_schema,
                    thinking_config=self.types.ThinkingConfig(
                        include_thoughts=config["include_thoughts"],
                        thinking_budget=config["thinking_budget"],
                    ),
                ),
            )
            latency_ms = (time.perf_counter() - started) * 1000
            usage = response.usage_metadata.to_json_dict() if response.usage_metadata else {}
            input_tokens = usage_int(usage, "prompt_token_count")
            output_tokens = usage_int(usage, "candidates_token_count")
            thinking_tokens = usage_int(usage, "thoughts_token_count")
            total_tokens = usage_int(usage, "total_token_count") or input_tokens + output_tokens
            raw_text = response.text or ""
            parsed = response.parsed
            if isinstance(parsed, parse_model):
                decision = parsed
            elif isinstance(parsed, dict):
                decision = parse_model.model_validate(parsed)
            else:
                decision = parse_model.model_validate_json(raw_text)
            decision_json = decision.model_dump(mode="json")
            rates = config["pricing_freeze"]
            return {
                "attempt_id": f"{logical_call_id}:attempt:{attempt_number}",
                "attempt_number": attempt_number,
                "valid": True,
                "request_sha256": sha256_json(request),
                "response_sha256": sha256_json(decision_json),
                "raw_response_sha256": sha256_bytes(raw_text.encode("utf-8")),
                "response_id": getattr(response, "response_id", None),
                "model_version": getattr(response, "model_version", None),
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "thinking_tokens": thinking_tokens,
                "total_tokens": total_tokens,
                "latency_ms": latency_ms,
                "estimated_cost_usd": (
                    input_tokens / 1_000_000 * rates["input_usd_per_million_tokens"]
                    + (output_tokens + thinking_tokens)
                    / 1_000_000
                    * rates["output_usd_per_million_tokens"]
                ),
                "usage": usage,
                "decision": decision_json,
            }
        except Exception as exc:  # every failed attempt is evidence
            return {
                "attempt_id": f"{logical_call_id}:attempt:{attempt_number}",
                "attempt_number": attempt_number,
                "valid": False,
                "request_sha256": sha256_json(request),
                "latency_ms": (time.perf_counter() - started) * 1000,
                "input_tokens": 0,
                "output_tokens": 0,
                "thinking_tokens": 0,
                "total_tokens": 0,
                "estimated_cost_usd": 0.0,
                "failure_class": type(exc).__name__,
                "failure": str(exc),
            }

    def call(
        self,
        *,
        logical_call_id: str,
        invocation: ProviderInvocation,
        parse_model: type[BaseModel],
        response_schema: dict[str, Any],
    ) -> dict[str, Any]:
        attempts: list[dict[str, Any]] = []
        for attempt_number in range(1, 4):
            attempt = self.attempt(
                logical_call_id=logical_call_id,
                attempt_number=attempt_number,
                invocation=invocation,
                parse_model=parse_model,
                response_schema=response_schema,
            )
            attempts.append(attempt)
            if attempt["valid"]:
                break
            failure = str(attempt.get("failure", ""))
            if "429" not in failure and "503" not in failure:
                break
        return {
            "logical_call_id": logical_call_id,
            "valid": bool(attempts[-1]["valid"]),
            "attempts": attempts,
            "decision": attempts[-1].get("decision"),
        }


def load_tasks() -> list[ReplacementT1PublicTask]:
    if len(SHARDS) != 6:
        raise RuntimeError(f"Expected six r3 shards, found {len(SHARDS)}")
    tasks: list[ReplacementT1PublicTask] = []
    for path in SHARDS:
        payload = json.loads(path.read_text(encoding="utf-8"))
        tasks.extend(ReplacementT1PublicTask.model_validate(item) for item in payload["tasks"])
    if len(tasks) != 240 or len({item.task_id for item in tasks}) != 240:
        raise RuntimeError("Public corpus is not exactly 240 unique tasks")
    return sorted(tasks, key=lambda item: item.task_id)


def probe_invocation(task: ReplacementT1PublicTask, fact_id: str) -> ProviderInvocation:
    state = task.runtime_state()
    gate = next(item for item in state.gates if item.id == task.aperture_request.gate_id)
    fact = next(item for item in state.facts if item.id == fact_id)
    payload = {
        "contract": {
            "authority": "DISCOVER/WAKE only",
            "allowed_output": "CandidateForExamination or no nomination",
            "mutation_permitted": False,
        },
        "current_context": {
            "human_anchor": state.human_anchor,
            "path_target": state.path_target_state,
            "active_gate": gate.model_dump(mode="json"),
            "lifecycle_position": state.lifecycle_position,
            "decision_request": task.decision_request,
        },
        "permitted_latent_item": {
            "case_id": task.task_id,
            "fact": fact.model_dump(mode="json"),
        },
    }
    return ProviderInvocation(
        system_instruction=PROBE_SYSTEM_INSTRUCTION,
        payload=payload,
        response_schema=identity_bound_probe_schema(task.task_id),
    )


def deterministic_reuse(task: ReplacementT1PublicTask) -> dict[str, Any]:
    state = task.runtime_state()
    decisions = [
        item.model_dump(mode="json")
        for item in state.decisions
        if item.gate_id == task.aperture_request.gate_id
    ]
    return {
        "type": "DETERMINISTIC_GOVERNED_REUSE",
        "task_id": task.task_id,
        "reused_decisions": decisions,
        "reuse_fact_ids": list(task.aperture_request.reuse_fact_ids),
        "provider_calls": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=12)
    args = parser.parse_args()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    provider_config = json.loads(PROVIDER_CONFIG.read_text(encoding="utf-8"))
    harness_config = json.loads(HARNESS_CONFIG.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    tasks = load_tasks()
    arm_b_prompt = ARM_B_PROMPT.read_text(encoding="utf-8")
    if sha256_bytes(arm_b_prompt.encode("utf-8")) != harness_config["arm_b_prompt_sha256"]:
        raise RuntimeError("Arm B prompt hash mismatch")

    selections: dict[str, Any] = {}
    for task in tasks:
        selection = select_adaptive_resolver_aperture(
            task.runtime_state(), task.aperture_request.to_runtime()
        )
        selections[task.task_id] = selection

    results: dict[str, Any] = {"H0": {}, "H1": {}, "B": {}}
    if CHECKPOINT.exists():
        checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
        if checkpoint.get("corpus_id") == manifest["corpus_id"]:
            results = checkpoint.get("results", results)

    jobs: list[tuple[str, str, ProviderInvocation, type[BaseModel], dict[str, Any]]] = []
    for task in tasks:
        task_id = task.task_id
        if task_id not in results["H0"]:
            invocation = governed_resolver_invocation(task, arm="H0", selection=None)
            if invocation is None:
                raise RuntimeError("H0 unexpectedly produced no invocation")
            jobs.append(
                (
                    "H0",
                    task_id,
                    invocation,
                    GovernedAdjudicationDecision,
                    identity_bound_schema(GovernedAdjudicationDecision, "task_id", task_id),
                )
            )
        if task_id not in results["B"]:
            invocation = broad_context_invocation(task, arm_b_prompt)
            jobs.append(
                (
                    "B",
                    task_id,
                    invocation,
                    GovernedAdjudicationDecision,
                    identity_bound_schema(GovernedAdjudicationDecision, "task_id", task_id),
                )
            )
        if task_id not in results["H1"]:
            selection = selections[task_id]
            mode = selection.receipt.selected_mode
            if mode == ExecutionMode.DETERMINISTIC_REUSE:
                results["H1"][task_id] = {
                    "logical_call_id": f"H1:{task_id}",
                    "valid": True,
                    "attempts": [],
                    "decision": deterministic_reuse(task),
                    "selection_receipt": selection.receipt.model_dump(mode="json"),
                }
            elif mode == ExecutionMode.PROBE_DISCOVERY:
                if len(selection.payload) != 1:
                    raise RuntimeError(f"Mode E {task_id} did not expose exactly one Fact")
                invocation = probe_invocation(task, selection.payload[0].id)
                jobs.append(
                    (
                        "H1",
                        task_id,
                        invocation,
                        ProbeDecision,
                        identity_bound_probe_schema(task_id),
                    )
                )
            else:
                invocation = governed_resolver_invocation(task, arm="H1", selection=selection)
                if invocation is None:
                    raise RuntimeError(f"H1 {task_id} unexpectedly produced no invocation")
                jobs.append(
                    (
                        "H1",
                        task_id,
                        invocation,
                        GovernedAdjudicationDecision,
                        identity_bound_schema(GovernedAdjudicationDecision, "task_id", task_id),
                    )
                )

    lock = threading.Lock()
    provider = Provider(provider_config)
    total = 688

    def save_checkpoint() -> None:
        payload = {
            "status": "provider_execution_in_progress",
            "corpus_id": manifest["corpus_id"],
            "completed_logical_calls": sum(len(results[arm]) for arm in ("H0", "H1", "B")),
            "total_logical_calls_including_zero_call_reuse": total,
            "results": results,
        }
        temp = CHECKPOINT.with_suffix(".tmp")
        temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        temp.replace(CHECKPOINT)

    save_checkpoint()

    def execute(
        job: tuple[str, str, ProviderInvocation, type[BaseModel], dict[str, Any]],
    ) -> tuple[str, str, dict[str, Any]]:
        arm, task_id, invocation, parse_model, response_schema = job
        result = provider.call(
            logical_call_id=f"{arm}:{task_id}",
            invocation=invocation,
            parse_model=parse_model,
            response_schema=response_schema,
        )
        if arm == "H1":
            result["selection_receipt"] = selections[task_id].receipt.model_dump(mode="json")
        return arm, task_id, result

    print(
        f"T1 r3 starting/resuming: {len(jobs)} provider calls pending; "
        "688 logical arm-task results total",
        flush=True,
    )
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(execute, job) for job in jobs]
        for future in as_completed(futures):
            arm, task_id, result = future.result()
            with lock:
                results[arm][task_id] = result
                save_checkpoint()
                done = sum(len(results[name]) for name in ("H0", "H1", "B"))
            if done % 20 == 0 or done == total:
                print(f"completed {done}/{total}", flush=True)

    raw = {
        "status": "provider_execution_complete",
        "corpus_id": manifest["corpus_id"],
        "public_artifact_hashes": {
            path.name: sha256_path(path)
            for path in (*SHARDS, HARNESS_CONFIG, PROVIDER_CONFIG, MANIFEST, ARM_B_PROMPT)
        },
        "provider_configuration": provider_config,
        "harness_configuration": harness_config,
        "task_count": len(tasks),
        "logical_results": {arm: len(results[arm]) for arm in ("H0", "H1", "B")},
        "results": results,
        "sealed_material_loaded": False,
        "authority_schedule_loaded": False,
        "production_mutated": False,
    }
    RAW_OUTPUT.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"complete: {RAW_OUTPUT}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
