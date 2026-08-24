# Artifact Human-Gate Correction — 2026-08-23

## Failure evidence

- Physical use of a valid 665,991-byte DOCX reached `Updating your plan…` and did not complete.
- The document passed deterministic Office XML extraction: 27 ZIP parts, 1,254,580 uncompressed bytes, 7,652 extracted characters, and no multimodal fallback.
- Cloud Run recorded `POST /api/confirm` as `504` after 119.991 seconds.
- During that request, the ADK runner repeatedly alternated model responses and tool calls instead of reaching a bounded final response.

## Root causes

1. The interface treated deliberate file selection as mere extraction, then required the human to confirm the same résumé again.
2. The ADK runner retained its framework default of up to 500 model calls and had no application wall-clock bound.

## Corrected contract

- Selecting a supported artifact is the human authorization to use it for one current-plan update.
- Cancel creates no request and no write.
- Extraction, deterministic orientation, bounded resolution, and the Firestore write occur in one optimistic-concurrency/idempotency boundary.
- Raw bytes are cleared after extraction.
- The full extracted document and contact-only text are not persisted; only priority-ranked decision-relevant statements and evidence links survive, capped at 24 artifact facts per update.
- The resolver is limited to three model calls and 18 seconds, then returns deterministic fallback rather than spinning.
- The browser aborts after 25 seconds with an actionable message and reload guidance.

## Regression evidence

- The exact human DOCX completes the corrected local path in one request in under 0.1 seconds with deterministic resolution.
- The persisted state contains 22 decision-relevant facts and three career hypotheses, but not the 7,652-character full résumé.
- Automated coverage locks direct artifact governance, cancellation, idempotent replay, stale-write rejection, résumé-sized DOCX processing, and resolver timeout fallback.
