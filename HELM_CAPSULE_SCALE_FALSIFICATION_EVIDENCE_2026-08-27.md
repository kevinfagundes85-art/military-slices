# HELM Capsule Scale Falsification Evidence

Date: 2026-08-27  
Contract: `helm-capsule-scale-falsification-2026-08-27`  
Frozen contract SHA-256: `2223b61d7c751698b9b11127c998b29e644529293a7ac7ee8cfe47101839fce3`

## 1. Executive disposition

The Capsule interpretation is **partially supported** in this implementation and experiment.

Measured support:

- Active context stayed at 8 facts and 5,739–5,774 serialized bytes from 10 through 100,000 governed facts.
- Histories from 0 through 1,000 governed decisions contributed zero historical decisions to the active packet; packet size stayed at 4,187–4,190 bytes.
- Decomposable dependencies from 0 through 100 were all accounted for by sequential one-at-a-time resolution.
- In fresh same-commit controls, sparse HELM used 92.72% fewer input tokens at 1,000 facts and 92.92% fewer at 100,000 facts than the capped competent broad-context control. Mean estimated model cost fell 91.03% and 90.77%, respectively.
- A hidden semantic dependency was missed by unprotected sparse HELM in 5/5 runs, recovered by Probe-protected HELM in 5/5, and recovered by the broad control in 5/5. Probe-protected mean cost was $0.002546 versus $0.018855 broad, an 86.50% reduction.
- Probe caused zero observed authority violations. Rejected nominations created no blocking Impact or dependency and did not alter Anchor or Path.

Measured limits and failures:

- At 10 facts, HELM used 44.15% more input tokens and cost 33.64% more than broad context.
- Coupled dependency cases with 3, 10, 25, 50, or 100 simultaneously required facts exposed only one fact, failed to account for the rest, and were classified as having an unsafe intermediate state.
- The fresh graduation first-discovery call failed its frozen response contract. No relationship was graduated in this run, so the 1/10/100/1,000 deterministic repeats all correctly reported zero successful handling. Earlier graduation evidence was not substituted.
- The Probe-rate ladder produced 11 provider-contract failures in 161 calls. Across 150 valid calls, recall was 100%, precision was 76.58%, and 26 false nominations remained.
- All three frozen false nominations were nominated on first presentation. After trusted-human rejection, two were nominated again; the third repeat failed provider validation. Rejection therefore caused no unauthorized residue but did not eliminate rediscovery burden.
- With five available context domains, one irrelevant Slice fact leaked into the active projection; the active Gate count nevertheless stayed at one.
- Deterministic work was not constant or sub-linear overall. At 100,000 facts, state construction took 2,215.96 ms and in-turn deterministic work took 284.64 ms, including 183.09 ms ordinary retrieval and 96.22 ms index reconstruction.
- The optional 1,000,000-fact cell was not run: the 100,000-fact in-memory graph peaked at 164,339,322 bytes, projecting about 1.64 GB at 1,000,000 facts.

The strongest supported statement is: under sparse or decomposable conditions, active model context tracked the consequential surface more closely than total governed state through 100,000 facts; the advantage did not survive the current implementation's coupled-dependency requirement, was economically negative at 10 facts, and fresh durable graduation was not demonstrated.

## 2. Frozen architecture/evidence baseline

The experiment preserved the supplied baseline without strengthening it:

- independently adjudicated starting disposition: `MATERIAL ADVANTAGE — CRITICAL GATES OPEN`;
- normal frontier previously measured at 8 active facts through 100,000 facts;
- prior sparse adversarial recall repair: 0/20 to 20/20;
- prior sequential dense result: 3/3 dependencies across 5/5 sequences;
- prior Probe result: 72.73% precision, 100% recall, zero authority violations, 4/4 governed graduations, and zero second-pass rediscovery;
- unresolved false-nomination burden, simultaneous Dense Dependency failure, total-system sub-linearity, orchestration, and physical/cold-human validation.

