# Release Candidate Evidence — 2026-08-23

## Locked candidate

- Deployed source commit: `c85ee82`
- Cloud Run revision: `military-slices-00008-mov`
- Traffic: `0%`
- Tagged URL: <https://competition-rc---military-slices-ztvqlzospa-uw.a.run.app/>
- Container image: `sha256:16dabfe9b1a9e30c5a97654364d7febe886d606c58b03db7f2f43be91c7752c0`
- Immediate rollback candidates: `military-slices-00007-qob` and `military-slices-00006-yes`
- Custom domain: purchased, intentionally unmapped pending human release approval

## Exact hosted bundle

| File | SHA-256 | Hosted match |
|---|---|---:|
| `static/app.js` | `0EC5B4FA75449BD3D8ECD42CB67FA67EACDB1C506778091C394458E7F91E7E24` | YES |
| `static/styles.css` | `040786480BFAD01AE60D8906737628C286F094A77090C46565E33704555CCB40` | YES |
| `static/index.html` | `93F63ABC473C13605B5B733CCDED4CD5C4E3DB27221A6E495ABD1F5E68E26133` | YES |

## Automated and hosted results

- 38 tests passed.
- Ruff, MyPy, Bandit, JavaScript syntax, diff validation, and dependency audit passed.
- Dependency audit: no known third-party vulnerabilities; the local package itself is not published to PyPI.
- Hosted ADK proof: `google-adk/gemini-3.7-flash`, Vertex AI backend, two model turns, four bounded tool calls, version 1 Firestore write.
- Aggregate synthetic-run telemetry at evidence lock: 14 recorded model calls, 23 tool calls, 10,344 input tokens, and 1,943 output tokens across eight test profiles.
- Final candidate proof: 254 resolver-context bytes, 2,384 full-state bytes avoided, 90.37% context reduction, 11,996 ms agent latency, one machine-closed gate, and `career-direction` as the next human gate.
- Hosted idempotency proof: identical replay returned version 1 with no second agent run.
- Hosted persistence: confirmed state, rejection, and refinement survived reload.
- Hosted isolation: two independent signed sessions produced distinct profile IDs; the untouched session remained version 0 with zero facts.
- Firestore: `military_slices_profiles`; artifact-only calls created zero documents or version changes.
- Hosted artifact matrix: TXT, DOCX, PDF, scanned PDF, PNG, JPG/JPEG, and imperfect provider MIME passed. Corrupt PDF, oversized TXT, executable, and spoofed JPG failed clearly.
- Raw artifact bytes were not written to Firestore or application logs. Extracted text remained editable and ungoverned until confirmation.
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
`output/pdf/military-slices-architecture.pdf`. Additional information cannot be
completed until the required public repository URL exists.

1. Physical Android native picker, keyboard, focus, and touch validation.
2. Real second-account/device isolation validation.
3. Founder cold-user/adult-tone convergence.
4. Eligibility, ownership, team roster, and third-party-content attestations.
5. GitHub account creation, terms acceptance, username selection, and public repository URL.
6. Canonical-domain cutover and post-cutover smoke test.
7. Unedited public demo recording of four minutes or less.
8. Final Devpost review and irreversible submission.

Phase acceptance and production release remain open until these genuinely human gates are complete.
