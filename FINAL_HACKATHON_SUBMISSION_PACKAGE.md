# Final Hackathon Submission Package

Status: **READY FOR HUMAN SUBMISSION GATE**  
Prepared: **2026-08-29**  
Category: **Collaborative Partner**  
Official deadline: **August 31, 2026 at 5:00 PM Pacific Time**  
Rules: <https://allthingsagentichackathon.devpost.com/rules>

This file is the submission source of truth. It packages and proves the existing Military SLICES candidate. It does not authorize or perform the final Devpost submission.

## 1. Final project summary

Military SLICES is a governed transition-planning partner for service members, veterans, and military families. It turns ordinary language, documents, and screenshots into one durable plan connecting career, education, location, family constraints, timing, decisions, experiments, and findings.

The interface does not ask the veteran to fill out the whole transition plan at once. It foregrounds what matters now, bundles questions that belong together, converts uncertainty into small real-world tests, and reconnects later evidence to the decisions it can affect. The veteran can review, revise, print, and export the complete accumulated plan in ordinary language.

Hosted candidate: <https://hackathon-rc---military-slices-ztvqlzospa-uw.a.run.app/>

## 2. Final HELM explanation

HELM is the governance layer beneath Military SLICES. It separates responsibilities that a normal assistant often blends:

- **Human intent** establishes the objective.
- **Slices** expose bounded views—Career, Education, Location, and Your Story—over one shared plan.
- The **Military Transition Domain Pack** provides the versioned path and permitted evidence surfaces for this domain.
- A **Gate** identifies the current unresolved decision.
- A **Resolver** may propose from deterministic logic or a bounded Google ADK/Gemini run.
- The **Authority Governor** checks scope, evidence, authority, and source-state version before a governed write.
- **Canonical state** preserves the durable plan, history, provenance, and current path in Firestore.

The model proposes; it does not authorize itself. Observation does not silently become plan truth. History remains read-only. What-If branches remain signed and non-canonical until the human explicitly promotes one. External operational effects and autonomous HELM Probe execution are disabled in this prototype.

The relationship is:

```text
human input
  → reviewable orientation
  → governed evidence
  → bounded Slice + Gate
  → Resolver proposal
  → Authority Governor validation
  → versioned plan state
  → next human decision, real-world action, or re-entry prompt
```

Architecture: [docs/architecture.svg](docs/architecture.svg)  
Presentation PNG: [docs/screenshots/08-helm-architecture.png](docs/screenshots/08-helm-architecture.png)

## 3. Devpost copy

### Project title

Military SLICES

### Tagline

One governed transition plan that remembers, adapts, and asks only when the human is needed.

### Inspiration / problem

Leaving military service creates a web of connected decisions: work, education, location, family needs, timing, and the story a person tells about their experience. Those decisions rarely arrive in a clean order. A new deadline can change an education plan. A spouse's school can constrain location. A real conversation with someone in the field can reverse a career direction.

Most planning tools respond with a large checklist or a stateless conversation. The first overwhelms the person; the second forgets why earlier choices mattered. We wanted a system that could keep the whole transition coherent while asking the veteran to focus on only the decision or action that matters now.

### What it does

Military SLICES turns ordinary language, documents, and screenshots into one durable transition plan. It first shows the user what it heard and saves nothing until the user approves it. It then connects Career, Education, Location, and Your Story through a shared governed state.

The interface foregrounds one bounded decision, but it does not force related questions across multiple screens. When the required questions belong together, the user answers them together. The system can propose career directions, help define a real-world test, remember what the veteran decided, and reconnect a later test result to the right direction. If reality changes, the affected part of the plan can reopen without erasing its history.

At any point the veteran can view the accumulated transition plan: objective, working direction, strengths, priorities, decisions, experiments, findings, unresolved questions, next actions, and dated milestones. The plan can be printed or exported as a standalone human-readable document.

### How it works

