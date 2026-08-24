# Military SLICES Transition Path Research Pack — 2026-08-24

This pack exists for one purpose: give BHE a **bounded, service-aware transition path** so Military SLICES stops treating the entire military-transition universe as active work.

## Core HELM rule applied

**HELM bounds agency by purpose.** Every execution begins with a declared target state and a defined path. Service/domain context constrains what the system may examine; the active path constrains what it may act upon. Information may enter governed state without entering the active interaction. Only information that materially advances, validates, blocks, or threatens the active path may be promoted into a gate or action.

Shorthand:

> **No unanchored work. No unbounded exploration.**

## What is in this pack

- `MILITARY_SLICES_TRANSITION_PATH_SPEC_2026.md` — canonical cross-service path and service overlays.
- `SERVICE_TERMINOLOGY_MATRIX_2026.md` — Army, Navy, Marine Corps, Air Force, Space Force, and Coast Guard terminology and office/system differences.
- `NAVY_2023_GUIDE_UPDATE_OVERLAY_2026.md` — what from the uploaded 2023 Navy retirement guide is still useful, what is stale, and how BHE should treat it.
- `BHE_PAYLOAD.md` — paste-ready execution order.
- `service_path_boundaries.json` — machine-readable task/path structure.
- `source_manifest.json` — authoritative source list and freshness metadata.
- `sources/navy/Navy_Retirement_Resource_Guide_2023_ORIGINAL.pdf` — original user-provided source for historical/contextual comparison.

## Important product constraint

The checklist/timeline is **not the UI** and **not a list of everything the product must solve**.

It is the task boundary.

Military SLICES should answer:

> **Given where this service member is on the transition path, what are the next 1–3 tasks that materially advance the declared transition goal, what gate blocks each task, and can the system close that gate or surface one human decision?**

Everything outside that current task horizon remains latent unless grounded evidence shows that it materially threatens, blocks, validates, or changes the active path.


## v2 shadow-test update

The 24 Aug 2026 shadow-agent test added the two-anchor model (`human_anchor` + `path_target_state`), Coast Guard retirement early-start nuance, and current DAF SkillBridge volatility handling. See `SHADOW_AGENT_TEST_2026-08-24.md`.
