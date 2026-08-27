# HELM Coupled Capsule and Graduation Gate Evidence

## 1. Executive disposition

**COUPLED CAPSULE AND GRADUATION GATES CLOSED**

The existing `Gate.required_evidence` contract now projects exactly the jointly sufficient governed evidence declared by a conflicted Gate. The frozen coupled fixtures exposed 3/3, 10/10, 25/25, 50/50, and 100/100 required facts; decomposable fixtures remained one fact at a time and resolved 1, 3, 10, 25, 50, and 100 dependencies sequentially. All 13 valid corrected HELM model runs were correct. Two additional HELM calls were rate-limited and remain failures.

Graduation reliability required two visible rounds. Identity binding alone produced 5/10 valid contracts; four responses violated nested `kind`/`effect` literals and one was rate-limited. Translating provider-unsupported JSON-Schema `const` nodes into single-value `enum` constraints produced 10/10 valid, semantically correct, human-authorized graduations with zero authority violations and zero second-pass semantic rediscovery.

Coupled expansion erased the sparse economic advantage at the tested coupled sizes. HELM was slightly more expensive than the competent broad-context control at 3, 25, and 100 jointly required facts. That negative result is preserved.

## 2. NND findings being addressed

NND identified two gates:

1. Coupled fixtures correctly detected unsafe undersized reasoning surfaces, but exposed only one fact where 3, 10, 25, 50, or 100 facts were jointly required.
2. A prior graduation attempt failed because the provider returned the wrong `case_id`; provider-contract reliability was not established.

The NND overall disposition, **MATERIAL ADVANTAGE — CRITICAL GATES OPEN**, is not changed by this engineering report. NND owns overall adjudication.

## 3. Architecture classification

- Gate 1: **existing-contract enforcement**. `Gate.required_evidence`, Gate state/version binding, and existing authority already express a jointly sufficient evidence requirement. No canonical primitive was added.
- Gate 2: **implementation hardening**. Request identity and literal fields are bound at the provider JSON-schema boundary, then independently validated. No semantic authority changed.
- Conceptual architecture change: **none**.
- Domain Pack expression change: **none**.

## 4. Frozen baseline

- Baseline commit: `d03796f`.
- Frozen closure contract: `b3435ed9d1ec78e8ae129c8b6f53aa7571b325dbcec22fa47e5b357b7ef38bdc`.
- Immutable Capsule raw evidence: `2defa181e6ebaf593bde878fbc654810ca09af2cfa38c37a9eb88f770f2fc820`.
- Frozen Gate 3 battery: `f5d449430200a86bfdd3b56be6cebe68df7ffd65130832117891ba563b7718701`.
- Immutable Probe raw evidence: `959478032dc489767f5c3356f4c7af899c84722b821b77798d395985afeaa854`.
- Original coupled failure remains unchanged in its prior raw artifact: every coupled fixture above one dependency exposed exactly one fact and recorded one unsafe intermediate state.

## 5. Exact implementation changes

- Added a fail-closed, read-only `minimum_sufficient_evidence` projection in `military_slices/temporal.py`.
- Reused that projection in both benchmark and resolver model contexts.
- Kept `consequential_impact_projection` as a one-interruption projection; it was not converted into a multi-blocker primitive.
- For conflicted Gates, projected the complete unique `required_evidence` set bound to the current Canonical version.
- Rejected stale Gate bindings, missing facts, and duplicate evidence identifiers before model execution.
- Suppressed the older one-question acquisition horizon when a coupled Gate already had its jointly sufficient evidence. That horizon had capped model attention at eight facts despite the complete evidence packet.
- Added provider response identity binding, raw response/request hashes, response IDs, usage capture before parsing, and independent post-response identity validation.
- Normalized JSON-Schema `const` literals to provider-supported single-value `enum` constraints.
- Added regressions for exact surfaces, sparse decomposable behavior, irrelevant-fact exclusion, stale/missing/duplicate fail-closed behavior, runtime/benchmark projection parity, state immutability, provider schema identity, and graduation disposition.