This benchmark did not create a Capsule primitive, persisted Capsule object, authority type, canonical state, or Domain Pack rule. It observed existing Facts, Gates, Impacts, Path, history, lineage, and Probe contracts.

Frozen behavior implementation commit recorded by the harness: `63b198d5359e747efa56e33a483118969484a5c1`.  
Frozen contract commit: `61e03bf`.  
Harness implementation commit: `63b198d`.  
Execution-resilience commits: `f59bfee`, `5ec38c7`.  
Machine-evidence commit: `567bd246a9cc55ad78f43c8ad5e0b4369570dfc9`.

Military Transition Domain Pack:

- ID: `military-transition`
- version: `2026-08-24-v2-shadow-tested`
- status: `LEGACY_VALID`
- `military_slices/domain_pack.py` SHA-256: `3c00b7c191b3267c08271557c1c2a3b2df261fced6b0426dbc62972a3f2e0f8f`

## 3. Exact implementation/harness changes

Added or changed only benchmark assets:

- `benchmark/contracts/capsule_scale_falsification_2026-08-27.json`: frozen scale/provider/ground-truth contract.
- `benchmark/run_capsule_scale_falsification.py`: synthetic state construction, deterministic timing, provider controls, Probe opportunity tests, governance traces, checkpoints, JSON, and CSV serialization.
- `tests/test_capsule_scale_falsification.py`: contract hash, coupled/decomposable boundary, history non-leakage, Slice projection, and Probe-disabled assertions.
- provider-failure resilience records contract failures as failures and resumes completed checkpoint rows without prompt tuning or response repair.

No runtime source file under `military_slices/` was changed for this experiment.

## 4. Dataset and contract hashes

| Artifact | SHA-256 |
|---|---|
| Frozen Capsule contract | `2223b61d7c751698b9b11127c998b29e644529293a7ac7ee8cfe47101839fce3` |
| Frozen Gate 3 battery | `f5d449430200a86bfdd3b56be6cebe68df7ffd65130832117891ba563b7718701` |
| Harness source | `5ab7b65e7f311aa46b173f23c4fc3094aff064cf02aa7611f5023e2468281882` |
| Raw JSON | `2defa181e6ebaf593bde878fbc654810ca09af2cfa38c37a9eb88f770f2fc820` |
| Summary CSV | `1169a5876b555aa2eba50b1c60b8481b4cba78b538e24d303e7d29b5b16c4278` |

Synthetic seed: `20260827`. State-width facts included realistic Career, Education, Location, Resume, and Work Preference statements; historical facts; resolved dependencies; and one previously graduated relationship. The consequential scenario and required IDs stayed fixed while irrelevant/latent state increased.

## 5. Scale matrix

| Axis | Frozen points | Executed | Primary result |
|---|---:|---:|---|
| State width | 10, 100, 1k, 10k, 100k; optional 1m | through 100k | 8 active facts throughout |
| Lifecycle length | 0, 10, 100, 1,000 decisions | all | 0 historical decisions in packet |
| Dependency density | 0, 1, 3, 10, 25, 50, 100 × 2 classes | all | decomposable passed; coupled >1 failed |
| Probe opportunity | 0%, 0.1%, 1%, 5%, 10% | all | 150 valid, 11 failed provider outputs |
| Graduation repeats | 1, 10, 100, 1,000 | all | first discovery failed; no graduation |
| Rejected nominations | 3 frozen false positives + repeat | all | no authority residue; rediscovery persisted |
| Temporal | 18 months pre-service through 3 years post-service | all 9 | no future-task leakage post-service |
| Multiple Slices | 1, 2, 3, 5 | all | one Gate; one leaked fact at 5 |
| Same-window controls | 10, 1k, 100k; protected hidden dependency | 5 reps each | crossover and recall-protection measured |

## 6. State-width results

