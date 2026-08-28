# HELM Adaptive Resolver Aperture v1 Implementation Evidence

## 1. T1 design identity and hashes

The accepted T1 design remains at commit `b120136ba564f84cd9b261702030edfb4deeb189`.

| Frozen artifact | Recomputed SHA-256 |
|---|---|
| T1 design | `dc8bd82ceb49d053ac67ac17843edfbe1f9f8b646a55871368c7412b3b4bbf6e` |
| Machine contract | `df78c5836a3886ad965611f780b84e65e30d1ff7bd56360c42b50d7a6b6139de` |
| Hidden-authority interface | `daf9e867c5f77d5f19683321bb915aa976c8f8d93c52d549ed226be8a973677c` |
| Role-separation attestation | `fbacd290c76b29991d9da742f1fd46ab5dd2b1ad5157770053eae6487a01f14b` |
| Manifest | `99c756a931f60f4a2292ef9f20b35c83fd80bf999e3ce3af36fc892f5fd2d8ed` |

No frozen T1 artifact was modified.

## 2. NND acceptance

Governing NND disposition: **T1 DESIGN FREEZE ACCEPTED**. The implementation follows NND's classification of Adaptive Resolver Aperture v1 as **existing-contract enforcement + implementation hardening**. The maximum T1 claim remains mechanism-level.

## 3. Exact implementation commit

Implementation commit: `e4b1fa624685d17711a5c68bcc4e836b192673ab`.

## 4. Files changed

| File | Purpose |
|---|---|
| `military_slices/adaptive_resolver_aperture.py` | Stateless selector, exact governed Payload construction, and non-authoritative receipt |
| `tests/test_adaptive_resolver_aperture.py` | 25 developer-fixture falsification tests |
| `benchmark/preflight_adaptive_resolver_aperture_t1_provider.py` | Metadata-only provider availability preflight |

The provider preflight ledger and this evidence package are evidence-commit artifacts, not implementation changes.

## 5. Architecture classification

The implementation adds no Canonical field, persisted aperture state, Gate type, authority, Probe capability, Domain Pack rule, or learned policy. It is a read-only function from a current `CanonicalState` plus ephemeral execution request to an `ApertureSelection`.

## 6. Proof no canonical primitive was added

`military_slices/models.py`, governance models, persistence code, Domain Pack data, and production routes are unchanged. `ExecutionReceipt` is a frozen telemetry model declared only in the new implementation module. Selection was tested against a before/after serialized Canonical-state identity; mutation count was zero.

## 7. Mode-selection implementation

The selector evaluates current governed structure only:

- Mode A: existing state-bound rejection and I1 governed-content lookup;
- Mode B: existing blocking `ImpactItem` sequence scoped to the current Gate;
- Mode C: exact current `Gate.required_evidence` surface;
- Mode D: existing protective path on conflict, invalidation, authority, lifecycle, human Gate, incomplete evidence, or ambiguity;
- Mode E: a permitted Latent Fact is structurally absent from existing required evidence, dependencies, Impacts, and governed rejection lineage.

No model participates in mode eligibility.

## 8. Statelessness proof/tests

The module contains no cache, mutable global policy, prior-mode input, category input, expected-answer input, score input, or learned threshold. The receipt binds the decision to a SHA-256 of the entire current governed snapshot. Identical snapshots and request configuration yield identical eligibility and Payload results.

Canonical governed history remains usable only through the current snapshot, including rejection Decisions, lineage, validity conditions, and lifecycle position.

## 9. Mode precedence

The implemented precedence is:

1. governed protection;
2. valid deterministic reuse;
3. explicit joint `Gate.required_evidence` or existing blocking-Impact sequence;
4. structurally eligible Probe;
5. protective fail-closed fallback.

Economics, coupling ratio, provider latency, prior outcomes, and model uncertainty are absent from this decision.

## 10. Mode A tests

Valid exact governed rejection selected Mode A with zero Payload facts. Authority change, lifecycle change, Gate-contract change, incomplete lineage, and materially different near-match identity did not reuse the prior conclusion. A material invalidation routes to Mode D.

## 11. Mode B tests

Existing blocking Impacts are the actual governed sequential/decomposable representation used by H0. Three declared conditions exposed one Fact at a time. Apparent decomposability without those governed records failed closed. No benchmark-only `decomposable=true` input exists in the selector API.

## 12. Mode C tests

Declared surfaces at 3, 10, 25, 50, and 100 facts exposed exactly 3, 10, 25, 50, and 100 Facts. An extra relevant-looking neighboring Fact was excluded. Missing, stale, unauthorized, duplicate, or stale-Gate evidence produced no partial Payload and selected Mode D.

## 13. Mode D tests

Conflict overrides valid cheap reuse. Explicit lifecycle, authority, and human-Gate runtime bindings select full examination. Rejection invalidation and all incomplete coupled surfaces select the protective path. Correct expensive routing is preserved as an operating boundary, not marked an implementation failure.

## 14. Mode E structural-eligibility tests

Probe eligibility requires all of the following: the runtime permits Probe discovery; a specific permitted Latent Fact exists; Latent state exists; the Fact is valid and Gate-scoped; and its relationship is absent from required evidence, dependencies, Impacts, and governed rejection lineage. Removing runtime permission prevents Mode E. An already-governed relationship prevents Mode E. Probe output cannot establish Probe eligibility.

This validates routing eligibility only; no Probe provider calls were made.

