# Military SLICES Human Control Layer — 2026-08-24

## Governing contract

Observe does not activate. Explore does not commit. Relevance does not grant execution authority. A hypothetical branch is not canonical state. Only explicit governed promotion changes human truth.

## Implementation

- `PathProgress` derives a target-specific denominator from the current objective, milestone, service, timing, and materially required decisions. Latent domains are never counted.
- `LensProjection` exposes bounded facts, settled/open/conflicted counts, latent dependencies, and a human explanation. Lens endpoints are GET-only and call neither the resolver nor the datastore writer.
- `MemoryStore` and `FirestoreStore` preserve the previous canonical snapshot on each successful versioned write. History endpoints return summaries or one exact stored version without replacing the current state.
- `WhatIfBranch` is derived deterministically from a selected canonical version. It carries the source version, explicit modification, affected gates and areas, consequences, evidence basis, uncertainty, and conflicts.
- What-If branch tokens are HMAC-signed, profile-bound, expiring, and integrity-checked. The branch itself is not persisted.
- Promotion requires an explicit `Use this plan` action, the current expected version, an idempotency key, token ownership, and branch reconstruction. It records human authority, preserves the prior version, recomputes bounded downstream state, and explains the consequences.

## Persistence topology

```text
military_slices_profiles/{profile_id}                 canonical current state
military_slices_profiles/{profile_id}/versions/{N}    immutable prior snapshot
browser memory + signed token                         ephemeral hypothetical branch
```

No new datastore, queue, bucket, agent, or background worker was added.

## Cost delta

- Fixed recurring infrastructure: `$0`.
- Lens, progress, history projection, and What-If creation: zero Gemini calls.
- Firestore: one additional snapshot write per successful canonical mutation; history reads occur only when the human opens History.
- Promotion: no model call unless the promoted change makes an already-authorized career gate require bounded resolution.
- At hackathon validation traffic, the usage-based Firestore/storage delta is expected to remain negligible; actual billing remains externally measurable rather than estimated as fact.

## Release boundary

The automated contract covers read-only Lens behavior, immutable history inspection, What-If isolation, ownership, conflict visibility, promotion, résumé-scope protection, target-specific progress, mobile CSS, security, and replay boundaries. Physical Android hover/tap substitution, focus behavior, and founder comprehension remain human-only release gates.
