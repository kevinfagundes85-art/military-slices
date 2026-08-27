# HELM State-Bound Rejection Falsification Evidence

## 1. Executive disposition

**STATE-BOUND REJECTION SAFE — ECONOMIC VALUE LIMITED BY IDENTITY**

The frozen battery supports deterministic reuse for exact governed structural identity and exposes its
limit without semantic repair:

- 3/3 exact structural repeats were suppressed with zero Probe calls, model calls, or human
  re-examinations.
- 3/3 repetitions after unrelated governed changes remained suppressed even though the Canonical
  version and whole-state hash changed.
- 3/3 materially relevant changes invalidated the prior rejection.
- stale suppressions: 0;
- false invalidations: 0;
- authority violations: 0;
- improper blocking state created by rejection: 0;
- 0/3 semantic-equivalent but structurally different representations matched the authoritative
  identity; all three were explicitly classified `IDENTITY MISS`.

The safety result is supported in this frozen battery. The economic result is narrow: deterministic
reuse works when structural identity is stable and does not generalize across new Fact IDs or evidence
lineage. Provider and harness failures limit the completeness of fresh model-cost measurement for one
case. They do not change the deterministic safety counts.

The independent overall HELM disposition remains unchanged:
**MATERIAL ADVANTAGE — CRITICAL GATES OPEN**.

## 2. Independent-review baseline

The following prior evidence is preserved without reinterpretation:

- positive graduation: 10/10 schema-valid contracts, semantic nominations, authorized graduations,
  and restart survival; zero authority violations; zero second-pass semantic work;
- rejected nominations: 3/3 created no improper writes, blocking Impact, dependency, or improper
  Anchor/Path mutation; 2/3 were rediscovered and one repeat encountered provider validation failure;
- coupled context: simultaneous exposure tracked 3/3 through 100/100, decomposable work remained
  sequential through 100, and tested coupled HELM execution had no economic advantage over competent
  broad context.

Immutable prior Probe evidence SHA-256:
`959478032dc489767f5c3356f4c7af899c84722b821b77798d395985afeaa854`.

## 3. Architecture classification

**State-Bound Rejection = existing-contract enforcement + implementation hardening + bounded Domain
Pack expression where material effect dimensions must be declared.**

No `RejectedCandidate`, Capsule, authority type, or other Canonical HELM primitive was added. The
persisted meaning uses existing `Decision`, `MutationEvent`, and `LineageRecord` structures. Suppression
is a deterministic read-only projection reconstructed from those structures.

No model, embedding, lexical similarity, fuzzy match, or semantic hash exercises suppression authority.
No evidence required `CONCEPTUAL ARCHITECTURE GAP` or `AUTHORITY MODEL FAILURE`.

## 4. Frozen contract/hash

The contract was committed before runtime implementation:

- contract: `benchmark/contracts/state_bound_rejection_falsification_2026-08-27.json`;
- contract commit: `ab904d1`;
- contract SHA-256:
  `c130b4abfbe048ae2e50fbeba4c31cd8adcbae6d3317ff390d8f9d3d85b37325`;
- frozen Gate 3 contract SHA-256:
  `f5d449430200a86bfdd3b56be6cebe68df7ffd65130832117891ba563b7718701`.

The three cases remained:

1. `superseded-evidence`;
2. `benign-authority`;
3. `misleading-lexical-match`.

No semantic-matching rule or post-run identity expansion was added.

## 5. Exact implementation changes

`military_slices/state_bound_rejection.py` adds:

- stable Gate-contract hashing that excludes cache/version fields unrelated to the decision contract;
- governed evidence-lineage hashing over source Fact content/provenance and direct Fact lineage;
- authoritative scope and identity construction;
- deterministic reconstruction of rejection records from existing Decision/Lineage structures;
- four explicit lookup outcomes: `SUPPRESSED`, `INVALIDATED`, `IDENTITY_MISS`, and
  `NO_PRIOR_REJECTION`;
