# Temporal Revalidation and Cross-Slice Impact

## Governing contract

Military SLICES persists decisions and revalidates assumptions. After an allowed canonical change, deterministic code asks what downstream state may no longer be safe to rely upon. It does not rotate topics, rebuild the receipt, or ask Gemini to invent relationships.

## Fact metadata

Facts support additive migration-safe metadata:

- `field_key`: deterministic canonical field identity;
- `status`: `valid` or `stale`;
- `last_validated_at`;
- `freshness_class`: `stable`, `slow`, `volatile`, or `external_expiring`.

Stable historical facts do not expire. Volatile facts use one centralized 14-day default. External-expiring facts use a centralized expiry and accept silent refresh only through an authoritative-source callback that supplies evidence provenance.

## Deterministic propagation

`military_slices/temporal.py` owns the reviewable dependency map, materiality rules, elapsed-time rules, receipt patches, and revalidation deltas. The MVP map is intentionally small:

- career target → relocation willingness and compensation floor;
- separation date → application, education, relocation, and résumé timing;
- relocation willingness → career search boundary.

Only existing downstream facts can be invalidated. Facts created in the same governed transaction are treated as freshly validated. Unmapped state stays untouched.

## State safety

- Staleness is metadata, not a sixth gate state.
- Stale facts are excluded from governing preference evidence.
- Stale location evidence cannot retain or create a location conflict.
- Stale facts cannot directly create paralysis.
- A machine-owned deterministic fact is silently refreshed.
- An external-expiring fact never asks the human to verify policy.
- A human-owned material assumption creates one compact impact candidate.
- Non-material impacts remain latent and receive no pixels.

## Human interaction

The primary gate stays primary unless its own dependency is affected. A non-blocking impact appears in a subordinate tray with natural copy and a one-tap confirmation. Choosing Update is explicit human intent and exposes only bounded options for the affected field. Lenses may show “May have changed”; inspecting them remains read-only.

## Receipt economics

Each status, validation-time, or value change creates a precise bounded patch. Recent patches are capped at 64 entries. Telemetry records dependencies evaluated, facts marked stale, silent refreshes, human prompts, confirmations, bounded updates, patch bytes/count, latency, errors, model calls caused by freshness logic, and full rebuilds.

Success invariants:

- freshness-detection Gemini calls: `0`;
- full receipt rebuilds: `0`;
- one primary gate;
- zero to three active tasks;
- one canonical state and one Firestore truth store.

## Human-only gates

Automated responsive checks approximate phone layout. A physical Android device and a cold human remain required to validate touch, native focus/keyboard behavior, copy comprehension, and the reaction “that makes sense” rather than “why is it asking me again?”