Military SLICES is powered by HELM, a governance layer that separates intent, evidence, reasoning, authority, and persistence. After reviewable orientation, HELM's installed Domain Pack supplies the versioned transition path. A Gate identifies the current bounded decision. A Resolver may use deterministic logic or Google ADK with Gemini 3.7 Flash to propose structured options from a purpose-limited projection. The Authority Governor validates scope, evidence, state version, and authority before Firestore records the governed change. The model cannot authorize its own proposal, close a human-only decision, or write directly to the plan.

### How we built it

- FastAPI and Pydantic for the application and typed contracts
- Google Agent Development Kit for the bounded agent runtime and structured tools
- Gemini 3.7 Flash through Vertex AI for bounded career proposals and language bridges
- Firestore for versioned canonical state, prior-version history, optimistic concurrency, and idempotency
- Cloud Run for the public containerized candidate
- HTML, CSS, and JavaScript for the responsive product, review, history, What-If, plan, and export surfaces
- PyPDF, PDFium, python-docx, and Pillow for supported ephemeral file extraction
- Deterministic transition windows, dependency revalidation, evidence filtering, and fail-safe fallback

### Technologies used

Gemini 3.7 Flash, Vertex AI, Google Agent Development Kit, Cloud Run, Firestore, FastAPI, Pydantic, Python, HTML, CSS, JavaScript, PyPDF, PDFium, python-docx, Pillow, Docker, Pytest, Ruff, Mypy, Bandit, and pip-audit.

### Challenges

The hard problem was not generating more advice. It was controlling what could become plan truth while keeping the experience useful. We had to separate model proposals from authorization, preserve unknown and conflicting information, prevent a file from inventing the user's objective, and keep state changes bound to the exact version the user reviewed.

The human experience was equally difficult. A technically correct workflow still failed when it asked one known question at a time, showed a “caught up” state while a real-world action remained, or displayed internal governance language. We repeatedly drove complete synthetic journeys and changed the projection—not the governance architecture—until the veteran could always see what to do, why it mattered, what changed, and what to report later.

### Accomplishments

- Built and deployed a complete transition-planning application rather than a chat-only demo.
- Preserved explicit human review before typed input changes the plan.
- Bound Gemini/ADK reasoning to a minimum-sufficient evidence surface and strict output schema.
- Enforced a separate Authority Governor before governed mutation.
- Supported persistent re-entry, history, signed What-If branches, changed-reality handling, and reversible direction choices.
- Produced a readable, dated transition plan that can be exported and understood without the application.
- Completed a clean synthetic end-to-end demo with no personal data or developer surfaces.
- Passed the final 335-test product suite, product/test Ruff, strict Mypy, Bandit, JavaScript syntax, and dependency auditing.

### What we learned

Attention is a scarce transition resource. “Ask one thing at a time” becomes frustrating when the system already knows three questions belong together. The better principle is to minimize human turns without reducing human control.

Persistence alone is not memory. Useful memory requires consequence: the system must know which earlier decision a new fact can change, which information should remain in the background, and when a real-world action—not another form—is the right next step.

Governance can be visible through behavior without exposing architecture jargon. Review-before-write, bounded evidence, reversible choices, and clear causal feedback let the user feel the control model without learning its internal names.

### What is next

The next step is product validation: physical-device testing, independent cold-user evaluation, additional accessibility review, and carefully governed expansion of the Military Transition Domain Pack. Any authoritative benefits or eligibility logic would require separately sourced, versioned, and approved domain rules; the current prototype does not claim that authority.

### Disclosure

Military SLICES was created in a new repository during the competition period. Pre-existing HELM methodology and prior product lessons informed the design, but no prior Veteran Slice application code, schemas, routes, deployment, or data were reused. OpenAI Codex assisted with implementation, testing, documentation, and release verification. The demo uses synthetic transition data.

## 4. Technology-use ledger

