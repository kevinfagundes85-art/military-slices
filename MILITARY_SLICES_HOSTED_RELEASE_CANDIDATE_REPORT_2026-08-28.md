# Military SLICES Hosted Release Candidate Report

Date: 2026-08-28

## Executive disposition

**HOSTED CANDIDATE READY — KEEP ZERO TRAFFIC FOR DEMO**

The tagged Cloud Run candidate is publicly reachable, healthy, session-persistent, and validated through a complete desktop judge journey and a critical Android-width journey. Production remains unchanged at 100% traffic. Keeping the candidate on a zero-traffic tag provides the required judge/demo URL without risking the protected production revision before submission.

## Release identity

| Item | Identity |
|---|---|
| Protected UX baseline | `c85e3e4` |
| UX evidence commit | `e5456025dd5657a6849bfbe4eabcfee5e3f8bccb` |
| UX report SHA-256 | `f9e106237ed5310303e5977ff96dfeb0ce39210a0d2ce28ebe70164792507c03` |
| Hosted source commit | `5143ac3a9df690995fe1d16d6a4251c0cced0fa4` |
| Source tree | `3b4a336ebc9987e9d5cea398eb672a528f336d3b` |
| Bounded fallback fix | `e920ae0a1a8d9ee1047f1d0f69fe8aeb7cd7f239` |
| Natural reversal fix | `0cf2d15074a5abdd138df5386fd1cbcebb5779a4` |
| Mobile target fix | `5143ac3a9df690995fe1d16d6a4251c0cced0fa4` |
| Container digest | `sha256:f41b68d2fc24d45eb06d4477e19f21ceab4d04c40d5b8fe4a3ede566fe439d3e` |

The three post-baseline changes were bounded judge/release fixes discovered only by using the hosted candidate. No canonical HELM, Domain Pack policy, production configuration, or research mechanism changed.

## Deployment

| Item | Value |
|---|---|
| Google Cloud project | `veteran-pathfinder-kf-2026` |
| Region | `us-west1` |
| Service | `military-slices` |
| Production revision | `military-slices-00001-niw` |
| Candidate revision | `military-slices-00047-doz` |
| Traffic | production `100%`; candidate `0%` |
| Candidate tag | `hackathon-rc` |
| Hosted URL | <https://hackathon-rc---military-slices-ztvqlzospa-uw.a.run.app> |
| Candidate created | `2026-08-28T20:47:14.657367Z` |
| Production change | None |

## Hosted desktop journey

**PASS.** A fresh synthetic Navy transition case stated a June 2027 separation, a stable remote cybersecurity goal, inability to relocate, and a part-time AI certificate. The hosted experience retained the natural statement and review boundary; produced relevant cybersecurity directions; selected Information Security Analyst; presented two related questions together; retained both answers; accepted and correctly attached a real-world job-post/recruiter test result; accepted a natural-language reversal to Cloud Security Engineer; reopened the right next decision without erasing prior history; and preserved state across reload.

The candidate exposes the actual HELM value through the interface: central human input, a coherent persistent plan, a bounded active focus, decision receipts, contextual re-entry, and changed-reality handling.

## Hosted mobile journey

**PASS at Android viewport 390 × 844.** The final uncached candidate had no horizontal overflow (`scrollWidth == clientWidth`), no clipped controls, zero interactive buttons below the 44 px touch-target floor, a usable persistent composer, readable direction cards and bundled controls, correct cybersecurity directions, a continuing active decision after reload, and no dead end or repeat loop.

One mobile automation pass asked for the transition date again after it had been entered during onboarding. The flow accepted the date and continued normally; the behavior did not reproduce as a blocking loop. It remains a low-severity observation for later physical-device validation, not a release blocker.

## Physical-device and cold-user status

- Physical Android device: **not performed** in this window.
- Independent cold user: **not performed**.
- Chief-engineer cold judge-path: **performed and passed** using fresh hosted sessions.

These optional checks remain accepted submission risks and must not delay the final package indefinitely.

## Authentication and session behavior

