# HELM / Military SLICES 30-Minute $30 Scenario Gauntlet

## Executive result

**FAIL for the frozen benchmark question.**

The threshold was: PASS allows contained, non-systemic failures; PARTIAL allows material but bounded gaps that preserve the core control loop; FAIL applies when a repeatable defect changes the Anchor/materiality result for common equivalent input, or when a required governed semantic cannot be represented. The candidate passed 68/81 frozen scenario receipts (83.95%), but failed this threshold for two reasons:

1. the same career/location facts produced different temporal feedback solely because sentence ordering changed which statement became the Anchor; and
2. the canonical schema does not contain an explicit `ACTIVE`, `PARALYZED`, or `COMPLETE` execution-state field, so scoped paralysis and completion cannot be governed or proven from persisted state.

The verdict does not mean the candidate is broadly nonfunctional. Its deterministic economics, state reuse, authority gates, task ceiling, artifacts, model boundary, conflict gate, isolation, and bounded receipts performed well. It means the frozen candidate does not yet **consistently** demonstrate the complete HELM behavior posed by this benchmark.

## Frozen system and integrity

- Candidate revision: `military-slices-00016-miz`, 0% traffic.
- Candidate source: `b200d5b940b058d1cd6e805c88acd47ed098835b`.
- Production: `military-slices-00001-niw`, 100% traffic throughout.
- Start: `2026-08-25T02:56:40.8559425Z`.
- Scenario scheduling stopped: `2026-08-25T03:13:09.0327853Z`.
- Systemic-defect stop condition ended scheduling after 16m 28.18s.
- Product/runtime changes during benchmark: 0.
- Production traffic changes/mutations, domain changes, and Devpost changes: 0.
- Synthetic profiles only.
- Candidate warning/error log query after execution: empty.

The initial driver hash was `D4AC7BFDAE3D6877BFF81F24D1874F847160ECB76AAF54B4953CAB5B86C13565`. Before any scenario ran, it failed because ReportLab was not installed. The only driver correction replaced that synthetic PDF generator with Pillow; corrected base-driver hash: `F6DD7D8F3E6C667826270DE7F3C14D47F88DE5CD40FF167194619C4301BC5CDD`. Spend and candidate calls before correction were zero.

## Budget and throughput

| Metric | Result |
|---|---:|
| Wall time through scheduling stop | 16m 28.18s |
| Estimated incremental model/tool spend | $0.497516 |
| Rail ending run | Systemic-defect stop condition |
| Unused time rail | 13m 31.82s |
| Unused cost rail | $29.502484 |
| Scenarios attempted / completed | 81 / 81 |
| Driver errors during scenarios | 0 |
| Governed version transitions | 140 |
| Scenarios per minute | 4.918 |
| Scenarios per estimated dollar | 162.809 |
| Average estimated cost/scenario | $0.006142 |
| Estimated cost/governed transition | $0.003554 |

Cost is a conservative benchmark estimate: $2.00/M input tokens, $8.00/M output tokens, and $0.01/tool call. Actual provider billing was not exposed. Fixed Cloud Run/Firestore infrastructure is excluded as ordered; the run produced 140 governed version increments, but exact incremental Firestore billing was unavailable.

## Population coverage

### Service

| Service | Scenarios |
|---|---:|
| Army | 15 |
| Air Force | 14 |
| Navy | 14 |
| Marine Corps | 13 |
| Coast Guard | 13 |
| Space Force | 12 |

### Person

| Person | Scenarios |
|---|---:|
| Separating member | 38 |
| Retiring member | 13 |
| Recently separated veteran / veteran | 12 |
| Military spouse | 10 |
| Dual-military household | 2 |
| Gate-progression receipts without persona label | 6 |

### Transition stage

| Stage | Scenarios |
|---|---:|
| >18 months | 6 |
| 12–18 months | 8 |
| 6–12 months | 27 |
| 90–180 days | 8 |
| <90 days | 5 |
| Terminal period | 2 |
| Recently separated | 2 |
| Post-transition | 7 |
| PCS-driven | 10 |
| Gate-progression receipts without stage label | 6 |

### Major family

| Family | Scenarios |
|---|---:|
| Temporal/revalidation | 23 |
| Career/decision | 17 |
| Family/location | 13 |
| Messy/no-goal/other | 13 |
| Résumé/artifact | 11 |
| Education | 2 |
| Conflict/authority | 2 |

Artifacts included TXT, DOCX, scanned PDF, PNG/screenshot, job-posting text, multiple artifacts, and evidence containing intentionally irrelevant career material.

## Invariant results

