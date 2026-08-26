# HELM Governed Implementation Evidence — 2026-08-25

## Release disposition

- Baseline commit: `0d8e6e83a6ee4a271f42a29004ac57368295c657`
- Contract implementation commit: `cc31870cc3cab16c5f5efcc604956056f95ee487`
- Ambiguity-boundary correction commit: `8608bed`
- Production revision: `military-slices-00001-niw` at 100% traffic
- Zero-traffic candidate: `military-slices-00029-taj` at 0% traffic
- Candidate URL: `https://helm-governance-rc---military-slices-ztvqlzospa-uw.a.run.app/`
- Exact frontend bundle: `app.js?v=6`
- Military Transition Domain Pack: `2026-08-24-v2-shadow-tested`
- Domain Pack SHA-256: `026a1508a3a2e6eb16907b2e8fc29c4f333af5c5ab908e6029903b8cbcbf9f4c`
- Domain Pack status: `LEGACY_VALID` (not activated; HG-02/HG-03 remain open)
- External effects: disabled
- Autonomous HELM Probe: disabled

No production traffic, profile, database schema, release tag, or policy authority was changed by this release Gate.

## Ordered execution record

| Item | Result | Evidence and enforced invariant |
|---|---|---|
| E00 | COMPLETE | Reproduced baseline at `0d8e6e8`; 150 existing tests passed; production and candidate identities recorded before mutation. |
| E01 | COMPLETE WITH HUMAN GATES OPEN | Added positive, ambiguity, contradiction, cross-user, replay, and concurrency fixtures. HG-01 through HG-05 remain explicit; fixtures do not activate policy. |
| E02 | COMPLETE | Added immutable pack reference, actor/event provenance, lineage, migration status, and explicit state categories. Legacy records load without invented history. |
| E03 | COMPLETE | Governed writes require trusted session actor provenance. Cross-user, absent/untrusted actor, and replay paths fail closed. Credentials and raw artifact bytes are excluded. |
| E04 | COMPLETE WITH ACTIVATION GATE OPEN | Exact pack payload is hash-pinned and compatibility checked. The installed pack remains `LEGACY_VALID`; no approver, thresholds, or policy values were invented. |
| E05 | COMPLETE | Versioned bounded Slice manifests and allowlist projections prevent broad profile serialization and direct Slice-to-Slice authority transfer. |
| E06 | COMPLETE | Deterministic Gate identity, parent scope and authority containment, construction provenance, source-version binding, required evidence, and legal transition validation are enforced. |
| E07 | COMPLETE | Resolver output is a nomination only. The Authority Governor independently checks scope, authority, evidence, actor, and version; a model cannot close a human Gate. |
| E08 | COMPLETE | State, mutation event, lineage, derived-index hash, idempotency, and version history commit in one transaction. Stale, missing, tampered, and replay paths fail closed or return the existing result. |
| E09 | COMPLETE FOR SYNTHETIC VALIDATION | Career/resume readiness reaches one bounded human Gate. Unknown input asks one question and writes nothing. External action remains impossible. |
| E10 | COMPLETE FOR SYNTHETIC VALIDATION | Actor and military-state subject remain separate; spouse/PCS and independent Education/Relocation entry fixtures pass without direct agent orchestration. |
| E11 | COMPLETE | Restart and legacy reconstitution preserve exact pack pinning and reduce authority when lineage is unavailable. No historical provenance is manufactured. |
| E12 | COMPLETE | Route/configuration guards keep external effects and autonomous Probe unreachable. Environment flags cannot enable them. |
| E13 | AUTOMATED PORTION COMPLETE; HG-06 OPEN | Full suite and hosted candidate checks are green. Physical Android, native picker, cold-user, founder convergence, real second-account, adult-tone, and policy acceptance remain human-only. |

## Automated validation

- Pytest: 176 passed.
- Targeted API/static/fixture regressions: 39 passed.
- Ruff: passed.
- Mypy strict: passed across 14 source files.
- Bandit: passed.
- Dependency audit: no known vulnerabilities in resolved third-party packages; local project package is not a public-index dependency and was skipped.
- JavaScript syntax: passed.
- Git whitespace validation: passed.
- Hosted health: `ok`; Gemini `3.7-flash`; Google ADK; exact pack hash; `LEGACY_VALID`; external effects and autonomous Probe disabled.
- Hosted logs: zero warning/error entries for `military-slices-00029-taj` after health and browser validation.
- Hosted bundle: exact `app.js?v=6` marker verified.
- Cloud Run traffic: production `00001-niw` remains 100%; candidate `00029-taj` remains 0%.

## Hosted transaction and isolation evidence

A synthetic, isolated hosted profile proved initial version 0, one confirmed mutation at version 1, lost-response replay returning version 1, reload continuity at version 1, one mutation event, one lineage record, exact pack pinning, and no duplicate event/version. A separate synthetic user remained at version 0 with zero inherited facts. No protected production profile was used.

## Cold-browser falsification

The first hosted pass discovered an enforcement defect: explicitly insufficient orientation displayed a save-oriented action. It was classified as a contract/enforcement implementation gap, not a conceptual architecture gap.

The correction now enforces both layers:

1. the frontend presents one clarification question, preserves the reviewed words, and exposes only `Check this clarification`;
2. submitting unchanged ambiguous input produces inline guidance;
3. the backend independently rejects confirmation of insufficient orientation with HTTP 400;
4. the rejected request creates no version or mutation event;
5. adding a decision-relevant clarification re-runs orientation and returns to review, requiring a separate explicit human save action.

Hosted read-back against `00029-taj` passed. Browser warning/error log: empty.

## Mobile and accessibility approximation

Hosted layout measurements at 320px, 375px, and 414px showed no horizontal overflow. The minimum visible interactive target was 44px at every width. The active clarification heading receives focus, the clarification textbox is programmatically labelled, and failure guidance is an inline alert beneath the active decision surface. Physical Android rendering, native file picker behavior, assistive-technology use, and human comprehension remain HG-06.

## HELM invariants exercised

- Capability does not imply authority.
- Resolver proposals cannot authorize or persist.
- Child Gates cannot expand parent scope or authority.
- Human decisions are trusted only through authenticated actor provenance.
- Authorization is bound to the evaluated canonical version.
- Canonical mutation is atomic, replay-safe, provenance-bearing, lineage-bearing, and reconstructable.
- Historical, Hypothetical, and Latent state never silently become Canonical.
- Required missing, stale, conflicting, or tampered lineage fails closed.
- Domain semantics remain pinned to an exact pack version and hash.
- Ambiguity is a valid outcome and causes one minimum clarification with zero writes.
- Slice context is allowlisted and does not become broad profile or direct agent-to-agent orchestration.
- External effects and autonomous Probe behavior remain unreachable.

## Remaining authority and human Gates

- HG-01: Client acceptance of the exact validation journey and target event.
- HG-02: Authenticated owner/approver for the exact Domain Pack version and hash.
- HG-03: Client-provided eligibility, evidence, threshold, and consequence policy values.
- HG-04: Client retention and deletion periods.
- HG-05: Client decision on whether any external effect is in scope; default remains none.
- HG-06: Physical Android, native picker, cold-user comprehension, adult tone, persistence, founder convergence, real second-account isolation, and final traffic-promotion approval.

## Verdict

The bounded automated implementation and zero-traffic release Gate pass. No demonstrated counterexample requires a new HELM primitive or architecture amendment. Military-domain activation and human acceptance do not pass by inference: the candidate must remain at zero traffic until the applicable human/client Gates are explicitly cleared.
