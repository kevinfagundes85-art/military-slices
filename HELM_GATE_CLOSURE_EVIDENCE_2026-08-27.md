# HELM Gate Closure Evidence — 2026-08-27

## 1. Executive disposition

**PARTIAL GATE CLOSURE.** Dense iterative sparse resolution, explicit lifecycle instantiation, lifecycle closure, and automated mobile validation passed. Consequentially indexed interruption lookup materially reduced decision-time lookup work, but index maintenance and ordinary evidence retrieval remain linear. The frozen interruption battery exposed material false positives and false negatives. The fresh 110-run model matrix and Probe benchmark could not execute because no Gemini/Vertex credential was available to the process. Physical Android and cold-human validation remain open. No evidence requires reopening frozen HELM architecture.

## 2. Frozen starting evidence

Benchmark 1 and Benchmark 2 were not edited. Benchmark 2 remains `LIMITED MEASURED ADVANTAGE`: four sparse adversarial classes 20/20 correct, normal frontier 8 facts, dense strict 0/5 for both conditions, Cheap Context loss, approximately 330 ms deterministic work at 100,000 facts, Probe disabled, zero production mutation.

Frozen contracts were committed before their implementations: Gate 1 at `b1b1512`; Gate 3 at `83007f2`; Gate 6 in implementation commit `73e9b86` before any Probe execution.

## 3. Gate-by-Gate PASS / PARTIAL / FAIL table

| Gate | Disposition | Evidence-backed reason |
|---|---|---|
| 1. Dense Dependency Semantics | **PASS** | 5/5 sequences accounted for all 3 immutable dependencies through three one-fact, human-governed mutations; first Gate was employment/IP; zero replay writes; no final unresolved interruption. |
| 2. Consequentially Indexed Lookup | **PARTIAL** | Candidate lookup became approximately 0.01–0.04 ms across 10–100,000 facts and active context remained 8 facts. Index construction and ordinary evidence retrieval remain linear; all 110 model calls failed before inference, so fresh end-to-end correctness/cost is unproven. |
| 3. Interruption Classifier Falsification | **PARTIAL** | 4 TP, 4 TN, 3 FP, 4 FN; precision 57.14%, recall 50.00%. Operating boundary is measured, not tuned away. |
| 4. Explicit Lifecycle Instantiation | **PASS (automated)** | WHO + lifecycle class + month-granularity WHEN + OUTCOME/Anchor existing path deterministically produced A/B, F, D, H, and unknown windows without model calls or irrelevant future-separation work for separated users. |
| 5. Lifecycle Closure | **PASS** | Human-authoritative satisfaction produced COMPLETE and zero active tasks; new human intent opened a new ACTIVE lifecycle while preserving historical facts. |
| 6. HELM Probe Benchmark | **FAIL (measurement limitation)** | Five cases frozen; zero valid model-mediated Probe runs because provider initialization failed. No deterministic proxy was substituted. Probe remains disabled. |
| 7. Integrated Human Validation | **PARTIAL / OPEN** | Browser widths 320/375/414 passed with no overflow/errors. Physical Android, cold user, second account, and full end-to-end authority journey remain open. |

## 4. Exact implementation changes

- `military_slices/temporal.py`: added a bounded, version-scoped derived interruption index; excluded already human-revalidated facts; projection reads the index instead of rescanning all facts.
- `benchmark/run_sparse_activation_benchmark.py`: builds the derived index during state construction and separately records index-build cost and bounded candidate lookups.
- `military_slices/models.py`, `engine.py`, `app.py`, `path_runtime.py`: added a month-granularity `transition_month` coordinate to the existing lifecycle/start-vector contract; no new Temporal Anchor primitive.
- `static/app.js`, `styles.css`, `index.html`: conditionally request the applicable month, expose month/year copy, provide a mobile-safe control, and bump exact bundles to `app.js?v=14` / `styles.css?v=11`.
- `benchmark/run_gate_closure_evidence.py` and frozen JSON contracts: reproducible deterministic evidence harness.
- `tests/test_gate_closure_contracts.py`, `tests/test_static_contract.py`: dense sequencing, replay, lifecycle ladder, closure/re-entry, and exact bundle regressions.

## 5. Falsification methodology

