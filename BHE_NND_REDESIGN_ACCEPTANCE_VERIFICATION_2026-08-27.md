# BHE Verification of NND Whole-Lifecycle Redesign Acceptance

Date: 2026-08-27  
Status: DESIGN VERIFIED — HUMAN AUTHORIZATION REQUIRED BEFORE AUTHORING  
Production/provider boundary: unchanged

## NND disposition

NND returned:

`REDESIGN CONTRACT ACCEPTED FOR AUTHORING`

The acceptance applies only to authoring a new scientific package. It does not adopt V1 or V2, authorize corpus generation, unseal prior artifacts, run either benchmark arm, enable Probe in production, or alter canonical HELM.

## Pinned implementation verified

- Git commit: `d968c15da3447c311f3322e1805bc8067383c29f`
- `military_slices/models.py`: `d7e1953ff22fc1fa4e55e5a1127ae8a9183471eb0ffe97035d08fbc56779c763`
- `benchmark/run_probe_decisive_falsification.py`: `9df75580d7fa0d7bc0dfc14210dc2369ca4628ccad4ffa09cfda46e1a217f9d3`
- `military_slices/state_bound_rejection.py`: `a8e4aa06a2bab11cad4b8a3277a77d4ecdefcd99faa4847bdc8424886722d4e5`
- `benchmark/run_state_bound_rejection_falsification.py`: `e7810d724e8653ccd0fca76328dfdcf56f98c731a78c81d5554f7b7b3e589a9b`
- Domain Pack identity: `military-transition / 2026-08-24-v2-shadow-tested / LEGACY_VALID`

The working tree contains only the previously authored untracked design/verification memos. No runtime source was modified during this negotiation.

## NND bounded selections

1. Human attention uses a requestable oracle.
2. The oracle is one-shot for a matching task-ID/event-ID tuple, returns only the frozen response, accepts no follow-up or reformulation, and returns null for unmatched requests.
3. The former eight-category corpus and fixed `n=240` are retired. A fresh corpus will be sized before generation to satisfy preregistered mechanism coverage and statistical requirements.
4. The Arm B prompt is re-authored and frozen for the new multi-turn, wave-based corpus.
5. Prior ground truth and scoring key remain sealed forever as artifacts of the abandoned package. New corpus identity requires new sealed ground truth, scoring, and control schedule.
6. Control-schedule generation is an NND-internal corpus-author/scorer action. Ground truth is never delivered to BHE; control events are revealed only after paired wave commitments.
7. BHE generates the runtime/schema snapshot from code; NND binds it by hash and does not manually recreate enums or schemas.
8. The new experiment receives a new contract ID, package identity, hashes, and Kevin authorization gate.

## Minimum mechanism coverage accepted

| Mechanism | Minimum tasks |
|---|---:|
| Probe nominations | 30 |
| Probe no-nominations | 30 |
| Governed acceptances | 10 |
| Governed rejections | 10 |
| Exact-content I1 suppression hits | 6 |
| Paraphrase/structurally different identity misses | 6 |
| True invalidations | 10 |
| Stale-suppression challenges | 5 |
| Graduated relationships with restart | 8 |
| Rejected examinations | 8 |
| Coupled 100-fact cases | 30 |
| Authority violations | 0 (safety constraint) |

## Runtime coherence findings

### Existing contracts support the proposed design

- `ActorProvenance.trusted_session` provides the existing trusted-human event representation.
- `AuthorityGovernor.record_human_mutation` supplies version-bound, idempotent governed mutation with MutationEvent and LineageRecord output.
- `ProbeDecision` and `CandidateForExamination` already provide strict, identity-bound, DISCOVER/WAKE-only provider output.
- `record_state_bound_rejection`, `lookup_state_bound_rejection`, and `lookup_governed_content_rejection` support governed rejection, I0/I1 reuse, material invalidation, and read-only suppression.
- Existing graduation harnesses demonstrate authorized examination, Impact/Decision persistence, restart/reconstitution, indexed deterministic reuse, and zero second-pass semantic rediscovery.
- Existing coupled-evidence projection supports Gate-declared minimum-sufficient simultaneous evidence without changing authority or Canonical truth.
- `probe_execution_enabled()` and `external_effects_enabled()` remain false, so this synthetic harness cannot implicitly enable production behavior.

### Probe eligibility is an implementation-hardening boundary

There is no standalone production `ProbeEligibility` primitive, and none is authorized. The new benchmark adapter can express eligibility deterministically from existing governed structure only:

- authored Fact state is Latent/permitted for the wave;
- Fact affected Slice intersects the Gate's governed Slice scope;
- effect dimension is within the Gate's authorized scope;
- Fact freshness/authority metadata satisfies the existing bounded Probe input contract;
- no valid I0/I1 rejection suppression already resolves the exact structural candidate.

This is a pre-frozen harness selection function over existing Fact/Gate/StateCategory/authority structures, not a new canonical semantic decision. It must be source-hashed and falsified before provider execution. If corpus coordinates cannot instantiate this rule without prose interpretation, execution stops.

### One-shot oracle is harness-only

The requestable oracle does not grant HELM authority. A released oracle event becomes an ordinary frozen trusted-human input only after both arms have committed the preceding wave. The matching and reveal mechanism is benchmark infrastructure; Arm H still mutates only through its existing Governor path. Arm B receives the information-equivalent human turn.

## Verification disposition

The accepted redesign is coherent with the pinned implementation as a new scientific package. No conceptual HELM amendment is required to author it.

The remaining work is not authorized yet. It includes runtime snapshot generation, new harness/adapter authoring, corpus/control-schedule generation, sealing, and pre-execution verification.

## Current hard boundary

- Provider calls: 0.
- Arm H: 0 tasks executed.
- Arm B: 0 tasks executed.
- Old sealed ground truth/scoring key: withheld and never to be reused.
- New corpus/control schedule: not generated.
- Production traffic/profile/state changes: 0.
- Production Probe/external effects: disabled.
- Canonical HELM/Domain Pack amendments: 0.

Kevin's next explicit authorization may authorize authoring and sealing the new package. It does not authorize provider execution; BHE must return the final hashes and an execution gate before calls begin.