| Technology | Actual use | Evidence | Status |
|---|---|---|---|
| Gemini 3.7 Flash | Typed, bounded career hypotheses and language bridges | `military_slices/agent_runtime.py` | Implemented/deployed configuration |
| Vertex AI | Provider route for Gemini and deployed image extraction | `.env.example`, `agent_runtime.py`, `artifacts.py` | Implemented |
| Google ADK | Agent, Runner, RunConfig, structured output, tools, and call limits | `agent_runtime.py:413-667` | Implemented |
| Cloud Run | Public containerized HTTPS candidate | `Dockerfile`, hosted release report, live URL | Implemented/deployed candidate |
| Firestore | Canonical session plan, versions, optimistic transactions | `military_slices/store.py:85-153` | Implemented/deployed configuration |
| FastAPI + Pydantic | API/web boundary and strict contracts | `app.py`, `models.py`, `plan.py` | Implemented |
| HTML/CSS/JavaScript | Responsive input, review, command post, plan, history, What-If, export | `static/` | Implemented |
| PyPDF/PDFium/python-docx/Pillow | Supported ephemeral document/image extraction | `artifacts.py`, `pyproject.toml` | Implemented |
| O*NET + BLS OOH | Public occupational exploration references | `agent_runtime.py:76-117` | Implemented data sources |
| Docker | Non-root Cloud Run image | `Dockerfile` | Implemented |
| Pytest/Ruff/Mypy/Bandit/pip-audit | Regression, lint, type, static security, dependency checks | `tests/`, `pyproject.toml`, validation report | Validation only |
| HELM Probe | Secondary discovery boundary | Architecture and capability guards | Autonomous execution disabled |
| External actions | Job applications/messages/filings | Capability guards and negative tests | Disabled |

Full ledger: [docs/TECHNOLOGY_USE_LEDGER.md](docs/TECHNOLOGY_USE_LEDGER.md)

## 5. Claim-to-evidence matrix

| Claim | Strongest evidence | Demo/screenshot |
|---|---|---|
| Starts from words, documents, or screenshots | `static/index.html`, `static/app.js`, `app.py` | `01-front-door.png`; 00:31.651 |
| Human review precedes a write | orientation/confirm routes and governance tests | `02-human-review.png`; 00:35.389–00:37.861 |
| Slices share one bounded plan | `models.py`, `slices.py`, `plan.py` | Architecture diagram and complete plan |
| Gemini sees a minimum-sufficient surface | `agent_runtime.py:_minimal_context`, `temporal.py` | Architecture diagram |
| ADK is in the running agent path | `Agent`, `Runner`, `RunConfig` in `agent_runtime.py` | Technology ledger |
| Resolver cannot authorize persistence | `governance.py:AuthorityGovernor`, `app.py` | Architecture diagram |
| Known related questions are bundled | `acquisition.py`, `static/app.js` | `04-bundled-decisions.png`; 00:45.246 |
| Career directions are testable alternatives | `engine.py`, `agent_runtime.py`, `plan.py` | `03-direction-choice.png`; 00:42.767 |
| A direction becomes a real-world action | direction/test flow in `app.py` and `plan.py` | `05-real-world-test.png`; 00:49.526 |
| Returned evidence changes the plan | governed test-result path | `06-plan-updated-from-evidence.png`; 00:52.143–00:58.924 |
| State persists with history | `store.py`, history routes | persistence/history tests |
| What-If does not silently mutate truth | `control.py`, `security.py`, promotion route | What-If tests |
| Complete plan can be exported | `plan.py`, `/api/plan/export` | `07-complete-plan-and-export.png`; 01:15.282–01:21.799 |
| Public candidate is testable anonymously | live candidate | Fresh 2026-08-29 smoke check |
| Final product suite passes | final validation report | 335/335 tests plus static checks |

Full matrix: [docs/JUDGING_EVIDENCE_MATRIX.md](docs/JUDGING_EVIDENCE_MATRIX.md)

## 6. Screenshot inventory

