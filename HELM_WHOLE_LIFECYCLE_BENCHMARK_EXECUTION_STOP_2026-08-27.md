# Whole-Lifecycle HELM vs. Competent Broad-Context Falsification — Execution Stop

Date: 2026-08-27  
Status: **FROZEN BENCHMARK CONTRACT NOT EXECUTABLE**  
Governing disposition remains: **MATERIAL ADVANTAGE — CRITICAL GATES OPEN**

## Executive finding

The frozen package passed byte-level identity verification, corpus integrity checks, and role-separation verification. Runtime execution did not begin because the delivered scientific contract does not define a faithful executable mapping from its natural-language runtime tasks into the existing Arm H pipeline.

The missing mapping cannot be invented by BHE without choosing benchmark semantics after seeing the runtime corpus. Doing so would either modify Arm H, create a benchmark-only semantic authority path, simulate unavailable human authorization, or use category/order cues excluded from runtime payloads. Each option violates an explicit frozen rule.

Provider calls made: **0**.  
Arm H tasks executed: **0/240**.  
Arm B tasks executed: **0/240**.  
Scoring artifacts accessed: **none**.  
Production mutations or traffic changes: **0**.

## Verified frozen package

| Artifact | SHA-256 | Result |
|---|---|---|
| `WHOLE_LIFECYCLE_BENCHMARK_DESIGN_2026-08-27.md` | `47543121bb6f68daa40a532a96ba89272c424a578b29692864d4e5278e5e8524` | Match |
| `whole_lifecycle_benchmark_contract_2026-08-27.json` | `ba8f8a33e97aa4b3bd5cfdbddd6d6261c7c75970bfa4532227ff3519346f3aee` | Match |
| `BENCHMARK_CORRIGENDUM_2026-08-27.md` | `b36a6475edafd454f29b7690bd8bd4c013c917edab6b180bb799d98a517a0c99` | Match |
| `arm_b_system_prompt_2026-08-27.md` | `3fd3a77a2c2b6512e39b627a70c92f23526ba3273e49031e45010e3a50099041` | Match |
| `whole_lifecycle_runtime_corpus_2026-08-27.json` | `5553d3224786cad139fdb96a768b056684b03ddac2eb81ad9b047f89ca58e265` | Match |
| `WHOLE_LIFECYCLE_BENCHMARK_ROLE_ATTESTATION_2026-08-27.md` | `7c6bacd730318749e93e09086797e2cd629843ce0cac579f4e3294d03bf45aef` | Match |
| `WHOLE_LIFECYCLE_BENCHMARK_PACKAGE_MANIFEST_2026-08-27.json` | `5bf1c5bd8b4fc1d0478b173c085263bbd5ba7568112238d1ce032a03ec100ebf` | Match |

The two corpus copies observed in Google Drive were byte-identical. The canonical filename above was retained.

The sealed ground truth (`9a32c3c91a70e826b93dd043d94d752bae3270a09d9db1048d6f9c7b7749fe23`) and sealed scoring key (`4836020de5cd448afb08a55044084e0f873620d1691c2d379b753873efaba9be`) were not delivered to or accessed by BHE.

## Corpus integrity observed

- Task count: 240.
- Unique task IDs: 240.
- Total fact rows: 3,931.
- Total distinct task turns: 961.
- Maximum facts in one task: 100.
- Maximum turns in one task: 25.
- Task object keys across the entire corpus: `task_id`, `question`, `turns` only.
- Turn object keys across the entire corpus: `turn`, optional `fact_index`, and `fact` only.
- No task contains governed Fact identity, authority, validity, lifecycle coordinate, effect dimension, Gate identity/version, evidence lineage, Path target, Human Anchor, or an authorized examination response.

## Exact execution blocker

Arm H is frozen as the existing full pipeline:

`Probe → governed examination → Gate authorization → state-bound rejection/I1 reuse → graduation → restart survival`

The existing implementation enforces the following boundaries:

1. Probe receives one permitted Latent item and may return only `CandidateForExamination` or no nomination.
2. Probe has `DISCOVER/WAKE` authority only and cannot establish an Impact, dependency, truth, Gate outcome, Path change, or Canonical mutation.
3. Governed examination and graduation require a trusted human-authoritative event.
4. State-bound rejection and I1 reuse require governed Fact identity/content, an effect dimension, Gate identity/version, evidence lineage, and validity dimensions.

The frozen runtime corpus supplies none of those governed coordinates and supplies no human-authorized examination outcome. The prior executable mechanism-level harnesses could complete graduation only because their frozen fixture contracts supplied structured fields and an explicit synthetic trusted-human control. This package does not.

Consequently, a runtime operator would have to choose at least one unauthorized approximation:

- infer authority, validity, Gate scope, effect dimension, or lineage from prose;
- introduce a new semantic ingestion/classification adapter;
- treat a Probe nomination as truth or authorization;
- simulate a human examiner without a frozen response contract;
- infer category membership or expected behavior from task order/content;
- replace the full pipeline with a single model judgment and label it Arm H.

Each would change what Arm H is or leak scientific-design information into execution. The package explicitly prohibits mechanism modification, ground-truth reconstruction, and convenient approximations.

## Additional missing runtime bindings

These are secondary to the Arm H blocker but must also be frozen before an admissible run:

- Arm H task-ingestion adapter and exact projection rule.
- Arm H output schema and the mapping from a governed/pending state to `accept`, `reject`, or `no-nomination`.
- Human-examination input/control for cases requiring authorization.
- Exact per-task call schedule: one call per task, one call per turn, or one Probe call per Latent fact.
- Matched provider configuration beyond model identity, including temperature, top-p, output limit, thinking budget, safety settings, and response schema.
- Symmetric retry/timeout policy.
- Frozen provider pricing basis and deterministic-cost conversion used by `dollar_cost`.

Selecting any of these after corpus visibility would alter the exam after seeing its shape.

## Why Arm B was not run alone

Arm B's system prompt is present and verified, but executing only Arm B would break provider-window parity, paired-task execution, and the completion gate. It would also incur cost without creating admissible paired evidence. Therefore both arms remain unexecuted.

## Required correction to make the frozen package executable

NND should issue a binding, pre-runtime execution addendum that supplies an implementation-independent adapter contract containing:

1. deterministic construction of Arm H's Human Anchor, Path target, Gate, effect dimension, Fact identity, authority/validity metadata, and evidence lineage from each runtime task;
2. the authorized examination input or a frozen rule for representing a pending human Gate without simulating authorization;
3. exact Arm H and Arm B output schemas;
4. exact call schedule and matched model configuration;
5. symmetric provider-failure policy; and
6. frozen cost conversion constants.

The addendum must be authored and hash-committed before runtime and must not expose category labels, ground truth, harm assignments, scoring weights, or expected winners. The existing corpus, design, contract, prompt, and hashes should remain immutable.

## Classification

- Primary: **scientific contract / enforcement gap**.
- Not demonstrated: canonical HELM conceptual architecture gap.
- Not demonstrated: Domain Pack policy gap.
- Not a provider failure.
- Not a production issue.

## Production and release audit

- No deployment performed.
- No Cloud Run traffic changed.
- No production profile or datastore mutation.
- Probe remains disabled in production.
- No external effect was authorized.
- No canonical HELM or Domain Pack change was made.

## Stop disposition

**FROZEN BENCHMARK CONTRACT NOT EXECUTABLE**

Execution stopped before the first provider call, as required by the frozen order.
