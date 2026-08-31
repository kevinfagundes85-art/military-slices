# Final Validation Report — 2026-08-29

## Scope

Submission-readiness validation for the existing Military SLICES candidate. No HELM architecture, product behavior, or production traffic was changed during this pass.

## Executed checks

| Check | Exact command or method | Result |
|---|---|---|
| Product and regression suite | `.venv\Scripts\python.exe -m pytest -q --disable-warnings` | **PASS — 335/335 collected tests** |
| Product/test lint | `.venv\Scripts\python.exe -m ruff check military_slices tests` | **PASS** |
| Strict typing | `.venv\Scripts\python.exe -m mypy military_slices` | **PASS — 18 source files** |
| Static security scan | `.venv\Scripts\python.exe -m bandit -r military_slices -q` | **PASS — no findings emitted** |
| Dependency vulnerability audit | `.venv\Scripts\python.exe -m pip_audit --cache-dir .pip-audit-cache-final` | **PASS — no known vulnerabilities; local package itself skipped because it is not on PyPI** |
| Browser JavaScript syntax | Node `--check` on `static/app.js`, `benchmark/cdp_eval.mjs`, and `benchmark/drive_judge_clean_take.mjs` | **PASS** |
| Architecture artifact | Python XML parse plus rendered PNG visual inspection | **PASS** |
| README image references | Deterministic local-path check | **PASS — no missing image references** |
| Live candidate smoke check | Public candidate loaded in a fresh query-bound browser tab; visible front door and console inspected | **PASS — page title and entry experience rendered; zero console warnings/errors** |
| Screenshot visual QA | Eight 2560×1440 product/architecture images individually inspected | **PASS** |
| Clean demo integrity | SHA-256, byte count, video metadata, event ledger, and 5-second contact-sheet review | **PASS** |

## Repository-wide Ruff result

`ruff check .` was executed and returned **155 findings** in historical benchmark/generator scripts, primarily long frozen corpus strings plus a smaller number of import-order and unnecessary-f-string findings. The production package (`military_slices`) and its tests pass Ruff with no findings.

Those benchmark files preserve research evidence and generated-corpus provenance. They were not reformatted in a submission-packaging pass because doing so would alter frozen research artifacts without improving the running product. This is disclosed repository debt, not represented as a green repository-wide lint result.

## Test warning

Pytest emits one third-party deprecation warning from `fastapi.testclient` about Starlette's current `httpx` integration. It does not fail the suite and is not an application warning.

## Public-release audit

- No private keys, API tokens, or committed `.env` values were found by the final tracked-file pattern scan.
- `.env.example` now uses `YOUR_PROJECT_ID` rather than a developer project identifier.
- Three developer-local absolute image-generation paths were removed from an evidence document.
- One test fixture containing a developer-like name was replaced with a neutral synthetic name.
- Local audit caches, screenshot tools, browser profiles, failed takes, stop files, private conversation export, and large demo-video files are excluded from version control with targeted rules.
- The verified demo ledger remains suitable for source control; the large clean MP4 remains a local upload artifact.
- Existing frozen benchmark evidence remains in the repository and is not part of the judge's primary reading path.

## Deployment status

- Public candidate: <https://hackathon-rc---military-slices-ztvqlzospa-uw.a.run.app/>
- Tagged candidate evidence: Cloud Run revision `military-slices-00050-cad`, region `us-west1`.
- Live verification performed: 2026-08-29.
- Anonymous front door: available.
- Browser console warnings/errors during smoke check: zero.
- Production traffic: unchanged; candidate remains the submission/test surface described by the hosted release report.

The live smoke check proves availability and front-door rendering. The clean demo and full regression suite prove the later journey on the current local source commit; no claim is made that a remote revision was rebuilt during this packaging pass.

## Clean demo evidence

Final public presentation: <https://youtu.be/EwAtrtrIUiI>

On 2026-08-30, YouTube resolved the title **Military SLICES — Powered by HELM | Hackathon Demo** and displayed a duration of `3:12`; the entrant separately confirmed signed-out playback. The local clean-take evidence below remains capture provenance; its hash is not represented as the byte hash of the final YouTube presentation.

- Video: `benchmark/output/MILITARY_SLICES_JUDGE_DEMO_CLEAN_TAKE_2026-08-28.mp4`
- SHA-256: `6c8c0bd12b2b58fca4267407928b9f2b037c8c93175f704093f6ac3fb00c9cc0`
- Bytes: `4,172,987`
- Capture duration: `89.6426s`; container duration: `88.8s`
- Video: H.264 High, 2560×1440, 15 fps, 1,332 frames
- Capture failures: `0`
- Final edit applied: `false`
- Ledger: `benchmark/output/MILITARY_SLICES_JUDGE_DEMO_CLEAN_TAKE_LEDGER_2026-08-28.json`
- Ledger SHA-256: `f84f1549a8459584fa2b394385279fcc9c755d1514635d0437c4db10d97cb42f`
- Export produced during take SHA-256: `65147eaa8350bba130315db7f667be923fe109b35644af3791f34bed514c6fd9`

The QA ledger records no lock screen, notifications, unrelated tabs, personal data, developer surfaces, or save dialog.

## Known limitations

1. Eligibility, entrant/team, ownership, and final submission attestations remain human-only.
2. Physical Android hardware and an independent cold-user study remain uncompleted; automated and emulated Android-width evidence exists.
3. Repository-wide Ruff is not green because frozen historical benchmark scripts retain 155 disclosed findings.
4. The reference Domain Pack is a bounded planning pack, not an authoritative benefits/eligibility engine.
5. External operational actions and autonomous Probe execution are disabled.
6. The hosted candidate is an anonymous-session prototype, not a production identity or case-management system.
7. The final presentation's title, duration, and reachability were verified, but its complete visual coverage of application action and Google Cloud evidence was not independently re-adjudicated during this documentation-only review.

## Submission blockers

No engineering blocker remains for packaging. The remaining Human Gates are to confirm the final video's rendered Devpost playback and required visual content, complete entrant/legal/IP attestations, and perform the irreversible Devpost submission before the official deadline.
