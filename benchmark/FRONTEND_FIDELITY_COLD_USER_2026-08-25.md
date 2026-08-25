# Military SLICES Frontend Fidelity / Cold-User Hardening

Date: 2026-08-25

## Locked boundary

- Frozen behavioral source: `military-slices-00019-ved` / `fe29bc8`
- Production: `military-slices-00001-niw` at 100%; unchanged
- Backend semantics, Firestore structure, routing policy, and production profiles: unchanged
- Candidate deployment: zero traffic; recorded after hosted verification below

## Initial cold-user observation

The first pass was completed before frontend edits. The page rendered a large transition shell, timeline, target/path cards, readiness metrics, four Lenses, History, What-If, and persistent feedback around one primary interaction. An existing plan therefore appeared to expose the machinery used to produce the decision rather than one coherent next decision.

Top defects observed:

1. Cold-start plan scaffolding was present before it could help.
2. Two competing first actions split typed and artifact entry before the user had begun.
3. `what_changed` replayed after reload as if an old change had just happened.
4. Lens previews and History exposed counts, versions, and state vocabulary.
5. Loading, inspection, and stale status feedback could coexist with the next surface.
6. No explicit frontend projection existed for `PARALYZED` or `COMPLETE`.
7. A pre-Anchor version could loop back to the initial intake instead of rendering the backend's next question.

Baseline image:

- `benchmark/frontend-before.png`
- SHA-256 `383EC258B17E2471FF2F4D747739A32AFD6FD686F0921651B2F82478B4016F16`

## Bounded frontend correction

- Cold start now renders one direct text intake, one primary Continue action, and a subordinate rich-file option.
- Timeline, target/path context, Lenses, History, What-If, impacts, and change feedback remain hidden until state earns them.
- A pre-Anchor saved state renders the backend's bounded objective question without revealing the full plan shell.
- Typed input retains review/confirm authority. Artifact copy accurately states that deliberate file selection authorizes the bounded update.
- `what_changed` is shown only for a change completed in the current page session and disappears on reload.
- `ACTIVE`, `PARALYZED`, and `COMPLETE` have distinct human-facing projections without exposing enum names.
- Completion suppresses old change feedback and does not invent a new goal.
- Tasks are secondary while a decision is open and become the foreground when no human question remains.
- Lens tap is explicitly a preview. Detail remains read-only. Counts and internal state terms were removed.
- What-If remains visually hypothetical; discard and explicit promotion remain separate.
- History uses read-only current/earlier language and removes profile-version presentation.
- Internal backend wording is projected into ordinary language before it reaches normal interactions.
- Action-in-progress state preserves the prior stable surface, disables the action, and uses one stable progress sentence.
- Network/provider error copy preserves prior-state orientation and suppresses provider/infrastructure vocabulary.
- Focus moves to the new primary heading after a successful transition.
- Mobile form controls use 16 px inputs and measured visible controls remain at least 44 px high.

After images:

- `benchmark/frontend-after-cold-320.png`
  - SHA-256 `F5125E322D623BC44A3FA1AAA9D84B9BDAD4C7EB1E44209956FF3995B3A91C4F`
- `benchmark/frontend-after-desktop.png`
  - SHA-256 `A0F3B7AECAEFF07B6B47ABFA83AD79EEC52F22040A2789BC22610A8E9F4636BA`

## Browser journeys

| Journey | Result |
|---|---|
| Cold start | PASS — intake only; no empty plan machinery |
| Messy work/location input | PASS — review, then one date decision; no UI explosion |
| Reload/resume | PASS — same next question; old change feedback suppressed |
| Genuine conflict | PASS — bounded explanation and choice; no enum/backend jargon |
| Conflict resolution | PASS — next interaction replaces conflict once |
| Complete goal | PASS — explicit completion; no tasks, spinner, or manufactured objective |
| Lens preview/detail | PASS — preview is obvious; detail is read-only; no mutation/model call |
| What-If discard | PASS — reload preserved current state |
| What-If promote | PASS — explicit promotion persisted; History retained prior state |
| Résumé target named | PASS — target question closed once and did not repeat |
| Spouse/PCS entry | PARTIAL — UI remains a general transition planner, but a frozen backend subject/timing contradiction remains |

## Frozen-backend contradictions discovered

These were not silently corrected because the execution order freezes backend semantics.

1. Exact sentence: `I want my résumé ready, but I haven’t picked a target role yet.`
   - Backend outcome: sufficient orientation is saved, but no human Anchor is selected; the next backend question asks the user to choose the objective.
   - Frontend correction: render that bounded question instead of looping to the original intake.
   - Remaining contract difference: the accepted journey expected the specific target-role question immediately. The user currently needs one extra explicit objective choice.

2. Spouse/PCS input: `My spouse is active-duty Army and we PCS to Colorado Springs in eight months...`
   - Backend can infer Army context but does not preserve who is serving versus who is planning.
   - After choosing the location objective, the next backend question can be `When do you expect to leave active service?`, addressed to the spouse.
   - This is a subject/meaning error in frozen path semantics. Frontend substitution of the PCS date would write a different meaning into `transition_date`, so it was not attempted.

## Responsive and accessibility evidence

| Width | Page overflow | Minimum visible control | Input font |
|---:|---:|---:|---:|
| 320 px | No | 48 px | 16 px |
| 375 px | No | 44 px | 16 px |
| 414 px | No | 44 px | 16 px |
| Desktop | No observed page-level overflow | 44 px or greater | Browser default |

- Timeline overflow remains contained inside its own horizontal rail; it does not create page-level scrolling.
- Reduced-motion mode disables the only processing pulse.
- Browser warning/error console: zero in local journeys.
- Native Android picker and soft-keyboard obstruction remain human-only physical-device gates.

## Automated validation

- `139 passed`
- JavaScript syntax: PASS
- Ruff on application/tests: PASS
- strict MyPy: PASS
- Bandit: PASS
- dependency audit: no known vulnerabilities (editable local distribution skipped)
- Frozen backend files changed: none

## Verdict

`PARTIAL`

The corrected frontend faithfully projects the frozen backend and materially improves cold-start, transition stability, human control, execution-state fidelity, progressive disclosure, History, Lens, and What-If behavior. Full `PASS` is not claimed because the résumé semantic-equivalence and spouse/PCS subject/timing contradictions are backend contract defects and because physical cold-user/Android gates remain open.

## Highest-value remaining frontend work for one additional day

These are recommendations only and were not implemented beyond this order:

1. Run an unbriefed-adult comprehension session and tune only the copy that causes observed hesitation.
2. Add a browser-level visual-regression harness for the three execution states and 320/375/414 px widths.
3. Add an explicit in-product retry affordance beside long-running model-backed actions, while retaining idempotency.

