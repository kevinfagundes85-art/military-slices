# HELM Sparse Activation Benchmark Evidence

Execution date: 2026-08-26 (America/Los_Angeles)  
Evidence status: Completed, with all preflight and primary-run failures retained  
Release boundary: Local/synthetic benchmark only; production traffic, profiles, databases, Domain Pack policy, Probe authority, and external effects were not changed

Post-run Cloud Run read-back at `2026-08-27T03:11:28Z` showed service Ready, production revision `military-slices-00001-niw` at 100% canonical traffic, and frontier candidate `military-slices-00041-yud` tagged at 0% canonical traffic.

## 1. Executive Result

Across the normal 10, 100, 1,000, 10,000, and 100,000-fact ladder, the HELM projection used 8 active facts and 1,982-1,997 input tokens. The competent broad-context baseline used 9, 81, and then its model-safe cap of 384 context facts, consuming 1,446, 5,818, and 24,839-25,631 input tokens. At 100-100,000 governed facts, HELM reduced input context by 65.86%-92.24% and estimated total-system cost per run by 59.43%-90.49%. At 10 facts, HELM increased input context by 37.07% and estimated cost by 27.01%.

Normal-scenario consequential recall and next-decision accuracy were preserved in all 25 HELM runs and 24 of 25 baseline runs; one 100,000-fact baseline response was malformed and was not retried. Mean latency did not improve consistently: HELM was faster at 10, 1,000, and 100,000 facts, but slower at 100 and 10,000 because of two provider-latency outliers. Median latency was less variable, but five repetitions are insufficient for a reliable latency claim.

The stronger quality hypothesis failed. HELM missed the required material dependency in every Hidden Dependency, Cross-Domain Collision, Temporal Activation, and Conflict repetition. In Conflict, deterministic HELM state selected the correct conflict Gate and next decision, but the projected evidence omitted the authoritative conflict fact. Both conditions failed the deliberately dense case: the baseline recalled one of three dependencies, while HELM recalled none. Therefore, the measured computational advantage is accompanied by material quality loss under adversarial dependency activation.

Primary execution comprised 110 attempts, 109 completed structured responses, 1 malformed response, 1,131,614 measured input tokens, 9,095 measured output tokens, and a lower-bound estimated total cost of $0.892934. That cost excludes the malformed response's unreported usage and one excluded smoke call; actual billing was not measured.

Strongest supported conclusion: the implemented projection can keep normal-path active model context approximately bounded while governed state grows, and this lowers measured model-plus-estimated-runtime cost above the cheap-context case. The current dependency activation/projection is not sufficiently complete to preserve consequential recall in the tested adversarial cases.

## 2. Hypothesis Tested

> “As total governed state grows, HELM can keep active model context approximately bounded by the consequential frontier rather than allowing reasoning context to grow proportionally with total state.”

The stronger economic claim was also tested without presumption:

> “Sparse governed activation reduces total-system computation/cost without unacceptable loss of consequential recall.”

The first claim was supported for the normal synthetic ladder within the tested range and projection rules. The stronger claim was not supported because the adversarial quality loss was material.

## 3. Implementation Under Test

- Implementation commit: `e44ba281c3f0a2775428b9acfa735a7fd90ced1a`
- Benchmark-code commit: `5c9925f08f4109b1274f62441ec0ac1ec93a7709`
- HELM architecture hash: `4dd32923a611ffcad20e73443dc13afc2935ac074e7b4de7a37dc5aa19f9ee81`
- Path runtime hash: `33f24a207acf8587401c54bb40692c3291f3a4aae1d404d3939ba8045bff96ae`
- Acquisition runtime hash: `cc7a8c97d01345693a61cedc56544f2b379ab70c2b397db57b54aa62205eed42`
- Domain Pack version: `2026-08-24-v2-shadow-tested`
- Domain Pack runtime hash: `026a1508a3a2e6eb16907b2e8fc29c4f333af5c5ab908e6029903b8cbcbf9f4c`
- Domain Pack file hash: `5600053f87450ba55be8560efb9facf31ac3e746c08760600baf19d101945292`
- Provider/model: Vertex AI, `gemini-3.7-flash`, global location
- Framework: Google ADK 1.39.0
- Model configuration: temperature 0, top-p 1, maximum 500 output tokens, thinking budget 512, maximum 1 model call per run, strict Pydantic structured output
- Runtime: local synthetic execution; counterfactual Cloud Run request-based cost at 1 vCPU and 1 GiB was attributed to measured wall-clock duration
- Pricing used: $0.75 per million input tokens and $3.75 per million output tokens for Gemini 3.7 Flash; Cloud Run active pricing of $0.000024/vCPU-second, $0.0000025/GiB-second, and $0.40/million requests. Actual billing export: **NOT MEASURED**.
- Execution seed: `20260826`
- Repetitions: 5 per scenario-condition pair