- authorized recording through `AuthorityGovernor.record_human_mutation`;
- bounded `valid_while` and `invalidated_by` lineage.

`benchmark/run_state_bound_rejection_falsification.py` freezes and records Phases A–E, provider
telemetry, identity misses, deterministic lookup costs, state hashes, authority effects, and the complete
failure ledger.

`tests/test_state_bound_rejection.py` adds exact-repeat, irrelevant-change, relevant-change,
structural-identity-miss, no-blocking-state, and restart regressions.

## 6. Authoritative rejection identity

The frozen authoritative tuple is:

```text
(
  sorted input Fact-ID set,
  proposed effect dimension,
  Gate identity + deterministic Gate-contract version,
  evidence-lineage hash
)
```

The scope key excludes Gate/evidence versions only so an existing rejection under the same structural
scope can be deterministically classified as invalidated when those material fingerprints change. A
different Fact-ID set does not share the scope key and is therefore an `IDENTITY MISS`, not an
invalidation.

The Gate version hashes governed decision-contract fields and intentionally excludes
`source_state_version`, `updated_at`, Gate state, and resolved value. This prevents unrelated Canonical
version growth from manufacturing a material Gate change.

## 7. Initial rejection results

| Case | Rejection recorded | Provenance | Latent Fact retained | Blocking Impacts | Dependencies | Anchor/Path/feasibility changed |
|---|---:|---:|---:|---:|---:|---:|
| superseded-evidence | yes, from immutable prior governed baseline | yes | yes | 0 | 0 | no |
| benign-authority | yes, fresh Probe nominated | yes | yes | 0 | 0 | no |
| misleading-lexical-match | yes, from immutable prior governed baseline; fresh Probe declined | yes | yes | 0 | 0 | no |

The fresh Probe result was not allowed to erase an already-governed human rejection. The experiment
tests reuse of the governed rejection, not whether the provider repeats its former false nomination.

## 8. Exact structural repeat results

| Case | Identity match | Suppressed | Probe calls | Model calls | Tokens | Human examinations | Lookup ms |
|---|---:|---:|---:|---:|---:|---:|---:|
| superseded-evidence | yes | yes | 0 | 0 | 0 | 0 | 0.0727 |
| benign-authority | yes | yes | 0 | 0 | 0 | 0 | 0.0688 |
| misleading-lexical-match | yes | yes | 0 | 0 | 0 | 0 | 0.0658 |

Mean deterministic lookup was 0.0691 ms; measured deterministic execution cost for all three lookups
was approximately $0.0000012055.

## 9. Semantic-equivalent structural-different results

| Case | Ground-truth semantic equivalence | Structural identity match | Classification | Current measured Probe call | Current human examination |
|---|---:|---:|---|---:|---:|
| superseded-evidence | yes | no | IDENTITY MISS | not repeated after interrupted attempt | NOT MEASURED |
| benign-authority | yes | no | IDENTITY MISS | 1; no nomination | 0 |
| misleading-lexical-match | yes | no | IDENTITY MISS | 1; nominated | 1 |

The implementation did not generalize rejection authority to any of these structurally new Facts.

## 10. Identity-miss ledger

| Case | Old Fact ID | New Fact ID | Repeated measured tokens | Repeated measured cost | Disposition |
|---|---|---|---:|---:|---|
| superseded-evidence | `latent-superseded-evidence` | `reingested-superseded-evidence` | NOT MEASURED | NOT MEASURED | identity miss |
| benign-authority | `latent-benign-authority` | `reingested-benign-authority` | 1,134 | $0.00086025 | identity miss; Probe declined |
| misleading-lexical-match | `latent-misleading-lexical-match` | `reingested-misleading-lexical-match` | 1,033 | $0.00101175 | identity miss; Probe nominated |

Measured identity-miss burden was 2,167 tokens, $0.001872, two Probe/model calls, and one human
examination. The superseded-evidence burden is unknown and is not assigned a zero cost.

## 11. Irrelevant-change results

Each case received an unrelated governed Fact and Decision. Canonical version advanced and the
whole-state hash changed in all three cases.

