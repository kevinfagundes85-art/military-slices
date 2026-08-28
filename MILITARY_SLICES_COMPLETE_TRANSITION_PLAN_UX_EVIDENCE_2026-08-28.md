# Military SLICES Complete Transition Plan UX Evidence

Date: 2026-08-28  
Disposition: **COMPLETE PLAN GATE CLOSED — MILITARY SLICES DELIVERS A USABLE TRANSITION PLAN**

## Synthetic veteran

The rendered-product drive used a synthetic 23-year-old active-duty Navy service member leaving in May 2027. The veteran had logistics and small-team leadership experience, an uncertain civilian direction, a spouse entering nursing school in Tacoma, a preference for steady nearby work with some flexibility, interest in a short certificate but not a four-year degree, and an idea for an application that helps veterans compare transition programs.

No personal employment or intelligence history belonging to the product owner was used.

## Complete rendered journey

The drive was completed through the actual browser UI on a fresh local application instance, not by substituting API calls for user interaction.

1. Entered the uncertain transition objective and background in ordinary language.
2. Reviewed and approved what Military SLICES heard.
3. Compared three proposed directions.
4. Selected Logistics Analyst as the first working direction.
5. Answered all three known test-planning questions together.
6. Left with the action to build a public-information program comparison and ask a recently separated veteran to use it unaided.
7. Reloaded the product. Re-entry said, “Welcome back,” named the planned test, and asked what happened.
8. Reported that the veteran understood the dashboard only after a conversation and that direct support fit better than analysis.
9. Used that result to reverse the prior direction.
10. Military SLICES reopened direction selection without erasing prior history and proposed veteran-transition roles.
11. Selected Veteran transition program coordinator.
12. Defined the fit question, the evidence to obtain, and a new real-world coordinator interview in one bundled interaction.
13. Added a Cross-Slice Tacoma, work-format, education, and June 15, 2027 target update.
14. Entered the irrelevant statement “My favorite coffee mug is blue.” The UI responded “This doesn’t change your plan,” stated that nothing was saved, and did not pollute the plan.
15. Opened the accumulated transition plan.
16. Used Export my plan from Android width and captured the rendered plan as the take-away artifact.

## Final current plan

- Current direction: Veteran transition program coordinator, marked exploratory.
- Why: helping veterans navigate confusing programs fit the veteran’s observed preference for explaining information one-to-one and organizing follow-up.
- Alternatives retained: Veteran services navigator and Transition program operations coordinator.
- What the veteran brings: planning work, working with people, and problem solving, with O*NET and BLS source references shown as lightweight provenance.
- Completed experiment: the Logistics Analyst dashboard test and the reported conversational finding.
- Active experiment: interview a local coordinator next Tuesday and revise the one-page guide from the feedback.
- Next action: run that interview/test and return with what happened.
- Constraints and priorities: Tacoma-area stability, on-site or hybrid work within an hour, and a short-certificate decision.
- Timeline: separation target month May 2027 and certificate-choice target June 15, 2027.
- Unresolved: exact job-title fit and a matching real job post.
- Decision history: prior Logistics Analyst direction is retained as earlier; the current veteran-transition direction and its bounded decisions are retained as current.

## End-state export test

The exported artifact was read without relying on telemetry or raw Canonical state. A spouse, mentor, counselor, or future self can identify the current direction, why it changed, strengths, constraints, completed experiment and finding, present test, unresolved questions, next action, and dates.

Artifact: `benchmark/output/MILITARY_SLICES_COMPLETE_TRANSITION_PLAN_EXPORT_2026-08-28.html`  
SHA-256: `84d9edfa53de864b1fecc72259084fd61cb90447627a04d9cebecc0757c95681`

The artifact contains no Canonical serialization, hidden prompt, chain-of-thought, Resolver/Probe internals, authority metadata, secrets, or telemetry.

## Desktop and mobile result

Desktop: the current foreground action remains primary; My transition plan opens as a secondary review surface with eleven plain-language sections and export/print controls.