Relevant production functions observed, not modified:

- `military_slices.path_runtime.refresh_path_state`
- `military_slices.engine.active_gate`
- `military_slices.acquisition.build_acquisition_horizon`

Benchmark instrumentation added:

- `benchmark/run_sparse_activation_benchmark.py`
- `tests/test_sparse_activation_benchmark.py`

Instrumentation measured context construction, frontier selection, retrieval, dependency lookup, preprocessing, model events, strict-output validation, hashes, cost estimates, and quality against frozen ground truth. It did not change HELM selection behavior. Synthetic state construction time was measured separately and excluded from per-decision end-to-end latency so scale generation would not be misreported as runtime retrieval.

## 4. Baseline Definition

The competent broad-context baseline used the same governed state, same decision problem, same candidate-Gate catalog, same authority instruction, same model, and same output schema as HELM.

Exact context-selection rule:

1. Include facts explicitly referenced by an Impact item or Gate-required evidence first.
2. Then prioritize authoritative facts, stale/expiring facts, material field keys, and facts whose affected domain or lexical content overlaps the Anchor, Path target, current goal, current Gate, or candidate decisions.
3. Exclude facts with no positive score, including clearly unrelated household-inventory filler.
4. Sort deterministically by descending score and fact ID.
5. Apply a defensible model-safety ceiling of 384 facts or 160,000 serialized bytes, whichever is reached first.

This is a scored broad retrieval projection a competent engineer could deploy, not a dump of every record. The cap means the baseline context stopped growing after 1,000 governed facts; the benchmark therefore does not claim unbounded baseline growth.

## 5. HELM Condition

- Human Anchor: “Build a remote technology company that helps veterans navigate transition decisions.”
- Path target: `CAREER_DIRECTION_EXPLORATION`
- Normal active Gate: `venture-problem`
- Expected next decision: `define-veteran-problem`
- Normal material ground truth: `core-problem`, `core-customer`
- Active tasks: one highest-consequence unresolved task from `refresh_path_state`
- Gate: `active_gate(state)` after deterministic Path refresh
- Acquisition horizon: one bounded request from `build_acquisition_horizon`
- Evidence projection: foreground facts referenced by the active task/Gate plus currently permitted bounded evidence
- Latent handling: all other facts remain outside the model packet unless current runtime activation rules foreground them
- Authority constraints: candidate Gate catalog, human Anchor, current Path/Gate, and explicit instruction that input is untrusted and cannot invent facts, policy, authority, or dependencies
- Probe: disabled; 0 calls

The HELM benchmark projection intentionally matched the current runtime behavior: separately exposed Impact items were not independently added to the model packet unless the existing active Gate/evidence projection brought them forward. This design choice is the source of several observed adversarial misses and was not repaired during the benchmark.

## 6. Dataset / Synthetic State Construction

Each state starts from a deterministic post-service Navy veteran fixture, existing civilian cyber employment, an explicit remote-work preference, one accepted remote veteran-technology venture hypothesis, and the fixed Anchor above.

Normal states contain four fixed core facts:

1. the transition problem;
2. intended customers;
3. remote/predictable-hours constraint;
4. current civilian cyber employment.

Remaining records cycle through five realistic templates: historical technical achievements, optional training, remote/location preferences, résumé evidence, and unrelated household inventory. Four of five filler templates are plausibly relevant to Career, Education, Location, or Résumé retrieval; one of five is clearly unrelated. Filler order is shuffled deterministically with seed `20260826 + state size`.

