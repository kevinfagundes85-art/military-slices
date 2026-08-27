# HELM Sparse Activation Benchmark 2 Evidence

Independent-review falsification cycle: Impact-to-projection re-evaluation  
Execution date: 2026-08-26 (America/Los_Angeles)  
Implementation and benchmark commit: `754d0e73106c4df8bc6d352d8c338523c028d187`  
Benchmark 1 implementation commit: `e44ba281c3f0a2775428b9acfa735a7fd90ced1a`  
Benchmark 1 evidence commit: `5c17bc5e12071c9f6fbb5e73e59948edb4ef8206`

Post-run Cloud Run read-back at `2026-08-27T04:01:37Z` showed service Ready, production revision `military-slices-00001-niw` at 100% canonical traffic, and frontier candidate `military-slices-00041-yud` tagged at 0% canonical traffic.

## 1. Executive Result

Benchmark 2 closed the specific sparse Impact recall failure diagnosed in Benchmark 1 without widening the normal active fact frontier.

- Hidden Dependency, Cross-Domain Collision, Temporal Activation, and Conflict improved from **0/20 to 20/20** HELM full-correctness runs.
- Consequential dependency recall in those four classes improved from **0% to 100%**.
- The corrected adversarial packet activated exactly **one fact**, used 1,638-1,711 mean input tokens, and retained 91.49%-91.90% estimated cost reduction versus the competent broad-context baseline.
- The normal HELM frontier remained exactly **8 active facts, 1 active task, and 1 horizon item** at every scale.
- Normal HELM input rose by exactly 11 tokens per run because the packet now carries a null-safe re-evaluation field: 1,993-2,008 tokens versus 1,982-1,997 in Benchmark 1.
- At 100-100,000 governed facts, Benchmark 2 normal HELM still reduced input context 65.68%-92.19% versus its same-run baseline.
- Dense Dependency remains a deliberate failure: HELM recalled 1/3 dependencies and baseline recalled 1/3. Both were 0/5 strict correctness.
- Cheap Context remains an economic loss: HELM used 37.83% more input tokens and cost 30.79% more than baseline.
- Deterministic selection/projection overhead grew materially at large state. At 100,000 facts it rose from 206.738 ms in Benchmark 1 to 330.103 ms in Benchmark 2, a 123.365 ms / 59.67% increase. This is still a linear scan, not sub-linear total computation.
- Latency remains unfit for an external performance claim because hosted-provider variance dominated several means.

Strongest supported conclusion: **the localized Impact re-evaluation correction preserved bounded normal context and repaired the four tested sparse consequential-recall classes at approximately the same model cost. It did not solve dense dependency, cheap-context overhead, linear deterministic scanning, or orchestration.**

Disposition: **LIMITED MEASURED ADVANTAGE — SPARSE IMPACT RECALL CORRECTED IN THE TESTED BATTERY; DENSE AND TOTAL-COMPUTE LIMITS REMAIN.**

## 2. Governing Falsification Order

The independent review identified one structural failure: a blocking Impact, temporal change, cross-domain dependency, or conflict could be visible in governed state while remaining absent from the active model packet. The review ordered the smallest correction that allowed such an Impact to force projection re-evaluation, followed by an unchanged replay of Benchmark 1.

The correction was explicitly bounded against:

- widening the normal frontier;
- changing the human Anchor or Path semantics;
- creating or persisting a new canonical Gate, Impact, fact, or authority;
- changing Benchmark 1 ground truth, seed, scenarios, baseline, model, prompt contract, limits, or repetition count;
- enabling Probe;
- changing production traffic, profiles, datastore, Domain Pack, or external effects.

## 3. Integrity of the Comparison

The Benchmark 1 and Benchmark 2 dataset manifests are byte-identical:

- Dataset semantic SHA-256 recorded by both raw runs: `4d89fbb0cfb6ed8588ec414b05d68b3e79cd0a404c25ef2be28da9f31e8f7437`
- Dataset file SHA-256 for both runs: `eb599eaf866259483d7ed3a31bbe698ffa78f43cb5713faecf25af54b5dcf15d`

Frozen controls:

|Control|Benchmark 1|Benchmark 2|
|---|---|---|
|Provider/model|Vertex AI / `gemini-3.7-flash`|Same|
|Location|`global`|Same|
|Framework|Google ADK 1.39.0|Same|
|Temperature / top-p|0 / 1|Same|
|Thinking budget|512|Same|
|Maximum output tokens|500|Same|
|Maximum model calls/run|1|Same|
|Repetitions|5|Same|
|Scale ladder|10, 100, 1k, 10k, 100k|Same|
|Adversarial scenarios|6|Same|
|Seed|`20260826`|Same|
|Competent baseline selection and caps|384 facts / 160,000 bytes|Same|
|Ground-truth hash|`4d89...7437`|Same|
|Probe calls|0|0|
|Production mutations|0|0|

Benchmark 2 wrote to a separate output namespace. No Benchmark 1 artifact was overwritten. A regression test fails if the frozen dataset manifest hash changes.

## 4. Minimum Implementation Change

The correction adds one ephemeral, read-only `ConsequentialImpactProjection` over existing governed state. It selects at most one interruption using this precedence:

1. required evidence for an already-conflicted Gate;
2. an existing blocking Impact;
3. an unmaterialized valid authoritative restriction/conflict from a bounded Slice.

If an interruption exists, the sparse packet discards the ordinary Gate evidence packet for that call, projects only the interruption's fact, and asks the bounded decision auditor to re-evaluate the current candidate Gate. It does not mutate state or authorize anything.

Ordinary evidence, non-blocking reminders, benign authoritative references, and unmaterialized unrelated deadlines remain Latent. The fallback restriction/conflict recognition is intentionally narrower than a generic keyword search for every deadline or expiration; temporal and cross-domain deadlines must arrive through the existing Impact contract.

Production integration is limited to adding the same one-item interruption to the career resolver's minimal context when present. Existing Slice manifests and their ordinary projections remain unchanged.

Files changed:

- `military_slices/temporal.py`
- `military_slices/agent_runtime.py`
- `benchmark/run_sparse_activation_benchmark.py`
- `tests/test_sparse_activation_benchmark.py`
- `tests/test_temporal_revalidation.py`

No canonical model schema, persisted state schema, Domain Pack file, Gate transition, Path rule, Probe path, Firestore contract, or UI surface changed.

## 5. Aggregate Run Comparison

|Metric|Benchmark 1|Benchmark 2|Interpretation|
|---|---:|---:|---|
|Primary attempts|110|110|Identical matrix|
|Completed structured responses|109|110|B1 had one malformed 100k baseline response|
|Failed responses|1|0|No retries in either run|
|Strict-correct runs|79|100|Remaining 10 failures are Dense Dependency in both conditions|
|Model calls|110|110|Identical call count|
|Measured input tokens|1,131,614|1,150,240|B1 excludes usage for its malformed response; totals are not directly cost-normalized|
|Measured output tokens|9,095|8,808|Hosted response variance|
|Measured total tokens|1,146,447|1,164,709|Includes provider token accounting|
|Estimated model cost|$0.882817|$0.895710|B1 is a lower bound because malformed-call usage was lost|
|Estimated runtime cost|$0.010117|$0.009712|Counterfactual Cloud Run active-time accounting|
|Estimated total cost|$0.892934|$0.905422|Not actual billing; B1 undercounts one call|
|Probe calls|0|0|Probe remained disabled|
|Production mutations|0|0|Release boundary preserved|

Aggregate cost rose 1.40%, but that comparison is confounded by Benchmark 1's unmetered malformed model response and hosted output/latency variance. Per-scenario input tokens and deterministic overhead are the more defensible comparison.

## 6. Normal Scaling: Benchmark 1 vs Benchmark 2

All normal HELM runs were correct in both benchmarks. Active facts remained 8 at every scale.

|Governed Facts|B1 HELM Input|B2 HELM Input|B2 Baseline Input|B2 Context Reduction|B1 HELM Cost|B2 HELM Cost|B2 vs B1 Cost|B1 Deterministic|B2 Deterministic|
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|10|1,982|1,993|1,446|-37.83%|$0.001880|$0.001873|-0.39%|0.220 ms|0.259 ms|
|100|1,986|1,997|5,818|65.68%|$0.001932|$0.001882|-2.60%|0.415 ms|0.463 ms|
|1,000|1,990|2,001|24,839|91.94%|$0.001884|$0.001872|-0.66%|1.636 ms|2.422 ms|
|10,000|1,990|2,001|25,630|92.19%|$0.001957|$0.001841|-5.94%|18.787 ms|26.411 ms|
|100,000|1,997|2,008|25,631|92.17%|$0.001875|$0.001919|+2.33%|206.738 ms|330.103 ms|