Anonymous first value worked without account creation or payment. Sessions were isolated and Firestore-backed state survived reload. Secure cookies and the existing dedicated runtime identity remained configured. No second-account test was performed in this window.

## Provider and runtime

- Runtime: Cloud Run, Google ADK, Vertex AI, Gemini 3.7 Flash.
- State: Firestore.
- External effects: disabled.
- Autonomous production Probe: disabled.
- Health endpoint: HTTP 200 with expected service, model, Domain Pack, and protection metadata.
- Candidate readiness: `Ready=True`, `ContainerHealthy=True`; container healthy in 5.41 seconds.

An earlier zero-traffic revision reached the provider's three-call limit and safely used the deterministic fallback. The fallback initially produced generic, irrelevant career options for an explicit cybersecurity goal. The preserved failure led to a bounded deterministic cybersecurity fallback and regression test. The final hosted journey used the provider successfully and returned relevant options. Generic fallback coverage outside recognized families remains a known, fail-safe quality boundary.

## Logs and browser diagnostics

For final revision `military-slices-00047-doz`:

- server logs at severity `WARNING` or higher: none;
- HTTP responses with status 400 or higher: none;
- browser console warnings/errors during final validation: none.

## Automated validation

- Pytest: **320 passed**.
- Changed-file Ruff: passed.
- Strict Mypy: passed across 17 source files.
- Bandit: passed.
- JavaScript syntax: passed.
- Dependency audit: previously completed with **0 known vulnerabilities**; no dependency changed during hosted fixes.
- Repository-wide Ruff: 155 pre-existing benchmark-only violations remain, separate from the release changes.
- Pre-existing environment debt: audit-cache permission warnings and one Starlette/httpx deprecation warning.

## Governance audit

No production traffic moved. No canonical HELM primitive, authority, Gate, Probe capability, or Domain Pack policy changed. Human confirmation remains the write boundary. Provider fallback remains deterministic and safe. Reversal changes the current target only from explicit human input. External effects and production Probe remain disabled.

## Artifact hashes

| Artifact | SHA-256 |
|---|---|
| `military_slices/engine.py` | `95fae390d1f93577e02bdb5b5079e4bd22f64c29585a513e224d973b01bcf14b` |
| `military_slices/agent_runtime.py` | `936dbdd7ad0578ce09075a903c27e79d49876e7a9f3e9397be5d7af4d9781c53` |
| `static/styles.css` | `7cd485e26d52939aa990a9b2f60db673dacc9fb88b15a854b30ad39f5b09ced3` |
| `static/app.js` | `4c97223cc36f61ad33985f4f6450119e8c807ee7b4ff75621e35979824014362` |
| `static/index.html` | `6b23ae403a5e1d380a2498855333b5b2d733d43464290bdbcb906408d45e3aa5` |
| `pyproject.toml` | `d248dd31e2e3fc4eb026985db7761271596437d264118206efd991fbb906115d` |
| `Dockerfile` | `858de4ea00b3eadefb06012ea8d92879b3a0765aa0946a00594a56970c1214c6` |

## Known defects and accepted risks

1. Physical Android and independent cold-user testing remain open.
2. The mobile timing re-prompt is a non-blocking observation to watch during physical-device rehearsal.
3. A provider call-limit failure can invoke deterministic fallback; explicit cybersecurity intent is now covered, but unrecognized job families may receive broader fallback options.
4. The tagged candidate depends on retained Cloud Run tag availability through judging.
5. Repository publication/access, final video, entrant attestations, and final submission remain Human Gates.

## Submission readiness and exact next Human action

The candidate does not need production traffic to be judge-accessible. The lowest-risk path is to keep production untouched and submit the tested tagged URL.

**Recommended Human action:** record the unedited, no-longer-than-four-minute demo from the tagged candidate using `docs/DEMO_SCRIPT.md`; upload it publicly to YouTube or Vimeo; choose public repository access or grant `testing@devpost.com` and `cloudhackathons@google.com` access if private; confirm eligibility/team/IP attestations; then return for final submission review. The irreversible Devpost submission remains the Human Gate.
