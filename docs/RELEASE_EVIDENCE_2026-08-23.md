# Release Candidate Evidence — 2026-08-23

## Installed transition-pack candidate

- Deployed source commit: `19a26d4`
- Cloud Run revision: `military-slices-00012-cof`
- Traffic: `0%`
- Tagged URL: <https://competition-rc---military-slices-ztvqlzospa-uw.a.run.app/>
- Container image: `sha256:419b8ea7c4326c8e1a202bc4f379d9eb9d74c34501fd7da4966f5424cbd17214`
- Protected service traffic: `military-slices-00001-niw` at `100%`
- Installed path pack: `2026-08-24-v2-shadow-tested`

### Hosted transition-path proof

- Hosted `/api/state`, DOCX extraction, three governed writes, and reload all returned 200.
- Version progression was exactly `0 → 1 → 2 → 3 → 3` after reload.
- The artifact contributed evidence but left `human_anchor` empty, surfaced `transition-human-anchor`, produced zero career hypotheses, and made zero model calls.
- Choosing résumé work surfaced only `resume-target-role`. Declaring `Senior program manager` produced three bounded résumé tasks, zero career hypotheses, and zero model calls.
- Reload preserved the declared target and transition-pack version.
- Hosted `app.js` and `styles.css` hashes matched local tested files exactly; the removed four-area dashboard did not reappear.
- Candidate readiness is `True`; its post-validation warning/error query returned zero entries.
- A local wheel inspection proved both executable JSON files are included in the package.

### Zero-traffic failure caught and superseded

`military-slices-00011-qev` passed process health but failed its first Firestore state read. `google-cloud-firestore 2.29.0` and `google-api-core 2.35.0` had been published together earlier on 24 August and routed `(default)` as `%28default%29`; Firestore rejected it. The new candidate pins the immediately previous hosted-known-good versions (`2.28.1` and `2.34.0`). The failed revision received zero production traffic.

## Prior corrected artifact candidate

- Deployed source commit: `11c7a4d`
- Cloud Run revision: `military-slices-00010-low`
- Traffic: `0%`
- Tagged URL: <https://competition-rc---military-slices-ztvqlzospa-uw.a.run.app/>
- Container image: `sha256:58ed946eaa261cec8673ad9b723aab732525be7a2a1acc01137ad94159bd47ee`
- Protected service traffic: `military-slices-00001-niw` at `100%`
- Immediate candidate rollback evidence: `military-slices-00008-mov` and `military-slices-00009-nap`

### Artifact gate correction

- A deliberate file selection now authorizes one bounded plan update; the Career path does not ask the human to approve the same résumé again.
- Resolver work is capped at three model calls and 18 seconds, after which deterministic hypotheses preserve the decision path instead of leaving a spinner or returning a `504`.
- A résumé-sized hosted DOCX completed in 13.45 seconds using `google-adk/gemini-3.7-flash`, advanced state from version 0 to 1, produced three hypotheses, and surfaced the next human gate.
- Identical replay returned version 1 without a second write or model run.
- Artifact-derived governed facts are priority-ranked and capped at 24; a 55-statement stress fixture did not retain its omitted tail.
- Raw bytes and full extracted documents remain ephemeral. File cancel sends no request and therefore creates no write.
- Hosted `app.js`, `styles.css`, and `index.html` hashes match the locally tested files exactly.
- Candidate health returned 200; environment, session secret binding, runtime service account, Gemini model, and Google ADK identity match the intended configuration.
- Candidate warning/error log query returned zero entries after the hosted test.

## Superseded candidate

- Deployed source commit: `c85ee82`
- Cloud Run revision: `military-slices-00008-mov`
- Traffic: `0%`
- Tagged URL: <https://competition-rc---military-slices-ztvqlzospa-uw.a.run.app/>
- Container image: `sha256:16dabfe9b1a9e30c5a97654364d7febe886d606c58b03db7f2f43be91c7752c0`
- Immediate rollback candidates: `military-slices-00007-qob` and `military-slices-00006-yes`
- Custom domain: purchased, intentionally unmapped pending human release approval

This candidate failed the physical artifact gate: its upload request reached the
resolver but the unbounded ADK tool loop returned a Cloud Run `504` after about
120 seconds. It also treated deliberate file selection as extraction-only and
required a redundant second authorization. It remains at zero traffic and is
retained only as rollback evidence.