## 15. Coupling-inference prohibition

There is no coupling classifier, heuristic, text rule, statistical model, learned policy, or density threshold. Mode C is reachable only through current `Gate.required_evidence`. Missing or incomplete declarations fail closed.

## 16. Coupling-ratio telemetry isolation

The receipt reports `jointly_required / relevant_available` with `telemetry_only=true`. A regression added 20 relevant-but-not-required Facts, changed the ratio, and verified that selected mode, required evidence IDs, and Payload were unchanged.

## 17. Fail-closed tests

The implementation distinguishes missing required evidence, stale Gate binding, invalid Fact, unauthorized Fact, unknown relationship, and ambiguous mode. Each emits a stable reason code and an empty Payload under Mode D. Partial coupled adjudications observed: **0**.

## 18. Authority audit

| Invariant | Local result |
|---|---:|
| Stale suppressions | 0 |
| Authority violations | 0 |
| Improper governance bypasses | 0 |
| Model-selected authority | 0 |
| Inferred coupling | 0 |
| Ratio-driven routing | 0 |
| Ungoverned broad exposure | 0 |
| Partial coupled adjudication | 0 |
| Relevant invalidation bypass | 0 |
| Unauthorized Canonical mutation | 0 |
| Probe self-eligibility | 0 |

These are developer-fixture results, not T1 evaluation results.

## 19. H0 non-regression

H0 source code was not modified. The complete existing suite, including sparse activation, coupled capsule, governed identity, state-bound rejection, lifecycle, Probe-contract, and runtime tests, passed: **297/297**. The pre-existing Starlette/httpx deprecation warning remains.

## 20. Execution-receipt schema

Every receipt contains task/decision ID, governed snapshot hash, Gate identity/version, selected mode, stable deterministic reason code, evidence IDs, Payload hash, rejected alternative modes, coupling-ratio telemetry, and any fail-closed condition. It is frozen telemetry/provenance and is not stored in Canonical state.

## 21. Full validation results

| Check | Result |
|---|---|
| Targeted H1 Pytest | PASS — 25/25 |
| Complete Pytest | PASS — 297/297 |
| Changed-file Ruff | PASS |
| Repository-wide Ruff | FAIL — 152 pre-existing errors in benchmark utilities; no H1-file error |
| Strict Mypy | PASS — 17 source files |
| Bandit | PASS |
| Dependency audit | PASS — no known vulnerabilities; unpublished local package skipped |
| JavaScript syntax | PASS — `static/app.js` |

Repository-wide Ruff debt was not repaired under this order.

## 22. Provider availability preflight

Configuration: Vertex AI, project `veteran-pathfinder-kf-2026`, location `global`, model `gemini-3.7-flash`.

Attempt 1 failed locally before reaching the provider because a temporary SDK client closed before `models.get`; this failure is preserved. After retaining the client, attempt 2 successfully resolved `publishers/google/models/gemini-3.7-flash`, version `default`.

The operation was metadata-only `models.get`. Benchmark task content transmitted: **false**. Benchmark generation calls: **0**.

## 23. Production status

Production state, traffic, profiles, Domain Packs, and canonical HELM are unchanged. Production Probe remains disabled. No external effects occurred. No T1 corpus, ground truth, scoring key, or hidden authority schedule was opened. T1 execution has not begun.

## 24. Known limitations

- These are synthetic developer fixtures, not the sealed T1 corpus.
- The selector returns the governed mode and exact Payload boundary; the sealed T1 runtime operator must bind that output to the already-existing path identified by the mode without changing eligibility semantics.
- Mode E testing covers structural eligibility, not provider nomination quality.
- The implementation deliberately provides no inference when Gate evidence topology is absent.
- Correct Mode D/E routing may remain more expensive than H0 or broad context.

## 25. Exact artifacts and hashes

| Artifact | SHA-256 |
|---|---|
| H1 module | `17a232c7b61d995ad9c4d08cab0d47586c7d6b18ed08f478033a5b60226d0ef1` |
| H1 tests | `ece28ba7b442f85979eacaf41d0be38275aa5f1a56417f1a82f2683b9b725701` |
| Provider preflight script | `0a55ecdc1ea3b6ddc9a55fd6751986db9f6df02d6ec38f9e909f5951f68b344c` |
| Provider preflight ledger | `de919ba8212a0e6a58581979877bc35749eb6646e9c95caf02c9b7f5032070af` |
| Raw implementation evidence | `e69a6914b22349c2b3a2227977ae27b62cb3ffe9daacccd73fbaa46c9578d0d9` |

## 26. NND pre-execution questions

1. Does the use of existing blocking Impacts as the real governed sequential/decomposable declaration satisfy Stratum 2's non-label requirement?
2. Does the Mode E structural test preserve the accepted discovery boundary without allowing the candidate or Probe model to authorize eligibility?
3. Does returning a mode plus exact Payload boundary provide a sufficient H1 runtime binding, provided the sealed runtime invokes only the corresponding existing path?
4. Does NND accept the preserved local preflight-client failure followed by one valid metadata resolution as provider availability evidence?
5. May NND now independently inspect commit `e4b1fa624685d17711a5c68bcc4e836b192673ab` and, if accepted, seal the T1 corpus without exposing labels, ground truth, or authority schedule to BHE?

## Implementation disposition

**H1 IMPLEMENTATION READY FOR SEALED T1**

This is a pre-execution implementation disposition only. No T1 benchmark claim is made.