| Governed facts | Historical | Latent | Active | Payload bytes | Build ms | Index ms | Lookup ms | Ordinary retrieval ms | Frontier ms | Total deterministic ms |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 2 | 2 | 8 | 5,768 | 6.72 | 0.005 | 0.016 | 0.123 | 0.088 | 0.281 |
| 100 | 28 | 92 | 8 | 5,739 | 3.01 | 0.022 | 0.034 | 0.158 | 0.176 | 0.416 |
| 1,000 | 276 | 992 | 8 | 5,766 | 6.75 | 0.214 | 0.243 | 1.105 | 0.179 | 1.572 |
| 10,000 | 2,789 | 9,992 | 8 | 5,762 | 73.68 | 5.822 | 4.197 | 13.946 | 0.400 | 18.635 |
| 100,000 | 28,001 | 99,992 | 8 | 5,774 | 2,215.96 | 96.223 | 97.228 | 183.095 | 4.240 | 284.642 |

The active model-facing representation was bounded in this ladder. Total deterministic computation was not: ordinary retrieval, index reconstruction, state construction, and consequential lookup grew with total state.

The optional 1,000,000-fact point was skipped under the frozen stop rule. The 100,000-fact run used a peak 164,339,322-byte in-memory graph. Linear projection was 1,643,393,220 bytes and 22.16 seconds build time. Running that point would primarily measure workstation/Pydantic graph pressure and would require an infrastructure change not authorized here.

## 7. Lifecycle-length results

| Governed decisions | Historical decisions in active packet | Payload bytes | Total deterministic ms |
|---:|---:|---:|---:|
| 0 | 0 | 4,187 | 0.178 |
| 10 | 0 | 4,188 | 0.215 |
| 100 | 0 | 4,189 | 0.173 |
| 1,000 | 0 | 4,190 | 0.438 |

WHO, WHEN, OUTCOME, current Path/Gate, Canonical version, MutationEvent, and LineageRecord were retained. Historical decisions remained available in state but were not serialized merely because they existed.

## 8. Dependency-density results

| Class | Dependencies | Simultaneous minimum | Visible facts | Accounted | Resolution ms | Rework | Unsafe intermediate |
|---|---:|---:|---:|---|---:|---:|---:|
| Decomposable | 0 | 0 | 0 | yes | 0.000 | 0 | 0 |
| Decomposable | 1 | 1 | 1 | yes | 0.520 | 0 | 0 |
| Decomposable | 3 | 1 | 1 | yes | 1.442 | 0 | 0 |
| Decomposable | 10 | 1 | 1 | yes | 10.806 | 0 | 0 |
| Decomposable | 25 | 1 | 1 | yes | 54.422 | 0 | 0 |
| Decomposable | 50 | 1 | 1 | yes | 195.884 | 0 | 0 |
| Decomposable | 100 | 1 | 1 | yes | 1,005.723 | 0 | 0 |
| Coupled | 0 | 0 | 0 | yes | 0.000 | 0 | 0 |
| Coupled | 1 | 1 | 1 | yes | 0.000 | 0 | 0 |
| Coupled | 3 | 3 | 1 | **no** | 0.000 | 2 | 1 |
| Coupled | 10 | 10 | 1 | **no** | 0.000 | 9 | 1 |
| Coupled | 25 | 25 | 1 | **no** | 0.000 | 24 | 1 |
| Coupled | 50 | 50 | 1 | **no** | 0.000 | 49 | 1 |
| Coupled | 100 | 100 | 1 | **no** | 0.000 | 99 | 1 |

Sequential sparse resolution remained correct where the contract declared dependencies decomposable. Its repeated immutable-state reconstruction cost rose to about one second at 100 dependencies. Reality required expansion in coupled cases; the implementation did not expand and therefore failed visibly in the harness rather than being scored correct.

## 9. Probe-rate results