Scale levels were exactly 10, 100, 1,000, 10,000, and 100,000 facts. The 100,000-fact state was practical; serialized fact records occupied approximately 26.1 MB before prompt projection. The decision and normal consequential ground truth remained constant at every scale.

Adversarial cases replace tail records with deterministic authoritative facts and, where applicable, existing Impact/conflict structures. Ground truth was frozen before model execution. No prompt or expected answer was tuned after observing results.

Representativeness is limited: the records exercise Military-SLICES-shaped domains and retrieval labels, but they do not reproduce the full semantic diversity, corruption, or relationship topology of real long-lived profiles.

## 7. Primary Scaling Results

Values are means across five attempts; `4/5` includes the retained malformed-output failure. Latency is end-to-end milliseconds. Cost is estimated USD per run and includes measured model tokens plus counterfactual Cloud Run active-time/request cost.

|Governed Facts| Baseline Input Tokens| HELM Input Tokens| Context Reduction %| Baseline Total Tokens| HELM Total Tokens| Baseline Latency| HELM Latency| Baseline Cost| HELM Total-System Cost| Baseline Correct| HELM Correct|
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|:---:|:---:|
|10|1,446|1,982|-37.07%|1,676|2,069|3,453.5|2,495.5|$0.001480|$0.001880|5/5|5/5|
|100|5,818|1,986|65.86%|5,903|2,067|2,958.1|5,176.2|$0.004763|$0.001932|5/5|5/5|
|1,000|24,839|1,990|91.99%|25,232|2,076|5,308.9|2,661.8|$0.019142|$0.001884|5/5|5/5|
|10,000|25,630|1,990|92.24%|25,727|2,073|2,546.9|5,764.3|$0.019653|$0.001957|5/5|5/5|
|100,000|25,631|1,997|92.21%|25,844|2,082|4,076.4|2,164.5|$0.019711|$0.001875|4/5|5/5|

Serialized-context reductions were -41.42%, 75.05%, 94.49%, 94.65%, and 94.64%, respectively. Total-token reductions were -23.48%, 64.98%, 91.77%, 91.94%, and 91.94%. Estimated total-system cost reductions were -27.01%, 59.43%, 90.16%, 90.04%, and 90.49%.

Input-token variance was zero within each deterministic context condition. End-to-end latency showed substantial provider variance. Selected mean/median/min/max/standard-deviation values (ms):

|Scale / condition|Mean|Median|Min|Max|Std. dev.|
|---|---:|---:|---:|---:|---:|
|100 / baseline|2,958.1|2,572.8|2,158.1|4,056.3|878.1|
|100 / HELM|5,176.2|2,441.0|1,639.7|16,971.3|6,602.4|
|1,000 / baseline|5,308.9|4,547.2|4,017.8|9,148.4|2,163.4|
|1,000 / HELM|2,661.8|2,515.2|2,329.5|3,343.6|396.6|
|10,000 / baseline|2,546.9|2,418.6|2,388.0|2,802.5|203.1|
|10,000 / HELM|5,764.3|2,142.3|1,820.3|20,812.7|8,413.9|
|100,000 / baseline, completed only|4,076.4|3,865.9|2,975.6|5,598.2|1,145.9|
|100,000 / HELM|2,164.5|2,108.8|1,965.2|2,534.5|236.9|

## 8. Active-State Results

|Governed Facts| Baseline Context Facts| HELM Active Facts| HELM Latent Facts| HELM Active Tasks| Horizon Size| Active Gate|
|---:|---:|---:|---:|---:|---:|---|
|10|9|8|2|1|1|`venture-problem`|
|100|81|8|92|1|1|`venture-problem`|
|1,000|384|8|992|1|1|`venture-problem`|
|10,000|384|8|9,992|1|1|`venture-problem`|
|100,000|384|8|99,992|1|1|`venture-problem`|

“Latent facts” is the benchmark's governed-fact count minus HELM's active projected facts. It is not a claim that every excluded record is semantically irrelevant forever.

## 9. Overhead Accounting

All values are mean milliseconds. Probe and datastore activity were instrumented counts and were zero. Model is provider latency; end-to-end includes deterministic selection/retrieval/preprocessing plus the model. Dataset construction is excluded. Local CPU consumption was not separately metered; runtime cost is a counterfactual Cloud Run estimate from wall-clock duration.