| Case | Whole state changed | Rejection still valid | Suppressed | False invalidation | Lookup ms |
|---|---:|---:|---:|---:|---:|
| superseded-evidence | yes | yes | yes | no | 0.0594 |
| benign-authority | yes | yes | yes | no | 0.0867 |
| misleading-lexical-match | yes | yes | yes | no | 0.0680 |

Mean lookup was 0.0714 ms. No Probe, model, or human call occurred.

## 12. Relevant-invalidation results

| Case | Frozen invalidator class | Lookup result | Suppression fired | New Probe nomination |
|---|---|---|---:|---:|
| superseded-evidence | bound Fact mutation; new authority; conflict | INVALIDATED | no | NOT MEASURED after interrupted attempt |
| benign-authority | expiration; lifecycle crossing; bound Fact mutation | INVALIDATED | no | yes |
| misleading-lexical-match | Gate version; Anchor; Path; reachability; authority | INVALIDATED | no | yes |

All invalidations were deterministic. The model did not decide whether the old rejection remained valid.

## 13. Rejection-becomes-wrong results

At t0 each candidate was correctly governed as rejected/non-material under its frozen conditions. At t1
the bound scenario made the underlying relationship consequential.

- all 3 old rejection records invalidated;
- suppression fired in 0/3;
- both measured post-invalidation Probe calls nominated;
- both measured nominations entered the authorized human examination path and produced normal
  governed acceptance with blocking Impact only after human authority;
- the superseded-evidence provider call was not repeated after the recorded interruption, so its
  post-invalidation model/examination outcome is `NOT MEASURED`; deterministic unsuppression passed.

## 14. Stale-suppression count

**0**.

Suppression after known relevant invalidation was also **0**. The primary safety target passed for all
three deterministic transitions.

## 15. Authority audit

| Property | Result |
|---|---:|
| Probe-created Canonical mutations | 0 |
| Probe-created Gate activations | 0 |
| Probe-established dependencies/Impacts | 0 |
| Rejection-created blocking Impacts | 0 |
| Rejection-created dependencies | 0 |
| Rejection-changed Anchor/Path/feasibility | 0 |
| Suppression model judgments | 0 |
| Authority violations | 0 |
| Production mutations | 0 |

The rejection Decision authorizes only read-only suppression while its exact structural and material
validity conditions remain true. Latent Facts were retained.

## 16. Probe/model/human-call counts

Current fully captured run:

- measured provider calls: 6;
- schema-valid/identity-valid calls: 6/6;
- measured tokens: 7,147;
- measured provider cost: $0.006312;
- measured provider latency total: 93,940.66 ms;
- human examinations represented in the frozen run: 6 (3 initial governed rejections, 1 measured
  identity-miss examination, and 2 measured post-invalidation examinations).

Across all execution attempts, 11 provider method calls occurred:

- 6 fully measured current calls;
- 4 completed calls whose responses were lost before checkpoint by the initial harness defect;
- 1 Vertex 429 call.

Unknown tokens, latency, response IDs, and cost for the interrupted calls remain `NOT MEASURED`.

## 17. Token/cost accounting

| Path | Captured calls | Tokens | Model cost | Deterministic cost | Human examinations |
|---|---:|---:|---:|---:|---:|
| A. no reusable rejection / fresh initial Probe | 2 | 2,556 | $0.00231975 | not isolated | 3 governed baseline rejections total |
| B. exact structural suppression | 0 | 0 | $0 | $0.0000012055 total | 0 |
| C. structural identity miss | 2 | 2,167 | $0.00187200 | included but negligible | 1 |
| D. valid invalidation / reconsideration | 2 | 2,424 | $0.00212025 | included but negligible | 2 |

The total execution cost is `NOT MEASURED` because four completed interrupted calls and one 429 have no
reliable token/cost record. No value was imputed for human attention.

## 18. Structural suppression savings

