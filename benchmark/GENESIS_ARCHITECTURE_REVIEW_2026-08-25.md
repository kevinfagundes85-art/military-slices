# Genesis Architecture and Schema Review — 2026-08-25

## Disposition

Genesis completed one independent architecture review through Google ADK, Gemini 3.7 Flash, and Vertex AI. The successful call used a frozen 21,202-byte packet containing the architecture contract, compact field/type/constraint schemas, Slice manifests, the deterministic dependency map, and the pinned Domain Pack identity. It contained no user profiles, production records, artifacts, credentials, or raw application source.

The first proposed 68 KB package was stopped locally before any provider call as broader than necessary. The reduced packet was frozen before execution. The first provider attempt rejected the native structured-output schema with HTTP 400 and produced no review; the successful retry kept the packet unchanged and used JSON response transport with the same locally validated output contract.

## Provenance and telemetry

- Source commit: `1efb6db`
- Packet SHA-256: `11b71b6f72d3a6e568f03d37701324c5e1f98f7be36859775ea8036238072ef5`
- Architecture SHA-256: `4dd32923a611ffcad20e73443dc13afc2935ac074e7b4de7a37dc5aa19f9ee81`
- Compact-schema SHA-256: `8d6799a9d2889ad8e5e24459116f08846cacd6e52aedf00622850d0dac5a6c1a`
- Response SHA-256: `e0c39a74eb765975a463d1a882cda700d8b946e08e0ae935ecd4b5ee49a57cbf`
- Model/provider: `gemini-3.7-flash` / Vertex AI global
- Framework: Google ADK
- Latency: 10,182 ms
- Tokens: 6,064 prompt; 1,219 response; 7,283 total
- Provider-billed cost: not exposed
- Production mutations: 0

## Genesis verdict

Genesis reported high confidence that the architecture cleanly separates human authority, ephemeral exploration, and deterministic execution. Its strongest patterns were:

1. unidirectional governed promotion with zero-write inspection/exploration;
2. deterministic `ACTIVE | PARALYZED | COMPLETE` execution projection outside model authority;
3. a static temporal dependency graph with bounded receipt patches and no model-inferred freshness.

## Recommendations and implementation disposition

### REC-01 — Atomic expected-version enforcement (`P1`, small)

Genesis recommends verifying the stored profile version against `MutationEvent.expected_version` inside the Firestore transaction and proving that two concurrent writes yield exactly one winner.

Current disposition: **implemented; integration-test hardening remains useful.** `FirestoreStore._save` reads and checks the stored version inside the transaction, `validate_mutation_commit` requires exactly one version advance and matching mutation event, and the in-memory concurrency regression passes. The smallest remaining improvement is a Firestore-emulator or disposable-collection concurrency test before production promotion; no runtime redesign is required.

### REC-02 — What-If HMAC and source-version integrity (`P1`, small)

Genesis recommends constant-time HMAC verification, expiry/ownership/source-version checks, and tamper rejection before hypothetical promotion.

Current disposition: **implemented; add two direct regressions.** `_decode` uses SHA-256 HMAC plus `hmac.compare_digest`; the token binds profile, source version, modification kind/value, statement, and expiry. The promotion endpoint checks ownership, expected version, retrieves the source snapshot, deterministically rebuilds the branch, and compares its signed modification. Cross-user and stale-source tests already pass. Signing the rendered hypothetical summary would duplicate a server-derived value and is not recommended. The useful addition is explicit forged-token and expired-token unit coverage.

### REC-03 — Stale evidence cannot cause paralysis (`P2`, medium)

Genesis recommends clearing dependent conflict/paralysis when its supporting fact becomes stale.

Current disposition: **already implemented and directly tested.** `test_stale_relocation_cannot_ground_conflict_or_paralysis` marks the fact stale, verifies conflicts are removed, verifies no gate remains `CONFLICTED`, and verifies the path is not `PARALYZED`. No change is indicated.

## Recommended next actions

1. Add the two missing direct What-If token tests: forged signature and expired token, both zero-write.
2. Add a Firestore concurrency integration fixture when a safe emulator or disposable test collection is available.
3. Keep the stale-fact/paralysis regression and current authority boundaries unchanged.

These are bounded validation improvements, not evidence for a new HELM primitive or architecture amendment. No production traffic, profile, database, or release state changed during the review.
