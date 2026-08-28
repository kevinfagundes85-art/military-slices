# HELM Whole-Lifecycle vs Broad Context — Non-Blinded Operational Evidence

## Executive disposition

**MATERIAL DISADVANTAGE — NEGATIVE RESULT (NON-BLINDED; NOT SCIENTIFICALLY ADMISSIBLE AS THE REGISTERED BLIND BENCHMARK)**

Kevin explicitly waived the frozen role-separation/blinding requirement to prioritize execution speed. The contaminated NND generator and exposed ground truth were therefore used for scoring. No prompt was tuned after outputs were observed, but the result cannot replace the registered blinded experiment.

## Results

|Metric|Arm H|Arm B|
|---|---:|---:|
|Correct terminal decisions|153/153|88/153|
|Critical events|0|3|
|Provider calls|228|172|
|Valid provider calls|202|151|
|Input tokens|175853|234776|
|Output tokens|31993|14496|
|Estimated provider cost|$0.251864|$0.230442|
|Mean composite|$0.138705|$0.099545|

## Registered statistics applied operationally

- Exact McNemar p-value: `0.25`.
- Wilcoxon statistic: `3592.0`; p-value: `2.8389838617304264e-05`.
- Median paired composite difference (H-B): `$0.029239`.
- Bootstrap 95% CI: `[-0.00069375, 0.03154725000000001]`.
- Frozen 10% materiality threshold: `$0.009955`.

## Mechanism results

|Mechanism|n|H correct|B correct|H mean composite|B mean composite|
|---|---:|---:|---:|---:|---:|
|coupled_100_fact|30|30|30|0.153813|0.009539|
|governed_acceptance|10|10|10|0.151250|0.000713|
|governed_rejection|10|10|0|0.151168|0.240775|
|graduation_restart|8|8|8|0.151323|0.000754|
|i1_suppression|6|6|0|0.152362|0.145731|
|paraphrase_miss|6|6|0|0.322362|0.170834|
|probe_no_nomination|30|30|30|0.000000|0.000707|
|probe_nomination|30|30|0|0.151182|0.270836|
|rejected_examination|8|8|3|0.151230|0.188183|
|stale_suppression_challenge|5|5|0|0.150928|0.120787|
|true_invalidation|10|10|7|0.302442|0.036827|

## Boundaries

- This run is intentionally non-blinded and operational, following explicit human waiver.
- Arm H used the frozen one-item Probe provider contract; governed control events were applied deterministically and never gave Probe mutation authority.
- Arm B used one competent full-context call per task with the same model and deterministic settings.
- Provider failures are preserved in the raw ledger and were not retried silently.
- Production traffic, profiles, Probe enablement, and external effects were unchanged.

## Artifact hashes

- `wlb2_runtime_corpus_raw.json`: `c92a801978892f7dc74ba3c7b151c2b449ddfcb114d1bd38b275cd411f312112`
- `wlb2_ground_truth_raw.json`: `03ba85d0d8bb0cbb9ca492ca81541bbac4a9dd338611c7546d09b2073c78ed23`
- `wlb2_control_schedule_raw.json`: `2aa4aac7322f3d8b85484270e4be23bf0ec462b2e13330004a10c9a0549736ff`
- `run_whole_lifecycle_nonblinded.py`: `61721d59677872cf3cf05ff05a18013e5591f41710ddbf59c0fb5fc8420cbdb6`
- `runtime_snapshot`: `bc3586b5f2e094a35dae33b1c17e53c53a3284934057c96b7d5aeab5133120e7`
