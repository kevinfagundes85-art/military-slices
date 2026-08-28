# Military SLICES Human Attention UX Closure Evidence

Date: 2026-08-28  
Implementation commits: `286bcab70432392791ae6898dc3d1733962a5c40`, `35cd08b1af2a813c9cfeaf078a65634012a7e839`  
Candidate revision: `military-slices-00052-sag`

## Disposition

**HUMAN ATTENTION GATE CLOSED — RELEASE CANDIDATE READY**

I personally drove the final rendered implementation from a fresh profile through orientation, candidate selection, bundled decisions, a working direction, caught-up state, interruptions, reversal, irrelevant input, a Cross-Slice update, refresh survival, and an Android-width check. The final implementation consistently presents one foreground objective and one primary action while keeping context and reality-interrupt input available but subordinate.

## Prior failure and systemic diagnosis

The prior candidate exposed too many simultaneously active workflows. The persistent composer, current Gate, non-blocking Impact, direction carousel, command post, and plan controls competed for attention. The dashboard technically represented governed state but made the veteran decide which subsystem to operate. The result was a control room with multiple radios speaking at once.

The before-state observed in the rendered product included:

- a large composer occupying the top of the workspace even when a specific Gate was active;
- a non-blocking related Impact rendered with visual authority comparable to the current Gate;
- `DIRECTION 1 OF 3`, which looked like a required sequence instead of alternatives;
- dense candidate cards with clipped content and nested scrolling;
- a plan route that expanded inside a fixed rail and overflowed;
- several always-visible plan-tool buttons competing with the primary action;
- internal vocabulary such as `HELM FOCUS` and an operations-center-style input label;
- repeated generic next-action questions that obscured which plan obstacle was actually active.

## Human-attention hierarchy changes

The workspace now follows a fixed hierarchy:

1. **NOW** — the current governed question, required answers, and one primary action dominate the left workspace.
2. **NEXT** — the command post provides orientation only: do this next, why now, and what it affects.
3. **RELATED / WATCHING** — non-blocking Impacts render as a quiet collapsed `Related check for later` surface.
4. **PLAN** — the full route is available through `Open your full plan checklist` in a centered dialog; it no longer covers the active work or expands inside a constrained rail.

The current Gate cannot be replaced by the checklist, related information, or an input composer. Programmatic focus follows the current task without leaving a visible focus artifact in normal use.

## Composer changes

- `COMMAND YOUR PLAN` was removed.
- The persistent entry point is now the header action `Something changed?`.
- Opening it produces a centered desktop modal and a mobile bottom sheet.
- Copy says `Tell Military SLICES what's different.` and uses ordinary examples.
- Closing or canceling returns the veteran to the active plan instead of leaving a second workflow open.
- A submitted change still requires review before governed state changes.

## Direction-card changes

- Candidate framing is `3 directions to consider` and explicitly says `These are alternatives, not steps.`
- The current candidate has one primary action: `Explore this direction`.
- Initial card content is limited to a short description, up to two fit signals, and one item to check.
- Fixed card height and nested card scrolling were removed.
- Detailed test information remains available on demand.

## Bundled-question behavior

Once a direction is explored, all already-known related questions appear together under `Answer the known questions together.` The veteran reviews one form and selects `Use these decisions`; each answer is still governed and persisted independently. No artificial one-question-at-a-time step selling remains.

Distinct active tasks now retain their governed titles as the visible next action. The final drive caught and removed a generic fallback that had rendered different obstacles as the same question.

## Plan/checklist behavior

The command post is a compact orientation surface rather than another workflow. The route opens only on request in a focused dialog. Current, cleared, and upcoming obstacles remain visible there, while plan tools are collapsed beneath `More plan tools`. The current Gate takes precedence over stale or completed route presentation.

## Personally driven final journey

The final journey was executed against a fresh local runtime containing the exact committed code, followed by a rendered check of the deployed candidate.

1. Started a new veteran/service-member profile: Navy, active duty, leaving within about 12 months, May 2027.
2. Entered a transition objective: stable work near Tacoma, little travel, maintenance-team and scheduling experience, civilian direction unclear.
3. Reviewed the parsed statements and explicitly accepted them.
4. Reviewed three candidate directions framed as alternatives.
5. Explored a Maintenance Planner direction.
6. Answered the full three-question governed bundle in one form.
7. Reached the working-direction/caught-up state with the real-world test visible.
8. In the extended critical drive, reported a real-world result, reversed the prior direction to Customer Success Specialist, and completed the resulting governed review.
9. Submitted irrelevant information (`My favorite coffee mug is blue.`); the product returned `This doesn't change your plan` and created no plan change.
10. Submitted a Cross-Slice update covering a spouse's Seattle job, a 30-minute location constraint, and evening-only education; Work, Education, and Location were shown for review and saved only after approval.
11. Reloaded and confirmed the active state and question survived.
12. Repeated the five-second hierarchy check at 390 × 844: current objective, required content, and update access appeared before optional context, with no collision.