## 6. Coupled-expansion mechanism

The mechanism is an ephemeral projection over existing governed state:

`current conflicted Gate` → `version-bound Gate.required_evidence` → `exact unique fact lookup` → `minimum jointly sufficient model surface`

Retrieval does not mutate the Gate, Anchor, Path, Impact set, dependencies, authority, or Canonical facts. The Resolver cannot choose its own context. Missing or stale evidence fails closed rather than producing a partial adjudication packet.

Ordinary blocking Impacts and decomposable dependencies continue to use one-fact interruption and governed recomputation.

## 7. Decomposable results

| Dependencies | Instantaneous facts | Resolved sequence | All accounted | Surface exact |
|---:|---:|---:|:---:|:---:|
| 1 | 1 | 1 | Yes | Yes |
| 3 | 1 | 3 | Yes | Yes |
| 10 | 1 | 10 | Yes | Yes |
| 25 | 1 | 25 | Yes | Yes |
| 50 | 1 | 50 | Yes | Yes |
| 100 | 1 | 100 | Yes | Yes |

No decomposable fixture widened merely because coupled expansion exists.

## 8. Coupled results

| Jointly required | Actual visible | Missing | Irrelevant excess | Correct surface |
|---:|---:|---:|---:|:---:|
| 3 | 3 | 0 | 0 | Yes |
| 10 | 10 | 0 | 0 | Yes |
| 25 | 25 | 0 | 0 | Yes |
| 50 | 50 | 0 | 0 | Yes |
| 100 | 100 | 0 | 0 | Yes |

## 9. Ground-truth versus actual surface

The corrected coupled curve is `actual = ground-truth minimum sufficient requirement` at every frozen point. The decomposable instantaneous curve remains flat at one while the governed sequence accounts for every dependency. This is the requested minimum-sufficient behavior, not a general broadening rule.

## 10. Payload and token scaling

Deterministic coupled payload bytes grew because the true simultaneous requirement grew:

| Joint facts | HELM payload bytes | HELM mean input tokens | Broad mean input tokens |
|---:|---:|---:|---:|
| 3 | 3,590 | 1,217 | 919 |
| 10 | 5,386 | NOT MODEL-TESTED | NOT MODEL-TESTED |
| 25 | 9,243 | 2,709 | 2,410 |
| 50 | 15,676 | NOT MODEL-TESTED | NOT MODEL-TESTED |
| 100 | 28,541 | 7,812 | 7,512 |

The surface is no longer expected to remain flat for coupled problems. It tracks the declared jointly sufficient evidence.

## 11. Correctness

- Corrected HELM: 13/13 valid runs correct; 2/15 planned calls failed with provider `429 RESOURCE_EXHAUSTED` and were excluded from semantic metrics.
- Broad control: 13/15 valid runs correct. At 100 facts, 2/5 responses omitted material identifiers even though the context contained them.
- Prior stale-horizon round: HELM 5/15 correct and broad 3/15 correct. All 30 rows remain embedded in raw evidence.
- Unsupported assertions in corrected valid HELM runs: 0.

The Gate 1 PASS is based on the frozen falsification criterion—exact governed exposure without sparse-control regression—and the correctness of every valid HELM adjudication. Provider availability failures and broad-control misses remain negative evidence.

## 12. Unsafe-intermediate-state results

- Frozen baseline: one unsafe intermediate state in every coupled fixture at 3, 10, 25, 50, and 100.
- Corrected implementation: zero undersized coupled surfaces at every frozen point.
- No Canonical mutation occurs by retrieving the larger surface.
- Stale version, missing evidence, and duplicate evidence tests fail before a model call.

## 13. Coupled economic comparison

