# Devpost Submission Copy

Paste the narrative sections in their displayed order. The URL block below is a reference for Devpost's separate project, repository, and video fields; copy those three values exactly.

## Submission URLs

- Hosted project: https://hackathon-rc---military-slices-ztvqlzospa-uw.a.run.app/
- Source repository: https://github.com/kevinfagundes85-art/military-slices
- Demo video: https://youtu.be/cpM1sqzRtEU

## Project title

Military SLICES

## Tagline

One governed transition plan that remembers, adapts, and asks only when the human is needed.

## Category

Collaborative Partner

## Inspiration / problem

Leaving military service creates a web of connected decisions: work, education, location, family needs, timing, and the story a person tells about their experience. Those decisions rarely arrive in a clean order. A new deadline can change an education plan. A spouse's school can constrain location. A real conversation with someone in the field can reverse a career direction.

Most planning tools respond with a large checklist or a stateless conversation. The first overwhelms the person; the second forgets why earlier choices mattered. We wanted a system that could keep the whole transition coherent while asking the veteran to focus on only the decision or action that matters now.

## What it does

Military SLICES turns ordinary language, documents, and screenshots into one durable transition plan. It first shows the user what it heard and saves nothing until the user approves it. It then connects Career, Education, Location, and Your Story through a shared governed state.

The interface foregrounds one bounded decision, but it does not force related questions across multiple screens. When the required questions belong together, the user answers them together. The system can propose career directions, help define a real-world test, remember what the veteran decided, and reconnect a later test result to the right direction. If reality changes, the affected part of the plan can reopen without erasing its history.

At any point the veteran can view the accumulated transition plan: objective, working direction, strengths, priorities, decisions, experiments, findings, unresolved questions, next actions, and dated milestones. The plan can be printed or exported as a standalone human-readable document.

## How it works

Military SLICES is powered by **HELM—Human Enabled Lifecycle Management**—a governance layer that separates intent, evidence, reasoning, authority, and persistence. HELM governs **how** work may proceed; the installed Domain Pack governs **what** evidence and transition rules apply; Slices govern **where** bounded work occurs over one shared plan.

1. The person supplies ordinary input.
2. A deterministic orientation step extracts only what the person actually provided.
3. The person reviews and corrects it before it becomes plan state.
4. HELM's installed Military Transition Domain Pack supplies the versioned path and permitted evidence surfaces.
5. A Gate identifies the current bounded decision.
6. A Resolver may use deterministic logic or Google ADK with Gemini 3.7 Flash to propose structured options from a purpose-limited projection.
7. The Authority Governor validates scope, evidence, state version, and authority before a governed write.
8. Firestore stores the versioned canonical plan and prior versions.
9. The runtime recomputes the next decision, real-world action, or re-entry prompt.

The model cannot authorize its own proposal, close a human-only decision, or write directly to the plan.

The deployment roles are distinct: **Cloud Run hosts** the FastAPI application, static interface, and HELM runtime. A signed cookie binds the anonymous prototype session to its plan; it is not a production login system. Inside that runtime, **Google ADK orchestrates** bounded Resolver calls and **Gemini 3.7 Flash runs through Vertex AI** to produce typed proposals. HELM validates proposals before **Firestore transactionally stores** the canonical plan and prior versions. Firestore stores state; it does not host the application.

## How we built it

- FastAPI and Pydantic for the application and typed contracts
- Google Agent Development Kit for the bounded agent runtime and structured tool use
- Gemini 3.7 Flash through Vertex AI for bounded career-direction proposals and language bridges
- Firestore for versioned canonical state, prior-version history, optimistic concurrency, and idempotency
- Cloud Run for the public containerized candidate
- HTML, CSS, and JavaScript for the responsive foreground, review, history, What-If, transition-plan, and export surfaces
- PyPDF, PDFium, python-docx, and Pillow for supported ephemeral file extraction
- Deterministic transition windows, dependency revalidation, evidence filtering, and fail-safe fallback

## Technologies used

Gemini 3.7 Flash, Vertex AI, Google Agent Development Kit, Cloud Run, Firestore, FastAPI, Pydantic, Python, HTML, CSS, JavaScript, PyPDF, PDFium, python-docx, Pillow, Docker, Pytest, Ruff, Mypy, Bandit, and pip-audit.

## Challenges

The hard problem was not generating more advice. It was controlling what could become plan truth while keeping the experience useful. We had to separate model proposals from authorization, preserve unknown and conflicting information, prevent a file from inventing the user's objective, and keep state changes bound to the exact version the user reviewed.

The human experience was equally difficult. A technically correct workflow still failed when it asked one known question at a time, showed a “caught up” state while a real-world action remained, or displayed internal governance language. We repeatedly drove complete synthetic journeys and changed the projection—not the governance architecture—until the veteran could always see what to do, why it mattered, what changed, and what to report later.

## Accomplishments

- Built a complete, deployed transition-planning application rather than a chat-only demo.
- Preserved explicit human review before typed input changes the plan.
- Bound Gemini/ADK reasoning to a minimum-sufficient evidence surface and strict structured output.
- Enforced a separate Authority Governor before governed mutation.
- Supported persistent re-entry, history, signed What-If branches, changed-reality handling, and reversible direction choices.
- Turned governed state into a readable, dated transition plan that can be exported and understood without the application.
- Completed a clean synthetic end-to-end product drive with preserved screenshots, export evidence, and no personal data in the demonstrated journey.
- Passed the final 335-test product suite, strict Mypy, product/test Ruff, Bandit, JavaScript syntax, and dependency auditing.

## What we learned

Attention is a scarce transition resource. “Ask one thing at a time” sounds simple, but becomes frustrating when the system already knows three questions belong together. The better principle is to minimize human turns without reducing human control.

We also learned that persistence alone is not memory. Useful memory requires consequence: the system must know which earlier decision a new fact can change, which information should remain in the background, and when a real-world action—not another form—is the right next step.

Finally, governance can be visible through behavior without exposing architecture jargon. Review-before-write, bounded evidence, reversible choices, and clear causal feedback let the user feel the control model without learning its internal names.

## What is next

The next step is not a larger reasoning architecture. It is product validation: physical-device testing, independent cold-user evaluation, additional accessibility review, and carefully governed expansion of the Military Transition Domain Pack. Any authoritative benefits or eligibility logic would require separately sourced, versioned, and approved domain rules; the current prototype does not claim that authority.

## Required disclosures

Military SLICES was created in a new repository during the competition period. Pre-existing HELM methodology and prior product lessons informed the design, but no prior Veteran Slice application code, schemas, routes, deployment, or data were reused. OpenAI Codex assisted with implementation, testing, documentation, and release verification.

The demonstration uses synthetic transition data. Occupational references support exploration only and do not claim qualification, hiring probability, salary, benefits, clearance, or guaranteed outcomes.

## Links

- Hosted project: <https://hackathon-rc---military-slices-ztvqlzospa-uw.a.run.app/>
- Source repository: <https://github.com/kevinfagundes85-art/military-slices>
- Demo video: <https://youtu.be/cpM1sqzRtEU>