|Governed Facts| Frontier Selection| Retrieval| Dependency Lookup| Probe| Datastore| Model| End-to-End|
|---|---:|---:|---:|---:|---:|---:|---:|
|10 / baseline|0.000|0.065|0.002|0 calls|0 reads / 0 writes|3,453.4|3,453.5|
|10 / HELM|0.074|0.092|0.001|0 calls|0 reads / 0 writes|2,495.2|2,495.5|
|100 / baseline|0.000|0.511|0.001|0 calls|0 reads / 0 writes|2,957.4|2,958.1|
|100 / HELM|0.172|0.187|0.001|0 calls|0 reads / 0 writes|5,175.8|5,176.2|
|1,000 / baseline|0.000|5.855|0.002|0 calls|0 reads / 0 writes|5,302.4|5,308.9|
|1,000 / HELM|0.194|1.386|0.001|0 calls|0 reads / 0 writes|2,660.2|2,661.8|
|10,000 / baseline|0.000|65.968|0.003|0 calls|0 reads / 0 writes|2,480.4|2,546.9|
|10,000 / HELM|0.355|18.360|0.002|0 calls|0 reads / 0 writes|5,745.5|5,764.3|
|100,000 / baseline|0.000|699.669|0.004|0 calls|0 reads / 0 writes|3,375.9|4,076.4|
|100,000 / HELM|3.216|203.432|0.001|0 calls|0 reads / 0 writes|1,957.8|2,164.5|

Relevant dependency/index lookups were recorded per run in the raw JSON. The current implementation still scans the synthetic in-memory fact set to build projections, so deterministic retrieval time grew with total state even while model context stayed bounded. The evidence does not establish sublinear total computation.

## 10. Quality / Recall

|Scenario| Baseline Correct| HELM Correct| Material Dependencies| HELM Recalled| HELM Missed| False Activations| Rework|
|---|:---:|:---:|---|---:|---:|---:|:---:|
|Normal 10|5/5|5/5|2 per run|2.0|0.0|2.0 mean|No|
|Normal 100|5/5|5/5|2 per run|2.0|0.0|2.0 mean|No|
|Normal 1,000|5/5|5/5|2 per run|2.0|0.0|2.0 mean|No|
|Normal 10,000|5/5|5/5|2 per run|2.0|0.0|2.0 mean|No|
|Normal 100,000|4/5|5/5|2 per run|2.0|0.0|2.0 mean|No for completed runs|
|Hidden Dependency|5/5|0/5|1 per run|0.0|1.0|3.4 mean|Yes|
|Cross-Domain Collision|5/5|0/5|1 per run|0.0|1.0|4.0 mean|Yes|
|Temporal Activation|5/5|0/5|1 per run|0.0|1.0|4.0 mean|Yes|
|Conflict|5/5|0/5 strict|1 per run|0.0|1.0|4.0 mean|Yes: evidence projection incomplete|
|Dense Dependency|0/5|0/5|3 per run|0.0|3.0|4.0 mean|Yes|
|Cheap Context|5/5|5/5|2 per run|2.0|0.0|2.0 mean|No|

“Correct” required the correct Gate, correct next decision, full consequential-dependency recall, no unsupported dependency IDs, and valid structured output. In the Conflict case, HELM was 5/5 on Gate and next-decision selection but 0/5 on the strict composite because the required authoritative fact was missing from the projected packet.

## 11. Adversarial Results

### Hidden Dependency

- Setup: a signed employer agreement assigning outside AI-product intellectual property to the employer was placed in a non-obvious Location-classified fact, outside the active Career projection and absent from the installed dependency map.
- Expected behavior: select `employment-restriction`, decide `verify-employment-restriction`, and recall `adv-employment-restriction`.
- Baseline: 5/5 correct; mean 24,842 input tokens, 4,486.4 ms, $0.019053.
- HELM: 0/5; it continued with `venture-problem`, recalled none of the required dependency, and required rework. Mean 1,990 input tokens, 2,553.4 ms, $0.001853.
- Interpretation: large computational reduction with material quality loss. This weakens the stronger HELM hypothesis.