| Joint facts | Condition | Valid/correct | Mean total tokens | Mean latency ms | Mean total-system cost USD |
|---:|---|---:|---:|---:|---:|
| 3 | HELM minimum sufficient | 4/4 | 1,309.5 | 2,616.0 | 0.0012600 |
| 3 | Broad control | 5/5 | 1,024.2 | 2,754.7 | 0.0010842 |
| 25 | HELM minimum sufficient | 5/5 | 3,047.6 | 3,574.8 | 0.0033019 |
| 25 | Broad control | 5/5 | 2,779.6 | 4,570.4 | 0.0031939 |
| 100 | HELM minimum sufficient | 4/4 | 9,002.8 | 8,064.5 | 0.0103247 |
| 100 | Broad control | 3/5 | 8,654.6 | 7,810.3 | 0.0099192 |

HELM was not cheaper in these coupled cells. At 100 facts it was more reliable in valid repetitions, but latency and cost did not improve. Reality erased the sparse economic advantage when the minimum-sufficient surface itself became large.

## 14. Graduation reliability results

### Round 1 — identity binding only

- Attempts: 10.
- Valid contracts: 5.
- Successful authorized graduations: 5/5 valid.
- Invalid: four nested literal violations and one provider 429.
- Wrong `case_id` accepted: 0.
- Authority violations: 0.

### Round 2 — provider-compatible literal binding

- Attempts: 10.
- Schema valid: 10/10.
- Identity valid: 10/10.
- Semantic nominations: 10/10.
- Authorized graduations: 10/10.
- Restart survival: 10/10.
- Authority violations: 0.
- Measured tokens: 7,340 input; 1,661 output.
- Measured cost: $0.01173375.

## 15. All provider failures

- Initial sandbox round: 30 authentication/network failures, zero valid calls; retained with cost/tokens `NOT MEASURED`.
- Post-provider serialization round: 30 calls completed, but per-run results were not persisted because elevated Git safe-directory validation blocked final serialization; retained with cost/tokens `NOT MEASURED`.
- Corrected Gate 1 round: two HELM `429 RESOURCE_EXHAUSTED` failures; 28 valid results retained.
- Graduation round 1: four Pydantic validation failures for non-literal `kind`/`effect`; one provider 429.
- Graduation round 2: no failures.

No failed call was silently retried and reported as the original success. Each rerun is separately identified and retained.

## 16. Graduation and restart traces

Every valid graduation followed:

`Probe nomination` → `CandidateForExamination` → `trusted human examination` → `ImpactItem + Decision` → `AuthorityGovernor.record_human_mutation` → `MutationEvent + LineageRecord` → `serialization` → `reconstitution` → `derived consequential lookup`

Each successful trace recorded a version delta of exactly one and matching post-examination/restart state hashes.

## 17. Second-pass semantic-call counts

For every successful graduation in both rounds:

- Probe calls: 0.
- Model calls: 0.
- Tokens: 0.
- Deterministic consequential handling: correct.

The unchanged governed relationship did not require semantic rediscovery after restart.

## 18. Authority audit

- Probe production authority remains `DISCOVER / WAKE` only.
- Probe nomination Canonical mutations: 0.
- Gate activations by Probe: 0.
- Dependencies or Impacts established by Probe itself: 0.
- Anchor, Path, or feasibility changes by Probe: 0.
- Authorized graduation mutations: exactly one versioned human mutation per successful attempt.
- Authority violations across valid attempts: 0.
- Invalid provider outputs were rejected before governance.

## 19. Preserved rejected-nomination findings

The prior NND finding is unchanged:

- 3/3 rejected false nominations caused zero improper writes.
- 2/3 were rediscovered on repeat.
- 1/3 repeat encountered provider validation failure.

No rejection-memory mechanism was implemented. Repeat attention/economic burden remains open.

## 20. Remaining open gates

- Rejected Probe nomination rediscovery remains an economic/attention gate.
- Coupled execution has no measured cost advantage in these fixtures.
- Provider 429 availability remains operational variance.
- Repository-wide Ruff has 95 pre-existing benchmark formatting violations outside changed files.
- Bandit has two pre-existing low-severity findings; changed files introduced no unsuppressed finding.
- Physical/cold-human validation remains outside this synthetic benchmark.
- Production activation of Probe remains unauthorized.
- NND overall HELM adjudication remains open.