| Invariant | Result | Failures | Material note |
|---|---:|---:|---|
| Anchor preservation | 86.42% | 11 | 10 temporal failures shared an Anchor-selection root; one image-first path retained a target without establishing the objective. |
| Path preservation | 87.65% | 10 | No task escaped its computed path, but the wrong Anchor/domain suppressed material Location work in 10 cases. |
| Relevant ≠ Actionable | 98.77% automated; 100% after adjudication | 1 automated | The one automated flag was the no-goal meta-Anchor “choose a direction,” which is permitted because establishing the Anchor is the task. Résumé evidence did not activate unrelated work. |
| Active task bound | 100% | 0 | Maximum active tasks was 3. |
| Authority enforcement | 100% | 0 | Orientation caused zero writes; conflict, career choice, bounded update, and protected decisions stopped for human authority. |
| Feedback | 87.65% | 10 | Canonical target changes persisted, but their material downstream Location consequence was not surfaced. |
| State reuse | 100% of 47 measured reload/replay journeys | 0 | No persistence, replay, duplicate-write, or duplicate-question failure was recorded. |
| Freshness/revalidation | 50% in the controlled order matrix | 10 | All 20 mapped facts became stale; only 10 material impacts surfaced. Employment-first wording passed 6/6; preference-last wording failed 6/6. |
| Conflict semantics | PASS for represented conflict gates | 0 false/missed in tested paths | Stale Location did not create conflict; a validated income/education conflict created a human conflict gate and cleared after the human chose a staged combination. |
| Paralysis semantics | **UNPROVABLE / FAIL contract** | systemic | No canonical execution-state field exists. The candidate cannot persist or expose scoped `PARALYZED` semantics. |
| Model discipline | 100% | 0 | Freshness model calls 0; full receipt rebuilds 0; no model-overuse failure. |
| Stop condition | PARTIAL | 1 material | A generic résumé Anchor containing “target role yet” produced no target-role gate because the phrase was treated as an already-known target. Explicit completion state is also absent. |

Frozen driver failure classes were: `BAD_REVALIDATION` 10, `ANCHOR_DRIFT` 1, `OTHER` 1, and `UNAUTHORIZED_ACTIVATION` 1. The last was adjudicated as permitted no-goal orientation; the `OTHER` scenario was superseded by a valid heavy rejection journey and is not treated as a product rejection failure.

## Economics and context

| Metric | Result |
|---|---:|
| Model calls | 24 |
| Tool calls | 41 |
| Input tokens | 28,730 |
| Output tokens | 3,757 |
| Scenarios with zero model calls | 70/81 (86.42%) |
| Machine-closed gates | 8 |
| Gates evaluated | 137 |
| Scenarios ending at a human gate | 43 |
| Average final receipt size (74 measured) | 5,510.93 bytes |
| Receipt patches | 42 / 6,986 bytes |
| Average receipt patch | 166.33 bytes |
| Full receipt rebuilds | 0 |
| Freshness dependency evaluations | 321 |
| Facts marked stale | 20 |
| Human revalidations | 9 |
| Machine revalidations | 0 |
| Freshness-related model calls | 0 |

The public end-to-end surface did not expose a way to age an authoritative external fact safely, so the external-expiring machine-refresh path was not exercised in this hosted gauntlet. Its local contract tests are outside this frozen scenario result. The compact scenario receipt also omitted the existing context-avoided telemetry, so no new gauntlet-wide avoided-byte claim is made.

An exact machine-closure share of *resolved* gates cannot be computed from these compact receipts because human-resolved gate totals were not exported. The measured proxy is 8 machine closures across 137 evaluated gates; a human gate remained foregrounded at 43 scenario endpoints.

## Latency

| Metric | Seconds |
|---|---:|
| Median scenario | 2.5338 |
| p90 scenario | 13.1245 |
| p95 scenario | 16.6807 |
| Maximum scenario | 26.1000 |
| Median deterministic interaction (118 measured) | 0.4821 |
| p90 deterministic interaction | 0.9943 |
| Median provider-reported model interaction (9 measured) | 13.2647 |
| p90 provider-reported model interaction | 16.9743 |

The slowest complete scenario was `M43`, a résumé artifact journey at 26.10s. The slowest model-backed multi-turn journey was `H02`, heavy rejection resolution, at 21.6069s with three model calls. Multimodal extraction is not consistently labeled as `agent_run` in the compact receipt, so the deterministic/model split should not be interpreted as a provider billing partition.

## Material failures

### BAD_REVALIDATION / ANCHOR_DRIFT — systemic

Ten realistic target-change journeys correctly marked the Location fact stale but produced no Impact Tray. The controlled comparison isolated the cause:

- preference-last: `I will stay local and want predictable hours` became the Anchor, classified as general, and suppressed material Location feedback — 6/6 failed;
- employment-first: `I want civilian work with predictable hours` became the Anchor, classified as employment, and the same target/location change produced and cleared the Impact Tray — 6/6 passed.

This makes temporal correctness depend on sentence order rather than governed meaning.

### Missing execution-state contract — systemic

The canonical schema has facts, gates, conflicts, tasks, impacts, and path target state, but no persisted execution state. A conflict gate can stop foreground progression, yet `ACTIVE`, scoped `PARALYZED`, and `COMPLETE` cannot be captured or proven as governed state.