## Exact hosted bundle

| File | SHA-256 | Hosted match |
|---|---|---:|
| `static/app.js` | `E6138E187388020C503432F757D2D7D44EB9DC649125D2C2A07EC9FF306BE4C7` | YES |
| `static/styles.css` | `0E10E882C16F1639601AF27383DE4A83E58210FB50836CBB0BF33723D532B0AB` | YES |
| `static/index.html` | `D64D9CC72C2E5C8608D0514607C18A845BB3AF1A80259FF69521E949BB198F5E` | YES |

## Automated and hosted results

- 57 tests passed.
- Ruff, MyPy, Bandit, JavaScript syntax, diff validation, and dependency audit passed.
- Dependency audit: no known third-party vulnerabilities; the local package itself is not published to PyPI.
- Hosted ADK proof: `google-adk/gemini-3.7-flash`, Vertex AI backend, two model turns, four bounded tool calls, version 1 Firestore write.
- Aggregate synthetic-run telemetry at evidence lock: 14 recorded model calls, 23 tool calls, 10,344 input tokens, and 1,943 output tokens across eight test profiles.
- Final candidate proof: 254 resolver-context bytes, 2,384 full-state bytes avoided, 90.37% context reduction, 11,996 ms agent latency, one machine-closed gate, and `career-direction` as the next human gate.
- Hosted idempotency proof: identical replay returned version 1 with no second agent run.
- Hosted persistence: confirmed state, rejection, and refinement survived reload.
- Hosted isolation: two independent signed sessions produced distinct profile IDs; the untouched session remained version 0 with zero facts.
- Firestore: `military_slices_profiles`; on this superseded candidate, artifact-only calls created zero documents or version changes.
- Hosted artifact matrix: TXT, DOCX, PDF, scanned PDF, PNG, JPG/JPEG, and imperfect provider MIME passed. Corrupt PDF, oversized TXT, executable, and spoofed JPG failed clearly.
- Raw artifact bytes were not written to Firestore or application logs. This superseded flow kept extracted text ungoverned until a redundant confirmation; the corrected contract treats deliberate file selection as authority for one bounded update while keeping raw bytes and full extracted text ephemeral.
- Mobile 375×812: no horizontal overflow; primary visible controls measured 48–72 px high.
- Ambiguous input remained reviewable and disappeared on reload before confirmation.
- `/api/health` returned 200 with the intended model/framework identity and security headers.
- Repeated hammer testing produced an expected Vertex `429 RESOURCE_EXHAUSTED`; the deterministic fallback returned 200 and preserved the user decision path. No user-facing 5xx occurred.

## Defects found and closed

1. Cloud Run environment names did not initially match the app contract; corrected and independently verified.
2. Intermediate ADK tool text contaminated the final structured response; final-event capture fixed.
3. Gemini output contract was not enforced at the provider boundary; native ADK output schema added.
4. Gemini introduced unsupported local-employer context; grounding rules tightened and proposal capabilities/gaps made explicit.
5. Rejecting one role expanded the foreground to five choices; recomputation capped at three.
6. HTTP lost-response retries returned 409 before engine idempotency; replay now returns current state without another write or model call.
7. Cloud Run's tagged front end intercepted `/healthz`; a routable `/api/health` alias was added while retaining the container endpoint.

## Remaining human gates

The Devpost draft exists as `1150977-military-slices`; its project name, pitch,
story, candidate URL, category, Google stack, and testing instructions are
staged. The architecture PDF is frozen at
`output/pdf/military-slices-architecture.pdf`. The public repository exists;
final attestations and irreversible submission remain intentionally open.

1. Physical Android native picker, keyboard, focus, and touch validation.
2. Real second-account/device isolation validation.
3. Founder cold-user/adult-tone convergence.
4. Eligibility, ownership, team roster, and third-party-content attestations.
5. Public repository exists at <https://github.com/kevinfagundes85-art/military-slices>; final public-content review remains open.
6. Canonical-domain cutover and post-cutover smoke test.
7. Unedited public demo recording of four minutes or less.
8. Final Devpost review and irreversible submission.

Phase acceptance and production release remain open until these genuinely human gates are complete.