All product frames were extracted from the SHA-256-verified clean take at 2560×1440. No personal data or developer surfaces are present.

| # | File | Purpose | Demo time | SHA-256 |
|---:|---|---|---:|---|
| 1 | [Front door](docs/screenshots/01-front-door.png) | Three low-friction entry paths and review promise | 00:31.9 | `6947a17919bfa7b70a46d18e5ad370fa089a032411bd16692fabf600326b695b` |
| 2 | [Human review](docs/screenshots/02-human-review.png) | Extracted statements remain correctable before plan write | 00:35.7 | `9d685d99988083ec95d81aff81132716ecbd13cfb164a6b5dcb87c7cddc87cc5` |
| 3 | [Direction choice](docs/screenshots/03-direction-choice.png) | Bounded alternatives, command post, and preserved choice | 00:43.1 | `9ea3942b949d252ad42a53d132170f6fec23e6769c71e12b8d91105dca455dad` |
| 4 | [Bundled decisions](docs/screenshots/04-bundled-decisions.png) | Related known questions answered together | 00:45.5 | `c4ee038527ba9f921b22e09e9bc2f5acb45862993d46f022ffd7eec6bfed685d` |
| 5 | [Real-world test](docs/screenshots/05-real-world-test.png) | Working direction, evidence, next action, and return path | 00:49.8 | `73bbafafac373cf9f04e10c7836cd112c99feedab274fb8061057eb4b82cfadb` |
| 6 | [Evidence changes plan](docs/screenshots/06-plan-updated-from-evidence.png) | Reported result recorded and the next consequential question recomputed | 00:56.8 | `86ca4fe6913e156c2ab2bea19a4c3c9737af6112e4033d50a6c37318adfa9f30` |
| 7 | [Complete plan and export](docs/screenshots/07-complete-plan-and-export.png) | Durable objective, direction, evidence, dates, and export controls | 01:15.6 | `dbba3680bc18545384d9dda0e28a2dfc546a048406f7ebb1148429d2b9b3f525` |
| 8 | [HELM architecture](docs/screenshots/08-helm-architecture.png) | Judge-readable authority and data flow | n/a | `def8d122cd1b751bff52e70b407a7597c3e4c56a5e2fe76793e725354a16fc80` |

## 7. Demo evidence and exact timestamp ledger

- Clean take SHA-256: `6c8c0bd12b2b58fca4267407928b9f2b037c8c93175f704093f6ac3fb00c9cc0`
- Bytes: `4,172,987`
- Recorder duration: `89.6426s`; container duration: `88.8s`
- Format: H.264 High, 2560×1440, 15 fps, 1,332 frames
- Capture failures: `0`
- Final edit applied: `false`
- Ledger SHA-256: `f84f1549a8459584fa2b394385279fcc9c755d1514635d0437c4db10d97cb42f`
- Export SHA-256: `65147eaa8350bba130315db7f667be923fe109b35644af3791f34bed514c6fd9`

| Event | Relative time |
|---|---:|
| Landing visible | 00:27.565 |
| Starting vector complete | 00:29.570 |
| Front door visible | 00:31.651 |
| Initial objective entered | 00:33.173 |
| First governed review visible | 00:35.389 |
| Approved objective saved | 00:37.861 |
| Direction answer entered | 00:39.676 |
| Direction review visible | 00:41.089 |
| Directions visible | 00:42.767 |
| Bundled questions visible | 00:45.246 |
| Bundled answers entered | 00:46.854 |
| Real-world experiment visible | 00:49.526 |
| Test result entered | 00:52.143 |
| Test-result review visible | 00:54.154 |
| Updated consequence visible | 00:56.426 |
| Post-result choice visible | 00:58.924 |
| Next experiment entered | 01:00.942 |
| Next-experiment review visible | 01:02.750 |
| Plan opened for timeline | 01:06.178 |
| Timeline entered | 01:08.391 |
| Timeline review visible | 01:10.796 |
| Complete plan visible | 01:15.282 |
| Export activated | 01:18.790 |
| Export complete | 01:21.799 |

