# Mobile Human-Control Correction — 2026-08-26

## Human evidence

The physical Android pass exposed four coupled defects:

1. `Civilian work` appeared selected before the human made a choice.
2. A promoted target experiment displayed comparison-era consequences saying no target or fact had
   changed, directly contradicting the saved-change headline.
3. Earlier Plans exposed persistence versions, including repeated targets and pre-target writes,
   rather than meaningful changes in direction.
4. Plan scaffolding and a clipped five-stage timeline preceded `What matters now` on a phone.

These were interaction correctness defects, not visual polish.

## Bounded correction

- Choice Gates render with no default radio selection. The existing inline validation requires an
  explicit human choice.
- Target-experiment promotion now reports exactly what happened: the possibility was saved as
  context, the direction choice remains open, and the context will carry forward after that choice.
- Other promoted hypotheticals use a saved-change headline instead of the old generic headline.
- Earlier Plans removes pre-target writes, collapses consecutive versions with the same target, and
  displays at most four actual target changes. With no earlier direction change, it says so plainly.
- `What matters now` precedes plan context in document and focus order.
- The redundant transition hero and horizontally clipped timeline are suppressed below 480 px. The
  current target and path position remain available beneath the active decision.

## Falsification and local proof

- A separated 1–5 year Navy veteran reaches `transition-direction` with all radios unchecked.
- Promoting `What if I build a useful AI tool for veterans?` preserves the open direction Gate and
  yields a truthful three-line causal receipt with no comparison-era contradiction.
- Earlier Plans shows no raw versions when the target has not changed.
- Selecting `Civilian work` advances to `next-work-preferences`; `transition-direction` is no longer
  active.
- At a 360 px test viewport, `What matters now` begins at page position 101 px, plan context begins
  at 886 px, the timeline is absent, document width equals scroll width at 345 px, and there is no
  horizontal overflow.
- Full suite: 197 passed.
- Ruff, strict Mypy, Bandit, JavaScript syntax, and dependency audit: passed.

Production traffic was not moved during implementation or local validation.
