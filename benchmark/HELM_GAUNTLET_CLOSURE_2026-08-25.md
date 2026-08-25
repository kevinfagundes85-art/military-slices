# HELM Gauntlet Failure Closure and Revalidation

## Verdict

**PASS**

The three authoritative failures from the 30-minute/$30 gauntlet are closed on a new zero-traffic candidate. The exact frozen failures replayed cleanly before the bounded confirmation run. Production remained unchanged.

## Frozen and final states

| Item | Value |
| --- | --- |
| Frozen failed candidate | `military-slices-00016-miz` |
| Frozen source | `b200d5b940b058d1cd6e805c88acd47ed098835b` |
| Production | `military-slices-00001-niw` - 100% |
| Final candidate | `military-slices-00019-ved` - 0% |
| Final source | `fe29bc8b9b9abe9d972e935967b6a64a4236dd3e` |
| Candidate URL | `https://competition-rc---military-slices-ztvqlzospa-uw.a.run.app` |
| Container digest | `sha256:030e42bd24885cda3ed48e2da1622599d40a9530d3f993aff5e2d6757f6a1eed` |

## Defect closure

### 1. Anchor order sensitivity - CLOSED

**Root cause:** `extract_human_anchor` selected the first oriented goal/preference. The deterministic orientation kind was too coarse to distinguish an objective from a constraint, so equivalent sentence orders could choose different Anchors and suppress path materiality.

**Fix:** the controller now builds semantic candidate clauses, classifies explicit objectives, task requests, milestones, and constraints, then applies deterministic authority precedence. Constraints may modify but cannot replace a higher-priority objective. Equal-authority cross-domain objectives produce one human Anchor gate. Gemini does not select the governed Anchor.

**Additional adversarial corrections:** hosted confirmation exposed two bounded equivalence gaps before finalization: compound conjunction parsing dropped the leading intent, and plural `Our anchor is...` was not recognized. Both received deterministic regressions before final candidate `00019-ved` was built.

**Tests:** 10 exact prior temporal failures, 6 passing employment-first controls, 25 deliberately equivalent packets, ambiguous cross-domain intent, compound work comparison, and shared-household intent.

### 2. Explicit execution state - CLOSED

**Root cause:** canonical state had facts, gates, conflicts, tasks, impacts, and a path target but no persisted execution projection.

**Fix:** canonical state now contains additive `execution` state with:

```json
{
  "state": "ACTIVE | PARALYZED | COMPLETE",
  "blocked_transition": null,
  "blocking_gate_id": null,
  "reason_code": null,
  "derived_from_version": 0,
  "anchor_fingerprint": null,
  "resolving_authority": null,
  "updated_at": "..."
}
```

The deterministic controller derives execution after path/gate recomputation. A current validated material conflict may paralyze only the named next transition. Stale evidence cannot validate paralysis. Human resolution records authority. Human-authoritative Anchor satisfaction produces `COMPLETE`, clears autonomous tasks, and survives reconstitution while the same Anchor remains current.

No datastore, collection, queue, or orchestrator was added. Legacy Firestore documents receive an additive default on read and are deterministically reconstituted without a destructive migration.

### 3. Resume target specificity - CLOSED

**Root cause:** readiness used raw substring tests such as `" role" in anchor`, so generic or negated phrases like `target role yet` looked concrete.

**Fix:** deterministic specificity now classifies `concrete`, `generic`, `negated`, or `absent`. A specific named role or explicit uploaded posting/description closes the gate. Generic, ambiguous, cleared, and negated targets keep or reopen `resume-target-role`. The same check protects direct gate decisions and career-target extraction.

## Exact frozen failure replay

Raw evidence: `benchmark/output/gauntlet-exact-replay-20260825T041014Z.json`

| Scenario class | Previous | Final | Result |
| --- | --- | --- | --- |
| `O1A`-`O6A` preference-last | 0/6 passing | 6/6 passing | CLOSED |
| `O1B`-`O6B` employment-first controls | 6/6 passing | 6/6 passing | PRESERVED |
| `M11`, `M21`, `M41`, `M51` | 0/4 passing | 4/4 passing | CLOSED |
| Generic resume target | Gate missed | Gate open | CLOSED |
| Persisted execution/paralysis contract | Unprovable | `PARALYZED` with named transition/gate | CLOSED |

Exact replay totals: **18 attempted, 18 completed, 18 invariant-clean, zero driver errors, zero model calls, $0 estimated variable spend.**

## Equivalence matrix

The deterministic local matrix tested 25 materially equivalent employment packets with objective-first, objective-last, preference-first, constraint-last, punctuation, conjunction, short/long, milestone, task-request, target, and family-constraint variations.

- semantic Anchor classification: 25/25;
- path classification: 25/25;
- active gate/materiality: 25/25;
- execution state: 25/25;
- sentence-order-caused material divergence: 0/25.

## Execution-state proof

Deterministic fixtures and hosted scenarios prove:

1. `ACTIVE`: civilian-work Anchor with a valid next transition;
2. `ACTIVE -> PARALYZED`: current human evidence establishes simultaneous immediate-income and full-time-education requirements, producing `priority-first-six-months` and a named blocked transition;
3. scoped continuation: additional resume/evidence context is accepted while the career transition remains paralyzed;
4. `PARALYZED -> ACTIVE`: a human priority decision clears the conflict and records `human` as resolving authority;
5. `ACTIVE -> COMPLETE`: human-authoritative evidence confirms a civilian job was accepted and the current goal is complete;
6. reload/reconstitution: `COMPLETE` persists with zero autonomous tasks;
7. stale protection: stale relocation evidence cannot validate `CONFLICTED` or `PARALYZED`.

