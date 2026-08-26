# Mobile Direction-Gate Correction — Human Gate Evidence

## Human verdict

The physical mobile pass failed. A separated veteran had the saved target “Choose the post-service
direction worth pursuing first,” but `What matters now` exposed no direction choice. It rendered
“Your next steps are ready,” one inactive task description, and an `Add an update` button. A large
grid of Lens previews then dominated the page, including empty domains and repeated context.

This was a correctness and orchestration defect, not polish.

## Root causes

1. `_recompute_gates` required `transition_date` before creating `transition-direction`. A veteran
   already separated 1–5 years ago correctly has no future separation date, so the active task and
   target survived while their actionable Gate disappeared.
2. `remote` was classified as Location context. “Remote AI position” therefore repeated a work
   preference in both Work needs and Location.
3. `buildLensTopics` padded the Lens cloud with starter domains even when they had no facts, impact,
   open Gate, conflict, or current-path relevance.
4. The entire Lens cloud was visible by default, making secondary state more prominent than the
   missing decision.
5. Generic decision receipts said a preference was applied across domains even when the human had
   simply selected “I am still deciding.”

## Bounded correction

- A separated lifecycle plus established service identity now satisfies the deterministic
  prerequisites for `transition-direction`; no fabricated transition date is required.
- `remote`, `hybrid`, and `position` are classified as Career/work context. `remote` is no longer a
  Location keyword.
- Empty Lens topics are not emitted. No starter topics pad a saved plan.
- Secondary exploration is collapsed behind `Look at this another way` and exposes no more than six
  meaningful topics when deliberately opened.
- Legacy remote-only Location facts are filtered from the Location preview so existing profiles do
  not continue displaying the prior misclassification.
- Preview copy now states the useful relationship, provides an explicit `Add context about …`
  action, and avoids repeated containment language.
- “I am still deciding” now produces a causal receipt stating that work, education, and location
  remain open and that one direction choice comes next.

## Regression and local mobile proof

- Exact separated-veteran fixture: no `transition_date`; active Gate is `transition-direction` with
  `Civilian work`, `Education or training`, and `Location and family fit`.
- Exact remote-AI statement: affected Slice is Career only.
- Default saved-plan view: Lens cloud hidden.
- Secondary topics: empty domains are not padded; maximum six.
- Browser walkthrough at 360×800: the three choices render inside `What matters now`; the primary
  action is 48 px high; each choice target is 57 px high; no horizontal overflow.
- Updated receipt: `Kept work, education, and location open` and
  `Put one clear direction choice in front of you next`.
- Full automated suite: 194 passed.
- Ruff, strict Mypy, Bandit, and JavaScript syntax: passed.

Production traffic was not moved during implementation or local validation.
