# HELM Adaptive Resolver Aperture T1 — Execution Stop Evidence

Date: 2026-08-28

## Disposition

**FROZEN T1 BENCHMARK CONTRACT NOT EXECUTABLE**

Execution stopped before the first benchmark provider call. No T1 task was executed, no sealed material was opened, and production remained unchanged.

## Verified execution-package state

- Public manifest: `484d7a062668cdb6636375eab2e4debbcc0b3f26713ec917e40abf3e789f4ed5` (5,851 bytes)
- All six public corpus shards, the public harness configuration, and the public provider configuration matched their manifest SHA-256 values and byte counts.
- Public corpus: 240 tasks.
- Provider availability had already been confirmed for `gemini-3.7-flash` without transmitting benchmark content.
- NND deterministic authority oracle: `033375e57033a00c15c026b370c75aaea3816665b0c0c660ad0a1f51e5af3e5` (2,909 bytes), with schedule commitment `375fe496e267e2478562b676d851111ee3b81963e7108b9403b45dd61c94b71f`.
- NND execution binding C-6: `6e2f5d73c604aa70c34baf89f2ea20e75181bd3dd32e38712423967723989d83` (3,229 bytes).

## Blocking defects

1. **Mode E cannot be bound structurally.** The accepted H1 `ApertureRequest` requires `permitted_latent_fact_id` and `probe_discovery_permitted`. The frozen public corpus provides neither and does not designate a Latent fact. Choosing one would infer Probe eligibility, which the frozen contract prohibits.
2. **Mode A cannot be bound to governed rejection reuse.** H1 uses the state-bound-rejection exact/content lookup and its governed lineage. The corpus exposes generic prior `PASS`/`FAIL` decisions without an authorized mapping to state-bound-rejection records. Treating them as reusable rejections would manufacture canonical semantics.
3. **H0/H1 lack an executable generic adjudication Resolver.** Repository-wide inspection of accepted H1 commit `e4b1fa624685d17711a5c68bcc4e836b192673ab` found no generic governed gate-adjudication instruction capable of producing the frozen `PASS`/`WAIT`/`HUMAN`/`REANCHOR`/`TERMINATE`/`FAIL` envelope. The available implementation Resolver is a career-hypothesis Resolver and is not semantically interchangeable.

These are frozen-contract defects, not transport or provider failures. A post-hoc adapter, inferred Latent designation, invented rejection mapping, or newly authored Resolver prompt would change the experiment after seal.

## Independent NND adjudication

NND independently confirmed all three defects and issued:

- Artifact: `NND_T1_EXECUTABILITY_ADJUDICATION_2026-08-28.json`
- SHA-256: `f4c19dd09270d61ba9eeacdfaa506596ab94d192f99f3b59bb8efb8737dc1a71`
- Bytes: 3,713

NND classified D1 and D2 as corpus-authoring failures and D3 as an upstream implementation/review failure. NND confirmed that the sealed corpus cannot exercise Modes A or E against implemented H1 and that neither HELM arm has a runnable generic adjudication path.

## Integrity audit

- H0 runs: 0
- H1 runs: 0
- Broad-context runs: 0
- Benchmark provider calls: 0
- T1 task executions: 0
- Provider benchmark spend: $0.00
- Sealed material exposed: no
- Results contaminated: no
- Canonical HELM changed: no
- Domain Pack changed: no
- Production changed: no

## Required remedy

D3 must be resolved first through an independently reviewed, hash-frozen executable generic Resolver contract belonging to the implementation—not authored post-hoc by the scorer. A replacement corpus under a new identity must then be authored against the real `CanonicalState`/`ApertureRequest` surface, including deterministic Mode A lineage and Mode E structural eligibility. Because execution count is zero, this can be a replacement seal rather than a repair of observed results.

No benchmark execution may begin under the current frozen corpus identity.