Deterministic time is frontier selection + retrieval + dependency lookup + serialization. It excludes synthetic state construction and model latency.

Normal context bytes increased by 42 bytes at every scale: 5,726→5,768 bytes at 10 facts and 5,739→5,781 at 100,000. That is the complete measured normal-packet expansion. The active fact count, task count, horizon size, Gate, and dependency recall did not change.

At 100,000 facts, Benchmark 2 added a second bounded scan to find a consequential interruption: dependency lookup rose from 0.001 ms to 138.545 ms while retrieval fell from 203.432 ms to 188.854 ms. Total deterministic work therefore rose 123.365 ms even though model context remained bounded.

This supports “bounded active context.” It does not support “sub-linear total-system computation.”

## 7. Sparse Adversarial Recall Comparison

|Scenario|B1 HELM Correct|B2 HELM Correct|B1 Recall|B2 Recall|B1 Active Facts|B2 Active Facts|B1 Input|B2 Input|B2 vs Baseline Context Reduction|B2 vs Baseline Cost Reduction|
|---|:---:|:---:|---:|---:|---:|---:|---:|---:|---:|---:|
|Hidden Dependency|0/5|5/5|0%|100%|8|1|1,990|1,704|93.14%|91.56%|
|Cross-Domain Collision|0/5|5/5|0%|100%|8|1|1,997|1,697|93.20%|91.49%|
|Temporal Activation|0/5|5/5|0%|100%|8|1|1,998|1,711|93.14%|91.55%|
|Conflict|0/5 strict|5/5|0%|100%|8|1|1,937|1,638|93.41%|91.90%|

Every Benchmark 2 repetition selected the expected Gate, selected the expected next decision, recalled the required fact ID, introduced no unsupported dependency, and required no downstream rework under the frozen rubric.

The Conflict correction is substantive: Benchmark 1 named the correct conflict Gate but omitted its authoritative evidence. Benchmark 2 projected that evidence and achieved full strict correctness in 5/5 runs.

## 8. Adversarial Computational Comparison

|Scenario|B1 HELM Deterministic|B2 HELM Deterministic|B1 HELM Cost|B2 HELM Cost|B2 Baseline Cost|
|---|---:|---:|---:|---:|---:|
|Hidden Dependency|1.867 ms|2.298 ms|$0.001853|$0.001606|$0.019032|
|Cross-Domain Collision|1.807 ms|2.077 ms|$0.001894|$0.001634|$0.019200|
|Temporal Activation|1.851 ms|1.827 ms|$0.001951|$0.001611|$0.019078|
|Conflict|2.060 ms|1.565 ms|$0.001806|$0.001538|$0.018993|

The corrected sparse packets were smaller than Benchmark 1 because the new projection replaces ordinary active-Gate evidence with the single material interruption. Model-cost reductions versus the broad baseline therefore survived the recall fix in these four cases.

No claim is made that the same result holds when many Impacts are simultaneously material.

## 9. Dense Dependency: Preserved Negative Result

The dense case contains three simultaneously material facts:

- employer intellectual-property restriction;
- fourteen-day location deadline;
- expiring income-supporting certification.

Frozen strict ground truth requires the employment-restriction Gate/decision and recall of all three dependencies.

|Condition|B1 Correct|B2 Correct|B1 Recall|B2 Recall|B2 Selected Gate|B2 Recalled|B2 Missed|
|---|:---:|:---:|---:|---:|---|---|---|
|Baseline|0/5|0/5|1/3|1/3|`renew-certification`|Certification|Employer restriction; location deadline|
|HELM|0/5|0/5|0/3|1/3|`employment-restriction`|Employer restriction|Certification; location deadline|

Benchmark 2 HELM improved Gate/decision selection and recalled one dependency, but it still failed the strict dense contract in every repetition. The one-item interruption projection is intentionally sparse; it cannot represent three simultaneously material blockers.

