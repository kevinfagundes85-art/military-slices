CORRIGENDUM TO: helm-whole-lifecycle-vs-broad-context-falsification-2026-08-27
Frozen: 2026-08-27
Status: BINDING ADDENDUM — supplements, does not modify, the two previously frozen artifacts.

The following two hashes remain unchanged and are not superseded by this corrigendum:
- Contract:    ba8f8a33e97aa4b3bd5cfdbddd6d6261c7c75970bfa4532227ff3519346f3aee
- Design doc:  47543121bb6f68daa40a532a96ba89272c424a578b29692864d4e5278e5e8524

This corrigendum resolves three items raised in commissioning review.

---

## 1. Arm B system prompt — binding

The Arm B system prompt is bound to this contract as follows:

- File: arm_b_system_prompt_2026-08-27.md
- SHA-256: 3fd3a77a2c2b6512e39b627a70c92f23526ba3273e49031e45010e3a50099041
- Size: 3,979 bytes
- This hash is now a required precondition for execution: any Arm B run against a system
  prompt whose SHA-256 does not equal the value above is not a run of this contract and
  produces no admissible evidence toward this benchmark's disposition-changing decision rule.

## 2. Secondary weighted re-aggregation weights

Per design §5 and §9.4, a secondary, descriptive re-aggregation of the composite score is
reported alongside — never in place of — the primary equal-weighted pooled analysis in
§9.1–9.2. These weights are fixed now, before any corpus item exists, so they cannot be
selected or adjusted in light of a result.

| Category | Weight | Basis |
|---|---|---|
| 1. decomposable_sequential | 0.20 | Common case: most real multi-fact intake is sequential and moderate in size |
| 2. coupled_simultaneous_at_scale | 0.10 | Rarer in practice: large simultaneous-dependency surfaces are the exception, not the norm |
| 3. exact_structural_repeat | 0.15 | Moderately common: duplicate ingestion of identical records occurs regularly in intake pipelines |
| 4. paraphrase_reentry | 0.10 | Less common than exact repeat, but a known recurring pattern in re-submitted case material |
| 5. true_invalidation_becomes_consequential | 0.05 | Rare by construction: a previously-correct rejection later becoming wrong is an edge condition, not typical |
| 6. irrelevant_distractor_change | 0.15 | Common: most state changes in a live case file are unrelated to any given open question |
| 7. misleading_lexical_trap | 0.05 | Rare: adversarially-worded near-misses are a minority of real input, though disproportionately risky |
| 8. base_rate_non_material | 0.20 | Common: most individual facts in a real case file do not bear on any specific pending decision |

Sum = 1.00. This table is descriptive context for interpreting results against a plausible
real-world task mixture. It does not alter the pooled, equal-weighted statistical tests in
§9.1–9.2, and per design §9.4 it is not disposition-determining on its own.

## 3. Corpus-author / runtime-operator isolation — attestation requirement

Design §6 already states the rule: the corpus author must be isolated from whoever operates
Arm H and Arm B at runtime. This corrigendum freezes the attestation required to satisfy that
rule at execution time, since no corpus author or runtime operator can be named before the
corpus exists:

Before execution begins, the implementing team must file a signed attestation record
containing, at minimum:

- the distinct identity (person or credentialed system account) serving as Corpus Author;
- the distinct identity/identities serving as Arm H Operator and Arm B Operator;
- the distinct identity serving as Scorer (may be the same as Corpus Author, but must be
  distinct from both runtime operators, since the Scorer needs the sealed key the operators
  must not see);
- a statement that no identity serving as a runtime operator had access to the ground-truth
  or scoring-key artifacts prior to unsealing per design §6 and §12 step 4;
- the SHA-256 of the generated corpus and the SHA-256 of the sealed scoring key, committed
  at the same time as this attestation, before either arm is run.

Absence of this attestation record at execution time means the isolation rule's satisfaction
is unverified, not merely undocumented — execution should not proceed without it.

---

No corpus generation, provider execution, repository mutation, or production change has
occurred as a result of this corrigendum. This document completes package composition only.
