# Military SLICES Judge Demo Timing — 2026-08-28

## 1. Application identity

- Source commit: `93ff30337e88799b2bc6010a24b7b688dd023d79`
- Product code was not changed during this calibration.
- Exact inputs: `MILITARY_SLICES_JUDGE_DEMO_INPUTS_2026-08-28.md`
- Recording method: full-monitor H.264 capture, 2560×1440, 15 fps, no edits.

## 2. Frozen persona and inputs

The synthetic participant is a 23-year-old active-duty Navy veteran leaving on May 15, 2027. He led a five-person logistics team, must remain near Tacoma while his wife attends nursing school, prefers steady meaningful work with some remote flexibility, and is exploring veteran-focused technology. The frozen journey selects Logistics Analyst, creates and completes one work-sample test, plans a second job-posting test, adds seven dated milestones, reviews the accumulated plan, and exports it.

## 3. Take A — natural-use duration

- Raw capture duration: `164.00 s` (`02:44.00` media duration).
- Product journey, landing to export completion: `135.940 s`.
- Capture pre/post roll accounts for the difference.

### Take A event ledger (relative to product landing)

| Event | Time |
|---|---:|
| Landing visible | 00:00.000 |
| Starting vector complete | 00:06.973 |
| Initial objective entered | 00:07.972 |
| First governed response visible | 00:11.574 |
| Approved objective saved | 00:25.339 |
| Directions visible | 00:27.929 |
| Direction selected / bundled questions visible | 00:31.317 |
| Bundled answers entered | 00:45.601 |
| Bundled answers submitted | 00:47.380 |
| Decision receipt and real-world experiment visible | 00:47.380 |
| Experiment selected / action state visible | 00:56.869 |
| Re-entry initiated | 00:59.374 |
| Evidence review visible | 01:18.896 |
| New evidence submitted / consequence visible | 01:22.501 |
| Next experiment selected | 01:47.091 |
| Plan opened for timeline update | 01:48.385 |
| Complete plan visible | 02:11.332 |
| Export activated | 02:14.126 |
| Export complete | 02:15.940 |

### Take A observed latency

| Wait | Duration |
|---|---:|
| Initial orientation transition | 1.591 s |
| Initial governed confirmation | 1.592 s |
| Bundled-decision processing | 1.514 s |
| Evidence review plus acceptance cluster | 5.009 s |

No provider wait was individually disqualifying. The natural take's largest intervals were human reading/typing/tool-orchestration time: objective review (~13.8 s), bundled-answer entry (~14.3 s), deciding the next experiment (~24.6 s), and timeline/plan inspection (~22.9 s).

## 4. Take A confusion and UX observations

- The original calibration script expected a redundant “Find civilian work” objective choice. The product correctly treated the approved opening statement as the human objective and skipped that screen. Inputs were corrected before the scored take.
- The bounded sequence is understandable once underway: context → timing → direction → bundled test plan → field action → evidence → next test → complete plan.
- The transition from a saved experiment to “Add a test result” is a strong continuity moment and should remain in the final demo.
- The complete plan is the strongest product payoff; it contains the objective, direction, alternatives, strengths, decisions, active test, learned result, unresolved items, next action, and dates.

## 5. Take B — optimized-use duration

- Raw capture duration: `113.60 s` (`01:53.60` media duration).
- Optimized product journey, landing to export completion: `81.949 s`.
- This clears the candidate `100 s` product budget by `18.051 s`.

### Take B event ledger (relative to product landing)

| Event | Time |
|---|---:|
| Landing visible | 00:00.000 |
| Initial objective entered | 00:02.414 |
| First governed response visible | 00:04.007 |
| Directions visible | 00:20.441 |
| Direction selected / bundled questions visible | 00:21.385 |
| Bundled answers entered | 00:21.493 |
| Bundled answers submitted | 00:23.251 |
| Decision receipt / experiment selected / action state visible | 00:23.251 |
| Re-entry initiated | 00:38.000 |
| New evidence submitted / consequence visible | 00:41.175 |
| Next experiment selected | 00:43.425 |
| Complete plan visible | 01:20.049 |
| Export activated | 01:21.241 |
| Export complete | 01:21.949 |