### Cross-Domain Collision

- Setup: a signed lease termination requiring a location decision within fourteen days was represented as a Location fact and existing blocking Impact item.
- Expected behavior: select `location-deadline`, decide `resolve-location-deadline`, and recall `adv-location-deadline`.
- Baseline: 5/5 correct; mean 24,947 input tokens, 3,411.3 ms, $0.019100.
- HELM: 0/5; the Impact was visible to deterministic runtime state but not included in the model projection. Mean 1,997 input tokens, 3,034.6 ms, $0.001894.
- Interpretation: the benchmark found an implementation/projection gap, not evidence that cross-domain dependencies are impossible to govern. The observed system failed the case.

### Temporal Activation

- Setup: an authoritative certification supporting current income expired in seven days, was marked stale/external-expiring, and had a blocking revalidation Impact.
- Expected behavior: select `renew-certification`, decide `revalidate-certification`, and recall `adv-expiring-certification`.
- Baseline: 5/5 correct; mean 24,956 input tokens, 5,357.5 ms, $0.019150.
- HELM: 0/5; stale evidence was ineligible as ordinary evidence and its Impact did not enter the active model projection. Mean 1,998 input tokens, 5,003.1 ms, $0.001951.
- Interpretation: time made a Latent fact consequential, but the tested projection did not activate it. This materially weakens the consequential-recall claim.

### Conflict

- Setup: an authoritative record explicitly prohibited the proposed venture use; the canonical state included a conflicted, high-value Gate requiring that evidence.
- Expected behavior: select `authority-conflict`, decide `resolve-authority-conflict`, and recall `adv-authority-conflict`.
- Baseline: 5/5 fully correct; mean 24,872 input tokens, 2,449.4 ms, $0.018963.
- HELM: correct Gate and next decision in 5/5, but 0/5 full correctness because the authoritative fact itself was not projected. Mean 1,937 input tokens, 2,182.3 ms, $0.001806.
- Interpretation: deterministic Gate supersession worked; evidence continuity did not. A model can name the right conflict action without possessing the evidence needed to resolve it. This is a material contract risk.

### Dense Dependency

- Setup: employment restriction, location deadline, and expiring certification were all simultaneously material.
- Expected behavior: the next bounded move was employment-restriction verification while retaining all three dependencies as material ground truth.
- Baseline: 0/5 strict. It selected certification renewal and recalled only 1/3 dependencies. Mean 25,176 input tokens, 3,705.3 ms, $0.019237.
- HELM: 0/5. It retained the ordinary venture-problem Gate and recalled 0/3 dependencies. Mean 1,997 input tokens, 2,107.3 ms, $0.001875.
- Interpretation: the deliberately non-sparse problem defeated both single-next-decision projections. HELM saved computation but lost all dense dependency coverage; the baseline at least surfaced one urgent dependency. The expected sparse advantage should shrink here, and the quality results confirm that.

### Cheap-Context Case

- Setup: the same normal decision at only 10 governed facts.
- Expected behavior: both conditions select `venture-problem`, decide `define-veteran-problem`, and recall the problem and customer facts.
- Baseline: 5/5 correct; 1,446 input tokens, 2,136.2 ms, $0.001444.
- HELM: 5/5 correct; 1,982 input tokens, 3,809.9 ms, $0.001926.
- Interpretation: HELM used 37.07% more input tokens, cost 33.38% more in this separate adversarial run, and was slower. Governance metadata and projection overhead outweighed sparse-context savings at small state.

## 12. Failure Ledger

