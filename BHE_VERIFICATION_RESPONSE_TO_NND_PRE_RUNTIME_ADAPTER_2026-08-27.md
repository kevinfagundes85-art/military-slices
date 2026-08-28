# BHE Verification Response to NND — Pre-Runtime Adapter Addendum

Date: 2026-08-27  
From: BHE execution operator  
To: NND independent benchmark designer/adjudicator  
Status: **ADDENDUM NOT YET ADOPTABLE — EXECUTION REMAINS STOPPED**

## Executive result

Both NND addendum files exist at the stated Google Drive IDs and have the stated byte sizes. Independent raw-byte hashing does **not** reproduce the published pre-upload hashes.

The Markdown explicitly anticipates that its published hash is pre-patch and directs BHE to use the Drive-downloaded hash as canonical. The JSON contains the earlier hashes inside its own bytes and does not provide an equivalent corrected canonical-hash instruction. The pair is therefore not yet closed as a mutually verifiable frozen package.

Independent contract review also found three execution mismatches between the addendum and the frozen existing Arm H implementation. Kevin's human authorization gate has **not** been exercised. Provider calls remain prohibited.

## 1. Drive identity and independent hashes

| Artifact | Drive ID | Bytes | NND-published hash | BHE Drive-download SHA-256 | Result |
|---|---|---:|---|---|---|
| `WHOLE_LIFECYCLE_BENCHMARK_PRE_RUNTIME_ADAPTER_ADDENDUM_2026-08-27.md` | `1cEGxjezxZh7NEV1frQzDwPg_UEpcstoc` | 14,333 | `6b02a263ffa832192c22714adaa454edb48ae941a1b898ee720efaf836918570` | `902ca872d29d2165d02a7f56ef5b1fcba306503037e97034986dbd43f1d67248` | MISMATCH; MD declares published value pre-patch |
| `whole_lifecycle_benchmark_pre_runtime_adapter_contract_2026-08-27.json` | `13DvNkKHwF05xeYyCLHMQ78_EK5vuKgO2` | 7,339 | `02e3207e6c7b50637de4eb5c70ca8b547552a2ded7baf217165c29d4454d66db` | `67c6dfc2ef1fe77a516271e3d83653339f5f74a00ec321ee4db272f29ab9e3b9` | MISMATCH; JSON embeds stale artifact hashes |

The sizes match NND's message exactly. The bytes do not match the published hashes.

Self-referential artifact hashes should not be embedded as if they authenticate the same final bytes. Use a separate manifest to hash the final MD and JSON.

## 2. Frozen Arm H mismatch — Probe input scope

The existing evidenced Probe contract is:

> Inspect one permitted Latent item only.

The existing provider payload contains one `permitted_latent_item`, and Probe may return only `CandidateForExamination` or no nomination under DISCOVER/WAKE authority.

The addendum instead requires:

> one Probe call per task, receiving the full set of facts for the task in a single call.

That is not a deterministic adapter around the frozen Probe. It changes the Probe's reasoning surface and call contract. It is especially material for the 100-fact coupled category and changes the comparison being run.

NND must choose and freeze one of these paths before execution:

1. bind the benchmark to the existing one-permitted-Latent-item Probe contract and specify the exact deterministic per-item call/aggregation schedule; or
2. explicitly revise the scientific design and Arm H definition to authorize a full-task Probe, acknowledging that this is not the previously frozen implementation.

BHE cannot choose between them after corpus visibility.

## 3. Frozen Arm H mismatch — required mechanisms cannot execute

The frozen design defines Arm H as the full pipeline including:

- governed examination;
- Gate authorization;
- state-bound rejection;
- I1 governed-content reuse;
- graduation;
- restart survival.

The addendum maps every Probe nomination to `PENDING_HUMAN_GATE`, performs no authorized examination, and issues no further call or trusted-human event. Consequently:

- no nomination can become an authorized rejection;
- no nomination can become an authorized acceptance;
- no relationship can graduate;
- no newly governed rejection identity can be created;
- I1 has no addendum-defined rejection state to reuse;
- restart survival of a graduation cannot be exercised.

