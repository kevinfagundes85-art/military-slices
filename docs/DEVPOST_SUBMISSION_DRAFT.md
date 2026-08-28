# Devpost Submission Draft

## Project name

Military SLICES

## Tagline

One connected transition plan that remembers, adapts, and asks only when the human is needed.

## Category

Collaborative Partner

## What it does

Military SLICES helps transitioning service members, veterans, and spouses connect career, education, location, and résumé decisions without completing a giant intake form or learning an internal workflow. A person can start with a natural sentence, résumé, document, or screenshot. The system extracts only decision-relevant context, presents it for correction, and writes nothing until the human confirms it.

The fixed dashboard keeps natural input central while showing the current direction, what has already been decided, and what matters for the decision in front of the user. Related questions are bundled so the veteran can answer them together. Real-world test results remain attached to the relevant direction. When intent or circumstances change, Military SLICES reopens the affected decision without discarding the governed history.

## How it was built

- FastAPI and a responsive HTML/CSS/JavaScript dashboard on Cloud Run
- Google Agent Development Kit with Gemini 3.7 Flash through Vertex AI
- Firestore for canonical, versioned state and cross-session continuity
- Secret Manager and a dedicated least-privilege runtime identity
- Deterministic orientation, time-window calculation, output validation, optimistic concurrency, and idempotent writes
- Ephemeral TXT, DOCX, PDF, scanned-PDF, PNG, and JPG/JPEG extraction; only decision-relevant statements persist after deliberate human confirmation

## What makes it agentic

The agent does more than answer a chat question. HELM projects a purpose-limited surface from confirmed state, authorizes a bounded resolver call, validates the structured result, and updates the persistent plan. The runtime then evaluates time, conflicts, dependencies, rejected options, and new evidence to decide what needs attention next. Gemini performs bounded reasoning; the human remains the authority for consequential decisions.

## Data and evidence

The demo uses synthetic transition data only. Occupational exploration cites O*NET Online and the U.S. Bureau of Labor Statistics Occupational Outlook Handbook. Public evidence supports exploration; it does not assert qualification, hiring likelihood, salary, clearance, benefits, or guaranteed outcomes.

## What we learned

The hard problem was not generating more advice. It was keeping the foreground focused while the plan grew. Useful transition planning required explicit unknowns, human correction before governance, bundled related questions, context-preserving re-entry, and the ability to reverse a decision without losing the prior record. Rich input matters too: bounded reasoning should not force a veteran to translate ordinary experience into developer-friendly language.

## Fresh-build and AI-assistance disclosure

Military SLICES was implemented in a new repository during the competition period. Pre-existing HELM methodology and product lessons informed the design, but no Veteran Slice source code, schemas, routes, data, deployment, or app identity were reused. OpenAI Codex assisted with implementation, testing, documentation, and release validation, as permitted by the competition rules.

## Submission links

- Hosted candidate: <https://hackathon-rc---military-slices-ztvqlzospa-uw.a.run.app>
- Source repository: **HUMAN GATE — add public URL or grant the two required private-repository reviewer accounts**
- Demo video: **HUMAN GATE — record, upload publicly to YouTube or Vimeo, and paste the URL**

## Testing instructions

1. Open the hosted candidate in a fresh browser session; no account setup is required for first value.
2. Enter a synthetic transition objective and review it before confirming.
3. Choose a career direction, answer the bundled questions, and add a real-world test result.
4. Use the central input to change the target, then reload to verify continuity.
5. Do not enter real sensitive, medical, benefits, clearance, or government information.
