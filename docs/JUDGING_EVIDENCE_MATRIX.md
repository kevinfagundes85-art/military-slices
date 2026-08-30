# Judging Claim-to-Evidence Matrix

| Judge-facing claim | Primary evidence | Corroboration |
|---|---|---|
| A person can start with ordinary language, a document, or a screenshot. | `static/index.html`, `static/app.js`, `military_slices/app.py` upload/orientation routes | Screenshot `docs/screenshots/01-front-door.png`; demo 00:31.651 |
| Typed input is reviewed before it changes the plan. | `military_slices/app.py` orientation/confirm flow; governance tests | Screenshot `02-human-review.png`; demo 00:35.389–00:37.861 |
| The system connects Career, Education, Location, and Your Story through one plan. | `military_slices/models.py:615+`; `military_slices/slices.py`; `military_slices/plan.py` | Human-review affected-Slices copy; complete-plan screenshot |
| Slices are bounded projections, not independent agents or duplicate state. | `military_slices/slices.py:20-91`; `docs/ARCHITECTURE.md` | `docs/architecture.svg` |
| Gemini receives a purpose-limited surface. | `military_slices/agent_runtime.py:_minimal_context`; `military_slices/temporal.py:minimum_sufficient_evidence` | Resolver/context-regression tests; architecture diagram |
| Google ADK is part of the running agent path. | ADK imports, `Agent`, `Runner`, `RunConfig`, structured output, and call limits in `military_slices/agent_runtime.py:413-667` | `pyproject.toml`; hosted release report |
| Gemini cannot authorize or write plan state by itself. | `ResolverProposal` and `AuthorityGovernor` separation in `military_slices/agent_runtime.py`, `military_slices/governance.py`, and `military_slices/app.py` | Governance/adversarial tests; architecture diagram |
| Related known questions are answered together rather than step-sold. | Bundled-acquisition rendering in `static/app.js`; acquisition horizon in `military_slices/acquisition.py` | Screenshot `04-bundled-decisions.png`; demo 00:45.246–00:46.854 |
| The product generates multiple career directions and preserves alternatives. | Resolver and deterministic hypotheses in `agent_runtime.py`/`engine.py`; plan alternative projection in `plan.py` | Screenshot `03-direction-choice.png`; demo 00:42.767 |
| A chosen direction becomes a real-world experiment, not just advice. | Direction/test cycle in `engine.py`, `app.py`, and `plan.py` | Screenshot `05-real-world-test.png`; demo 00:49.526 |
| Returning evidence changes only the relevant plan surface. | Test-result handling and governed write path in `app.py`; plan findings/changes in `plan.py` | Screenshot `06-plan-updated-from-evidence.png`; demo 00:52.143–00:58.924 |
| The product keeps versioned state and survives re-entry. | Firestore transactions and version subcollection in `store.py:85-153`; history routes in `app.py:202-235` | Persistence/history tests; hosted release report |
| What-If exploration does not silently change current truth. | Signed branch creation/promotion in `control.py`, `security.py`, and `app.py:236-289` | What-If governance tests |
| The veteran can view and export a complete dated transition plan. | `plan.py:194+`; `/api/plan/export` in `app.py:166-181` | Screenshot `07-complete-plan-and-export.png`; demo 01:15.282–01:21.799; verified export SHA-256 |
| The UI works at Android width. | Responsive CSS and targeted browser/UX regression tests | `MILITARY_SLICES_COMPLETE_TRANSITION_PLAN_UX_EVIDENCE_2026-08-28.md` |
| The application is publicly testable without account setup. | Hosted candidate URL | Live verification on 2026-08-29: title and front door rendered; zero console warnings/errors |
| The candidate uses Cloud Run and Firestore. | `Dockerfile`, `store.py`, hosted release report | Public `.run.app` URL and deployment identity in evidence report |
| The final product suite passes. | Executed final validation | 335/335 Pytest; product/test Ruff; strict Mypy on 18 source files; Bandit; JS syntax; pip-audit |
| The final presentation is publicly reachable. | <https://youtu.be/EwAtrtrIUiI> | YouTube title and oEmbed metadata resolved on 2026-08-29; visible duration 3:12 |
| The demonstrated journey uses synthetic data. | Final presentation plus clean-take ledger and video SHA-256 | Seven extracted product screenshots; frame/contact-sheet QA |
