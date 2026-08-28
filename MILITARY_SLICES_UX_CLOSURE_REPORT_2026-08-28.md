# MILITARY SLICES UX CLOSURE REPORT

Date: 2026-08-28  
Implementation commit: `c85e3e4`  
Disposition: **UX GATE CLOSED — CANDIDATE READY**

## Journeys actually driven

BHE used the rendered product from a fresh profile rather than relying on API or ledger inspection. The clean journey was run on desktop and repeated at a 390×844 Android viewport. It covered onboarding, a human goal, direction selection, a three-answer decision bundle, an experiment result, refresh/re-entry, and a later direction reversal.

The five-decision lifecycle was:

1. Choose **Veteran-focused AI product builder** as the working direction.
2. Define the veteran problem and the real-world test.
3. Define the first experiment and its success condition.
4. Report what happened in the experiment.
5. Re-enter through the normal update surface with additional evidence and then reverse the working direction.

Back, refresh, correction, cancellation, persistent input, and plan-history paths were exercised during the same drive.

## Exact decisions entered

- Goal: “I need steady civilian income, but I want to build AI tools that help veterans navigate benefits and career decisions.”
- Working direction: “Veteran-focused AI product builder.”
- Problem: “Veterans cannot tell which benefits guidance applies to their service history and current goal.”
- Test: “Give one veteran a source-linked answer and ask them to verify every recommendation against the cited agency page.”
- Experiment: “Build one benefits-answer prototype; success means the veteran can verify the answer and name the next action without help.”
- Outcome: “The veteran completed the task and verified every recommendation. They hesitated when two sources disagreed, so the next version must show effective dates and explain which source controls.”
- Re-entry evidence: “A second veteran trusted the answer only after the source name and date appeared beside it. That confirms source visibility is a required product feature, not an optional detail.”
- Mobile outcome: “The veteran verified the answer but hesitated when two sources disagreed. The next version must show effective dates and which source controls.”
- Reversal: “I changed my mind. I no longer want to build a product; I want a stable cybersecurity analyst role.”

## Defects observed

- Three already-known direction questions were serialized into three screens.
- The dashboard displayed generic status instead of the human’s actual decisions, experiment, and findings.
- Active-fact metrics implied the entire stored record was in the current reasoning surface.
- Plan history omitted meaningful decision progression when the Anchor did not change.
- Normal primary actions and neutral review guidance used warning-like orange/red treatment.
- “Navy, not Air Force” was treated as vague instead of an explicit correction.
- Irrelevant input triggered another question instead of being dismissed without consequence.
- A novel platform goal was initially classified as unrelated.
- A negative/positive reversal sentence could preserve the rejected product clause instead of the new role.
- The direction-learning placeholder survived after the direction was replaced.
- Approved-input receipts could echo an email address from an uploaded document.
- The bundled-question explanation exposed internal Gate/governance vocabulary.

## Defects fixed

- Added a bounded three-answer presentation over the existing three independent path-task Gates.
- Added direct projections for the working direction, exact experiment, prior decisions, learned evidence, and next action.
- Made HELM-focus counts reflect current required evidence and open decisions rather than total stored facts.
- Made history include decision progression as well as Anchor changes.
- Changed normal primary actions to teal; warning colors remain reserved for actual conflicts.
- Added deterministic service-branch correction and replay coverage.
- Added a non-material result path: no save, no invented consequence, and no forced explanation.
- Recognized explicit product/platform goals and routed a new goal through controlled plan-change review.
- Preserved the positive specific role in post-decision reversal while retaining the established generic first-job Anchor contract.
- Reset input context and placeholder after completed or cancelled flows.
- Redacted email addresses from human-facing receipt summaries.
- Replaced internal bundled-question language with ordinary language.

## Before/after behavior

Before, the system made the human traverse backend-shaped steps, displayed generic receipts, and could lose the meaning of the experiment between screens. After, one bounded interaction collects the complete known answer set, each answer still passes through its own existing Gate, and the dashboard immediately shows the resulting decision record. Irrelevant information now exits cleanly; consequential changes enter review; accepted updates show their exact effect.

## Bundled-question behavior

The UI presents the problem, test, and success-condition questions together. One human action submits them. Runtime persistence remains sequential and version-checked: every answer uses its current Gate ID, current expected state version, and a separate idempotency key. The bundle stops on any failed decision; it does not bypass conflict, invalidation, or human authority.

## Persistent-input behavior

“What changed?” remains visible at the top of the fixed desktop dashboard and remains reachable at mobile width. It accepts text or a file without requiring Slice selection. “Fix the plan,” “Earlier plans,” “Try a what-if,” and “View connected areas” remain available as secondary tools. Completed and cancelled flows clear stale input context.

## Re-entry behavior

“Add a test result” preserves the selected direction in the input context. After review and approval, the exact finding appears under **What you learned**, and **What to test next** changes to a strengthen/change/stop decision. Refresh preserved the current target, experiment, decisions, findings, and next action. Reversal cleared the obsolete direction-learning prompt.

