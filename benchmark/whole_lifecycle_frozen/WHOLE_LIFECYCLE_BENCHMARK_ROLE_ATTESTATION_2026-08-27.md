# Whole-Lifecycle Benchmark — Role-Separation Attestation
Contract: helm-whole-lifecycle-vs-broad-context-falsification-2026-08-27
Sealed: 2026-08-27

## Corpus Author: NND

Responsibilities discharged:
- Generated the 240-task runtime corpus per the frozen design (8 categories × 30 tasks),
  using a fixed, recorded random seed (20260827) so generation is reproducible and auditable.
- Generated the complete ground-truth record for all 240 task IDs.
- Generated the complete scoring key (harm taxonomy, lambda constants, category weights,
  subgroup mapping, statistical inputs) for all 240 task IDs.
- Sealed and hash-committed the runtime corpus, ground truth, and scoring key before any
  execution began.
- Did not operate Arm H.
- Did not operate Arm B.

## Runtime Operator: BHE

Responsibilities to be discharged at execution time (not yet performed):
- Receives the runtime corpus only — no category labels, ground truth, harm mappings, or
  scoring weights are present in that artifact (independently verified in §Validation below).
- Operates Arm H and Arm B against the identical runtime corpus.
- Preserves complete outputs and telemetry for both arms, unmodified, for all 240 tasks.
- Does not access the sealed ground truth prior to completing and hash-committing both arms.
- Does not access the sealed scoring key prior to completing and hash-committing both arms.
- Does not alter the runtime corpus.
- Does not score results.

## Scorer / Independent Adjudicator: NND

Responsibilities to be discharged after runtime completion (not yet performed):
- Receives BHE's immutable, hash-committed outputs for both arms.
- Verifies execution hashes before any scoring begins.
- Unseals the ground truth and scoring key only after verification.
- Applies the frozen scoring function, statistics, and disposition rule exactly as specified
  in the frozen design and contract — no parameter may be adjusted after outputs are visible.
- Independently adjudicates and reports the result, including any negative or inconclusive
  outcome, per the symmetric decision rule already on record.

## Separation Invariant (in force from the moment this attestation is sealed)

BHE may receive: frozen design, frozen contract, corrigendum, Arm B system prompt, the
runtime corpus, provider/runtime requirements, and artifact hashes.

BHE must not receive, before both arms are complete and hash-committed: the sealed ground
truth, the sealed scoring key, category labels, harm assignments, or any expected-winner
signal.

## Validation performed before sealing (see manifest for hashes)

- Task count: 240. Categories: 8. Tasks per category: 30 (exact).
- Every runtime task has exactly one ground-truth record and exactly one scoring-key record;
  no orphans, no duplicates.
- Automated scan of the serialized runtime corpus for forbidden terms (category names,
  decision labels, harm codes, severity values, weight fields) returned zero matches.
- Secondary category weights sum to exactly 1.00.
- Harm taxonomy contains all 7 frozen codes; H1 and H2 are correctly flagged critical.
- Frozen Arm B prompt hash cross-checked against the corrigendum:
  3fd3a77a2c2b6512e39b627a70c92f23526ba3273e49031e45010e3a50099041 (match confirmed).

No corpus generation error was found. No task was patched after generation; the artifacts
below are the first and only frozen version.