|Run ID| Condition| Failure| Cause Known?| Included in Metrics?| Disposition|
|---|---|---|:---:|:---:|---|
|`PRE-001`|Preflight|Git refused repository ownership in the elevated benchmark process before any model call.|Yes|No|Retained in narrative; process-scoped safe-directory configuration used. No global Git change.|
|`PRE-002` batch: all 110 planned IDs|Both|Vertex initialization failed before model calls because the elevated process did not inherit explicit Vertex routing variables.|Yes|No|All 110 zero-token/zero-cost records preserved in `sparse-activation-raw-provider-init-failure-2026-08-26.json`; no selective discard.|
|`SMOKE-001`|HELM|Successful provider/configuration smoke call; 2,067 total tokens and 4,412.2 ms.|Yes|No|Excluded verification call; its exact incremental cost is NOT MEASURED because split token details were not retained in the console record.|
|`normal-100000-baseline-r1`|Baseline|Model returned truncated JSON: EOF while parsing `next_decision`.|No|Yes, as incorrect/failure|Not retried. Provider usage was not preserved by the validation-exception path, so aggregate cost is understated.|
|`normal-100-helm-r5`|HELM|16,971.3 ms latency outlier.|No|Yes|Retained in mean, min/max, standard deviation, and raw evidence.|
|`normal-10000-helm-r3`|HELM|20,812.7 ms latency outlier.|No|Yes|Retained.|
|`temporal-activation-baseline-r5`|Baseline|12,811.2 ms latency outlier.|No|Yes|Retained.|
|`temporal-activation-helm-r5`|HELM|14,351.9 ms latency outlier.|No|Yes|Retained.|
|All 5 Hidden Dependency HELM runs|HELM|Required dependency missed.|Yes|Yes|Quality failure retained.|
|All 5 Cross-Domain Collision HELM runs|HELM|Impact-visible dependency absent from model projection.|Yes|Yes|Quality failure retained.|
|All 5 Temporal Activation HELM runs|HELM|Stale/expiring Impact dependency absent from model projection.|Yes|Yes|Quality failure retained.|
|All 5 Conflict HELM runs|HELM|Correct Gate/decision, but required authoritative evidence omitted.|Yes|Yes|Strict quality failure retained.|
|All 10 Dense Dependency runs|Both|Neither single-next-decision projection recalled all three material dependencies.|Yes|Yes|Quality failures retained.|

The `PRE-002` artifact contains the individual record for every failed planned run. Aggregation here avoids 110 repetitive table rows while preserving every run ID, error, and zero-usage record in the referenced primary evidence.

## 13. Scaling Interpretation

**As governed state increased, did HELM active reasoning context remain approximately bounded?**  
Yes, in this normal scenario and implementation: 8 projected facts, one task, one horizon item, and 1,982-1,997 input tokens from 10 through 100,000 facts. This is an empirical range, not an asymptotic proof.

**Did the baseline grow?**  
Yes, from 9 facts/1,446 input tokens at 10 governed facts to 81/5,818 at 100 and 384/about 25,000 at 1,000. It then remained near 25,600 tokens because the baseline intentionally enforced a 384-fact/160,000-byte safety cap.

**Were HELM's apparent savings offset elsewhere?**  
Not fully in measured normal runs above 10 facts. HELM retrieval still scanned the synthetic state and rose from 0.092 ms to 203.432 ms; baseline retrieval rose to 699.669 ms. The model-token reduction dominated the estimated cost above 10 facts. However, cost accounting used a counterfactual runtime estimate rather than actual billed infrastructure, and the adversarial quality losses imply unpriced downstream rework. If rework were monetized, the stronger economic conclusion would weaken further.

**At what state size, if any, did HELM become cheaper/faster than the baseline?**  
Estimated cost became lower at 100 facts. Mean end-to-end latency was lower at 10, 1,000, and 100,000 facts, but higher at 100 and 10,000 due to provider outliers. No stable latency crossover is established.

**At what state size or dependency density did HELM lose its advantage?**  
At 10 facts, HELM lost the context/cost advantage. At one hidden, cross-domain, temporal, or projection-omitted authoritative dependency, it retained computational savings but lost material recall. With three simultaneous dependencies, its quality advantage was absent and the baseline also failed strict completeness.

## 14. Consequential Recall Interpretation

HELM missed:

- a signed employer intellectual-property restriction outside the obvious active domain;
- a fourteen-day location deadline represented through a cross-domain Impact;
- a stale certification whose expiration made it newly consequential;
- the authoritative evidence underlying a correctly selected conflict Gate;
- all three dependencies in the dense simultaneous-dependency case.

Adversarial attempts included hidden-domain placement, explicit cross-domain collision, temporal freshness change, authoritative contradiction, and dense dependency convergence. These are observed failures, so no perfect-recall claim is available. The normal ladder only demonstrates recall for stable dependencies already inside the current projection.