| Opportunity rate | Calls | Valid | Failed | TP | TN | FP | FN | Precision | Recall | Valid tokens | Known provider cost |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0% | 0 | 0 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | 0 | $0 |
| 0.1% | 1 | 0 | 1 | 0 | 0 | 0 | 0 | not measured | not measured | 0 | $0 known |
| 1% | 10 | 9 | 1 | 6 | 1 | 2 | 0 | 75.00% | 100% | 7,816 | $0.011988 |
| 5% | 50 | 45 | 5 | 26 | 11 | 8 | 0 | 76.47% | 100% | 36,933 | $0.051934 |
| 10% | 100 | 96 | 4 | 53 | 27 | 16 | 0 | 76.81% | 100% | 80,161 | $0.115990 |
| Aggregate nonzero | 161 | 150 | 11 | 85 | 39 | 26 | 0 | 76.58% | 100% | 124,910 | $0.179912 |

Probe input was per permitted new/changed latent opportunity, not a scan of all 1,000 facts. Cost and false-nomination burden grew approximately with opportunities: 2, 8, and 16 false nominations in the valid 1%, 5%, and 10% cells. The examination cost of those false nominations was **NOT MEASURED** because this axis stopped at nomination; it is not hidden inside provider cost.

## 10. Graduation results

The frozen first relationship was `paraphrased-restriction`. The provider returned case ID `probe-eval` rather than `paraphrased-restriction`. Frozen validation rejected it. No retry, repair, or alternative provider was used.

Consequences:

- first discovery valid: no;
- governed version delta: 0;
- persisted accepted relationship: none;
- repeat Probe calls: 0 because semantic repeat execution was conditioned on authorized graduation;
- correct deterministic handling at 1/10/100/1,000 repeats: 0 at every point;
- restart equality: yes, but it only proves unchanged state reconstitution.

This run does not reproduce the prior 4/4 graduation result. It is a fresh provider-contract failure and a material negative result. It does not prove that the representation is impossible; it proves that the end-to-end graduation path is not operationally reliable under this execution.

## 11. Rejected-nomination results

| Case | First nominated | Probe zero-write | Rejection persisted | Blocking Impact | Dependency | Path/Anchor unchanged | Repeat result |
|---|---|---|---|---:|---:|---|---|
| Superseded evidence | yes | yes | Decision + MutationEvent + Lineage | 0 | 0 | yes | nominated again |
| Benign authority | yes | yes | Decision + MutationEvent + Lineage | 0 | 0 | yes | provider validation failure |
| Misleading/negated restriction | yes | yes | Decision + MutationEvent + Lineage | 0 | 0 | yes | nominated again |

The governed residue records that a human performed and rejected an examination; it does not establish the rejected relationship as truth, create an Impact, or alter Path/Anchor. No rejection-memory mechanism was invented. The two valid repeat calls incurred 993 and 966 tokens and were false nominations again. This is preserved operational burden.

## 12. Temporal/lifecycle results

| Point | Lifecycle | Window | Stage | Path target | Eligible task |
|---|---|---|---|---|---|
| 18 months out | currently serving | B | PREPARE | PATH_IDENTIFIED | choose a post-service direction |
| 12 months out | leaving within 12 months | C | PREPARE | PREPARATION_BASELINE_READY | complete TAP preparation |
| 6 months out | leaving within 12 months | E | SEPARATE | CAPSTONE_READY | complete TAP preparation |
| 90 days out | leaving within 12 months | F | TRANSITION | FINAL_OUT_READY | complete CAPSTONE/CRS |
| 45 days out | leaving within 12 months | F | TRANSITION | FINAL_OUT_READY | complete CAPSTONE/CRS |
| Transition month | leaving within 12 months | H | STABILIZE | POST_SERVICE_STABLE | choose post-service direction |
| 30 days post | separated within last year | H | STABILIZE | POST_SERVICE_STABLE | choose post-service direction |
| 1 year post | separated 1–5 years | H | STABILIZE | POST_SERVICE_STABLE | choose post-service direction |
| 3 years post | separated 1–5 years | H | STABILIZE | POST_SERVICE_STABLE | choose post-service direction |

