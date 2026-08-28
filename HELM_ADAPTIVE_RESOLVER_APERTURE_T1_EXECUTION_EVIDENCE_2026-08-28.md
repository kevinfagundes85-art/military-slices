# HELM Adaptive Resolver Aperture v1 — T1 Execution Evidence

## 1. Executive disposition

**ADAPTIVE APERTURE INCONCLUSIVE — OPERATING BOUNDARY**

The sealed r3 T1 corpus executed across H0, H1, and the competent broad-context arm. The run did not establish or falsify Adaptive Resolver Aperture because the frozen execution binding did not define a scoreable final outcome for Mode A or Mode E. Sixty-six H1 tasks (27.5%) therefore produced the correct frozen path-specific artifact but no value in the frozen final-outcome enum. No post-hoc mapping, repair, selective rerun, or scoring-rule amendment was performed.

This is mechanism-level evidence only. It does not change the overall HELM disposition.

## 2. Frozen corpus identity

- Corpus: `helm-arav1-t1-corpus-2026-08-28-r3`
- Final public manifest: `e0afb2f05d072de3dc89e4b0b5e8139f30839bfb82595cf131b7e9ce8803eee0` (5,069 bytes)
- Corpus and runner commit: `7a7b396d52d64e4506e890615ab0e5744a45f5cd`
- Tasks: 240, six shards of 40
- Public corpus validation: 240/240 valid against the actual `ReplacementT1PublicTask` model and H1 selector
- Sealed ground truth, expected modes, harm assignments, authority schedule, and scoring key remained in NND custody.

## 3. Execution identity

- Clean provider-output commit: `ed451fd4b532236d3c5cef003ccad0dbeff6550f`
- Compact scoring-extract commit: `054661dc47d5d1f4f0306161bcb6aa51898d96b2`
- Clean raw ledger SHA-256: `533bfa3d61f1f778c04ab33f9f458ecda236e82aa66ad362d1593a5317a91834`
- Preserved sandbox transport-failure ledger SHA-256: `549e648de3812028c81a2ea03994faefe5913ea545360e25d6aee047d5b5dcf6`
- NND frozen disposition SHA-256: `bd9354367ac161f84f7874dd0814251691094e60cabf1537a1b09d2e94ec66ed`

## 4. Arms and completeness

| Arm | Arm-task results | Logical provider calls | Attempts | Valid provider responses | Final provider failures | Zero-call reuse |
|---|---:|---:|---:|---:|---:|---:|
| H0 | 240 | 240 | 246 | 232 | 8 | 0 |
| H1 | 240 | 208 | 219 | 195 | 13 | 32 |
| B | 240 | 240 | 254 | 240 | 0 | 0 |

The earlier summary phrase “227 valid H1 provider responses” was incorrect because it included the 32 zero-call reuse results. The reconciled H1 accounting is 195 valid provider responses + 13 final provider failures + 32 zero-call reuse results = 240.

## 5. H1 deterministic selections

| Mode | Count |
|---|---:|
| A — Deterministic reuse | 32 |
| B — Sparse aperture | 40 |
| C — Wide governed aperture | 44 |
| D — Full governed examination | 90 |
| E — Probe/discovery | 34 |

Reason-code counts were: 44 declared joint requirements, 40 declared decomposable surfaces, 34 structurally eligible Probe cases, 32 valid deterministic reuses, 25 full invalidation examinations, 20 ambiguous-mode fail-closed cases, 13 authority examinations, 10 lifecycle examinations, 8 conflict examinations, 8 human-Gate examinations, and two each for invalid Fact, missing evidence, and stale Gate fail-closed handling.

NND independently reported that selected modes and reason codes matched its sealed expected modes on every row it inspected. NND inspected 240 of the 720 compact arm-task rows (shards 1 and 2); it did not assert corpus-wide scoring results.

## 6. Provider configuration and observed behavior

All requests were made to Vertex AI `gemini-3.7-flash` with the frozen request configuration: temperature 0, top-p 1, maximum output 900, `include_thoughts=false`, and `thinking_budget=0`.

Vertex nevertheless returned nonzero `thoughts_token_count`. The request configuration remained conformant; the returned telemetry is preserved as a **provider configuration behavior deviation / availability limitation**. Thinking tokens were charged at the frozen output-token rate and were not erased or reclassified.

| Arm | Input tokens | Output tokens | Provider-reported thinking tokens | Total tokens | Provider cost | Mean attempt latency | Median attempt latency |
|---|---:|---:|---:|---:|---:|---:|---:|
| H0 | 799,054 | 23,352 | 5,938 | 828,344 | $0.709128 | 5,794 ms | 2,319 ms |
| H1 | 507,557 | 26,577 | 12,274 | 546,408 | $0.526359 | 7,571 ms | 3,088 ms |
| B | 336,144 | 27,350 | 28,287 | 391,781 | $0.460747 | 8,242 ms | 3,420 ms |

These cost figures are descriptive only. The frozen design prohibited economic adjudication before completeness, hard-gate validation, and correctness non-inferiority passed.