## 8. Repository and readiness status

- Judge-facing README: complete.
- Judge-readable architecture SVG and PNG: complete and visually verified.
- Devpost copy: complete.
- Technology ledger: complete.
- Claim-to-evidence matrix: complete.
- Eight-image screenshot pack: complete.
- Local setup/run/test commands: checked against current implementation.
- Environment example: sanitized to use placeholders.
- Private developer-local paths: removed from tracked evidence.
- Secrets/API key/private-key scan: no matching committed credentials found.
- Local caches, browser profiles, failed takes, private transport artifacts, and large MP4 files: excluded from version control.
- Historical frozen benchmark evidence: preserved and kept outside the judge's primary reading path.

## 9. Test and deployment status

| Validation | Result |
|---|---|
| Pytest | **PASS — 335/335 tests** |
| Ruff, production package + tests | **PASS** |
| Strict Mypy | **PASS — 18 source files** |
| Bandit | **PASS** |
| pip-audit | **PASS — no known vulnerabilities; local project skipped as non-PyPI** |
| Browser JavaScript syntax | **PASS** |
| Architecture XML/render QA | **PASS** |
| README image references | **PASS** |
| Public candidate smoke check | **PASS — rendered anonymously; zero console warnings/errors** |

Repository-wide `ruff check .` is **not green**: 155 disclosed findings remain in historical benchmark/generator scripts. Product code and tests are clean. See [the full validation report](docs/FINAL_VALIDATION_REPORT_2026-08-29.md).

Deployment evidence identifies tagged Cloud Run candidate revision `military-slices-00050-cad` in `us-west1`. The public URL was live-checked on 2026-08-29. Production traffic was not moved during submission packaging.

## 10. Known limitations

- Reference-domain prototype; not an authoritative benefits, legal, medical, financial, clearance, or eligibility engine.
- Occupational suggestions are hypotheses for exploration, not qualification or hiring predictions.
- Anonymous browser sessions are not a production identity system.
- Physical Android hardware and independent cold-user evaluation remain open.
- Provider failure safely falls back, but fallback suggestions are intentionally generic outside recognized evidence families.
- Autonomous HELM Probe and external operational effects are disabled.
- Historical benchmark scripts retain disclosed lint debt.
- The large clean demo MP4 is local and hash-verified but still needs public upload.

## 11. Final submission checklist

### Complete

- [x] Existing product packaged without architecture or behavior changes
- [x] Judge-facing README
- [x] Architecture SVG and presentation PNG
- [x] Devpost field copy
- [x] Technology-use ledger
- [x] Claim-to-evidence matrix
- [x] Eight-image screenshot pack
- [x] Full validation report
- [x] Public candidate live smoke check
- [x] Clean demo integrity and timestamp ledger
- [x] Repository credential/private-path cleanup
- [x] Synthetic demo content confirmed

### Human Gate — required before submission

- [ ] Confirm entrant eligibility, conflicts, team roster, ownership, and third-party rights attestations
- [ ] Verify `https://github.com/kevinfagundes85-art/military-slices` is publicly reachable, or grant `testing@devpost.com` and `cloudhackathons@google.com` access if private
- [x] Repository URL is present in the Devpost copy
- [ ] Upload the verified clean take to public YouTube or Vimeo
- [ ] Add the demo URL to the Devpost copy
- [ ] Select **Collaborative Partner**
- [ ] Verify the hosted candidate URL in the final form
- [ ] Review all pasted text and screenshots
- [ ] Submit before **August 31, 2026 at 5:00 PM PT**
- [ ] Perform the irreversible Devpost submission

## 12. Final gate

**READY FOR HUMAN SUBMISSION GATE**

No final submission, repository publication, video upload, permission change, production deployment, or traffic movement was performed by this packaging pass.