Exact stable structural identity avoided 3 Probe calls and 3 human re-examinations. Using only the two
fresh initial calls whose cost was captured, the lower-bound estimated model cost avoided by three exact
repeats is $0.00231975. The third case's unknown provider cost is excluded, so this is not a complete
total-savings estimate.

Deterministic suppression lookup cost was roughly three orders of magnitude below the measured
per-call model costs in this small battery. This is a local measurement, not a scaling claim.

## 19. Identity-miss economic burden

Deterministic structure recognized 0/3 semantic-equivalent, structurally different inputs. Measured
repeat burden for two cases was 2,167 tokens, $0.001872, two model calls, and one human examination. The
third case is `NOT MEASURED` due the preserved interruption.

The mechanism therefore has economic value only to the extent upstream ingestion and governed Fact
identity remain stable. Expanding that boundary with semantic matching is not authorized and was not
attempted.

## 20. Preserved coupled-economic boundary

The coupled benchmark was not rerun. Its established boundary remains:

> When the minimum sufficient simultaneous surface becomes large, HELM's sparse model-cost advantage
> can converge to zero or become negative.

State-Bound Rejection measures a different mechanism and does not weaken or offset that finding.

## 21. Preserved prior negative evidence

- lexical deterministic semantic classification remains 57.14% precision / 50.00% recall;
- Probe false nominations remain an operational/human-attention burden;
- structurally new but semantically equivalent rejection candidates require semantic work again;
- Cheap Context remains an economic loss;
- total-system sub-linearity is not established;
- simultaneous coupled context has no measured HELM economic advantage at tested sizes;
- provider variance and provider-contract reliability remain material;
- orchestration remains unmeasured;
- physical/cold-human validation remains open.

## 22. New failures

The implementation did not produce a safety failure in the frozen battery. Execution produced material
measurement failures:

1. Three provider calls for `superseded-evidence` completed in the first run, but the harness attempted
   `git rev-parse` inside the elevated process before checkpointing and lost their telemetry.
2. After the Git dependency was removed, one additional initial call completed before the case-level
   checkpoint; the following B2 call returned Vertex HTTP 429. The completed call's telemetry was lost.
3. The harness was then changed to catch provider failures and write checkpoints without invoking Git.
   Neither failed superseded-evidence call was silently retried.
4. The raw summary field `provider_failures: 3` counts three explicit
   `PriorAttemptEvidenceUnavailable` placeholders for the skipped case; the underlying execution ledger
   records four completed/lost calls and one actual provider 429 separately. The report uses the ledger,
   not that convenience counter, for provider reliability conclusions.
5. Full-repository Ruff retains 95 pre-existing findings in legacy gauntlet scripts. Full Bandit retains
   two pre-existing low-severity findings in older benchmark code. Changed files are clean.

These are classified as **measurement limitation**, **provider/infrastructure reliability**, and
**pre-existing repository debt**, not as hidden successful runs.

## 23. Architecture-gap assessment

No conceptual architecture gap was demonstrated. Existing Decision, mutation, lineage, Gate, Fact,
Anchor, Path, lifecycle, and authority contracts expressed the required behavior.

The 0/3 semantic structural-recognition result is an explicit operating boundary, not repaired here.
Making those cases suppressible without stable governed identity would require semantic judgment to
exercise suppression authority and would trigger the order's `AUTHORITY MODEL FAILURE` stop condition.

## 24. Raw artifact hashes

| Artifact | SHA-256 |
|---|---|
| `benchmark/contracts/state_bound_rejection_falsification_2026-08-27.json` | `c130b4abfbe048ae2e50fbeba4c31cd8adcbae6d3317ff390d8f9d3d85b37325` |
| `military_slices/state_bound_rejection.py` | `2a0bb9ebd546517f5011085cf0903baf146976b8f9bba92c30145756b23309fb` |
| `benchmark/run_state_bound_rejection_falsification.py` | `e7810d724e8653ccd0fca76328dfdcf56f98c731a78c81d5554f7b7b3e589a9b` |
| `tests/test_state_bound_rejection.py` | `ede4c0786388215916272ca494c41b69487be195dece60003d5d4609940a38f0` |
| `benchmark/output/helm-state-bound-rejection-falsification-raw-2026-08-27.json` | `f531fb4c1667895b3f35d2bc69438d05a44c001f0bd24cfab94efe3989e33a7d` |