### Take B observed latency

| Wait | Duration |
|---|---:|
| Initial orientation | 0.991 s |
| Bundled-decision processing | 1.097 s |
| Evidence processing | 1.793 s |

Prepared text and deliberate direct clicks remove roughly `53.991 s` from the product journey versus Take A (`39.7%`). The optimized flow does not skip a governed decision or use backend state manipulation.

## 6. Take C — full timing rehearsal

- Final raw media duration: `220.00 s` (`03:40.00`).
- Recorder wall-clock duration: `222.163 s`; encoded frames: `3300`; capture failures: `0`.
- The target duration was achieved exactly at the media level.
- Two overlength rehearsals and one capture-failure rehearsal were preserved rather than overwritten.

## 7. Raw-recording visual QA — release blocker

The raw screen recordings are **not valid release footage** even though the browser event timing is valid:

- Take A sampled at 01:10 shows the Windows lock screen, not the product.
- Take B sampled at 00:55 shows the Windows lock screen, not the product.
- Take C sampled at 00:50 and 03:20 shows an unfocused/wrong browser instance (including the Codex work surface and an older local product tab), not the browser tab being driven for the final rehearsal.

Verification frames:

- `benchmark/output/take_a_verify.png`
- `benchmark/output/take_b_verify.png`
- `benchmark/output/take_c_product_verify.png`
- `benchmark/output/take_c_close_verify.png`

This is a capture/focus defect, not a Military SLICES behavior defect. No final demo should be assembled from these files. A new recording pass must first prove that the recorder sees the controlled foreground browser at three checkpoints.

## 8. Preliminary narrative timing

| Section | Target |
|---|---:|
| Human problem / hook | 0:00–0:18 |
| Founder context | 0:18–0:42 |
| Product reveal | 0:42–0:50 |
| Real product journey | 0:50–2:30 |
| Complete plan and export | 2:30–2:50 |
| HELM explanation | 2:50–3:20 |
| Closing identity and value | 3:20–3:40 |

The optimized product journey requires only 1:21.949, leaving about 18 seconds inside the 1:40 product allocation for readable holds and transition margin.

## 9. Longest sections and margin

- Natural product journey: 2:15.940.
- Optimized product journey: 1:21.949.
- Final presentation budget: 3:40.000.
- Product allocation: 1:40.000.
- Product margin: 18.051 seconds.
- Presentation-level margin to a 3:45 ceiling: 5.000 seconds.
- The evidence-review cluster is the only notable system wait and remains approximately five seconds in the natural pass.

## 10. Recommended recording strategy

**Recommended: hybrid narration plus prerecorded real product footage.**

Use a clean, continuous real product capture for the 1:22 optimized journey, with narration and minimal title/identity frames around it. This protects the judge flow from provider/network variance while preserving an honest rendered-product demonstration. Do not use an edited simulation, backend mutation, or screenshots standing in for interaction.

This recommendation is contingent on repairing the screen-capture focus problem and recording a valid foreground-browser take.

## 11. Exact candidate shot sequence

1. 0:00–0:18 — problem: transition decisions change together across work, family, place, dates, and identity.
2. 0:18–0:42 — founder context: why an ordinary checklist is insufficient.
3. 0:42–0:50 — Military SLICES reveal.
4. 0:50–1:02 — veteran context and governed review.
5. 1:02–1:14 — exact separation date and Logistics Analyst direction.
6. 1:14–1:26 — bundled questions answered once; no step-selling.
7. 1:26–1:38 — test plan saved; veteran leaves with a real-world action.
8. 1:38–1:52 — veteran returns with evidence; evidence is reviewed before use.
9. 1:52–2:05 — result changes the next test without erasing history.
10. 2:05–2:30 — add dates and open the accumulated transition plan.
11. 2:30–2:50 — show chronological timeline and activate Export my plan.
12. 2:50–3:20 — explain HELM as bounded attention, governed state, and continuity—not unrestricted chat memory.
13. 3:20–3:40 — close on the durable veteran-owned plan and the next real-world action.