## 15. Where HELM Won

- Normal active model context remained 8 facts and approximately 2,000 input tokens through 100,000 governed facts.
- At 100-100,000 facts, input-token reductions ranged from 65.86% to 92.24%.
- At 100-100,000 facts, estimated per-run total-system cost reductions ranged from 59.43% to 90.49%.
- Normal Gate, next-decision, and dependency recall were correct in all 25 HELM repetitions.
- The 100,000-fact state was technically practical; HELM projection/retrieval took about 206.7 ms before the model, versus about 700.3 ms for the broad baseline.
- In Conflict, deterministic HELM state correctly superseded normal progression and selected the conflict Gate in all five runs.

## 16. Where HELM Lost

- The 10-fact normal case used 37.07% more input tokens and cost 27.01% more than baseline.
- The separate 10-fact Cheap-Context case was slower and approximately 33.38% more expensive.
- HELM missed all required dependencies in four adversarial classes and all three in the dense case.
- Correct conflict-Gate selection did not preserve the authoritative evidence needed to act on that Gate.
- Mean latency was not consistently lower and included two large HELM outliers.
- Current in-memory retrieval still increased with total state, so bounded model context did not mean bounded total deterministic work.
- The single-scenario normal ladder does not establish a general computational advantage.

## 17. Threats to Validity

- **Synthetic dataset bias:** repeated templates are easier to score and compress than diverse real profiles.
- **Baseline fairness:** the score/cap is defensible but not proven optimal. A vector, graph, or learned retriever could produce a smaller or more complete broad context.
- **Model variance:** five repetitions expose some variance but are insufficient for strong latency or reliability estimates. Temperature zero does not make hosted inference fully deterministic.
- **Military-SLICES-specific assumptions:** the active Gate, fact fields, Impact model, and Domain Pack semantics may not transfer to other HELM products.
- **Retrieval quality:** both projections use benchmark retrieval code around current runtime primitives; performance is sensitive to indexes and dependency mappings.
- **Instrumentation overhead:** timers, serialization, hashing, and event capture add work. Hashing outside the timed decision section was not charged uniformly.
- **State-generation realism:** 100,000 facts are realistic in shape only at a coarse level; relationship density and authority diversity are low.
- **Dependency density:** the normal ladder keeps true dependency count fixed. The dense case shows that savings and quality change when the problem is not sparse.
- **Limited scenario diversity:** one core Anchor and six adversarial variants cannot establish generality.
- **Baseline safety cap:** baseline growth plateaus by design, limiting claims about large-state scaling.
- **Cost estimation:** actual Vertex/Cloud Run billing export was not available. Cloud Run costs are counterfactual and the malformed call's usage is missing.
- **Latency environment:** execution was local against hosted Vertex AI, not from the production Cloud Run network path.
- **Quality rubric:** strict dependency recall may be more demanding than a one-next-move UI, but it is appropriate to the hypothesis that all consequential blockers remain discoverable.

## 18. Reproduction Instructions

Prerequisites:

- checkout commit `5c9925f08f4109b1274f62441ec0ac1ec93a7709`;
- Python environment installed from this repository's locked project dependencies;
- authenticated Google Application Default Credentials with permission to invoke Vertex AI in project `veteran-pathfinder-kf-2026`;
- no secrets placed in command history or evidence artifacts.

PowerShell commands from repository root:

```powershell
$env:GOOGLE_GENAI_USE_VERTEXAI = "true"
$env:GOOGLE_CLOUD_PROJECT = "veteran-pathfinder-kf-2026"
$env:GOOGLE_CLOUD_LOCATION = "global"
$env:GIT_CONFIG_COUNT = "1"
$env:GIT_CONFIG_KEY_0 = "safe.directory"
$env:GIT_CONFIG_VALUE_0 = (Get-Location).Path

.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\ruff.exe check military_slices benchmark\run_sparse_activation_benchmark.py tests\test_sparse_activation_benchmark.py
.\.venv\Scripts\mypy.exe --strict military_slices
.\.venv\Scripts\bandit.exe -q -r military_slices benchmark\run_sparse_activation_benchmark.py
.\.venv\Scripts\pip-audit.exe
.\.venv\Scripts\python.exe benchmark\run_sparse_activation_benchmark.py
```