Every point had one active Gate/task and zero future-task leakage for post-service users. This synthetic axis did not contain changed evidence that should generate stale-state invalidation, so that subclaim was not exercised.

## 13. Multi-Slice results

| Available domains | Represented core enums | Governed facts | Active facts | Active Gates | Irrelevant Slice leakage |
|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 1 | 1 | 1 | 0 |
| 2 | 2 | 2 | 1 | 1 | 0 |
| 3 | 3 | 3 | 1 | 1 | 0 |
| 5 | 4 | 5 | 2 | 1 | **1** |

`Work Preferences` is represented by the existing Career enum rather than a fifth core Slice enum. Multiple available Slices did not multiply Gates, but the five-domain case activated one irrelevant fact and expanded the packet from 3,617 to 3,838 bytes.

## 14. Contemporaneous broad-context A/B

Provider and model: Vertex AI, `gemini-3.7-flash`, global; temperature 0; top-p 1; thinking budget 512; maximum output 700. Pricing basis: $0.75/million input tokens and $3.75/million output plus thought tokens. Each cell has five valid repetitions.

The competent broad control selected plausibly relevant facts under a 384-fact/160,000-byte cap. It did not dump clearly unrelated state. The cap was frozen before execution and means the 1,000- and 100,000-fact broad packets measure a deployable capped retrieval policy, not serialization of every governed fact.

| Facts | Condition | Context facts | Input tokens mean | Total tokens mean | Correct | Mean latency ms | Mean model cost |
|---:|---|---:|---:|---:|---:|---:|---:|
| 10 | Broad | 9 | 1,239 | 1,321.2 | 5/5 | 3,764.1 | $0.001238 |
| 10 | HELM | 8 | 1,786 | 1,869.8 | 5/5 | 3,900.0 | $0.001654 |
| 1,000 | Broad | 384 | 24,632 | 24,799.6 | 5/5 | 4,804.5 | $0.019103 |
| 1,000 | HELM | 8 | 1,794 | 1,892.2 | 5/5 | 3,478.9 | $0.001714 |
| 100,000 | Broad | 384 | 25,424 | 25,534.4 | 5/5 | 4,015.5 | $0.019482 |
| 100,000 | HELM | 8 | 1,801 | 1,920.2 | 5/5 | 3,647.6 | $0.001798 |

At 10 facts, HELM lost economically. At 1,000 and 100,000 facts it reduced input tokens by 92.72% and 92.92% and model cost by 91.03% and 90.77%. Observed mean latency was 27.59% lower and 9.16% lower, but five repetitions and provider variance are insufficient for a general latency claim.

Hidden-dependency protection, five repetitions:

| Condition | Correct | Mean model/combined tokens | Mean cost |
|---|---:|---:|---:|
| Broad | 5/5 | 24,732 | $0.018855 |
| HELM sparse, unprotected | 0/5 | 1,891.8 | $0.001712 |
| HELM sparse + Probe + governed examination | 5/5 | 2,383 combined | $0.002546 combined |

Probe protection cut mean known provider cost 86.50% and combined tokens about 90.36% versus broad while restoring correctness in this one frozen hidden-dependency scenario. It does not establish the fresh graduation-repeat claim, which failed separately.

## 15. Active-context scaling curve data

State width curve:

`10 → 8`, `100 → 8`, `1,000 → 8`, `10,000 → 8`, `100,000 → 8` active facts.

Payload curve:

`5,768 → 5,739 → 5,766 → 5,762 → 5,774` bytes.

Dependency-density curve:

- decomposable `0/1/3/10/25/50/100` dependencies → `0/1/1/1/1/1/1` simultaneously visible facts;
- coupled `0/1/3/10/25/50/100` minimum-sufficient facts → implementation exposed `0/1/1/1/1/1/1`.

