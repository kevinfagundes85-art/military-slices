# Backend Contract Corrections — 2026-08-25

## Scope

The backend semantic freeze was opened for exactly two confirmed contract defects:

1. explicit résumé-readiness intent did not satisfy the human objective anchor;
2. spouse/PCS input conflated the person planning with the person whose military status was described.

During physical review, the founder separately required removal of bottom-toast notifications as an interaction-driving mechanism. That bounded frontend correction was applied without changing the primary interaction or adding a panel.

## Corrections

- `I want my résumé ready, but I haven’t picked a target role yet.` now establishes `Make my résumé ready for a specific target` and routes directly to `resume-target-role`.
- Canonical state now independently records `planning_actor` and `military_state_subject`.
- `My spouse is active-duty Army ...` records `military_spouse` / `planning_actor_spouse`; it does not populate the planner's separation date, surface `planned-transition-date`, or generate Army TAP tasks.
- Governed changes and consequences remain inline in the existing `What matters now` interaction and causal receipt.
- Required human corrections render inline. The transient status channel is limited to non-decision acknowledgement (`Saved.` / `No changes saved.`) and retryable failures. Successful status text remains available to assistive technology without a visible bottom popup.

## Automated validation

- `pytest`: 145 passed.
- Ruff: passed.
- MyPy: passed.
- Bandit: passed.
- `pip-audit`: no known vulnerabilities (local package excluded because it is not published to PyPI).
- JavaScript syntax: passed.
- Hosted candidate warning/error logs: none after validation.

Exact regression fixtures:

- `test_explicit_resume_readiness_intent_routes_directly_to_missing_target_role`
- `test_spouse_pcs_planner_is_not_given_service_member_separation_milestones`
- `test_success_updates_are_announced_without_a_competing_visual_toast`
- `test_governed_changes_and_required_actions_never_depend_on_toasts`

## Hosted evidence

- Production revision: `military-slices-00001-niw` at 100% traffic.
- Candidate revision: `military-slices-00023-cuv` at 0% traffic.
- Candidate tags: `competition-rc`, `contract-rc`, and `frontend-rc`.
- Candidate container: `sha256:e3a1057b70b7fbb5f5ec47eb46cd46d440d2e7a825485c31378578dadf5351b1`.
- Hosted health: `ok`.
- Hosted `app.js?v=4` SHA-256: `A9CBD3931B22163292B939C3807289877FC457112D33DB2FB2DEB387E85B6BE1`.
- Hosted `styles.css?v=4` SHA-256: `E8380963FDC0DA9781EDFBFC5B739FA48926B5BC3742C2E208139C375A994B83`.
- Both hosted hashes exactly match the committed local assets.

Hosted résumé fixture result:

- target: `Make my résumé ready for a specific target`;
- active question: `What role or specific use should this résumé support?`;
- consequence receipt: inline;
- visible bottom success popup: absent;
- console warnings/errors: none.

Hosted spouse/PCS fixture result after choosing location:

- `planning_actor`: `military_spouse`;
- `military_state_subject`: `planning_actor_spouse`;
- `service`: `army`;
- `transition_date`: absent;
- separation-date gates: 0;
- active-service separation questions: 0;
- TAP tasks: 0.

## Human gates still open

- physical Android interaction;
- cold-user comprehension.

This candidate remains at zero traffic. No human-only gate is claimed complete.
