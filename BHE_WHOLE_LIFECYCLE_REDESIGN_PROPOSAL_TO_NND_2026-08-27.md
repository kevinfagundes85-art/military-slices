# BHE Whole-Lifecycle Benchmark Redesign Proposal to NND

Date: 2026-08-27  
From: BHE  
To: NND  
Status: DESIGN NEGOTIATION ONLY — NO EXECUTION AUTHORITY

## Purpose

Repair the scientific contract so the registered comparison can execute the actual HELM full pipeline without simulated authority, ground-truth leakage, or changes to canonical HELM.

The original package, V1, V2, execution stop, and formal NND disposition remain immutable evidence. The repaired experiment must receive a new contract ID, corpus/package identity, hashes, and authorization gate.

## Architecture classification

This proposal is a scientific-design and corpus-contract repair. It is not a HELM primitive, Domain Pack amendment, production change, or runtime optimization.

Implementation under test remains pinned to git commit:

`d968c15da3447c311f3322e1805bc8067383c29f`

Relevant implementation hashes:

| File | SHA-256 |
|---|---|
| `military_slices/models.py` | `d7e1953ff22fc1fa4e55e5a1127ae8a9183471eb0ffe97035d08fbc56779c763` |
| `benchmark/run_probe_decisive_falsification.py` | `9df75580d7fa0d7bc0dfc14210dc2369ca4628ccad4ffa09cfda46e1a217f9d3` |
| `military_slices/state_bound_rejection.py` | `a8e4aa06a2bab11cad4b8a3277a77d4ecdefcd99faa4847bdc8424886722d4e5` |
| `benchmark/run_state_bound_rejection_falsification.py` | `e7810d724e8653ccd0fca76328dfdcf56f98c731a78c81d5554f7b7b3e589a9b` |

Installed Domain Pack remains `military-transition / 2026-08-24-v2-shadow-tested`; its runtime/file hashes must be recomputed and bound in the new package before execution.

## Minimum executable design

### 1. New structured lifecycle corpus

The new runtime corpus may reuse the substantive natural-language scenarios, but every task must carry the governed coordinates the real runtime requires. They must be authored before execution, not inferred by BHE from prose:

- planning actor and military-state subject;
- lifecycle position and applicable service coordinates;
- Human Anchor;
- Path target;
- Gate identity/version and Gate contract;
- effect dimension;
- Fact ID, statement/value, authority, freshness, field key, affected Slice, state category, and lineage seed;
- ordered event/turn identity;
- explicit supersession/invalidation references where the scenario contains them.

These coordinates are part of the task's factual input, not scoring labels. Arm B must receive information-equivalent source, authority, temporal, and supersession metadata in ordinary broad-context form. Neither arm receives category, expected winner, harm assignments, scoring weights, or final truth labels.

NND must not assign one lifecycle value to every task. Lifecycle state must follow each scenario's authored subject and time evidence.

### 2. Runtime contract snapshot generated from code

BHE will generate, before corpus execution, a machine-readable snapshot directly from the pinned implementation containing:

- every enum value used by the adapter;
- exact `ProbeDecision` and `CandidateForExamination` JSON Schemas;
- Gate, Fact, Decision, ActorProvenance, MutationEvent, LineageRecord, and relevant state schemas;
- exact identity-bound `case_id` rule;
- Domain Pack identity/hash;
- relevant source-file hashes.

NND should bind this generated snapshot by hash. NND should not manually recreate provider schemas or enum values.

### 3. Deterministic ingestion and Probe eligibility

The adapter may only translate authored structured coordinates into existing runtime objects. It may not classify prose, infer authority, invent lifecycle state, or determine materiality.

Probe eligibility must be derived from the existing bounded runtime contract. A candidate is eligible only when the structured event is in permitted Latent state and falls within the declared Gate/effect/Slice discovery scope. `Every corpus fact` is not an admissible default.

The exact deterministic eligibility function and its source hash must be frozen before either arm runs. If the existing runtime cannot express the rule without new semantics, stop as an implementation/Domain-Pack contract gap.

### 4. Precommitted trusted-human-control schedule

NND, acting as corpus author/scorer, must generate a separate schedule from the sealed ground truth at corpus-generation time. This is not a simulated runtime decision: it is frozen experimental input representing the trusted human's later authoritative response.

Each control event must include at least:

- task ID and event/wave ID;
- the prerequisite committed output hash or checkpoint identity;
- candidate/Gate identity to which the response applies;
- trusted-human response: accept, correct, reject, defer, or no response;
- authoritative statement/value where applicable;
- validity and invalidation conditions;
- event integrity/hash and signature or manifest binding;
- the natural-language equivalent supplied to Arm B.

The schedule is hashed and sealed before runtime. It remains withheld while both arms produce the preceding outputs.

### 5. Staged reveal protocol

Use barrier-synchronized waves:

1. Both arms process the same pre-control event stream.
2. Both arms' outputs, telemetry, failures, and state hashes are checkpointed and committed for every task in the wave.
3. Only after the paired commitment does NND release the next control-event wave.
4. A pre-frozen, hash-bound runner injects each event in task order. The operator cannot edit events or prompts.
5. Arm H ingests the event through `ActorProvenance.trusted_session` and the existing Governor path.
6. Arm B receives the information-equivalent human-review event as a new case turn and re-evaluates under its independently frozen prompt.
7. Repeat until the frozen lifecycle sequence completes, including restart/reconstitution checkpoints.

To avoid runtime discretion, the harness and its control-event consumer must be committed before the first control wave is unsealed. Future waves may be visible to the operator after release, but the already-hashed harness must enforce event order and prevent future-event exposure to either model.

### 6. Matched human-attention accounting

NND must preregister one of two defensible treatments and apply it symmetrically:

#### Fixed-event treatment

Both arms receive the same frozen human-control event and both are charged the same base human examination event. Architecture-specific extra examinations are charged separately.

#### Requestable-oracle treatment

Both arms may request the same frozen human oracle through a matched tool contract. Arm H requests through its Gate; Arm B may explicitly request review when uncertain. Every request is counted. The oracle response is predetermined and identical.

BHE recommends the requestable-oracle treatment because it preserves attention as a measured architectural outcome, but NND owns the scientific choice. The choice must be frozen before execution and may not depend on expected winner.

### 7. Output and scoring compatibility

Both arms must produce the same scored semantic outcome classes at each registered checkpoint:

- `ACCEPT`;
- `REJECT`;
- `NO_NOMINATION`;
- `PENDING_HUMAN_GATE` only as an intermediate, nonterminal runtime state.

`PENDING_HUMAN_GATE` must never be coerced to `NO_NOMINATION`. Scoring must either wait for the frozen human-control event or score the phase-specific nomination separately under a preregistered rule.

The new scoring contract must distinguish:

- discovery correctness;
- authority compliance;
- post-examination governed outcome;
- stale suppression/invalidation;
- graduation and deterministic repeat handling;
- restart survival;
- provider/deterministic/human-attention cost.

The final disposition rule must operate only on comparable terminal outputs.

### 8. Required full-pipeline traces

The new corpus/schedule must ensure the frozen pipeline is genuinely exercised and report counts, not merely names:

- Probe nominations and no nominations;
- governed acceptances;
- governed rejections;
- exact-content I1 suppression hits;
- paraphrase identity misses;
- relevant invalidations;
- stale-suppression challenges;
- accepted graduations;
- rejected examinations;
- restart/reconstitution and deterministic reuse;
- coupled 100-fact cases;
- provider failures and schema failures;
- authority violations.

Minimum coverage per mechanism must be fixed by NND before task generation. Coverage counts are design constraints; task identities and answers remain sealed.

### 9. Execution identity and manifest discipline

The new package requires separate immutable artifacts for:

- scientific design;
- contract;
- structured runtime corpus;
- Arm B prompt;
- generated Arm H runtime/schema snapshot;
- deterministic adapter/harness;
- sealed ground truth;
- sealed scoring key;
- sealed trusted-human-control schedule or oracle;
- role attestation;
- execution manifest.

The manifest must be produced only after final file bytes and upload IDs exist. It must bind actual Drive IDs, actual Drive byte sizes, actual Drive SHA-256 hashes, local pre-upload hashes, source commit, freeze timestamp, and supersession relationships. No artifact may authenticate itself with placeholders.

### 10. Scientific stop rules

Stop before provider execution if any of the following remain unresolved:

- provider/model identity is unavailable or not parity-matched;
- actual runtime schemas differ from the bound snapshot;
- an authored lifecycle/Gate coordinate cannot instantiate the pinned runtime;
- control schedule cannot be revealed without leaking future events to the models;
- Arm H and Arm B do not receive information-equivalent human-control input;
- terminal output classes are not comparable;
- the adapter must infer semantics from natural language;
- sealed artifacts or scoring information are exposed prematurely.

## Requested NND response

Please return one of:

1. `REDESIGN CONTRACT ACCEPTED FOR AUTHORING` — accompanied by NND's selected human-attention treatment and any bounded corrections to this protocol; or
2. `REDESIGN REQUIRES ARCHITECT ADJUDICATION` — identifying the exact unresolved authority/scientific contradiction; or
3. `WHOLE-LIFECYCLE EXPERIMENT ABANDONED` — preserving the negative design evidence.

Do not generate the 240-task corpus or unseal existing ground truth yet. First freeze the redesign protocol and role boundaries. Kevin must separately authorize corpus generation and execution after BHE verifies the returned design artifacts.

## Current boundary

- Provider calls: 0.
- Arm H: 0/240.
- Arm B: 0/240.
- Sealed ground truth/scoring key: withheld.
- Production/traffic/profile mutations: 0.
- Canonical HELM/Domain Pack changes: 0.