The first curve supports bounded projection under irrelevant-state growth. The second identifies the density threshold: the current implementation remains sparse past the point where correctness requires expansion. That is a failure, not a context-saving win.

## 16. Computational scaling data

At 100,000 governed facts:

- in-memory state build: 2,215.96 ms;
- index reconstruction: 96.22 ms;
- consequential lookup: 97.23 ms;
- ordinary retrieval: 183.09 ms;
- frontier selection: 4.24 ms;
- serialization: 0.08 ms;
- total in-turn deterministic work: 284.64 ms.

The indexed consequential candidate surface did not make all work sub-linear because the harness rebuilt the index and ordinary retrieval still scanned total state. The model packet was bounded, not the full computation.

For 100 decomposable dependencies, single-turn selection remained 0.189 ms but the complete sequential governed-resolution sequence took 1,005.72 ms. This reconstitution/recompute work is material and is reported separately rather than hidden in the single-frontier number.

## 17. Economic crossover data

| Governed facts | HELM input-token reduction | HELM model-cost reduction | Mean latency delta |
|---:|---:|---:|---:|
| 10 | **−44.15%** | **−33.64%** | +3.61% |
| 1,000 | 92.72% | 91.03% | −27.59% |
| 100,000 | 92.92% | 90.77% | −9.16% |

The measured crossover lies somewhere above 10 and at or below 1,000 facts for this scenario and configuration. The contract did not include a 100-fact model-mediated control, so a narrower crossover claim is unsupported.

Known measured provider cost for completed, telemetry-bearing calls was $0.5276865. Provider costs for failed/malformed outputs and two pre-checkpoint decision calls are **NOT MEASURED**, so this is a lower bound, not total spend. Fixed recurring cost delta is $0.

## 18. Domain Pack operating profile

This is non-authoritative experimental evidence, not a policy change:

- **Small-state direct-reasoning region:** 10 facts; broad context was cheaper and smaller.
- **Sparse-frontier advantageous region:** 1,000–100,000 facts in the normal frozen scenario; HELM remained correct with roughly 91% measured model-cost reduction.
- **Probe-protected region:** a bounded hidden semantic dependency; correct 5/5 at 86.50% lower known provider cost than broad.
- **High opportunity-rate region:** Probe maintained 100% recall across valid outputs but generated 26 false nominations and 11 provider-contract failures; unmeasured human/examination burden grows with opportunity count.
- **Decomposable high-density region:** correct sequentially through 100 dependencies, with about one second deterministic resolution overhead at 100.
- **Coupled region:** more than one simultaneous dependency is currently outside the correct operating envelope. Broad/simultaneous context is minimum-sufficient, but the implementation did not materialize it.

Economics may inform a future choice between equivalently authorized strategies. It does not change governance or authority.

## 19. Recall/precision measurements

- Normal broad and HELM width controls: 100% Gate/decision correctness in 30/30 runs.
- Hidden dependency: broad 5/5, sparse unprotected 0/5, sparse plus Probe 5/5.
- Probe-rate aggregate over valid calls: TP 85, TN 39, FP 26, FN 0; precision 76.58%, recall 100%.
- Provider-contract failures: 11/161 Probe-rate calls (6.83%); they are excluded from precision/recall numerators and denominators and separately counted.
- Coupled dependency recall: 1/1 only; counts 3–100 each missed all but one required fact.
- Fresh graduation recall: not established because first discovery failed provider validation.

No claim of perfect recall is made. The 100% Probe recall applies only to the 150 valid repeated frozen-case outputs.

## 20. Authority audit

- Probe authority violations: 0 in all valid and failed recorded calls.
- Probe nomination caused Canonical mutation: no.
- Human-rejected relationships became blocking Impacts/dependencies: 0/3.
- Rejection changed Path/Anchor: 0/3.
- External effects: disabled.
- Production Probe: disabled.
- Production profile mutation: none.
- Domain Pack/canonical HELM mutation: none.