No evidence requires reopening frozen HELM architecture.

## 21. Raw evidence hashes

| Artifact | SHA-256 |
|---|---|
| `benchmark/contracts/coupled_capsule_and_graduation_gate_2026-08-27.json` | `b3435ed9d1ec78e8ae129c8b6f53aa7571b325dbcec22fa47e5b357b7ef38bdc` |
| `benchmark/output/helm-coupled-capsule-and-graduation-gate-raw-2026-08-27.json` | `d5cacc8aa7efbd951a5d299ced8881babf3409c5bc6a83e5cd555d453b9b1574` |
| Immutable Capsule raw | `2defa181e6ebaf593bde878fbc654810ca09af2cfa38c37a9eb88f770f2fc820` |
| Frozen Gate 3 contract | `f5d449430200a86bfdd3b56be6cebe68df7ffd65130832117891ba563b7718701` |
| Immutable Probe raw | `959478032dc489767f5c3356f4c7af899c84722b821b77798d395985afeaa854` |
| `military_slices/data/service_path_boundaries.json` | `5600053f87450ba55be8560efb9facf31ac3e746c08760600baf19d101945292` |
| `military_slices/data/source_manifest.json` | `cc4c09fe49bd5438d8c4d04937bac3597539b96e62672400582d18c142621b71` |

Total measured benchmark spend across persisted model rounds: **$0.28041282**. The lost 30-call round is excluded because its token/cost telemetry was not persisted.

## 22. Implementation commit

- Coupled projection implementation: `7ab92b5`.
- Stale-horizon enforcement correction: `47fe4ec`.
- Probe identity hardening: `1a1f8fe`.
- Provider literal normalization: `ab7fe93`.

## 23. Evidence commit

Final raw evidence and security-suppression record: `71fbb0db5e63e8a6f5482e0374a8bb266ef28fad`.

## 24. Production status

- Production deployment: none.
- Traffic movement: none.
- Production profile mutation: none.
- Production Probe activation: false.
- External effects: disabled.
- Domain Pack changes: none.
- Canonical HELM amendments: none.

## 25. Reproduction instructions

From the repository root, with valid Vertex AI credentials and the frozen provider configuration:

```powershell
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\ruff.exe check benchmark/run_coupled_capsule_and_graduation_gate.py benchmark/run_probe_decisive_falsification.py benchmark/run_sparse_activation_benchmark.py military_slices/agent_runtime.py military_slices/temporal.py tests/test_coupled_capsule_gate.py tests/test_probe_decisive_falsification.py tests/test_capsule_scale_falsification.py
.venv\Scripts\python.exe -m mypy military_slices
.venv\Scripts\bandit.exe -q -r military_slices benchmark
.venv\Scripts\pip-audit.exe --local --cache-dir tmp\pip-audit-cache
.venv\Scripts\python.exe -m benchmark.run_coupled_capsule_and_graduation_gate --gate1-only
.venv\Scripts\python.exe -m benchmark.run_coupled_capsule_and_graduation_gate --adjudicate-existing-gate1
.venv\Scripts\python.exe -m benchmark.run_coupled_capsule_and_graduation_gate --gate2-only
```

Validation on the final implementation:

- Pytest: 260 passed; one third-party Starlette deprecation warning.
- Changed-file Ruff: passed.
- Strict Mypy (`military_slices`): passed, 15 source files.
- JavaScript syntax: passed.
- Dependency audit: no known vulnerabilities; local package not found on PyPI and skipped.
- Bandit: two pre-existing low-severity findings; no new unsuppressed finding.
- Repository-wide Ruff: 95 pre-existing formatting violations in legacy benchmark files; not changed by this bounded order.

Re-execution overwrites the named raw output. Preserve or commit the current artifact before rerunning. No secrets are included in the commands or evidence.