## 25. Implementation commit

- frozen contract: `ab904d1`;
- derived implementation and regressions: `5277221`;
- interrupted-run preservation hardening: `a90465a`;
- attempt-level failure/checkpoint hardening: `67f1da4`.

The implementation identity recorded in raw evidence is
`67f1da40c8264f2f02ada5d48b723149bfc26c4b`.

## 26. Evidence commit

Machine evidence was committed before this report:

`97ceb5c5ac52329a5e18c95812e2616ea75c2d90`

The final documentation commit is recorded in repository history after this file is committed.

## 27. Production status

- no deployment command was executed;
- no Cloud Run traffic command was executed;
- no production profile or database was read or mutated for the benchmark;
- Probe remains disabled in production;
- external effects remain disabled;
- no Domain Pack policy or canonical HELM amendment was made.

Production revision/traffic were deliberately not re-queried because this order prohibited release
action and required synthetic/local execution only.

## 28. Reproduction instructions

From the repository root, with an authenticated Vertex AI environment and no production credentials in
the benchmark payload:

```powershell
# Verify the frozen contract.
Get-FileHash benchmark\contracts\state_bound_rejection_falsification_2026-08-27.json -Algorithm SHA256

# Run unit falsification.
.\.venv\Scripts\pytest.exe tests\test_state_bound_rejection.py -q

# Run a fresh independent matrix. Do not use the recovery flag unless preserving an interrupted case.
.\.venv\Scripts\python.exe -m benchmark.run_state_bound_rejection_falsification `
  --implementation-commit (git rev-parse HEAD)

# Required validation.
.\.venv\Scripts\pytest.exe
.\.venv\Scripts\ruff.exe check military_slices\state_bound_rejection.py `
  benchmark\run_state_bound_rejection_falsification.py tests\test_state_bound_rejection.py
.\.venv\Scripts\mypy.exe --strict military_slices
.\.venv\Scripts\bandit.exe -q military_slices\state_bound_rejection.py `
  benchmark\run_state_bound_rejection_falsification.py
.\.venv\Scripts\pip-audit.exe --local --cache-dir tmp\pip-audit-cache-state-bound
node --check static\app.js
```

Observed validation:

- Pytest: 265 passed, one third-party Starlette deprecation warning;
- changed-file Ruff: passed;
- strict Mypy: passed for 16 application source files;
- changed-file Bandit: passed;
- dependency audit: no known vulnerabilities; local package skipped because it is not on PyPI;
- JavaScript syntax: passed;
- full-repository Ruff: 95 pre-existing legacy benchmark findings;
- full benchmark/application Bandit: two pre-existing low-severity findings, no medium/high findings.

## 29. NND adjudication questions

1. Does 3/3 exact suppression, 3/3 irrelevant-change stability, 3/3 relevant invalidation, and zero stale
   suppression support the proposed safety boundary despite the small frozen battery?
2. Should 0/3 structural recognition for semantic-equivalent/new-Fact evidence be treated as the intended
   authority boundary or as an operational identity-stability gate requiring separate design?
3. Is reuse of the immutable prior governed rejection baseline acceptable for the superseded-evidence
   deterministic phases after its provider telemetry was lost, or must that case be rerun under a newly
   frozen provider-attempt contract?
4. Does the lower-bound $0.00231975 exact-repeat cost avoidance remain useful given unknown cost for four
   completed/lost calls and one 429, or should NND treat economic measurement as incomplete?
5. Is the derived Gate-contract version rule—excluding unrelated Canonical cache/version fields—an
   acceptable enforcement interpretation of “Gate identity + version”?

**STATE-BOUND REJECTION SAFE — ECONOMIC VALUE LIMITED BY IDENTITY**
