# Military SLICES — Static Front Door + Lens Cloud Evidence

## Verdict

**PASS for automated and hosted candidate gates.** Human-only physical Android,
native-picker, unbriefed-adult comprehension, founder acceptance, and production
cutover gates remain open.

## Release state

- Production: `military-slices-00001-niw` — 100% traffic, unchanged.
- Candidate: `military-slices-00026-cub` — 0% traffic.
- Candidate URLs:
  - <https://static-frontdoor-rc---military-slices-ztvqlzospa-uw.a.run.app/>
  - <https://frontend-rc---military-slices-ztvqlzospa-uw.a.run.app/>
- Source commits: `74fcf61`, `a723406`.
- Container image: `sha256:ebd5e66d3802d192a118ee2bbd707c8adadf55234b4c6e8352e72e71e186580b`.
- Runtime: `google-adk` with `gemini-3.7-flash`; Firestore persistence; production configuration and service account preserved.

## What shipped

- An immediate static, photo-led front door appears before the restore request
  completes. It offers three human choices: document, image/screenshot, or an
  unpolished thought.
- Entry-method selection is local UI state. It performs no orientation call,
  model call, governed write, Anchor change, or gate transition.
- The existing reviewed-input and artifact trust boundaries remain the first
  backend interactions after deliberate content submission.
- A deterministic, state-aware cloud of 6–10 accessible topic buttons sits
  below `What matters now`. Fresh state receives eight bounded starter topics.
- Topic opening and dismissal are read-only DOM operations. Updating is a
  separate explicit action, and COMPLETE/PARALYZED states do not receive a new
  update action.
- A grounded spouse PCS date is retained as `pcs_relocation_date`. It never
  becomes the spouse planner's service-member separation date and creates no TAP
  or self-separation gate.

## Screenshots

- [Fresh mobile](../output/screenshots/fresh-mobile.jpg)
- [Active-plan mobile](../output/screenshots/active-plan-mobile.jpg)
- [Lens preview mobile](../output/screenshots/lens-preview-mobile.jpg)
- [Fresh desktop](../output/screenshots/fresh-desktop.jpg)

Screenshot SHA-256 values:

| Capture | SHA-256 |
|---|---|
| Fresh mobile | `A0D4B31B133E16D2073BF5C6CA4D8C39DAC16677D7027F020D05325AB850E8B8` |
| Active-plan mobile | `FA21A422D2076C88F15BFF87786F1D6039EBF70E5158C7CF1C14A937266B9D5E` |
| Lens preview mobile | `DD047C2F48A97595FD6944C0B164C98222C436407C079CA97BD03DF1F745BD0A` |
| Fresh desktop | `8C152A1AC4067EBC585C474301A9E421C72535A70E94357BDB3FD822060AE330` |

## Automated validation

- `150` tests passed.
- Ruff passed for application and test code.
- MyPy passed for all 11 application modules.
- Bandit passed.
- JavaScript syntax and Git diff validation passed.
- Dependency audit found no known third-party vulnerabilities; the local
  `military-slices` package is not published to PyPI and was skipped.
- The complete existing History, What-If, inline-feedback, résumé routing,
  artifact security, concurrency/idempotency, multi-user isolation, COMPLETE,
  PARALYZED, and spouse/PCS suites remain green.

Key new regressions prove:

- the static front door and entry-choice functions contain no API call;
- the file choices retain TXT/PDF/DOCX and PNG/JPG/JPEG contracts;
- the three optimized WebP assets are each below 50 KB;
- cloud construction is deterministic, capped at 10, and contains no model or
  API call;
- preview/render paths contain no API call;
- server Lens projections leave state version, telemetry, active gate, and
  active tasks unchanged, with `model_calls == 0`;
- a spouse PCS date remains relocation context and never separation timing.

## Hosted and browser evidence

- `/api/health` returned 200 with `google-adk`, `gemini-3.7-flash`, and transition
  pack `2026-08-24-v2-shadow-tested`.