The synthetic trusted-human examination path alone created a Decision, MutationEvent, and LineageRecord. Accepted relationships would additionally create the existing ImpactItem representation; fresh acceptance did not occur because graduation discovery failed.

## 21. Preserved negative findings

1. Cheap-context economic loss remains.
2. Coupled/simultaneous Dense Dependency remains a correctness failure.
3. Total-system sub-linearity remains unestablished.
4. Ordinary retrieval and index reconstruction remain total-state-sensitive.
5. Provider latency remains variable; no general latency claim is made.
6. Probe false nominations remain an operational burden.
7. Rejected patterns can be semantically rediscovered.
8. Probe remains disabled in production.
9. Multi-agent orchestration remains untested.
10. Physical Android/cold-user validation remains open.

## 22. New failures

| Failure | Evidence | Classification |
|---|---|---|
| Coupled projection fails to expand at dependency count >1 | counts 3–100 expose one fact and mark unsafe intermediate | enforcement/contract gap |
| Fresh graduation unavailable | wrong provider `case_id`; 0 correct repeats | implementation hardening / provider-contract reliability |
| Probe output reliability | 11/161 rate calls failed; one rejected repeat failed | implementation hardening / measurement limitation |
| Rejected false nominations recur | 2/2 valid repeats nominated again | operational/process issue; no rejection memory was authorized |
| Five-domain projection leaks one irrelevant fact | active facts 2, leakage 1 | Slice-level change / enforcement hardening |
| 1,000,000-fact cell impractical in current harness | projected 1.64 GB graph | infrastructure decision / measurement limitation |
| Pre-checkpoint telemetry loss | two decision calls + one failed Probe call have no token/cost records | measurement limitation |

The provider's wrong-case output in the first protected attempt was not retried. Completed width calls were checkpointed and reused. The later protected matrix completed 15/15 decision calls and 5/5 Probe calls.

## 23. Architecture-gap assessment

No conceptual architecture gap is demonstrated by this experiment.

Frozen HELM already permits the minimum-sufficient surface to expand when dependencies are genuinely coupled. The observed coupled failure is that this implementation did not materialize that larger surface; it is an enforcement/implementation gap, not evidence that a new Capsule or multi-blocker primitive is necessary.

The fresh graduation failure occurred before governed examination because provider output violated the existing schema. Existing Impact, Decision, MutationEvent, and LineageRecord representations remain sufficient in the prior passing evidence and synthetic authorized path. No new persisted relationship primitive is justified by this failed call.

Rejection rediscovery may motivate an efficiency design decision, but the frozen contract explicitly prohibited inventing rejection memory for this test. It is not classified as a conceptual gap.

## 24. Reproduction instructions

Prerequisites:

- Windows PowerShell;
- repository virtual environment installed from `pyproject.toml`;
- valid Google Application Default Credentials for project `veteran-pathfinder-kf-2026`;
- access to Vertex AI `gemini-3.7-flash` in `global`;
- no production credentials or profile IDs are required.

Commands from repository root:

```powershell
$env:PYTHONPATH='.'
.\.venv\Scripts\python.exe -m pytest tests\test_capsule_scale_falsification.py -q
.\.venv\Scripts\python.exe benchmark\run_capsule_scale_falsification.py --prepare-only
.\.venv\Scripts\python.exe benchmark\run_capsule_scale_falsification.py
```

The runner refuses execution if the frozen contract hash differs. It writes progress checkpoints to the raw JSON. `--prepare-only` makes no provider calls. A complete raw file should not be overwritten casually; archive it before a new repetition if independent reruns must remain separate.

Validation executed:

- full pytest: 248 passed, one Starlette deprecation warning;
- targeted Ruff: passed;
- targeted strict Mypy: passed;
- target Bandit: no findings;
- dependency audit: no known vulnerabilities; local `military-slices` skipped because it is not on PyPI;
- JavaScript syntax: passed;
- repository-wide Ruff: 95 pre-existing long-line/import findings in older gauntlet scripts; not changed;
- repository-wide Bandit: two pre-existing low-severity findings; no medium/high findings;
- one attempted repository-wide Mypy invocation encountered duplicate module discovery in the existing benchmark/test layout; package Mypy and benchmark-target strict Mypy passed.

## 25. Raw artifact hashes

| Artifact | Location | SHA-256 |
|---|---|---|
| Raw run records | `benchmark/output/helm-capsule-scale-falsification-raw-2026-08-27.json` | `2defa181e6ebaf593bde878fbc654810ca09af2cfa38c37a9eb88f770f2fc820` |
| Summary matrix | `benchmark/output/helm-capsule-scale-falsification-summary-2026-08-27.csv` | `1169a5876b555aa2eba50b1c60b8481b4cba78b538e24d303e7d29b5b16c4278` |
| Frozen contract | `benchmark/contracts/capsule_scale_falsification_2026-08-27.json` | `2223b61d7c751698b9b11127c998b29e644529293a7ac7ee8cfe47101839fce3` |
| Frozen Gate 3 cases | `benchmark/contracts/gate3_interruption_classifier_2026-08-27.json` | `f5d449430200a86bfdd3b56be6cebe68df7ffd65130832117891ba563b7718701` |
| Harness source at evidence generation | `benchmark/run_capsule_scale_falsification.py` | `5ab7b65e7f311aa46b173f23c4fc3094aff064cf02aa7611f5023e2468281882` |

Individual context, payload, and response hashes are embedded per run in the raw JSON where provider validation completed. Failed provider outputs lack response hashes because the frozen harness rejected them before a valid parsed record existed.

## 26. Implementation commit

- Frozen behavior/harness implementation identity: `63b198d5359e747efa56e33a483118969484a5c1`
- Contract freeze: `61e03bf`
- Identity pin: `618eefc`
- Failure-preserving execution resilience: `f59bfee`
- Null-safe failure accounting: `5ec38c7`

These commits changed benchmark assets only. Canonical HELM/runtime implementation was not amended.

## 27. Evidence commit

Machine evidence commit: `567bd246a9cc55ad78f43c8ad5e0b4369570dfc9`.

This report is added in the subsequent documentation commit so that it can cite the immutable machine-evidence commit.

## 28. Production/release status

- production traffic moved: no;
- production Probe enabled: no;
- autonomous external effects enabled: no;
- production profiles mutated: no;
- Domain Pack changed: no;
- canonical HELM changed: no;
- candidate promoted: no.

The benchmark used local/synthetic state and provider-backed model calls only. It does not authorize a release.

## 29. NND adjudication questions

1. Does the coupled-dependency failure remain an implementation/enforcement gap because frozen HELM already permits surface expansion, or does the inability to materialize that expansion expose a deeper contract ambiguity?
2. Should the graduation provider-contract failure be treated as ordinary model-output reliability debt, or does safe graduation require an independently reliable non-semantic transition before NND accepts the Capsule claim?
3. Is 76.58% valid-output precision sufficient when false nomination examination cost is unmeasured and rejected patterns can be nominated again?
4. Does the 6.83% Probe-rate provider failure rate invalidate the protected-region economic result despite 5/5 success in the separate hidden-dependency control?
5. Is the 384-fact competent broad-context cap a fair deployable control at 100,000 facts, or should an independent rerun use a stronger hierarchical broad retrieval baseline?
6. Does one irrelevant fact at five available domains materially weaken the multiple-Slice claim, or is it bounded implementation leakage?
7. What evidence threshold is required before extending this single-Resolver/Probe result to orchestration? This experiment did not test orchestration.

**CAPSULE HYPOTHESIS PARTIALLY SUPPORTED**