Android-width review: tested at 390 × 844. The plan dialog measured 336.7 CSS pixels wide within a 390-pixel viewport, had no horizontal document overflow, retained the current test, and kept Export my plan visible and operable. The plan stayed below the foreground until opened.

## Confusion and defect ledger

| Defect found during human drive | Fix |
|---|---|
| A saved real-world action could still produce “Caught up.” | Active accepted-direction tests now produce “In the field,” the specific test, and a return instruction. |
| Re-entry repeated generic onboarding. | Re-entry now names the remembered experiment and asks what happened. |
| Direction reversal inherited the old resolved direction Gate and could strand the user. | A changed human objective invalidates the old direction resolution while preserving decision history, then deterministically reopens selection. |
| A new role stated as “becoming a … coordinator” was not classified as employment. | Deterministic role-goal recognition now covers becoming/coordinator and related civilian-role terms. |
| Old direction answers appeared in the new direction. | UI and plan projection now scope path decisions to the latest accepted direction. |
| The plan showed a generic experiment instead of the veteran’s selected action. | The current-cycle terminal path answer is projected as the active experiment and next action. |
| A prior experiment finding was lost after reversal. | Completed experiments are projected across all direction cycles, including superseded directions. |
| A learning statement was misclassified as a strength. | Direction-learning records are excluded from historical-achievement projection. |
| Raw starting-vector and direction values appeared in decision history. | Human-readable decision translation removes enum/state-machine language. |
| Month-derived precision appeared as a known exact date. | Exact separation date is shown only when explicitly decided; otherwise the veteran-entered month remains a target month. |
| A date-only value displayed one day early in Pacific time. | Calendar dates are parsed at local noon before display; June 15 remains June 15. |
| Irrelevant context could clutter a durable plan. | The reviewed irrelevant statement was explicitly rejected and not saved. |

## Implementation

- Added a read-only `TransitionPlan` projection over existing governed state.
- Added `GET /api/plan` and a downloadable, no-store `GET /api/plan/export` HTML artifact.
- Added My transition plan UI, printable/exportable layout, mobile behavior, and human-readable provenance.
- Added continuity and direction-cycle scoping in the foreground.
- Added deterministic direction-reversal reopening; no new canonical primitive or authority was introduced.
- Added plan/export, direction-reversal, resolver, static contract, and governance regression coverage.

## Automated validation

- Complete Pytest suite: passed.
- Targeted plan/UX/governance suite: passed.
- Changed-file Ruff: passed.
- Strict Mypy over 18 source files: passed.
- Bandit: passed.
- Dependency audit: no known vulnerabilities; the local `military-slices` package itself is not published on PyPI and was skipped as expected.
- JavaScript syntax: passed.
- Browser validation: full rendered lifecycle, re-entry, reversal, irrelevant update, plan review, export activation, 11-section projection, and Android-width layout passed.
- Repository-wide Ruff remains blocked by pre-existing benchmark-script debt and unreadable audit-cache directories; none of those files were changed for this product gate.

## Governance audit

- The plan is projection only and does not mutate Canonical state.
- All material input still requires the existing human review/approval boundary.
- The irrelevant update was not persisted.
- Prior decisions and experiments remain visible after reversal.
- No raw hidden state or model reasoning is exported.
- No canonical HELM primitive, Gate type, authority, Domain Pack policy, or production profile was added or changed.

## Remaining limitations

- “What changed my plan” uses preserved feedback summaries; some long source statements are intentionally abbreviated in that history view. The substantive decision and experiment records remain complete in their dedicated sections.
- Dates are shown only when supported by governed state or deterministically parsed from a veteran-approved statement; the product does not invent schedules.
- The current export is clean HTML with browser print/save-to-PDF support rather than a server-generated PDF.

## Screenshots and visual evidence

The rendered browser drive visually verified the foreground working-direction record, re-entry brief, evidence-driven reversal, new direction carousel, complete plan dialog, and 390 × 844 mobile plan. Earlier reference captures used during the redesign remain in the project owner’s HELM screenshot folder; the final take-away evidence is the hash-bound HTML export above.

## Candidate commit

`c3f5f2e` — `feat: deliver complete transition plan UX`