## Contradiction behavior

The drive entered: “The service branch is wrong. I served in the Navy, not the Air Force.” The system proposed only `Air Force → Navy`, stated that nothing had changed yet, required approval, and retained the working product direction. The accepted correction created a normal governed reorientation event.

## Cross-Slice behavior

The drive entered: “I need remote work while completing a part-time AI certificate, and I cannot relocate.” Review identified work, education, and location together. After approval, the receipt named those three connected areas and preserved the existing working direction and résumé/story context.

## Irrelevant-input behavior

The drive entered: “My favorite coffee is dark roast.” The result was: **This doesn’t change your plan.** No save action was offered, no follow-up explanation was demanded, and the UI stated that nothing was saved.

## Novel-direction behavior

The drive entered: “I want to build a peer-to-peer disaster logistics platform for Guard families.” With an existing working direction, the input entered plan-change review. The system proposed the exact old-to-new goal change, did not silently map it to a stock occupation, and offered **Keep my current plan** or **Use this update**.

## Decision receipt behavior

Receipts now preserve the approved human text and the actual affected areas. Path-task receipts show the saved answer. Experiment receipts show the exact finding. Reorientation receipts show the actual field-level change. Email addresses are removed from receipt summaries. Generic “moved forward” copy is no longer the only visible evidence of a decision.

## Readability findings

Veteran-facing bundle copy no longer says Gate, governed payload, authority governor, Resolver, Canonical, Latent, or material uncertainty. Questions are direct, explanations are short, and buttons describe the action. The project’s plain-language regressions and full suite pass. Remaining unavoidable proper nouns and program labels are domain terms, not architecture terms.

## Desktop results

- Fixed dashboard keeps input central and the current decision immediately below it.
- Current target, path position, HELM focus, tools, and decision record remain simultaneously accessible.
- The complete five-decision drive passed.
- Contradiction, Cross-Slice, irrelevant, novel-direction, cancellation, history, refresh, and reversal paths passed.
- No visible runtime error or failed browser request appeared during the drives; local server logs showed successful responses for exercised actions.

## Mobile results

The critical journey passed at 390×844:

- persistent input remained usable;
- all three bundled questions were readable and independently editable;
- no horizontal overflow was observed;
- no required control was clipped or hidden;
- the accepted experiment and findings remained readable;
- the current target remained visible after reversal;
- refresh preserved the new target and restored the correct generic input prompt;
- buttons and controls remained practical touch targets.

## Automated validation

- Pytest: **318 passed**; one pre-existing Starlette/httpx deprecation warning.
- Targeted UX, reorientation, path-runtime, privacy, and static-contract regressions: **passed**.
- Strict Mypy: **passed**, 17 source files.
- Ruff (`military_slices`, `tests`): **passed**.
- Bandit (`military_slices`): **passed**.
- Dependency audit: **passed**; no known vulnerabilities. The local project package itself is not published on PyPI and was correctly skipped.
- JavaScript syntax (`node --check static/app.js`): **passed**.
- `git diff --check`: **passed**.
- Browser/runtime inspection: no page error surfaced in the in-app browser; exercised requests completed successfully in the local server log.

## Governance audit

- No canonical HELM primitive was added.
- No new authority type or Domain Pack policy was added.
- The bundle changes presentation only; existing Gate identity, versioning, idempotency, and human authority remain intact.
- Novel goals remain proposals until human acceptance.
- Fog-bank examination remains read-only until explicit acceptance.
- Irrelevant information creates no Canonical consequence.
- A reversal invalidates the old working direction without deleting unrelated facts or history.
- Probe authority, production Probe status, and external effects are unchanged.
- Production was not deployed or mutated; traffic was not moved.

## Remaining defects

- A new zero-traffic Cloud Run revision could not be created from this workstation because the Google Cloud CLI is unavailable. Hosted desktop/mobile validation therefore remains a release-step gate, not a local UX defect.
- The browser-control surface did not expose a downloadable console-message ledger. No browser error surfaced and no failed exercised request appeared in the server log, but this report does not claim an independently exported empty console ledger.
- Physical-device Android validation, native file-picker validation, and second-account isolation remain Human release checks.
- The pre-existing Starlette/httpx deprecation warning remains repository debt.

## Candidate status

**UX GATE CLOSED — CANDIDATE READY**

Implementation candidate: `c85e3e4`.

The local candidate satisfies the human-experience gate. It is ready to be built as a zero-traffic hosted revision and validated on hosted desktop and Android before any traffic decision. Last recorded production evidence remains `military-slices-00001-niw` at 100% traffic; this work did not query or change that external state because the Cloud SDK is unavailable locally.

The Chief Engineer statements are satisfied for the locally rendered candidate:

> I completed the Military SLICES journey as a veteran would use it, not as an engineer would test it.

> At every consequential point I could tell what the system understood, what it needed from me, what my previous decision was, and what would happen next.

> I did not rely on telemetry, logs, database state, or knowledge of HELM to understand the experience.