Contracts were written and committed before corrections. Gate 1 retained the original three facts and did not prescribe an unsupported order between certification and location. Gate 3 fixed 15 positive/negative cases before execution and prohibited vocabulary tuning. Gate 6 fixed five discovery cases before attempting provider execution. Benchmark 2 dataset semantic SHA remained `4d89fbb0cfb6ed8588ec414b05d68b3e79cd0a404c25ef2be28da9f31e8f7437`. Every provider failure is present in raw evidence.

## 6. Benchmark comparisons

| Comparison | Prior evidence | Closure evidence |
|---|---:|---:|
| Dense simultaneous strict | HELM 0/5; baseline 0/5 | Preserved |
| Dense HELM simultaneous recall | 1/3 | Preserved |
| Dense iterative sparse recall | NOT TESTED | 3/3 in 5/5 sequences |
| Sparse packet dependency facts | 1 | 1 at every iterative step |
| Fresh frozen-matrix model completion | 110/110 in Benchmark 2 | 0/110; credential initialization failure |

## 7. Recall measurements

Dense iterative recall was 100% across five deterministic repetitions. Gate 3 recall was 50% (4 TP, 4 FN). Misses were paraphrased restriction, indirect restriction, semantically equivalent blocker, and cross-domain consequence. Probe recall is **NOT MEASURED**.

## 8. Computational measurements

| Governed facts | Active facts | Indexed interruption lookup mean | Ordinary retrieval mean | Frontier mean |
|---:|---:|---:|---:|---:|
| 10 | 8 | 0.01 ms | 0.10 ms | 0.12 ms |
| 100 | 8 | 0.02 ms | 0.20 ms | 0.18 ms |
| 1,000 | 8 | 0.01 ms | 1.16 ms | 0.21 ms |
| 10,000 | 8 | 0.01 ms | 16.28 ms | 0.55 ms |
| 100,000 | 8 | 0.04 ms | 192.52 ms | 4.41 ms |

Index build remains O(n) at state construction/reconstitution. Indexed candidate lookup is O(g + i + c), where g is conflicted Gates, i blocking Impacts, and c indexed authoritative candidates. Ordinary fact retrieval still builds a fact projection from governed state and remains O(n). Therefore this evidence does **not** establish sub-linear total computation.

## 9. Cost measurements

Fresh model tokens and model cost are **NOT MEASURED** because all 110 provider attempts failed before inference. Estimated model/API spend for this closure run was $0. Deterministic local execution incurred no measurable cloud charge. Benchmark 2 token/cost findings remain immutable historical controls, not fresh results. Cheap Context remains an economic loss.

## 10. Preserved negative findings

- Cheap Context loss remains real.
- Simultaneous dense strict correctness remains 0/5 for both conditions.
- Total deterministic work is not demonstrated sub-linear.
- Provider/latency variance remains unresolved.
- Benchmark 2 model results were not reused as current execution.
- Probe and orchestration savings are unproven.

## 11. New failures

- Gate 3: 3 false positives—superseded evidence, negated “no restrictions,” irrelevant high-authority museum restriction.
- Gate 3: 4 false negatives—paraphrase, indirect restriction, equivalent blocker, cross-domain consequence.
- Gate 2/6: provider initialization failed with `No API key was provided`; 110/110 frozen-matrix calls failed and Probe made no calls.
- Initial mobile month input measured 30 px high; corrected to 56.125 px and revalidated.
- Dependency audit rerun was blocked by sandbox network access; prior lock state was not represented as a new audit.

## 12. Architecture-gap assessment

No demonstrated conceptual architecture gap. Dense dependencies were expressible through existing iterative Gate → human mutation → recompute contracts. Indexed lookup is implementation hardening. Classifier misses are an enforcement/contract gap and potential Probe use case, not evidence authorizing a new primitive. Probe validity remains a measurement limitation.

## 13. Domain-Pack implications

No eligibility, consequence policy, threshold, or Domain Pack status changed. The lifecycle month is an orientation coordinate used by existing window rules. The order between certification and location after the employment/IP blocker was observed, not elevated to Domain Pack policy. Pack remains `LEGACY_VALID`.

## 14. Lifecycle validation

Automated fixtures covered: serving 18 months (B), serving ~45 days (F), recently separated (H), three years post-service (H), long-term post-service (H), unknown date (`PATH_IDENTITY`), approximate month (D), and changed month (C→F). Separated cases exposed no future active-service separation task. Month/year remains human-visible; mid-month is used only internally for coarse window selection and does not assert an exact day.

