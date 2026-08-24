# Architecture and Governing Contract

## Topology

Military SLICES is one web service with one canonical state. Career, Education, Location, and Your Story are bounded projections, not independent applications or agents.

The transition runtime carries two distinct anchors:

- `human_anchor`: the outcome the person is pursuing now;
- `path_target_state`: the next bounded milestone on the service-aware transition path.

A task becomes active only when it is eligible on the current service/time path and materially advances or protects the human anchor. The runtime emits no more than three active tasks, and the interface foregrounds only one active gate.

```text
typed human input
  → stateless orientation
  → human review
  → governed promotion
deliberately selected artifact
  → safe ephemeral extraction
  → decision-relevant orientation
  → governed promotion without redundant confirmation
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
3. Typed input is not persisted until the human confirms or corrects it.
4. Deliberately selecting a supported artifact authorizes one plan update; it is not presented for redundant confirmation.
5. Raw bytes, contact-only text, and the full extracted artifact are not persisted. Artifact-derived governed facts are priority-ranked and capped at 24 per update so a document cannot be reconstructed as an unbounded fact list.
6. Artifact evidence does not create `human_anchor`. A missing artifact purpose produces one routing gate, not career hypotheses or a second document authorization.
7. Gemini returns bounded proposals, not truth.
8. Deterministic validation filters proposals before persistence.
9. Facts retain their authority and evidence identifiers.
10. Firestore writes use optimistic concurrency.
11. Replayed idempotency keys do not create new versions.

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

Raw files, full extracted artifacts, unconfirmed typed input, hidden reasoning, and chain-of-thought are not persisted.

The installed machine-readable path is `military_slices/data/service_path_boundaries.json`. Its durable task structure is executable; its source manifest is provenance metadata. Historical guides, prices, portal mechanics, and volatile service-program details are not bundled as governing runtime truth.

## Cost controls

- Deterministic orientation runs before any model call.
- One bounded ADK run is allowed per meaningful input or refinement. It is limited to three model calls and an 18-second wall-clock budget; failure deterministically falls back instead of leaving the human waiting.
- State is compact and reused; conversation history is not replayed.
- Public evidence is purpose-scoped.
- Firestore stores one compact document per session for the MVP.
- Cloud Run scales to zero.