- Hosted `app.js`, `styles.css`, and `index.html` hashes exactly matched tested
  local files:
  - `app.js`: `EF4CBEABC7696D1CDE631449BAEF53F6418546F7C7CF42CD73F320D9CE6775E8`
  - `styles.css`: `73F93D0B00AF2FB0FB90467904CD51C39B7916C12C71A73FDEB7DCCAFDD3B322`
  - `index.html`: `3D4877E178F0A6DF05A849FDC5821FDB3C96FD992D94322C17126D5DE03C70B2`
- Hosted cold-user interactions completed across topic preview/dismissal and
  thought-entry/back navigation without a browser interaction exception or
  error surface. The browser harness did not expose a retained console-log
  transcript; Cloud Run emitted zero warning/error entries for `00026-cub`.
- Responsive measurements:

| Viewport | Document width | Minimum visible target | Horizontal overflow |
|---:|---:|---:|---:|
| 320 px | 305 px | 44 px | No |
| 375 px | 360 px | 44 px | No |
| 414 px | 399 px | 44 px | No |
| 1440 px | desktop layout | 48 px primary actions | No observed overflow |

- Text inputs remain at least 16 px on phone breakpoints; reduced-motion and
  non-hover paths remain present. All three desktop entry actions fit within a
  1440×900 viewport after correcting intrinsic image height.

## Defects found and closed during cold review

1. Topic chips had an explicit list-item role that erased native button
   semantics. The override was removed; role queries, keyboard interaction, and
   screen-reader button semantics now agree.
2. The hidden file control remained in the accessibility tree as an unnamed
   control. It is now hidden from layout, focus order, and accessibility while
   visible buttons still invoke the native picker.
3. Intrinsic 640 px image height pushed desktop actions below a normal laptop
   viewport. Responsive height/aspect constraints now keep all three actions in
   view.
4. PCS preview copy lowercased the acronym. The deterministic copy now preserves
   `PCS` and has a regression.

## Visual asset provenance

Assets were generated with the built-in OpenAI image generation tool and then
locally resized/encoded as WebP. They carry no third-party stock-photo license.

1. `static/images/start-document.webp`
   - source: `C:/Users/kevin/.codex/generated_images/01a00e50-fa5e-7241-ae9d-c8adae055064/exec-c0fe486f-a2ee-40cb-b4ff-1cf1935d9226.png`
   - prompt intent: photorealistic Black woman reviewing transition documents at
     a kitchen table; natural light; no uniforms, weapons, logos, or text.
2. `static/images/start-image.webp`
   - source: `C:/Users/kevin/.codex/generated_images/01a00e50-fa5e-7241-ae9d-c8adae055064/exec-71ba5902-6462-42cf-b93a-87dbaef67e7b.png`
   - prompt intent: photorealistic Asian man comparing a phone screenshot with a
     laptop; natural home-office setting; no uniforms, logos, or text.
3. `static/images/start-thought.webp`
   - source: `C:/Users/kevin/.codex/generated_images/01a00e50-fa5e-7241-ae9d-c8adae055064/exec-272fbec4-e40c-4884-b2c1-4e26174cfbdb.png`
   - prompt intent: photorealistic military-connected couple discussing a move
     and career choice at home; natural and non-cheesy; no uniforms, logos, or
     text.

## Files changed

- `military_slices/models.py`
- `military_slices/engine.py`
- `static/index.html`
- `static/app.js`
- `static/styles.css`
- `static/images/start-document.webp`
- `static/images/start-image.webp`
- `static/images/start-thought.webp`
- `tests/test_control_layer.py`
- `tests/test_path_runtime.py`
- `tests/test_static_contract.py`
- `output/screenshots/*.jpg`
- this evidence document

## Frozen scope and remaining gates

No generalized event model, datastore migration, HELM semantic redesign,
History/What-If change, anonymous enablement, production promotion, or Devpost
submission occurred. The narrow `pcs_relocation_date` distinction is the only
permitted backend addition.

Still human-only:

1. Physical Android layout, soft keyboard, and native picker.
2. True unbriefed-adult comprehension and founder acceptance.
3. Real second-account/device isolation confirmation.
4. Production/canonical-domain cutover.
5. Final public repository review, demo recording, attestations, and Devpost submission.