This result was not patched, reweighted, or redefined after execution. It remains the boundary at which the tested sparse advantage loses quality completeness.

## 10. Cheap-Context Case: Preserved Economic Loss

|Metric|B1 Baseline|B1 HELM|B2 Baseline|B2 HELM|
|---|---:|---:|---:|---:|
|Correctness|5/5|5/5|5/5|5/5|
|Input tokens|1,446|1,982|1,446|1,993|
|Estimated cost/run|$0.001444|$0.001926|$0.001463|$0.001913|
|Mean end-to-end latency|2,136.2 ms|3,809.9 ms|2,747.8 ms|3,781.8 ms|

Benchmark 2 HELM used 37.83% more input tokens and cost 30.79% more than its baseline. The correction did not disguise or remove the small-state crossover loss.

## 11. Latency

No external latency claim is supported.

Benchmark 2 retained these hosted-provider outliers:

|Run ID|Condition|End-to-End|
|---|---|---:|
|`normal-1000-baseline-r2`|Baseline|9,642.5 ms|
|`cross-domain-collision-baseline-r1`|Baseline|23,836.6 ms|
|`cheap-context-helm-r5`|HELM|8,980.2 ms|

The normal 100,000-fact HELM mean increased from 2,164.5 ms to 3,476.9 ms, but deterministic overhead explains only about 123 ms of that change; hosted model variance explains the remainder. Five repetitions remain insufficient for a reliable latency distribution.

## 12. Failure Ledger

|Run/group|Benchmark|Failure or anomaly|Included?|Disposition|
|---|---|---|:---:|---|
|`normal-100000-baseline-r1`|B1|Malformed/truncated structured response|Yes|Not retried; usage missing from B1 cost|
|Hidden Dependency HELM, 5 runs|B1|0/5; required fact absent|Yes|Corrected to 5/5 in B2|
|Cross-Domain Collision HELM, 5 runs|B1|0/5; blocking Impact absent|Yes|Corrected to 5/5 in B2|
|Temporal Activation HELM, 5 runs|B1|0/5; stale/expiring Impact absent|Yes|Corrected to 5/5 in B2|
|Conflict HELM, 5 runs|B1|Correct Gate/decision but authoritative evidence absent|Yes|Corrected to 5/5 strict in B2|
|Dense Dependency, 10 runs|B1|Both conditions 0/5 strict|Yes|Retained|
|Dense Dependency, 10 runs|B2|Both conditions 0/5 strict|Yes|Retained; HELM recall improved 0/3→1/3|
|Cheap Context HELM|B1 and B2|Higher tokens/cost than baseline|Yes|Retained|
|Three latency outliers listed above|B2|Hosted latency variance|Yes|Retained in all statistics|
|All 110 primary attempts|B2|No malformed output or timeout|Yes|No retries performed|

The Google ADK run emitted the same non-fatal advisory warning about direct automatic function calling. It did not alter completion or scoring.

## 13. Total-System Accounting

Costs use the same published prices as Benchmark 1:

- Gemini 3.7 Flash: $0.75/million input tokens and $3.75/million output tokens;
- counterfactual Cloud Run request-based execution: $0.000024/vCPU-second, $0.0000025/GiB-second, and $0.40/million requests at 1 vCPU/1 GiB.

Actual billing export remains **NOT MEASURED**. Datastore reads/writes attributable to the synthetic selection were 0/0. Tools invoked were 0. Probe calls were 0.

Benchmark 2 did not merely count token savings: measured frontier, dependency, retrieval, preprocessing, model, and end-to-end durations are retained per run. The new linear dependency scan is charged through measured end-to-end runtime. Downstream rework is flagged but not monetized; dense-case costs therefore understate the economic effect of incomplete recall.

## 14. Falsification Answer

**Did the recall correction reintroduce broad context?**  
No in the tested battery. Normal active facts remained 8; corrected sparse adversarial packets used 1 fact.

**Did normal tokens regress materially?**  
No. The observed increase was 11 input tokens and 42 serialized bytes per normal HELM run.

**Did deterministic overhead regress?**  
Yes. At 100,000 facts it increased 59.67%, from 206.738 ms to 330.103 ms, because the implementation performs an additional scan. Total computation is still not sub-linear.

