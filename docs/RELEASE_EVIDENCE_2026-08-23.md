# Release Candidate Evidence — 2026-08-23

## Locked candidate

- Source commit: `dc0c3feb8f706584d901c09ef2a69f331d9feb60`
- Cloud Run revision: `military-slices-00006-yes`
- Traffic: `0%`
- Tagged URL: <https://release-candidate---military-slices-ztvqlzospa-uw.a.run.app/>
- Container image: `sha256:90dd6996a702b98d1b747e36ff9243bc2dc29afa43003b09796302579c31855f`
- Immediate rollback candidates: `military-slices-00005-goq` and `military-slices-00004-sih`
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
- Hosted idempotency proof: identical replay returned version 1 with no second agent run.
- Hosted persistence: confirmed state, rejection, and refinement survived reload.
- Hosted isolation: two independent signed sessions produced distinct profile IDs; the untouched session remained version 0 with zero facts.
- Firestore: `military_slices_profiles`; artifact-only calls created zero documents or version changes.
- Hosted artifact matrix: TXT, DOCX, PDF, scanned PDF, PNG, JPG/JPEG, and imperfect provider MIME passed. Corrupt PDF, oversized TXT, executable, and spoofed JPG failed clearly.
- Raw artifact bytes were not written to Firestore or application logs. Extracted text remained editable and ungoverned until confirmation.
- Mobile 375×812: no horizontal overflow; primary visible controls measured 48–72 px high.
- Ambiguous input remained reviewable and disappeared on reload before confirmation.
- Candidate logs contained no unexpected application errors after the final deployment.

## Defects found and closed

1. Cloud Run environment names did not initially match the app contract; corrected and independently verified.
2. Intermediate ADK tool text contaminated the final structured response; final-event capture fixed.
3. Gemini output contract was not enforced at the provider boundary; native ADK output schema added.
4. Gemini introduced unsupported local-employer context; grounding rules tightened and proposal capabilities/gaps made explicit.
5. Rejecting one role expanded the foreground to five choices; recomputation capped at three.
6. HTTP lost-response retries returned 409 before engine idempotency; replay now returns current state without another write or model call.

## Remaining human gates

1. Physical Android native picker, keyboard, focus, and touch validation.
2. Real second-account/device isolation validation.
3. Founder cold-user/adult-tone convergence.
4. Eligibility, ownership, team roster, and third-party-content attestations.
5. Public repository URL and access decision.
6. Canonical-domain cutover and post-cutover smoke test.
7. Unedited public demo recording of four minutes or less.
8. Final Devpost review and irreversible submission.

Phase acceptance and production release remain open until these genuinely human gates are complete.
