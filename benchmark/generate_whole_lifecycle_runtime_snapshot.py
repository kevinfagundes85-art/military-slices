from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import shutil
import subprocess
from enum import Enum
from pathlib import Path
from typing import Any

from benchmark.run_probe_decisive_falsification import (
    SYSTEM_INSTRUCTION,
    CandidateForExamination,
    ProbeDecision,
    identity_bound_probe_schema,
)
from military_slices.domain_pack import installed_domain_pack_payload, installed_domain_pack_ref
from military_slices.governance import external_effects_enabled, probe_execution_enabled
from military_slices.models import (
    ActorProvenance,
    Authority,
    CanonicalState,
    Decision,
    DomainPackStatus,
    Evidence,
    Fact,
    FreshnessClass,
    FreshnessStatus,
    Gate,
    GateState,
    ImpactItem,
    LifecyclePosition,
    LineageIntegrity,
    LineageRecord,
    MigrationStatus,
    MilitaryStateSubject,
    MutationEvent,
    PlanningActor,
    ServiceComponent,
    ServiceName,
    SliceName,
    StateCategory,
    SurfaceType,
)
from military_slices.state_bound_rejection import (
    lookup_governed_content_rejection,
    lookup_state_bound_rejection,
    record_state_bound_rejection,
)

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = (
    ROOT
    / "benchmark"
    / "whole_lifecycle_redesign"
    / "helm_runtime_contract_snapshot_2026-08-27.json"
)

MODEL_TYPES = (
    ActorProvenance,
    CanonicalState,
    Decision,
    Evidence,
    Fact,
    Gate,
    ImpactItem,
    LineageRecord,
    MutationEvent,
    CandidateForExamination,
    ProbeDecision,
)

ENUM_TYPES = (
    Authority,
    DomainPackStatus,
    FreshnessClass,
    FreshnessStatus,
    GateState,
    LifecyclePosition,
    LineageIntegrity,
    MigrationStatus,
    MilitaryStateSubject,
    PlanningActor,
    ServiceComponent,
    ServiceName,
    SliceName,
    StateCategory,
    SurfaceType,
)

SOURCE_PATHS = (
    "military_slices/models.py",
    "military_slices/domain_pack.py",
    "military_slices/governance.py",
    "military_slices/path_runtime.py",
    "military_slices/state_bound_rejection.py",
    "military_slices/temporal.py",
    "benchmark/run_probe_decisive_falsification.py",
    "benchmark/run_state_bound_rejection_falsification.py",
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_json(value: Any) -> str:
    return sha256_bytes(canonical_json(value).encode("utf-8"))


def file_identity(relative_path: str) -> dict[str, Any]:
    path = ROOT / relative_path
    data = path.read_bytes()
    return {
        "path": relative_path,
        "bytes": len(data),
        "sha256": sha256_bytes(data),
    }


def git_commit() -> str:
    git_executable = shutil.which("git")
    if git_executable is None:
        raise RuntimeError("git executable not found")
    return subprocess.run(  # noqa: S603 - executable is resolved from the trusted host PATH.
        [git_executable, "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def enum_values(enum_type: type[Enum]) -> list[str]:
    return [str(item.value) for item in enum_type]


def function_identity(function: Any) -> dict[str, str]:
    source = inspect.getsource(function)
    return {
        "qualified_name": f"{function.__module__}.{function.__name__}",
        "source_sha256": sha256_bytes(source.encode("utf-8")),
    }


def build_snapshot() -> dict[str, Any]:
    domain_pack = installed_domain_pack_ref()
    domain_payload = installed_domain_pack_payload()
    schemas = {model.__name__: model.model_json_schema() for model in MODEL_TYPES}
    enums = {enum_type.__name__: enum_values(enum_type) for enum_type in ENUM_TYPES}
    representative_case_id = "snapshot-case-id"
    snapshot = {
        "snapshot_id": "helm-whole-lifecycle-runtime-contract-2026-08-27",
        "source_commit": git_commit(),
        "runtime_flags": {
            "autonomous_probe_enabled": probe_execution_enabled(),
            "external_effects_enabled": external_effects_enabled(),
        },
        "domain_pack": {
            "reference": domain_pack.model_dump(mode="json"),
            "payload_sha256": sha256_json(domain_payload),
            "payload": domain_payload,
        },
        "enums": enums,
        "schemas": schemas,
        "probe_contract": {
            "system_instruction": SYSTEM_INSTRUCTION,
            "system_instruction_sha256": sha256_bytes(SYSTEM_INSTRUCTION.encode("utf-8")),
            "base_schema_sha256": sha256_json(ProbeDecision.model_json_schema()),
            "identity_binding_example_case_id": representative_case_id,
            "identity_bound_schema": identity_bound_probe_schema(representative_case_id),
            "identity_binding_function": function_identity(identity_bound_probe_schema),
        },
        "governed_rejection_contract": {
            "i0_lookup": function_identity(lookup_state_bound_rejection),
            "i1_lookup": function_identity(lookup_governed_content_rejection),
            "record": function_identity(record_state_bound_rejection),
        },
        "source_files": [file_identity(path) for path in SOURCE_PATHS],
    }
    snapshot["component_hashes"] = {
        "enums_sha256": sha256_json(enums),
        "schemas_sha256": sha256_json(schemas),
        "source_files_sha256": sha256_json(snapshot["source_files"]),
    }
    return snapshot


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the frozen HELM runtime contract snapshot.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    snapshot = build_snapshot()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )
    args.output.write_bytes(encoded)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "bytes": len(encoded),
                "sha256": sha256_bytes(encoded),
                "source_commit": snapshot["source_commit"],
                "domain_pack_hash": snapshot["domain_pack"]["reference"]["content_hash"],
                "schemas_sha256": snapshot["component_hashes"]["schemas_sha256"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