## Regression safety

- 133 local tests passed.
- Ruff passed.
- strict MyPy passed.
- Bandit passed with zero findings.
- dependency audit found no known vulnerabilities (the local package itself is not on PyPI).
- JavaScript syntax passed.
- architecture PDF text contract and one-page visual render passed.
- maximum active tasks remained at 3.
- Authority Governor behavior remained intact; no model self-authorization occurred.
- replay/idempotency and reload/persistence remained intact.
- temporal freshness detection used zero model calls.
- full receipt rebuilds remained zero.
- explicit second-user isolation scenario `A13` passed.

## Bounded confirmation gauntlet

Final candidate raw evidence:

- `benchmark/output/gauntlet-confirmation-20260825T041040Z.json` - 30 core journeys;
- `benchmark/output/gauntlet-heavy-20260825T041123Z.json` - 4 adversarial/model-boundary journeys;
- `benchmark/output/gauntlet-adaptive-20260825T041204Z.json` - 13 adaptive/re-entry/isolation journeys.

Combined result:

| Metric | Result |
| --- | ---: |
| Attempted / completed | 47 / 47 |
| Invariant-clean | 47 / 47 |
| Driver errors | 0 |
| Services | all 6 |
| People | separating member, retiring member, veteran, spouse/dual-military household |
| Zero-model scenarios | 42 / 47 (89.36%) |
| Model calls / tool calls | 8 / 12 |
| Input / output tokens | 6,952 / 778 |
| Estimated variable cost | $0.140128 |
| Governed transitions | 102 |
| Cost / scenario | $0.002981 |
| Cost / governed transition | $0.001374 |
| Average receipt (34 core/model journeys) | 6,350.30 bytes |
| Receipt patches | 52 / 8,800 bytes |
| Average patch | 169.23 bytes |
| Full rebuilds / freshness model calls | 0 / 0 |
| Median deterministic latency | 0.6360 seconds |
| Median model-backed latency | 15.0989 seconds |
| Combined wall time | 64.748 seconds |

The 15-minute/$5 rail was not approached.

## Efficiency comparison with the frozen failed gauntlet

| Metric | Frozen 81-scenario run | Final confirmation | Direction |
| --- | ---: | ---: | --- |
| Zero-model scenario rate | 86.42% | 89.36% | improved |
| Model calls / scenario | 0.2963 | 0.1702 | improved |
| Average receipt | 5,510.93 B | 6,350.30 B | +839.37 B for execution/provenance telemetry |
| Average receipt patch | 166.33 B | 169.23 B | +2.90 B |
| Full rebuilds | 0 | 0 | preserved |
| Freshness model calls | 0 | 0 | preserved |
| Cost / scenario | $0.006142 | $0.002981 | improved |
| Cost / governed transition | $0.003554 | $0.001374 | improved |
| Median deterministic latency | 0.4821 s | 0.6360 s | +0.1539 s absolute |
| Median model-backed latency | 13.2647 s | 15.0989 s | +1.8342 s |

Receipt growth is the bounded cost of the new execution/provenance contract and remains far below the 200 KB guard. Patch growth is 1.7%. The latency increase is visible and reported, but did not produce a timeout or failed journey on the final revision. Economics, full-rebuild discipline, and freshness-model discipline improved or held.

## Hosted candidate evidence

- Cloud Run readiness: `Ready=True`, `ContainerHealthy=True`.
- Health: HTTP 200; service `military-slices`; model `gemini-3.7-flash`; framework `google-adk`; transition pack `2026-08-24-v2-shadow-tested`.
- Store/config: Firestore, secure cookie, Vertex AI, global location, 18-second resolver budget, existing runtime service account and session secret.
- Warning/error log query after all final runs: empty.
- Hosted application bundle: `/static/app.js?v=3`, SHA-256 `2AD00D5F8B00A3C59CE8CFD5F959C6D9A690990C644BC4F766D21AA1DF555DB5`.
- Hosted stylesheet: `/static/styles.css?v=3`, SHA-256 `9F82E41DF9736248F6299A153327B89AB71851CDF7A6F6C7FE643816695E0EC4`.
- Core schema SHA-256: `1E4B24BA9359AC6C2E9174FA027B0C8CCA21A47A80FA4781BF7E000296E31875`.
- Path runtime SHA-256: `D87A334B68EDFDF5A61D6950DD1255D63EC7F1FABCDE2349E11FCF496309FCBA`.
- Engine SHA-256: `8DAD08F93EF097F8B668A074CD3107CD202FD78EE05B7AB4CD646839D823B610`.
- Architecture SVG SHA-256: `F21BA9439CBB321A2C936062F1A5289708F85B66050E7FD3C2F8DC7E2D8CA19E`.
- Architecture PDF SHA-256: `F468A66E2BF77D0B8F76FA2B228CBC6CCBA6BAA9298AFF02B195F613849737BC`.

## Production and human gates

Production remains `military-slices-00001-niw` at 100%. Candidate `military-slices-00019-ved` remains at 0%. No canonical-domain mapping, Devpost submission, production profile mutation, or traffic cutover was performed.

Genuine remaining human gates:

1. founder/cold-user acceptance of the candidate interaction on a physical device;
2. physical Android native-picker validation for ordinary artifacts;
3. production cutover approval after those human checks.

This report does not authorize or claim production release.
