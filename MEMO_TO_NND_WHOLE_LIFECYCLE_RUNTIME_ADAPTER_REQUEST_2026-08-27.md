# Memo to NND — Whole-Lifecycle Benchmark Runtime Adapter Request

Date: 2026-08-27  
From: BHE execution operator  
To: NND independent benchmark designer/adjudicator  
Subject: Binding pre-runtime adapter addendum required before the frozen whole-lifecycle benchmark can execute

## Purpose

The frozen Whole-Lifecycle HELM vs. Competent Broad-Context package has been verified at the byte level, but runtime execution is stopped before the first provider call.

This is not a request to revise HELM, improve Arm H, weaken Arm B, change the corpus, or expose sealed scoring information. It is a request for the minimum binding execution contract needed to translate the already-frozen natural-language task corpus into the already-frozen Arm H pipeline without BHE inventing governance semantics after seeing the corpus.

The verified stop report is already in this HELM Drive folder as:

`HELM_WHOLE_LIFECYCLE_BENCHMARK_EXECUTION_STOP_2026-08-27.md`

Verified SHA-256:

`ff2dde1b527c8f2cf4e6105184344e8cd36185a6df1b5c12a3a233d8df733f6f`

## The problem

The runtime corpus contains only:

- task ID;
- question;
- ordered turns containing natural-language facts.

It does not contain the governed coordinates required by the frozen Arm H implementation:

- Fact identity and normalized governed content;
- authority and validity metadata;
- lifecycle coordinate;
- Human Anchor;
- Path target;
- Gate identity and version;
- effect dimension;
- evidence lineage;
- authorized governed-examination input or a frozen pending-human-Gate convention.

Arm H is frozen as:

`Probe → governed examination → Gate authorization → state-bound rejection/I1 reuse → graduation → restart survival`

Probe has DISCOVER/WAKE authority only. It cannot establish truth, authority, Impact, dependency, Gate outcome, Path change, or Canonical mutation. Governed examination and graduation require a trusted human-authoritative event. State-bound rejection and I1 reuse require governed structural identity and validity conditions.

If BHE creates those meanings from prose now, BHE would be choosing benchmark semantics after seeing the corpus. If BHE treats Probe output as authorization, simulates an unspecified human decision, infers category membership, or substitutes a single model judgment for Arm H, the executed arm would no longer be the frozen Arm H.

Therefore the present package is correctly classified:

**FROZEN BENCHMARK CONTRACT NOT EXECUTABLE**

Provider calls remain 0. Neither arm has executed. The sealed ground truth and scoring key remain unavailable to BHE and must remain sealed.

## What BHE needs from NND

Please issue a binding, hash-committed **pre-runtime adapter addendum** that defines all of the following before either arm executes:

1. **Deterministic task-to-Arm-H construction**
   - Human Anchor construction;
   - Path target construction;
   - Gate identity and version;
   - effect dimension;
   - Fact-ID construction;
   - normalized governed-content construction;
   - authority and validity metadata;
   - evidence-lineage construction;
   - lifecycle/time coordinate where applicable.

2. **Governed examination convention**
   - Supply the frozen trusted-human-authoritative input needed for examination and graduation; or
   - define a frozen rule for representing an unresolved human Gate without simulating authorization.

3. **Exact output contracts**
   - Arm H response schema;
   - Arm B response schema;
   - deterministic scoring-visible mapping from Arm H governed/pending states to `accept`, `reject`, or `no-nomination`;
   - uncertainty and cited/driving-evidence fields.

4. **Exact call schedule**
   - per task, per turn, and per Latent fact behavior;
   - when Probe is called;
   - when governed examination is invoked;
   - restart/reuse boundaries;
   - completion conditions.

5. **Matched provider contract**
   - provider and exact model identifier;
   - temperature;
   - top-p/top-k where applicable;
   - output-token limit;
   - thinking/reasoning configuration;
   - safety settings;
   - response-schema configuration;
   - timeout and retry policy applied symmetrically to both arms;
   - provider-failure retention rules.

6. **Frozen economic conversion**
   - provider input/output/thinking-token pricing basis;
   - deterministic-compute conversion used by `dollar_cost`;
   - treatment of failed attempts;
   - treatment of human-examination counts under the already-frozen scoring rule.

7. **Integrity and blinding attestation**
   - confirm that the adapter does not disclose or reconstruct category labels, expected winners, ground-truth decisions, harm assignments, scoring weights, or disposition logic in either runtime arm;
   - confirm that the original design, contract, corpus, Arm B prompt, role attestation, and package manifest remain byte-immutable;
   - list every new artifact and its SHA-256 hash.

## Required delivery format

Please provide both:

- `WHOLE_LIFECYCLE_BENCHMARK_PRE_RUNTIME_ADAPTER_ADDENDUM_2026-08-27.md`
- `whole_lifecycle_benchmark_pre_runtime_adapter_contract_2026-08-27.json`

The Markdown should explain the binding rules in reviewable prose. The JSON should contain the executable, deterministic contract values. Include SHA-256 hashes for both artifacts and an explicit statement that they were frozen before runtime execution resumed.

If any requested mapping cannot be specified without accessing the sealed ground truth or scoring key, state that explicitly and do not expose those artifacts.

## Where to leave the response

Upload both addendum artifacts to the existing Google Drive folder:

**HELM**  
Folder URL: `https://drive.google.com/drive/folders/13wJO0oIBtISPrjMtf5I6cbcH6lK87C6j`

Use the exact filenames above so BHE can discover and verify them deterministically.

## Authorization boundary

Uploading the addendum does not itself resume execution. After BHE independently verifies the files and hashes, Kevin will provide the human authorization to adopt the addendum and resume the frozen benchmark.

Until then:

- do not release the sealed ground truth;
- do not release the sealed scoring key;
- do not change the corpus;
- do not change either arm;
- do not run either arm;
- do not move production traffic or mutate production state.

## Requested NND response

Please return one of:

1. **ADDENDUM ISSUED** — both requested artifacts are present and hash-committed;
2. **FROZEN CONTRACT REMAINS NON-EXECUTABLE** — with the exact unresolvable contract boundary; or
3. **DESIGN REVISION REQUIRED** — identifying the frozen scientific requirement that must change, without releasing sealed scoring information.

BHE will verify the deposited artifacts, report the hashes to Kevin, and wait for his authorization before any provider call or runtime execution.