## 12. Capture artifacts and SHA-256

Primary attempts:

| Artifact | Bytes | SHA-256 | Status |
|---|---:|---|---|
| `MILITARY_SLICES_JUDGE_DEMO_TAKE_A_2026-08-28.mp4` | 5,335,844 | `a0080da291b4b45be891982a7b916416e79b1eedb4835f42702a14df1cd11904` | Timing valid; visual capture invalid |
| `MILITARY_SLICES_JUDGE_DEMO_TAKE_B_2026-08-28.mp4` | 3,711,438 | `1cc29aa894f7126b8632357f4634555b6de56015acfce6a41dc7d662ec89027a` | Timing valid; visual capture invalid |
| `MILITARY_SLICES_JUDGE_DEMO_TAKE_C_2026-08-28.mp4` | 9,262,677 | `8e69a351612022373c1882e1abde4ea870f5bb37566271890ea37303aa334a96` | 3:40 timing valid; visual capture invalid |

Preserved failed calibration/rehearsal artifacts:

| Artifact | SHA-256 | Reason retained |
|---|---|---|
| `MILITARY_SLICES_JUDGE_DEMO_CALIBRATION_INVALID_2026-08-28.mp4` | `943b57f9d537b8b594ff46a62ceffac1f5e4212ab8276561b9db8aae8df5716b` | Stale expected direction in calibration |
| `MILITARY_SLICES_JUDGE_DEMO_TAKE_C_CAPTURE_FAILURE_2026-08-28.mp4` | `b8ca573e6f28dad09d9daf899c93288c0099f54da870606e3e7d4e9db630ce6a` | Windows BitBlt failure; partial but finalized |
| `MILITARY_SLICES_JUDGE_DEMO_TAKE_C_OVERLENGTH_2026-08-28.mp4` | `5592a4c059cd469e15b5da7f4ec2c62a68b2fb6076e54a5e46d283f770d2d108` | 4:17 overlength rehearsal |
| `MILITARY_SLICES_JUDGE_DEMO_TAKE_C_OVERLENGTH_2_2026-08-28.mp4` | `ada67ebbddd2fa69994be7f0e4b6b8ec948d033da675c1fc70effaade66a4d51` | 4:18 overlength due control scheduling |

## 13. Demo risks

- **Blocking:** current recorder does not reliably capture the controlled in-app browser tab.
- Provider/evidence review can visibly take about five seconds; narrate the governance boundary during this wait rather than treating it as dead air.
- Browser download completion needs a visible confirmation or download affordance in the final foreground capture.
- The complete-plan modal is information-dense; final capture should enter at the top, then show timeline/export deliberately rather than scroll erratically.
- The exact product-reveal and HELM-reveal graphics remain narrative placeholders; no final video was produced under this order.

## 14. Next human decision

Authorize only a **capture-environment repair and one clean recording pass** (foreground the controlled browser, disable lock/sleep, verify three live preview checkpoints). Do not authorize product redesign on the basis of this recording failure.

After a visually valid raw take exists, use the hybrid strategy and the shot sequence above for final production. Final video, narration, and submission remain behind their separate Human Gates.

## 15. Disposition

**TIMING CALIBRATION COMPLETE; RAW FOOTAGE NOT RELEASE-USABLE.**

The product fits the demonstration budget: the optimized journey is 1:21.949 and the full rehearsal envelope is exactly 3:40. The recording channel failed visual fidelity, so these files are evidence of timing only and must not be represented as release footage.
