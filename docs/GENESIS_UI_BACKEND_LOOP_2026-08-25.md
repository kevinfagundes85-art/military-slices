# Genesis / UI / Backend Loop — Contract Convergence

## Verdict

The existing Military SLICES topology can form a complete UI → backend → Genesis → Authority
Governor → Firestore → UI loop without a structural or authority change. BHE and Genesis converged
on two bounded contract corrections:

1. Bind every authorized career nomination to a deterministic identity covering the active Gate,
   prospective source version, and exact `CareerHypothesis` batch. Carry that identity through the
   existing mutation event and lineage record.
2. Extend the existing inline causal receipt, when a nomination occurs, to tell the human that new
   directions are options to explore based on confirmed experience and preferences. Do not expose
   provider or HELM machinery.

No new HELM primitive, agent, Slice, orchestrator, state class, datastore, queue, collection,
authority path, or UI surface was accepted or implemented.

## Frozen negotiation

- Source reviewed: `23d8917`
- Framework/provider/model: Google ADK / Vertex AI / `gemini-3.7-flash`
- Region: `global`
- Packet: 12,208 bytes
- Packet SHA-256: `6266bea3896b00b7180b43372834a52a17b4f5ff0a455ed82d62ed2649f1b870`
- System instruction SHA-256: `ab5cc6be16aa59ab004b8cf4f61a288e57f10c0fdc012f8374551c660450addd`
- Output contract SHA-256: `fc0540e2205a559c03e55515ad0ea699a48cf0565f112659c0079afac1fc4d5c`
- Session SHA-256: `0e20a8ef68f194eef0f232da306c0e84ba95750cc2e90db35cb29f15a6091735`
- Production mutations: 0
- User profiles, production records, raw artifacts, and credentials sent: none

### Turn 1 — critique

- Verdict: `compatible_with_bounded_deltas`
- Latency: 9,857.78 ms
- Tokens: 4,001 input / 1,230 output / 5,231 total
- Response SHA-256: `31b2a98b911939fcd94daa922f1a6d231d467e4c1a45aef016713fd046fb9898`

### Turn 2 — convergence

- Verdict: `compatible_with_bounded_deltas`
- Latency: 10,290.60 ms
- Tokens: 6,005 input / 1,227 output / 7,232 total
- Response SHA-256: `1f079ec113b17d22b03e8a1967b2bb1e0cd2183e8f32573214bb791165dc2280`
- Unresolved questions: none

The controller explicitly rejected/deferred structural ideas including asynchronous queues,
background model workers, a separate nomination datastore/entity, provider telemetry in the human
interface, and autonomous Gate resolution.

## Closed loop

1. The UI sends the active Gate identity, human value, expected version, and idempotency key.
2. The backend reconstitutes current state and rejects a stale version or inactive Gate.
3. The Authority Governor authorizes the human transition before deterministic mutation.
4. The engine applies the human choice and recomputes the next active Gate.
5. If and only if the next Gate requires career nomination, Genesis receives the minimum permitted
   Career projection.
6. Genesis returns typed hypotheses; it cannot persist or resolve the human Gate.
7. The backend hashes the exact Gate/version/hypothesis batch and validates that identity at the
   nomination boundary.
8. The Authority Governor verifies Gate identity, prospective state version, scope, authority, and
   `effect=nominate`.
9. The backend attaches authorized hypotheses, adds the proposal identity to the existing mutation
   dependencies, records one human mutation event, and commits with Firestore compare-and-set.
10. The API derives `StateEnvelope` from the saved version. The UI renders the next Gate plus one
    plain-language causal receipt. Reload reconstitutes the same result without another model call.

## Implemented boundaries

- `resolver_nomination_ref` creates a stable SHA-256 identity without retaining prompt text,
  artifact bytes, provider output, or a second copy of user context.
- `validate_resolver_nomination` rejects a missing, duplicate, or mismatched proposal identity.
- `_resolve_current_gate` validates the identity before requesting Governor authorization.
- Only an authorized nomination adds its identity to mutation dependencies and lineage.
- The existing `FeedbackEvent` gains one bounded consequence; no UI contract or surface was added.
- Idempotent replay returns before `_resolve_current_gate`, so it performs zero additional model
  calls and zero writes.

## Falsification and validation

- A tampered role title no longer matches the authorized batch identity and is rejected.
- The nomination remains `effect=nominate`, the Gate remains `PARTIAL`, and human choice remains
  required.
- The proposal identity appears exactly once in the mutation dependencies and in the matching
  lineage record.
- Retrying the identical confirmed action returns the same version and performs one total resolver
  call across original plus replay.
- The inline receipt contains `ready to explore` and contains none of `HELM`, `ADK`, `Gemini`,
  `resolver`, or `Governor`.
- Full suite: 191 passed.
- Ruff: passed.
- strict Mypy: passed.
- Bandit: passed.
- dependency audit: no known vulnerabilities; local package is not published on PyPI.
- JavaScript syntax: passed.
- Diff whitespace validation: passed.

External effects and autonomous Probe remain disabled. Production state and traffic were not
changed during negotiation or local validation.

## Zero-traffic candidate proof

- Source commit: `fd5c246`
- Revision: `military-slices-00034-vuz`
- Traffic: 0%
- Candidate tag: `genesis-loop-rc`
- Candidate URL: <https://genesis-loop-rc---military-slices-ztvqlzospa-uw.a.run.app/>
- Container digest: `sha256:5a6f3e75c0dc93b319729bbd18cf5d06b2f654c02ffbc08a804be63fd1bb68ec`
- Exact hosted bundles: `app.js?v=8`, `styles.css?v=6`
- Runtime identity: Firestore, secure cookie, Google ADK, `gemini-3.7-flash`, Vertex AI `global`,
  18-second resolver budget, existing runtime service account and session secret.
- Health: ready; installed Domain Pack hash
  `026a1508a3a2e6eb16907b2e8fc29c4f333af5c5ab908e6029903b8cbcbf9f4c`, status `LEGACY_VALID`.
- External effects: disabled.
- Autonomous Probe: disabled.
- Warning/error logs after hosted proof: none.

One isolated synthetic candidate session proved the hosted loop:

- versions advanced `0 → 1 → 2 → 3` across starting vector, confirmed intent, and transition-date
  decision;
- Gemini/ADK returned three hypotheses without fallback;
- `career-direction` remained `PARTIAL` and human-owned;
- the Governor recorded an authorized `nominate` decision;
- proposal ref
  `resolver-proposal:sha256:88e40b8738cc090f23e66b63225a636a50cdf1b761a332eddab2b0f3c2833431`
  appeared in both mutation dependencies and lineage;
- identical replay stayed at version 3;
- reload stayed at version 3 and reproduced `career-direction`;
- the inline receipt included the bounded exploration explanation.

Production remains `military-slices-00001-niw` at 100%. No traffic moved. The candidate remains at
the human acceptance Gate.