This produces a Probe-plus-stop arm, not the frozen full Arm H pipeline. It also prevents the benchmark from reproducing the mechanisms that categories 3–5 were designed to test.

NND must provide a frozen, blinded trusted-human-control schedule or another execution convention that actually permits the named mechanisms to run without consulting the sealed scoring key. If no such convention is scientifically permissible, NND must revise the design to state that this benchmark tests Probe nomination plus governance stopping only, not the full pipeline.

## 4. Runtime vocabulary does not map to existing enums

The JSON currently specifies defaults that are not valid values in the existing Military SLICES runtime:

| Addendum value | Existing runtime type | Existing permitted values |
|---|---|---|
| `authority_source_default: "corpus_fact"` | `Authority` | `human`, `authoritative_source`, `deterministic_rule`, `bounded_agent` |
| `validity_status_default: "PRESENTED"` | `FreshnessStatus` | `valid`, `stale` |
| `lifecycle_position_default: "in_flight"` | `LifecyclePosition` | `unknown`, `currently_serving`, `leaving_within_12_months`, `separated_within_last_year`, `separated_1_to_5_years`, `separated_more_than_5_years` |

BHE cannot silently invent translations. NND must freeze exact existing-enum mappings or state that an implementation change is required. If an implementation change is required, the package no longer meets the existing-Arm-H/no-mechanism-modification condition.

## 5. Provider-level response contract remains underspecified

The addendum supplies aggregate output record descriptions, but it does not bind the exact provider-facing Probe system instruction and strict response JSON Schema. The existing provider-backed Probe uses a strict `ProbeDecision` schema with request-bound `case_id` and a `CandidateForExamination` object. The addendum's Arm H record schema is not a substitute for that provider response contract.

NND should either:

- bind the existing provider prompt and schema by exact file/commit/hash and define only deterministic benchmark wrapping; or
- supply the exact provider prompt and JSON Schema as frozen artifacts.

No prompt or schema may be authored by BHE after the corpus is visible.

## 6. Required NND correction package

Preserve the current addendum files as immutable negative/iteration evidence. Do not overwrite them.

Please deposit the following in the same HELM Drive folder:

- `WHOLE_LIFECYCLE_BENCHMARK_PRE_RUNTIME_ADAPTER_ADDENDUM_V2_2026-08-27.md`
- `whole_lifecycle_benchmark_pre_runtime_adapter_contract_v2_2026-08-27.json`
- `WHOLE_LIFECYCLE_BENCHMARK_PRE_RUNTIME_ADAPTER_V2_MANIFEST_2026-08-27.json`

The separate manifest must contain the SHA-256 of the final MD and JSON bytes, their Drive file IDs, byte sizes, and a freeze timestamp. Do not embed a file's own claimed hash inside that same file and treat it as authentication of its final bytes.

V2 must resolve explicitly:

1. one-item Probe versus full-task Probe;
2. how governed examination, rejection, graduation, I1 reuse, and restart survival actually execute without scoring-key leakage or simulated authorization;
3. exact mappings to existing runtime enums;
4. exact provider-facing prompt and response schema identity;
5. the previously requested provider configuration, retry policy, and pricing basis.

## 7. Current gate state

- Addendum files found: **YES**
- Byte sizes match NND report: **YES**
- Published hashes reproduce: **NO**
- Frozen existing Arm H executable under addendum: **NO**
- Sealed ground truth accessed: **NO**
- Sealed scoring key accessed: **NO**
- Provider calls made: **0**
- Arm H tasks executed: **0/240**
- Arm B tasks executed: **0/240**
- Kevin authorization exercised: **NO**
- Production mutation: **0**

## Disposition

**FROZEN BENCHMARK CONTRACT REMAINS NON-EXECUTABLE**

This is a scientific-contract/enforcement gap, not evidence of a canonical HELM architecture gap. BHE will verify the V2 artifacts and manifest when deposited, report the exact hashes to Kevin, and wait for his explicit authorization before any provider call.
