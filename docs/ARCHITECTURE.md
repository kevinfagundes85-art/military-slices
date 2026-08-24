# Architecture and Governing Contract

## Topology

Military SLICES is one web service with one canonical state. Career, Education, Location, and Your Story are bounded projections, not independent applications or agents.

```text
human input
  → stateless orientation
  → human review
  → governed promotion
  → deterministic + ADK/Gemini resolution
  → Firestore versioned state
  → time/relationship evaluation
  → one highest-value interaction
  → human decision
  → concise causal feedback
  → recompute
```

## Trust boundary

1. Input is untrusted.
2. Orientation extracts only statements the human actually supplied.
3. Nothing is persisted until the human confirms or corrects.
4. Gemini returns bounded proposals, not truth.
5. Deterministic validation filters proposals before persistence.
6. Facts retain their authority and evidence identifiers.
7. Firestore writes use optimistic concurrency.
8. Replayed idempotency keys do not create new versions.

## Persistence

Collection: `military_slices_profiles`

One document per signed anonymous browser session contains:

- original confirmed intents;
- current goal and transition date;
- grounded facts and evidence pointers;
- typed decisions and conflicts;
- career hypotheses and rejections;
- bounded projections;
- causal feedback history;
- processed idempotency keys;
- aggregate-safe telemetry;
- version and timestamps.

Raw files, unconfirmed input, hidden reasoning, and chain-of-thought are not persisted.

## Cost controls

- Deterministic orientation runs before any model call.
- One Gemini call is allowed per meaningful confirmed input or refinement.
- State is compact and reused; conversation history is not replayed.
- Public evidence is purpose-scoped.
- Firestore stores one compact document per session for the MVP.
- Cloud Run scales to zero.