## 15. Probe validation

Probe contract was frozen as DISCOVER/WAKE only with five cases and explicit prohibitions on activation, adjudication, authorization, pruning, Canonical mutation, and Anchor creation. Execution was not valid because the provider could not initialize. Disposition: **FAIL — measurement limitation**. Production Probe remains disabled.

## 16. Human-validation status

Automated browser: PASS at 320, 375, and 414 px; no page overflow; orientation choice height 57.33 px; visible month input 56.125 px / 16 px text; zero console warnings/errors. Physical Android, cold-user comprehension, changed direction, full What-If authorization, COMPLETE stop, and real second-account isolation remain human gates and are not claimed complete.

## 17. Production/release status

No deployment or traffic command was executed. No production profile, Firestore record, governed truth, external effect, or Probe state was mutated. Last known production posture from accepted evidence remains `military-slices-00001-niw` at 100%; this environment lacked `gcloud`, so live traffic was **NOT RE-VERIFIED**. No candidate was deployed.

## 18. Reproduction instructions

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\ruff.exe check military_slices benchmark/run_sparse_activation_benchmark.py benchmark/run_gate_closure_evidence.py tests/test_gate_closure_contracts.py
.\.venv\Scripts\mypy.exe military_slices
.\.venv\Scripts\bandit.exe -q -r military_slices benchmark/run_gate_closure_evidence.py
.\.venv\Scripts\python.exe benchmark/run_gate_closure_evidence.py
.\.venv\Scripts\python.exe benchmark/run_sparse_activation_benchmark.py --output-label gate-closure --benchmark-commit 73e9b86
node --check static/app.js
```

The last command requiring Gemini needs valid Google credentials; absence must remain a failed run.

## 19. Raw artifact hashes

- Gate 1 contract: `5d24fb644d1590377ffa62ce9ca553c1bde51cb8958e86ec2073b7ae35234c75`
- Gate 3 contract: `f5d449430200a86bfdd3b56be6ceb68df7ffd65130832117891ba563b7718701`
- Gate 6 contract: `94f49e8f16daee77bfed8cc18fb686e215f8a1a1b37e1e3ad92431e3214399d9`
- Gate closure raw: `bb9f767abb3ed019310ce4655d1981e31b2b009f10a3068dba14f92b9d2cd098`
- Frozen rerun raw (provider failures): `9ac2eb5e9645ff39a3d89ca7659f8bb90d5a6e118e064740cf23e8e4def82694`
- Immutable Benchmark 2 raw: `2957ec634738ce947f50b6b8ed5c18df69880407f21535955c339e4d749179f0`
- Immutable Benchmark 2 report: `2d144d0a5d28734fe65214397af8512656e9dd845ad73ee6e1763ede02399e5c`

## 20. Evidence commit

Implementation commit: `73e9b86b63fe96a6493e6c3c1a92a9aec16d7a53`. Evidence commit: the Git commit containing this report; exact hash is recorded in the final BHE handoff.

## 21. Questions requiring NND adjudication

1. Is 50% recall / 57.14% precision sufficient to retain the lexical authoritative fallback at all, or should unmaterialized semantic relevance fail closed pending bounded Probe/human review?
2. Does linear index maintenance plus bounded lookup satisfy the intended indexed-hardening gate, given ordinary evidence retrieval remains linear?
3. Is deterministic, human-governed iteration an acceptable Dense Dependency resolution contract when the simultaneous model packet remains a preserved failure?
4. Should Probe be rerun only after credentials are restored, or independently in a separate provider-controlled evidence window?
5. Are physical Android and cold-user gates required before any zero-traffic candidate is built, or only before promotion?

### Unresolved-finding classification

| Finding | Classification |
|---|---|
| Classifier false positives/negatives | enforcement/contract gap |
| Linear index construction and ordinary retrieval | implementation hardening |
| Probe not executed | measurement limitation |
| Provider credential absence | infrastructure decision / operational issue |
| Physical Android and cold user open | operational/process issue |
| Month-level lifecycle UI | Slice-level change |
| No observed need for new primitive | conceptual architecture gap: **not demonstrated** |
