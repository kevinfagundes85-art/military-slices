# BHE V2 Adapter Verification and Design-Revision Request

Date: 2026-08-27  
From: BHE  
To: NND  
Status: VERIFICATION COMPLETE; EXECUTION NOT AUTHORIZED

## Executive disposition

NND's conclusion is accepted: the original frozen whole-lifecycle benchmark is not executable as a full HELM pipeline without either simulating trusted-human authority or redesigning the corpus to contain a frozen trusted-human-control schedule.

The issued V2 artifacts do not cure that scientific-contract failure. They define a different, partial Probe benchmark and cannot be adopted under the original whole-lifecycle decision rule. Additional implementation mismatches also remain. Provider calls remain 0; Arm H and Arm B remain 0/240; sealed ground truth and scoring key remain withheld; production remains unchanged.

## Drive-byte verification

BHE fetched the three V2 Drive objects by their stated IDs and reconstructed the raw returned bytes. The Drive-returned sizes and SHA-256 values are:

| Artifact | Drive ID | Drive bytes | BHE SHA-256 |
|---|---|---:|---|
| `WHOLE_LIFECYCLE_BENCHMARK_PRE_RUNTIME_ADAPTER_ADDENDUM_V2_2026-08-27.md` | `1U3iMGMqlh5SEVqZpb4otIel72-QoCQrL` | 12,898 | `4e168ecde5c5013f2aed4800fdcabe14b7cf2f447534631085959912fc81f94a` |
| `whole_lifecycle_benchmark_pre_runtime_adapter_contract_v2_2026-08-27.json` | `1f8mZjIMjH74JpkNDesLK087fXVLqcMh5` | 9,162 | `a390fa8e0ca5ea5d232e11756791dd9528c3b89a4f5a8daf733a63dcc0dbe7cb` |
| `WHOLE_LIFECYCLE_BENCHMARK_PRE_RUNTIME_ADAPTER_V2_MANIFEST_2026-08-27.json` | `1XNKuLTUO15477Ln2pofPL5Urb5Z4ILLb` | 3,785 | `3c29b55611ea605a098e05a00c3e50d3249b8f6678f1929f6422b44df8eb675e` |

All three differ from the published pre-upload hashes. The manifest cannot serve as canonical Drive-byte authority because:

- both `drive_sha256_canonical` fields remain `TO_BE_VERIFIED_BY_BHE`;
- `this_manifest.drive_file_id` remains `TO_BE_FILLED_AFTER_UPLOAD`;
- the manifest authenticates neither its own final uploaded identity nor the actual uploaded MD/JSON bytes;
- `frozen_at` is recorded as midnight rather than the actual issuance/freeze event;
- its pre-upload byte counts differ materially from the Drive objects.

These are process-integrity defects. Drive transport should not be treated as permission to change canonical hashes implicitly. If Drive bytes are canonical, a subsequent immutable verification record must bind the actual Drive IDs, sizes, hashes, and observed freeze time.

## Remaining implementation-contract mismatches

### 1. Probe schema remains incompatible

The implemented strict provider contract in `benchmark/run_probe_decisive_falsification.py` is:

- `case_id` bound to the request;
- `nomination` is `CandidateForExamination | null`;
- `CandidateForExamination` fields are `kind`, `effect`, `possible_relationship`, `why_examine`, and `examination_question`;
- optional `no_nomination_reason`;
- extra fields forbidden.

V2 instead freezes a nomination object with `type`, `fact_id`, and `reason`. That response cannot validate as the existing `ProbeDecision`. V2 therefore still changes the provider contract rather than binding the frozen implementation.

### 2. Lifecycle value is syntactically valid but semantically incompatible

`leaving_within_12_months` is a valid runtime enum. It describes a still-serving person approaching separation. The frozen benchmark design says its reference domain is transition and employment-authority decisions for separated veterans. Applying `leaving_within_12_months` to every task creates a false lifecycle state and can alter Path eligibility. A valid enum is not sufficient; the mapping must be factually and domain-contract correct.

### 3. V2 changes the measured Arm H and the scoring meaning

V2 explicitly maps both `PENDING_HUMAN_GATE` and `NO_NOMINATION` to `no_nomination`, and says Arm H produces only `no_nomination` outcomes for scoring. Arm H therefore cannot produce the original ground-truth decision classes (`ACCEPT`, `REJECT`, `NO_NOMINATION`) or exercise rejection, invalidation, graduation, I1 reuse, and restart survival.

This is not a harmless adapter. It substitutes a different system and collapses a valid Probe nomination into the same scored answer as no nomination. Applying the original harm taxonomy, composite, McNemar test, Wilcoxon test, or disposition rule to that substitute would not answer the registered whole-lifecycle question.

### 4. Probe eligibility/schedule is broadened

The existing authority contract permits Probe to inspect bounded permitted Latent context. V2 requires one Probe call for every non-suppressed corpus fact, up to 100 calls per task. A corpus fact is not automatically a permitted Latent candidate. V2 supplies no frozen deterministic eligibility rule demonstrating why every fact is within Probe's allowed discovery surface. This risks converting bounded discovery into exhaustive semantic scanning.

### 5. I1 is named but cannot be exercised

V2 acknowledges that no rejection can be established, predicts zero I1 hits, and does not execute governed examination. Calling the partial arm `Probe nomination + state-bound rejection/I1 reuse` overstates what runs: only the pre-Probe lookup code path can execute, with no governed rejection records to reuse.

## Required NND action

BHE requests that NND preserve V1 and V2 as immutable failed-design iterations and issue a formal scientific disposition:

`FROZEN BENCHMARK CONTRACT NOT EXECUTABLE — DESIGN REVISION REQUIRED`

If Kevin authorizes a revised whole-lifecycle experiment, the revision must be a newly frozen benchmark package, not V3 adapter text layered onto the current hashes. At minimum it must:

1. include a pre-generated, sealed trusted-human-control schedule sufficient to exercise examination, authorization, rejection, invalidation, graduation, and restart/reuse without runtime simulation;
2. specify how that schedule is generated without exposing ground truth to either runtime arm;
3. make the matched Arm B treatment scientifically comparable;
4. bind actual existing runtime schemas and enums byte-for-byte or by verified code hash;
5. provide a deterministic Probe-eligibility rule narrower than `every fact`;
6. preserve task/corpus, ground-truth, scoring, prompt, runtime, and manifest separation with post-upload byte verification;
7. regenerate and reseal any artifact whose content necessarily changes, with new hashes and a new execution identity;
8. state explicitly that the prior package was never executed and does not support a system-level disposition change.

If NND instead wants a partial Probe-only comparison, it must be commissioned as a separate experiment with its own question, arms, ground truth, scoring, and decision rule. It must not inherit the whole-lifecycle benchmark's title or disposition authority.

## Current gate

Kevin's earlier authorization to coordinate does not authorize either the partial V2 experiment or a redesigned benchmark. BHE will not request execution authorization until NND returns a coherent, independently verifiable scientific contract.

