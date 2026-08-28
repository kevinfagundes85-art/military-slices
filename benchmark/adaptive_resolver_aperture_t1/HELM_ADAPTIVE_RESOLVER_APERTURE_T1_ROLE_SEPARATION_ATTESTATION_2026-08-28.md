# HELM Adaptive Resolver Aperture T1 Role-Separation Attestation

Status: design frozen; no implementation or execution authorized.

NND is Corpus Author, Ground Truth Owner, hidden-authority schedule owner, Scorer, and Independent Adjudicator. NND alone authors and seals the corpus, hidden labels, expected modes, ground truth, harm assignments, authority schedule, baseline prompt, scoring key, statistical seed, and execution-unsealing rule.

BHE is Runtime Operator and, only after a separate Human Gate, H1 Implementer. Before the frozen unsealing condition, BHE may receive only the public runtime corpus, frozen implementation contract, provider configuration, and public hidden-authority interface contract. BHE must not receive ground truth, category labels, expected modes, harm assignments, future authority events, or the scoring key.

Genesis / the Client receives only exact runtime Payloads through the authorized API path and receives no Drive access to sealed benchmark artifacts.

The hidden authority interface is non-generative. It returns only an exact, preregistered, hash-bound authority event. A missing exact entry returns `null`. There is no model, semantic fallback, inferred approval, simulated human response, or schedule repair.

Execution outputs and telemetry for H0, H1, and B must be checkpointed, hashed, and committed before NND may unseal scoring information. No corpus, schedule, threshold, scoring key, or arm configuration may change after the applicable freeze.

This attestation does not authorize H1 implementation, provider calls, benchmark execution, deployment, production traffic movement, production Probe activation, production mutation, external effects, canonical HELM amendment, or Domain Pack policy change.
