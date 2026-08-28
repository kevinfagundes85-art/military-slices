# HELM Whole-Lifecycle v2 Authoring Stop

Date: 2026-08-27  
From: BHE  
Status: `FROZEN BENCHMARK CONTRACT NOT EXECUTABLE — ROLE-SEPARATION BREACH DURING AUTHORING`

## Executive finding

No provider call was made and neither benchmark arm executed. During the authorized authoring/sealing phase, NND exposed a deterministic package generator to the BHE/runtime-operator surface. That generator contains the ground-truth outcomes, harm mappings, control-event responses, validity conditions, and invalidation conditions for the same tasks it generates.

This violates the accepted redesign's scientific-separation requirement that fresh ground truth, scoring material, and the staged control schedule remain withheld from BHE until the registered reveal points. The package therefore cannot be adopted or executed as a blinded comparison.

## Triggering evidence

The exposed generator is:

- `benchmark/whole_lifecycle_redesign/generate_whole_lifecycle_v2_package.py`
- bytes: `42,235`
- SHA-256: `d72cc0d078de766ed8eddc208aea5874a2a137f7bc7e0ae137d036e673962b9b`

It generates all three artifacts in one process:

- runtime corpus;
- ground truth;
- human-control schedule.

The source contains `GROUND_TRUTH`, `CONTROL_SCHEDULE`, expected terminal outcomes, expected nominations, governed acceptances/rejections, invalidation expectations, harm mappings, and the exact oracle responses. Because the source was delivered to the runtime-operator conversation, its contents were disclosed before execution.

## Preserved incomplete artifacts

These are preserved as failed-authoring evidence only and are not an executable benchmark package:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `helm_runtime_contract_snapshot_2026-08-27.json` | 98,967 | `bc3586b5f2e094a35dae33b1c17e53c53a3284934057c96b7d5aeab5133120e7` |
| `generate_whole_lifecycle_v2_package.py` | 42,235 | `d72cc0d078de766ed8eddc208aea5874a2a137f7bc7e0ae137d036e673962b9b` |
| `wlb2_runtime_corpus_raw.json` | 3,265,979 | `c92a801978892f7dc74ba3c7b151c2b449ddfcb114d1bd38b275cd411f312112` |
| `wlb2_ground_truth_raw.json` | 220,127 | `03ba85d0d8bb0cbb9ca492ca81541bbac4a9dd338611c7546d09b2073c78ed23` |
| `wlb2_control_schedule_raw.json` | 129,349 | `2aa4aac7322f3d8b85484270e4be23bf0ec462b2e13330004a10c9a0549736ff` |

The generator produced 153 tasks and 123 control-schedule records. No design artifact, frozen contract, scoring key, re-authored Arm B prompt, role attestation, or final manifest was completed before NND reached its session limit.

## Required correction

NND must issue a fresh package with a new contract and corpus identity. The replacement authoring path must enforce actual information separation:

1. A blinded corpus-author/scorer generates the fresh corpus, ground truth, scoring key, and control schedule outside the BHE/runtime-operator conversation.
2. BHE receives only the runtime corpus, public design/contract, Arm B prompt, schema/harness contract, role attestation, and a manifest containing hashes of withheld artifacts.
3. The generator source, ground truth, scoring key, and unreleased control events are never attached to or rendered in the BHE/runtime-operator surface.
4. Control events are released one wave at a time only after paired outputs for the preceding wave are hash-committed.
5. The fresh corpus must use new task IDs and new substantive fixtures; renaming the exposed tasks is insufficient because BHE has already seen their outcomes and oracle responses.
6. NND must provide a statistical/sample-size justification for the replacement task count before corpus generation.
7. A separate final manifest remains the sole hash authority after uploads complete.

## Boundary audit

- Provider calls: `0`
- Arm H tasks executed: `0`
- Arm B tasks executed: `0`
- Production traffic moved: `no`
- Production state mutated: `no`
- Production Probe enabled: `no`
- Canonical HELM amended: `no`
- Domain Pack amended: `no`

## Disposition

The v2 authoring output is rejected for execution because blinding was compromised before sealing. This is a scientific-contract/operational separation failure, not evidence for or against HELM.

Overall HELM disposition remains unchanged:

**MATERIAL ADVANTAGE — CRITICAL GATES OPEN**

Execution may resume only after a fresh, independently authored and properly blinded package is delivered, independently verified, and separately authorized by Kevin.