## 7. Provider failures

- Initial sandboxed launch: 688/688 provider attempts failed before authentication with a local network `TransportError`; zero provider tokens and zero provider cost. The entire ledger is preserved separately.
- Clean launch: 31 retryable 429 attempts were retained (H0 6, H1 11, B 14).
- Final clean-run failures: H0 8 and H1 13, all schema/JSON truncation `ValidationError`; B 0.
- Failed tasks were not excluded, silently retried, or repaired.

## 8. Authority-oracle audit

The sealed authority schedule contained 21 preregistered entries. No oracle request was made during execution. Therefore:

- requests served: 0;
- events delivered: 0;
- generated or simulated responses: 0;
- authority result for every task: `null`;
- retrospective schedule application: prohibited and not performed.

This is an execution-protocol limitation, not a result repaired after provider outputs were visible.

## 9. Hard-gate audit

BHE's compact extract records zero for all nine hard-gate counters because H1 routing was read-only, provider outputs were non-authoritative proposals, and no Canonical mutation path executed. NND independently confirmed all nine counters were zero in the 240 rows it inspected, but did not make a corpus-wide independent assertion.

## 10. Decisive execution-binding defect

The frozen C-6/C-7 binding fixed provider call counts and response types but did not specify a deterministic conversion into the final adjudication enum for:

- 32 Mode A tasks, which directly emitted the existing governed Decision (`candidate_relationship_rejected`); and
- 34 Mode E tasks, which emitted only the ratified one-call `ProbeDecision`, with no follow-on adjudication call.

Neither artifact is one of `PASS`, `WAIT`, `HUMAN`, `REANCHOR`, `TERMINATE`, or `FAIL`. No implemented deterministic path emitted such a value for these modes. Mapping either after observing results would amend the frozen scoring rule. Consequently, correctness and non-inferiority were not adjudicated.

## 11. Arm B corpus defect

NND identified that `broad_context_case.case_file` supplied prose but no governed Fact identifiers. Arm B therefore could not reliably cite evidence IDs testable against sealed ground-truth evidence IDs. NND classified this as a corpus-authoring defect affecting the secondary H1-versus-B comparison; it was not relabeled as an Arm B failure.

## 12. Statistics and economics

No McNemar test, paired Newcombe interval, Wilcoxon test, Hodges–Lehmann estimate, bootstrap interval, or materiality adjudication was validly produced. Correctness was undefined for 66 H1 rows, so the frozen prerequisite for economics did not pass.

Descriptively, H1 used 32 fewer logical provider calls and cost about 25.8% less than H0, but it cost about 14.2% more than B. These figures do not support a mechanism disposition because the correctness gate was not executable.

## 13. Architecture assessment

No evidence demonstrated a need for a new HELM primitive or new model authority. The selector remained stateless and used existing governed structure. The failure is an **enforcement/contract and measurement-instrument gap**: the execution contract lacked a total, predeclared final-outcome binding for two authorized modes.

## 14. Preserved negative evidence

- T0 remains `MATERIAL DISADVANTAGE — NEGATIVE RESULT` and unchanged.
- R2 remained non-executable and was superseded, not patched.
- R3's initial transport failure remains preserved.
- R3 retained all quota and schema failures.
- Provider zero-thinking-budget behavior did not match the frozen expectation.
- Mode A/E final outcomes were not scoreable.
- The authority schedule was not invoked during runtime.
- Arm B's evidence-identity surface was structurally incomplete.
- Deterministic compute timing was not captured by the execution runner, so the requested total-system computation comparison is incomplete.

## 15. Production status

Production was unchanged. No traffic moved, production Probe remained disabled, no production profile changed, no external effect occurred, and canonical HELM and the Domain Pack were not amended.

## 16. Reproduction

1. Check out commit `7a7b396d52d64e4506e890615ab0e5744a45f5cd` for the sealed public package and runner.
2. Verify the final manifest hash `e0afb2f05d072de3dc89e4b0b5e8139f30839bfb82595cf131b7e9ce8803eee0`.
3. Run `python benchmark/run_adaptive_resolver_aperture_t1.py --workers 12` with the frozen Vertex configuration.
4. Verify the clean raw ledger hash `533bfa3d61f1f778c04ab33f9f458ecda236e82aa66ad362d1593a5317a91834` for this execution.
5. Run `python benchmark/build_t1_scoring_extract.py` and verify the scoring-extract manifest hash `0e32ae46b37840ae11d811fa4d0edec6de867ccc788088b53b0a3e073a16e541`.
6. Do not invent a Mode A/E outcome mapping or retrospectively apply the authority schedule.

## 17. Independent adjudication

NND's frozen disposition is:

**ADAPTIVE APERTURE INCONCLUSIVE — OPERATING BOUNDARY**

NND explicitly did not classify the mechanism as falsified because the deterministic selection contract was honored on the rows inspected and the observed failure was in the measurement instrument. The positive claim ceiling remains candidate mechanism, with nothing established for or against Adaptive Resolver Aperture by this run.