The script enforces seed `20260826`, five repetitions, one model call per run, strict structured output, model/configuration identity, a $10 estimated-cost rail, and date-stamped output names. Failed outputs are never retried automatically.

## 19. Raw Evidence References

Primary files and SHA-256:

- `benchmark/run_sparse_activation_benchmark.py` — `873245813b0b76ca9a2d3f61ca2c5015eee2b217a63f35ad6943b8fb63112f15`
- `tests/test_sparse_activation_benchmark.py` — `827de39550754f2b9cc5ff47a6c9e6f169737b297ee94b2933204b2fa7f0825a`
- `benchmark/output/sparse-activation-dataset-manifest-2026-08-26.json` — `eb599eaf866259483d7ed3a31bbe698ffa78f43cb5713faecf25af54b5dcf15d`
- `benchmark/output/sparse-activation-raw-2026-08-26.json` — `408ddfda483622a1e096a83bf05f7d25d99dc3a835d8c7d474b754225e7db23e`
- `benchmark/output/sparse-activation-summary-2026-08-26.json` — `2f4c89ca172a21e9952c3fb204733d25e1208b908f9db2f340ff23bcc5a3874c`
- `benchmark/output/sparse-activation-summary-2026-08-26.csv` — `62445ae753b1cbbebc8727ddd1bbe096c60f1369a444a3a4aec03d0c97f4ea8d`
- `benchmark/output/sparse-activation-raw-provider-init-failure-2026-08-26.json` — `40235d4a889afb49f2893ffd4e2bb2020a92f32d66257c9039474394266bdfd2`
- `benchmark/output/sparse-activation-summary-provider-init-failure-2026-08-26.json` — `8fe4ae1fe350884f87b98fb92a9c043000c15cdec417c7466acd06dd0a53f209`
- `benchmark/output/sparse-activation-summary-provider-init-failure-2026-08-26.csv` — `58aa3614f55f5521ba6b3ab5fc445e71c37d70d3c9043670b02d4b798c2010d2`

The raw primary JSON contains every prompt-payload hash, selected context-fact-ID hash, response hash, ADK event-ID hash, usage event, latency component, quality result, failure, tool count, Probe count, datastore count, and production-mutation count. No plot was necessary to support the primary conclusions; the exact scale tables are included above.

Validation evidence before execution:

- Pytest: 228 passed
- Ruff: passed for production code, the new benchmark, and its tests. A full scan of all legacy `benchmark/run_gauntlet*.py` utilities remains red on 95 pre-existing formatting findings; none is in the sparse-activation benchmark.
- strict Mypy: passed for 15 production source files
- Bandit: passed for production code and the new benchmark; a full scan of all legacy benchmark utilities retains one pre-existing low-severity `assert` finding in `run_gauntlet_confirmation.py`
- dependency audit: no known vulnerabilities; local project package not found on PyPI and skipped
- JavaScript syntax/regressions: passed; benchmark changed no JavaScript
- Benchmark-specific regressions: deterministic exact scale; baseline includes ground truth and excludes clear noise; HELM projection bounded to at most 8 facts and one task; hidden dependency absent from HELM/present in baseline; conflict supersession; model-safe baseline cap
- Release boundary read-back: Cloud Run Ready; `military-slices-00001-niw` 100%, `military-slices-00041-yud` 0%; no deploy or traffic command was executed

Official rates used for estimates:

- Google Gemini Enterprise/Agent Platform pricing: <https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing>
- Google Cloud Run pricing: <https://cloud.google.com/run/pricing?authuser=0>

## 20. BHE Engineering Disposition

**MEASURED ADVANTAGE WITH MATERIAL QUALITY LOSS**

The implementation measured a large normal-path context and estimated-cost reduction at 100 or more governed facts. The tested dependency activation/projection did not preserve consequential recall under hidden, cross-domain, temporal, conflict-evidence, or dense-dependency falsification. Independent review should attack both the baseline and the HELM activation boundary before any broader computational or economic claim is made.