## Confusion ledger and fixes

| Observation during critical drive | Classification | Fix in final commit |
|---|---|---|
| Removed panel still had a JavaScript reference | Broken flow | Removed stale binding and added static regression coverage |
| Checklist expanded beyond the fixed rail | Competing/overflowing workflow | Moved route to a centered dialog |
| Timing appeared cleared while timing was active | Unexplained state contradiction | Current Gate now overrides route-cleared state; canonical Gate ID used |
| Composer consumed the top of every dashboard | Competing primary workflow | Demoted to `Something changed?` modal/bottom sheet |
| Four plan tools competed with NOW | Competing calls to action | Collapsed beneath `More plan tools` |
| Direction cards clipped and scrolled internally | Hidden decision information | Removed fixed height and nested scrolling |
| Named direction reversal was dismissed as unrelated | Broken interruption flow | Added explicit plan-change routing and deterministic named-role recognition |
| Fog-bank cancel did not return to the composer | Dead end | Restored the composer and focus on cancel |
| `stay within 30 minutes` missed Location | Cross-Slice recognition gap | Added bounded location phrase handling and regression test |
| Separate plan tasks looked identical because of generic fallback copy | Repetitive question / unclear obstacle | Preserved each governed task title in the final screen |

All ledger items above were corrected before the final disposition. No unresolved material human-attention defect was observed in the final fresh drive.

## Five-second assessments

### Desktop

Pass. The primary answer is the large left-hand NOW surface. One primary action advances it. Current target and path position orient the veteran; command-post content, related checks, checklist, and plan tools remain subordinate. Candidate and bundle screens use the same hierarchy.

### Android width

Pass at 390 × 844. The header exposes `Something changed?`; the working direction and active content are first; required information appears before optional context. No text collision, horizontal overflow, or secondary control displaced the current objective.

### Resolution-tightening follow-up

The release candidate was additionally inspected at 1366 × 768 and 1440 × 900 after human review graded the hierarchy solid but noted slight screen-fit drift. Short-height desktop spacing is now compacted without changing the information hierarchy. The primary pane exposes a visible slim scroll rail whenever its fixed dashboard surface contains more governed content than the viewport can show; content no longer appears accidentally cropped. Android behavior remains unchanged.

## Automated validation

| Check | Result |
|---|---|
| Complete Pytest suite | PASS — 324 tests |
| Targeted UX/governance regressions | PASS, included in full suite |
| Changed-file Ruff | PASS |
| Strict Mypy | PASS — 17 source files |
| Bandit | PASS |
| Dependency audit | PASS — no known vulnerabilities; local project package not queried from PyPI |
| JavaScript syntax | PASS (`node --check static/app.js`) |
| Git whitespace check | PASS |
| Rendered browser drive | PASS |
| Local browser console during critical drive | PASS — no errors observed |
| Candidate Cloud Run error logs | PASS — zero `severity>=ERROR` entries after deployment verification |

Repository-wide Ruff still reports 155 pre-existing issues concentrated in benchmark/research files outside this UX change. Those are preserved as repository debt and were not introduced or repaired by this order. Audit-cache traversal also emits access-denied warnings for existing cache directories; the dependency audit itself completed successfully using a separate accessible cache.

## Governance audit

This change alters presentation and deterministic recognition of ordinary user wording only. It does not change canonical HELM, Gate semantics, Authority Governor behavior, Probe authority, Canonical-state meaning, Domain Pack policy, Adaptive Aperture status, or human authorization requirements. Updates remain review-before-write. Irrelevant input does not mutate the plan. Non-blocking information is visually demoted, not deleted. No production profile was mutated as part of implementation or validation.

## Remaining issues

No bounded issue remains that prevents the one-foreground-objective contract from closing. The broader project still has pre-existing lint debt in research/benchmark files, and final competition submission remains a separate Human Gate.

## Candidate and production status

- Implementation commits: `286bcab70432392791ae6898dc3d1733962a5c40`, `35cd08b1af2a813c9cfeaf078a65634012a7e839`
- Cloud Run revision: `military-slices-00052-sag`
- Candidate URL: <https://hackathon-rc---military-slices-ztvqlzospa-uw.a.run.app/?release=35cd08b>
- Candidate traffic: `0%`
- Production traffic: `100%` remains on `military-slices-00001-niw`
- Production Probe/profile state: unchanged
- External effects: none

The deployed candidate was opened after deployment and rendered the corrected bundled-decision hierarchy. Cloud Run reported the revision ready, and the revision error-log query returned an empty ledger.
