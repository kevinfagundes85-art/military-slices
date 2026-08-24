# Devpost Submission Draft

## Project name

Military SLICES

## Tagline

One connected transition plan that asks only for the next decision that matters.

## Category

Collaborative Partner

## What it does

Military SLICES helps transitioning service members, veterans, and spouses connect career, education, location, and résumé decisions without completing a giant intake form or learning an internal workflow. A user starts with a sentence, résumé, document, or screenshot. The system extracts only decision-relevant context, shows it for correction, and writes nothing until the human confirms it.

After confirmation, a bounded Google ADK agent using Gemini 3.7 Flash investigates civilian career hypotheses with public occupational evidence. Firestore retains one versioned plan, explicit uncertainty, human decisions, rejected directions, and compact causal feedback. The interface then reconstitutes around the one unresolved decision with the highest consequence.

## How it was built

- FastAPI and an adaptive HTML/CSS/JavaScript interface on Cloud Run
- Google Agent Development Kit with Gemini 3.7 Flash through Vertex AI
- Firestore for canonical, versioned state
- Secret Manager and a dedicated least-privilege runtime identity
- Deterministic orientation, time-window calculation, output validation, optimistic concurrency, and idempotent writes
- Ephemeral TXT, DOCX, PDF, scanned-PDF, PNG, and JPG/JPEG extraction with human review before persistence

## Data and evidence

The demo uses only synthetic transition data. Occupational exploration points to O*NET Online and the U.S. Bureau of Labor Statistics Occupational Outlook Handbook. Public evidence supports exploration; it does not assert qualification, hiring likelihood, salary, clearance, benefits, or guaranteed outcomes.

## What makes it agentic

The agent does more than answer a chat question. It receives a purpose-limited projection of confirmed state, calls bounded tools, returns structured career hypotheses, records aggregate-safe execution evidence, and changes the persistent plan. The runtime then evaluates time, conflicts, dependencies, and rejected options to determine the next interaction. Human confirmation remains the authority boundary.

## What we learned

The hardest part was not generating more advice. It was keeping the foreground quiet as state grew. Useful transition planning required explicit unknowns, human correction before governance, reusing one answer across several domains, and ensuring that rejected suggestions changed later reasoning. Rich input also mattered: minimizing required context should never mean forcing a human to convert an ordinary résumé into a developer-friendly format.

## Fresh-build and AI-assistance disclosure

Military SLICES was implemented in a new repository during the competition period. Pre-existing HELM methodology and product lessons informed the design, but no Veteran Slice source code, schemas, routes, data, deployment, or app identity were reused. OpenAI Codex assisted with implementation, testing, documentation, and release validation, as permitted by the competition rules.

## Links to add at the human gate

- Live project: `https://militaryslices.com`
- Source repository: pending public/private-access decision
- Demo video: pending unedited recording and upload