### Resume stop-condition gap — material, bounded

`My anchor is make my resume submission-ready, but I have not named the target role yet` produced no active target-role gate. The generic phrase `target role` was interpreted as if a specific target were already known.

### Non-product evidence issues

- Pre-run ReportLab import failure: driver-only, corrected before scenario execution.
- Initial no-goal automated flag: adjudicated as permitted meta-Anchor behavior.
- Initial rejection scenario never reached a recommendation: coverage-driver limitation; a later heavy rejection journey passed end to end.
- One multimodal journey used deterministic fallback and preserved the user path rather than returning a 5xx.

## Best scenario

`A13` — bounded Location update plus second-user isolation.

The owner changed career target, received one material Location impact, chose the bounded “Open to relocating” update, persisted only the governed Location fact, cleared the impact, reloaded successfully, made zero freshness model calls, and prevented a second signed session from using the first profile's impact ID. It demonstrated state, authority, minimization, continuity, idempotent scope, and isolation in one journey.

## Worst scenario

The `O*A` / `O*B` sentence-order comparison.

All facts and requested decisions were materially equivalent. Merely placing the employment statement before the location/work-preference statement changed the Anchor/domain classification and determined whether temporal revalidation appeared. That is the largest measured weakness because it directly changes governed downstream behavior based on prose order.

## Top three fixes — not implemented

1. **Make Anchor extraction semantic and priority-safe.** An explicit career target/current objective must outrank a trailing mixed preference; recognize normal `stay local` and work-condition language when determining the bounded domain. Recompute materiality from the governed Anchor, not the first lexical goal/preference.
2. **Restore explicit governed execution state.** Persist and deterministically derive `ACTIVE`, scoped `PARALYZED`, and `COMPLETE`; add fixtures proving stale state cannot paralyze, validated conflict can paralyze only the blocked transition, and unaffected bounded work continues.
3. **Tighten generic résumé-target detection.** Phrases such as `target role yet`, `specific role`, and `not named` must keep the target-role human gate open; only a concrete role or job use should close it.

## Scale signal

The run **supports** the bounded-context and economic parts of the HELM hypothesis:

- 86.42% of scenarios used no model call;
- receipts averaged 5.51 KB and patches 166 bytes;
- 0 full receipt rebuilds and 0 freshness-model calls;
- 47/47 measured replay/reload journeys preserved continuity;
- no task overflow, cross-user write, unrelated résumé activation, or provider 5xx;
- Gemini was concentrated in 11/81 scenarios and heavy career gates.

The run **weakens** the stronger claim that the current candidate consistently preserves intent and trustworthy temporal state. Anchor/materiality behavior was sentence-order-sensitive, and explicit execution-state governance is absent. The measured conclusion is therefore: the economic/control thesis is credible, but the frozen candidate is not yet a complete, reliable HELM implementation across ordinary human phrasing.

## Evidence hashes

### Result packets

```text
CEB6ADE3C6CA20BD1E3C672484B99CF0E802DE4D00AB21164982EF96043C966B  gauntlet-20260825T030235Z.json
04B72667CCF96EBDCCAA57407950CF9DC2477A9805C3F11D04E60DBECA5EA718  gauntlet-heavy-20260825T030424Z.json
7B3ACD74420468F90DD183C142382729D50083BF13579D51B400B303178BD6FA  gauntlet-adaptive-20260825T030646Z.json
49416EA00E900282D985B62DD54FC8D67253BFC2955DEE7E033F8680A04B048D  gauntlet-progression-20260825T030919Z.json
AE1687C615D63C7F9A816151AD41A0CA443D7254E802934F31923616500D6AD1  gauntlet-matrix-20260825T031043Z.json
380E709EC49F310007F3CB0F5F27341F3FB7D15FA131F28D00E1A6CEE48CDD44  gauntlet-anchor-order-20260825T031238Z.json
```

### Frozen drivers

```text
F6DD7D8F3E6C667826270DE7F3C14D47F88DE5CD40FF167194619C4301BC5CDD  run_gauntlet.py
76775260EC3B8FAD89A7F956EE86F12A9FD47ADC1B69461F792D63B8F920BC5C  run_gauntlet_heavy.py
93779A1B993B54E9EB73B2687507F7568E18BFB36CF6272DBD472C40D80EADAC  run_gauntlet_adaptive.py
AE647D17F4C5287DE0D2C3879E7FFDE0DEBE392AE26F34F31A9AB4A24910FAD4  run_gauntlet_progression.py
162EB024501A54ED310270A48F47F8E1E8CF3DA11D11E70F2ED8C6754674C5B2  run_gauntlet_matrix.py
172DAFB4AB3CD47B3D14DDFFD76F82D820475D640DB855CB18EBEC8C9B27FFDB  run_gauntlet_anchor_order.py
```