**Did sparse adversarial recall improve?**  
Yes for every frozen Hidden, Cross-Domain, Temporal, and Conflict repetition: 0/20 to 20/20.

**Did dense dependency become complete?**  
No. HELM improved from 0/3 to 1/3 recalled dependencies but remained 0/5 strict.

**Did HELM become cheaper in the cheap-context case?**  
No.

**Was orchestration tested?**  
No. This remains one bounded decision auditor, one model call, no tools, and Probe disabled. No multi-agent wake-only-affected-agent claim is supported.

## 15. New Risks Introduced by the Fix

- The unmaterialized authoritative fallback recognizes restrictions/conflicts using a bounded lexical rule. It may miss semantically equivalent blockers phrased without those terms.
- A falsely classified authoritative restriction could preempt the normal packet. Negative tests cover benign authoritative occupational evidence and an unrelated unmaterialized deadline, not all possible false positives.
- The implementation scans facts to find an authoritative interruption; large-state deterministic overhead increased.
- Only one interruption is projected. Simultaneous dependencies remain incomplete by construction.
- The career resolver can now see one cross-Slice interruption outside its ordinary Slice manifest, justified only by the read-time consequential-interruption contract. Independent review should verify this is the minimum permitted conclusion and does not become broad serialization.

## 16. Validation

Before the live run:

- Pytest: 234 passed
- Benchmark-specific frozen-manifest regression: passed
- Ruff on production code, Benchmark 2 code, and changed tests: passed
- strict Mypy on 16 source files: passed
- Bandit on production and Benchmark 2 code: passed; scoped deterministic/local-process suppressions retained
- Dependency audit: no known vulnerabilities; unpublished local package skipped
- JavaScript syntax: passed; no JavaScript changed
- `git diff --check`: passed
- Cloud Run release boundary: Ready; `military-slices-00001-niw` 100%, `military-slices-00041-yud` 0%; no deploy or traffic mutation command executed

Required regression coverage includes:

- byte-identical Benchmark 1/2 ground-truth manifest;
- normal 100,000-fact frontier remains 8 facts;
- hidden authoritative restriction forces exactly one fact;
- cross-domain and temporal blocking Impacts force exactly one fact;
- conflicted Gate includes its required authoritative evidence;
- non-blocking Impact remains Latent;
- benign authoritative reference remains Latent;
- unrelated unmaterialized deadline remains Latent;
- read-time projection performs zero governed mutation;
- Probe remains zero;
- baseline caps remain unchanged.

## 17. Reproduction Instructions

Checkout commit `754d0e73106c4df8bc6d352d8c338523c028d187`, authenticate Google Application Default Credentials, and run from repository root:

```powershell
$env:GOOGLE_GENAI_USE_VERTEXAI = "true"
$env:GOOGLE_CLOUD_PROJECT = "veteran-pathfinder-kf-2026"
$env:GOOGLE_CLOUD_LOCATION = "global"
$env:GIT_CONFIG_COUNT = "1"
$env:GIT_CONFIG_KEY_0 = "safe.directory"
$env:GIT_CONFIG_VALUE_0 = (Get-Location).Path
$env:SPARSE_BENCHMARK_IMPLEMENTATION_COMMIT = (git rev-parse HEAD)

.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\ruff.exe check military_slices benchmark\run_sparse_activation_benchmark.py tests\test_sparse_activation_benchmark.py tests\test_temporal_revalidation.py
.\.venv\Scripts\mypy.exe --strict military_slices benchmark\run_sparse_activation_benchmark.py
.\.venv\Scripts\bandit.exe -q -r military_slices benchmark\run_sparse_activation_benchmark.py
.\.venv\Scripts\pip-audit.exe
node --check static\app.js

.\.venv\Scripts\python.exe benchmark\run_sparse_activation_benchmark.py `
  --benchmark-commit $env:SPARSE_BENCHMARK_IMPLEMENTATION_COMMIT `
  --output-label benchmark-2
```

Do not omit `--output-label benchmark-2`; the separate namespace protects Benchmark 1 artifacts.

## 18. Raw Evidence and Hashes

Benchmark 1:

- `benchmark/output/sparse-activation-raw-2026-08-26.json` — `408ddfda483622a1e096a83bf05f7d25d99dc3a835d8c7d474b754225e7db23e`
- `benchmark/output/sparse-activation-summary-2026-08-26.json` — `2f4c89ca172a21e9952c3fb204733d25e1208b908f9db2f340ff23bcc5a3874c`
- `benchmark/output/sparse-activation-summary-2026-08-26.csv` — `62445ae753b1cbbebc8727ddd1bbe096c60f1369a444a3a4aec03d0c97f4ea8d`
- `benchmark/output/sparse-activation-dataset-manifest-2026-08-26.json` — `eb599eaf866259483d7ed3a31bbe698ffa78f43cb5713faecf25af54b5dcf15d`

Benchmark 2:

- `benchmark/output/sparse-activation-benchmark-2-raw-2026-08-26.json` — `2957ec634738ce947f50b6b8ed5c18df69880407f21535955c339e4d749179f0`
- `benchmark/output/sparse-activation-benchmark-2-summary-2026-08-26.json` — `71ed638930a81b17cc6e729cfbc3ba4b59c356eab554f149f56a9fc3a7d3795a`
- `benchmark/output/sparse-activation-benchmark-2-summary-2026-08-26.csv` — `c1e554f40245a426ec02c9f10ae39b2a256a160e3762c92fa9d510d558568d56`
- `benchmark/output/sparse-activation-benchmark-2-dataset-manifest-2026-08-26.json` — `eb599eaf866259483d7ed3a31bbe698ffa78f43cb5713faecf25af54b5dcf15d`

Benchmark 2 source:

- `benchmark/run_sparse_activation_benchmark.py` — `f6d587d1df1f8042b709325c21cb6607b28ca1cf46f6d383a5c250cc5f1fb175`
- `military_slices/temporal.py` — `a442ea5e51486b7e04c3491924eed43b27c6a756b4363ebffdfae4e425c31c55`
- `military_slices/agent_runtime.py` — `661356c4646f49455cd2c1ebad947b86e7639baf17d9981a0cec72457e396a69`
- `tests/test_sparse_activation_benchmark.py` — `af173a4af311d0bbd37614f8b43a88483851c1da4e2151803214d46a0ab85b2a`
- `tests/test_temporal_revalidation.py` — `0a19de9b725be080c30c75a6043add7eb9a4cd93b846c6187ee3516c8e60b467`

Official pricing references:

- <https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing>
- <https://cloud.google.com/run/pricing?authuser=0>

## 19. Scope Boundary

This benchmark does not establish:

- sub-linear total-system computation;
- general recall completeness beyond the frozen scenarios;
- dense-dependency completeness;
- a latency advantage;
- a cheap-context advantage;
- autonomous Probe safety or value;
- multi-agent orchestration savings;
- generalization beyond Military SLICES;
- production release fitness;
- actual cloud billing savings.

No production traffic, profile, database, Domain Pack policy, canonical HELM primitive, external effect, or Probe authority was changed.

## 20. NND Review Questions

1. Is the authoritative restriction/conflict fallback a fair minimum Impact materialization rule, or benchmark-specific retrieval tuning?
2. Does projecting a single cross-Slice interruption preserve epistemic permission, or should only an adjudicated conclusion cross the Slice boundary?
3. Is the 59.67% deterministic-overhead increase at 100,000 facts acceptable given the repaired recall and retained 92.17% token reduction?
4. Should Dense Dependency use an explicit multi-blocker decision shape, or should the smallest-frontier contract require iterative one-at-a-time resolution with a separate test rubric?
5. Does a one-item interruption index need a persisted/indexed implementation before any computational scaling claim can advance beyond “bounded model context”?
6. What broader adversarial vocabulary is required to test false-negative and false-positive authoritative interruption materialization?
7. What independent orchestration benchmark is necessary before any wake-only-affected-agent claim is discussed?

## 21. BHE Engineering Disposition

**LIMITED MEASURED ADVANTAGE**

Benchmark 2 is stronger evidence than Benchmark 1: it demonstrates that the four diagnosed sparse Impact failures can be corrected without giving up the measured normal-context and model-cost advantage. It also preserves the evidence that HELM loses at cheap context, remains incomplete under dense dependency, incurs linear selection overhead, and has not been tested as a multi-agent orchestration system.

This is sufficient to continue internal engineering and independent review. It is not sufficient for a general computational, safety, orchestration, investor, or production claim.
