# Deterministic Orientation + Fog Bank Release Evidence

Date: 2026-08-25 (America/Los_Angeles)  
Source commit: `12e5c19`  
Candidate revision: `military-slices-00030-xaq`  
Candidate traffic: `0%`  
Candidate URL: `https://orientation-fog-rc---military-slices-ztvqlzospa-uw.a.run.app/`  
Production revision: `military-slices-00001-niw`  
Production traffic: `100%`

## Issue classification

1. The acceptance-pass misorientation was an implementation/state-acquisition failure and contract-enforcement gap. Free text was being interpreted before a trusted lifecycle vector existed.
2. The future-separation question was a downstream path-runtime defect. Transition language could nominate a planned-separation gate despite explicit historical separation.
3. Resolving the target to `Find civilian work` was a target-resolution containment defect. Existing civilian employment was not being used to exclude the initial-transition interpretation.
4. The Career timing rationale was stale downstream rationale reuse caused by the incorrect planned-transition-date gate, not a missing HELM primitive.
5. The lack of a persistent human re-orientation control was an implementation gap. Fog Bank is implemented through existing candidate examination and human-authorized mutation contracts.

No evidence requires reopening the frozen HELM architecture.

## Implementation

Changed files:

- `military_slices/models.py`
- `military_slices/engine.py`
- `military_slices/path_runtime.py`
- `military_slices/security.py`
- `military_slices/app.py`
- `static/index.html`
- `static/app.js`
- `static/styles.css`
- `tests/test_starting_vector_and_fog_bank.py`
- `tests/test_static_contract.py`

The front door now records a human-confirmed planning role, lifecycle position, branch, and existing service category before open-ended orientation. Those facts orient state only; they do not create eligibility or policy consequences. Subsequent semantic interpretation is conditioned on that vector and cannot silently replace it.

Fog Bank is available as `Something doesn’t fit`. Examination is purpose-scoped, signed to profile/source version/text, and zero-write. A proposal requires the existing trusted human mutation path. Cancellation preserves the active plan. Accept performs normal ownership, optimistic-concurrency, idempotency, provenance, lineage, version, and replay checks.

## Automated validation

- Full pytest suite: `187 passed`; one pre-existing Starlette/httpx deprecation warning.
- Ruff: passed.
- strict Mypy: passed.
- Bandit: passed.
- Dependency audit: no known vulnerabilities; the local non-PyPI package was skipped.
- JavaScript syntax: passed.
- Git diff/check: passed.

Added coverage includes deterministic role/lifecycle/branch/component acquisition; current service and historical separation; spouse and counselor actor/subject separation; contradictory free text; prevention of a future-separation gate; existing civilian employment containment; Slice rationale relevance; Fog Bank entry from multiple lenses; zero-write activation; cancellation; insufficient context; contradiction detection; proposed/accepted/rejected re-orientation; stale version; replay/idempotency; cross-user isolation; provenance/lineage; restart/reconstitution; mobile and focus/static accessibility contracts.

## Hosted transaction evidence

Acceptance fixture:

- Version `0` became version `1` only after the starting vector was confirmed.
- Reviewed semantic input became version `2` through the ordinary trusted mutation path.
- Lifecycle remained `separated_1_to_5_years`.
- Path window resolved to post-service stabilization (`H`).
- The target preserved the user's existing civilian employment and build/impact intent; it did not become `Find civilian work`.
- The active gate was Career direction; no planned-transition-date gate or stale one-date rationale was produced.

Fog Bank falsification fixture:

- A deliberately wrong state contained a future departure, `leaving_within_12_months`, and `Find civilian work` at version `3`.
- Entering and examining Fog Bank left the profile at version `3`.
- Examination detected both the timeline contradiction and existing-civilian-employment contradiction.
- The proposal identified lifecycle position, transition date, and human anchor as affected without authorizing a Slice or mutation.
- Cancellation/rejection preserved the previous state.
- Human acceptance produced version `4`, removed the incompatible future date, retained historical separation, and replaced the insufficient target through mutation kind `fog_bank_reorientation`.
- Replay remained at version `4`; provenance and lineage were present.

## Hosted identity and safety

Health reports:

- status: `ok`
- model: `gemini-3.7-flash`
- framework: `google-adk`
- Domain Pack version: `2026-08-24-v2-shadow-tested`
- Domain Pack SHA-256: `026a1508a3a2e6eb16907b2e8fc29c4f333af5c5ab908e6029903b8cbcbf9f4c`
- Domain Pack state: `LEGACY_VALID`
- external effects: disabled
- autonomous Probe: disabled

Exact hosted bundles were `app.js?v=7` and `styles.css?v=6`. Candidate configuration matches the established production contract. Candidate warning/error log query returned no entries.

## Real-browser and mobile validation

A fresh candidate hostname was used temporarily to avoid a retained test cookie; it was removed after validation without moving traffic.

Real-browser results:

- Cold entry displayed the four deterministic choices before open semantic input.
- Veteran/service member + separated 1–5 years + Navy + active duty persisted, then revealed the existing rich-input front door.
- The exact acceptance-pass sentence reached review, then a post-service target and Career direction gate.
- No future-separation question appeared.
- No `Find civilian work` target appeared.
- `Something doesn’t fit` was discoverable from the active path.
- Fog Bank communicated that nothing had changed, accepted open context, requested one bounded clarification when the already-correct state made the submitted challenge insufficient, and cancellation restored focus to the active path.
- Browser warning/error console: empty.
- Widths 320, 375, and 414 px: no horizontal overflow; minimum visible interactive target was at least 44 px (48 px at the reloaded 320 px check).
- Focus returned to the Fog Bank launch control after cancellation.

## Remaining Gates

- Physical Android interaction and native-picker behavior.
- Cold-user comprehension and adult-tone review by a human unfamiliar with the implementation.
- Real second-account isolation.
- Founder convergence on the acceptance fixture and Fog Bank name/copy.
- Independent Domain Pack activation, policy-value, retention/deletion, external-effect, and autonomous-Probe authorizations remain unsatisfied.
- Production promotion remains a separate explicit human release gate.

Production traffic was not moved. The candidate remains zero traffic, and `military-slices-00001-niw` remains the immediate production rollback target.
