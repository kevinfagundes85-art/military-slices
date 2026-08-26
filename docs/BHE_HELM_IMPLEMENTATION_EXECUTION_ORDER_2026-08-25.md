# BHE Execution Order — HELM Minimum Governed Implementation

**Date:** 2026-08-25  
**Status:** Ready for independent HELM Architect classification  
**Canonical basis:** `HELM_BHE_BOOTSTRAP_2026-08-25.zip`  
**Bootstrap SHA-256:** `041F398A06876DCA1077018C8DA38942485D87CA095B049563A8FB417D9FA489`  
**Implementation baseline:** Military SLICES commit `0d8e6e83a6ee4a271f42a29004ac57368295c657`  
**Target:** Smallest working implementation capable of bounded client validation  

## 1. Executive disposition

The current Military SLICES application is a viable implementation substrate. It should be hardened in place, not replaced and not split into new services.

It already supplies:

- a single deployable application;
- signed user-session isolation;
- persistent Firestore profile state and version history;
- optimistic concurrency and request idempotency;
- human decision Gates;
- separate hypothetical branches with explicit promotion;
- deterministic temporal revalidation;
- bounded Gemini/ADK context with deterministic fallback;
- controlled artifact ingestion;
- evidence-grounded career hypotheses;
- mobile and accessibility regressions.

The current implementation does **not yet prove** the complete frozen HELM contract. The blocking gaps are:

1. immutable Domain Pack identity, activation, compatibility, and historical pinning;
2. trusted actor/event provenance on every governed mutation;
3. hierarchical Gate scope and authority containment;
4. an explicit Authority Governor decision separate from Resolver proposals;
5. deterministic dependency lineage and fail-closed lineage/index integrity;
6. restart-safe external-effect reconciliation before any real-world action is permitted;
7. a cumulative HELM Probe budget before autonomous dormant-state examination is permitted.

The minimum client-validation implementation therefore keeps the existing Cloud Run/Firestore application, closes items 1–5, explicitly disables external effects and autonomous Probe execution, migrates existing records without inventing lineage, and proves one end-to-end military-transition decision path plus adversarial safety fixtures.

No Kubernetes, microservices, multi-agent topology, vector database, event bus, new cloud provider, or model migration is required.

## 2. Governing constraints

The implementation must preserve these frozen invariants:

- A Slice observes only its permitted projection of governed state.
- A Resolver proposes; it does not authorize or mutate.
- The Authority Governor decides whether a proposed transition is permitted.
- Human authority cannot be inferred from model output or from mere relevance.
- Historical, Hypothetical, and Latent state never silently become Canonical.
- Child Gates cannot expand the scope or authority of their parent.
- Authorization is bound to the canonical version evaluated.
- Every canonical mutation is replay-safe, conflict-detecting, provenance-bearing, and reconstructable.
- Missing, stale, conflicting, or unverifiable required lineage fails closed.
- External effects are forbidden until a durable action ledger and reconciliation path exist.
- Autonomous examination is forbidden until a cumulative, inherited, non-expandable Probe budget exists.
- Audit evidence records governed inputs, rules, decisions, and state deltas—not hidden chain-of-thought.
- Client policy values are Domain Pack inputs. Engineering may not invent them.

## 3. Current implementation truth

| Contract area | Existing evidence | Disposition |
|---|---|---|
| Persistent governed state | `CanonicalState`, Firestore current document plus version subcollection | Reuse with additive contract metadata |
| Concurrency | `expected_version` checks and Firestore transaction | Reuse; bind authorization and mutation event to the evaluated version |
| Replay safety | `idempotency_key` and `processed_keys` | Reuse; replace/augment the unstructured key list with durable mutation-event records |
| User isolation | Signed session profile ownership and isolation tests | Reuse; add trusted actor/auth provenance |
| Human decisions | `/api/decision`, Gate state, Decision records | Reuse; enforce through Authority Governor |
| Hypothetical state | Read-only what-if branch plus explicit promotion | Reuse; add governed state category and source-version lineage |
| Latent observation | Deterministic Lens projections and latent facts | Reuse; keep observation non-authoritative |
| Temporal validity | freshness classes, impact evaluation, revalidation | Reuse; add explicit `valid_while`/`invalidated_by` lineage |
| Resolver | deterministic and ADK/Gemini career Resolver, bounded context, fallback | Reuse; prohibit direct mutation and add Governor evaluation |
| Gate model | state, question, surface, authority, dependencies | Harden with parent, scope, authority-set, construction provenance, source version |
| Domain semantics | transition pack version string and source manifest | Harden into immutable Domain Pack identity and activation record |
| Lineage | evidence IDs, dependencies, version history | Partial; add deterministic structural lineage and integrity status |
| External effects | no real-world action endpoint found | Preserve disabled; ledger required before enabling |
| Probe | no autonomous HELM Probe execution found | Preserve disabled; budget contract required before enabling |

## 4. Ordered build sequence

### E00 — Lock the implementation baseline and build a canonical conformance matrix

- **Objective:** Establish a reproducible starting point and classify every existing runtime behavior against the frozen HELM specification before changing semantics.
- **Dependency:** None.
- **Applicable HELM contract:** Full Specification §§23, 26; Canonical Lock Record; BHE-to-Architect handoff protocol.
- **State/data affected:** No runtime data. Evidence only: commit, dependency lock, configuration names, schema snapshot, route inventory, test inventory, deployment revisions.
- **Enforcement point:** CI evidence job and checked-in conformance matrix.
- **Failure behavior:** Stop implementation if the baseline cannot be reproduced or if protected production differs from the recorded revision/configuration.
- **Authoritative source:** `CANONICAL_LOCK_RECORD.md`; `FULL_STANDALONE_SPEC.md` §§23 and 26; repository commit `0d8e6e8`.
- **Implementation class:** Audit / reuse decision.
- **Test/evidence to close:** Clean repository; exact commit and dependency hashes; current schema snapshot; route-to-contract matrix; full existing suite green; production and zero-traffic candidate identities recorded without changing traffic.
- **Client decision:** None.

### E01 — Freeze the first validation fixture and policy decision register

- **Objective:** Define the smallest client-visible target event without silently choosing eligibility, evidence, approval, retention, or automation policy.
- **Dependency:** E00.
- **Applicable HELM contract:** Full Specification §§1–3, 5 (Anchor/Path/Slice/Gate), 23; Amendment 008 (Domain Pack governance).
- **State/data affected:** Test fixtures and a decision register only; no user profile mutation.
- **Enforcement point:** Acceptance-fixture loader and Domain Pack activation preflight.
- **Failure behavior:** Engineering may use synthetic `DRAFT` fixtures, but no Domain Pack becomes active and no production policy conclusion is emitted until required client decisions are authenticated.
- **Authoritative source:** `CLIENT_FEEDBACK_AND_REQUIREMENTS.md` (client acceptance standard, current implementation context, unresolved feedback); Amendment 008.
- **Implementation class:** Test definition / client Gate.
- **Test/evidence to close:** One positive fixture, one ambiguity fixture, one contradiction fixture, one cross-user fixture, and one replay/concurrency fixture. Recommended first path: career/résumé readiness ending in a human-adjudicated next step, with no external application submission.
- **Client decision:** **HG-01** validation journey and target event; **HG-02** Domain Pack policy owner/approver; **HG-03** required evidence and acceptance thresholds; **HG-04** retention period; **HG-05** whether any external effect is in scope. Default until answered: synthetic validation only, no external effects.

### E02 — Add the governed contract spine additively

- **Objective:** Represent frozen HELM identity and state semantics without breaking existing profiles.
- **Dependency:** E00; may proceed in parallel with unresolved client policy because values remain `DRAFT`/unknown.
- **Applicable HELM contract:** Full Specification §§4, 12, 17–19, 22; Amendment 007; Amendment 008.
- **State/data affected:** Additive models for `DomainPackRef`, `MutationEvent`, `ActorProvenance`, `LineageRecord`, `MigrationStatus`, and explicit governed-state category. Existing `CanonicalState` fields remain readable.
- **Enforcement point:** Pydantic validation at ingress/load and mutation command construction.
- **Failure behavior:** Reject malformed new records. Load legacy records only as `LEGACY_VALID`; do not infer missing historical provenance or lineage.
- **Authoritative source:** Full Specification §§4, 12, 17–19, 22; Amendment 008 identity/versioning and no-silent-reinterpretation rules.
- **Implementation class:** Additive schema hardening.
- **Test/evidence to close:** Round-trip serialization; old-state load; unknown-field rejection; all four state categories remain distinct; legacy records receive a migration status without fabricated facts; malformed pack/provenance/lineage fails closed.
- **Client decision:** None for schema. Pack activation fields remain unapproved until HG-02/HG-03.

### E03 — Bind trusted actor and event provenance at the control plane

- **Objective:** Ensure every human correction and governed mutation identifies a trusted actor, authentication context, source system, event, and time.
- **Dependency:** E02.
- **Applicable HELM contract:** Full Specification §12 and §21; Amendment 007 §3.
- **State/data affected:** Mutation-event provenance and audit receipt. Do not store credentials or session secrets.
- **Enforcement point:** Server-side authenticated request boundary before orientation confirmation, artifact application, human decision, revalidation, or what-if promotion reaches the engine.
- **Failure behavior:** Read-only/stateless orientation may continue where already allowed; any governed write with absent, untrusted, mismatched, or cross-user provenance fails closed.
- **Authoritative source:** Full Specification §§12 and 21; existing signed-session ownership contract.
- **Implementation class:** Security hardening / reuse of current session boundary.
- **Test/evidence to close:** Forged profile ID, absent session, altered session, replayed event, cross-user event, and authenticated human correction tests; logs prove no secret or raw artifact bytes are recorded.
- **Client decision:** Identity-provider choice is not required for the first implementation. Existing signed session may remain the trusted local control plane for client validation.

### E04 — Convert the transition pack into an immutable Domain Pack contract

- **Objective:** Pin every executable domain rule to an immutable, approved, compatible Domain Pack version and hash.
- **Dependency:** E02; activation depends on HG-02/HG-03.
- **Applicable HELM contract:** Amendment 008 in full; Full Specification §§6, 10, 15–17, 23.
- **State/data affected:** Domain Pack manifest with `domain_pack_id`, semantic version, content hash, HELM compatibility version, approval event, effective date, status, rule enforcement metadata, and source freshness. Profile state stores the exact reference used.
- **Enforcement point:** Application startup, profile load/reconstitution, rule evaluation, and canonical mutation authorization.
- **Failure behavior:** Missing hash, incompatible version, unapproved status, unknown rule, stale required source, or historical-version unavailability blocks the affected transition. It does not fall back to the newest pack.
- **Authoritative source:** Amendment 008; existing transition-pack source manifest is evidence input, not activation authority.
- **Implementation class:** Domain Pack hardening.
- **Test/evidence to close:** Hash determinism; tamper rejection; PATCH/MINOR/MAJOR compatibility matrix; historical profile stays pinned; retired version remains loadable; major upgrade requires migration/revalidation; every authoritative rule has enforcement point, failure behavior, and source.
- **Client decision:** HG-02/HG-03. Until approval, the existing `2026-08-24-v2-shadow-tested` pack is `DRAFT` or `LEGACY_VALID`, not silently elevated to activated canonical policy.

### E05 — Define bounded Slice manifests and governed projections

- **Objective:** Make each Slice consume only the smallest permitted state projection and prevent direct Slice-to-Slice authority transfer.
- **Dependency:** E02 and E04 identity shape; does not require pack activation.
- **Applicable HELM contract:** Full Specification §§2–5 and §25; Amendment 008 (Slice relationship and cross-domain integrity).
- **State/data affected:** Versioned Slice manifest: accepted projection fields, permitted Gate families, emitted candidate types, governed conclusions, and explicit cross-domain interfaces.
- **Enforcement point:** Projection builder before Resolver invocation and before rendering the active interaction.
- **Failure behavior:** Undeclared fields are omitted. A required but unauthorized field produces `context_needed`/human clarification, not broad profile serialization. Cross-domain conclusions without a governed interface remain unavailable.
- **Authoritative source:** Full Specification §5 (Slice) and §25; Amendment 008 cross-domain integrity; client requirement for independent Slice entry over shared governed state.
- **Implementation class:** Boundary hardening.
- **Test/evidence to close:** Projection allowlist tests; field-leakage tests; Career, Résumé, Education, and Relocation can enter independently; one Slice cannot consume another Slice's internal context; hypothetical/latent facts cannot appear as canonical inputs.
- **Client decision:** None for the boundary. Which optional Slices are included in the first client fixture is part of HG-01.

### E06 — Harden Gate identity, composition, and authority containment

- **Objective:** Make every Gate deterministic, scope-bounded, source-version-bound, and safe under factoring.
- **Dependency:** E02, E04, E05.
- **Applicable HELM contract:** Full Specification §§5, 7, 13, 18–19; Amendment 007 §1.
- **State/data affected:** Gate adds deterministic identity, `parent_gate_id`, `authorized_scope`, `authority_set`, construction provenance, source-state version, required evidence, legal transitions, and resolution event.
- **Enforcement point:** Gate constructor/factory and Authority Governor preflight; no ad hoc Gate construction in UI or model code.
- **Failure behavior:** Child scope or authority outside the parent fails closed. Unknown Gate identity, illegal transition, stale source version, or missing evidence cannot mutate canonical state.
- **Authoritative source:** Full Specification §§5 and 7; Amendment 007 §1.
- **Implementation class:** Core contract hardening.
- **Test/evidence to close:** Deterministic identity; legal transition table; parent/child subset property tests; union-of-children containment; duplicate/replay behavior; stale Gate rejection; human-only Gate cannot be machine-closed; adversarial synthetic sub-Gate authority escalation fails.
- **Client decision:** Threshold/evidence values for domain Gates come from HG-03. Unknown values keep those Gates unresolved.

### E07 — Separate Resolver proposals from Authority Governor decisions

- **Objective:** Ensure deterministic or Gemini/ADK Resolvers can nominate candidates but cannot authorize, persist, or expand scope.
- **Dependency:** E05 and E06.
- **Applicable HELM contract:** Full Specification §§2, 3, 5 (Resolver and Authority Governor), 20, 23.
- **State/data affected:** Ephemeral `ResolverProposal`; persisted `GovernorDecision`/receipt only when a governed transition occurs.
- **Enforcement point:** Application service between Resolver return and mutation command. Existing Resolver remains in-process; no service split is required.
- **Failure behavior:** Invalid schema, unsupported inference, provider disagreement, missing authority, stale state, or proposal outside the Slice/Gate scope yields reject, clarification, or unresolved inference. Deterministic fallback cannot silently increase authority.
- **Authoritative source:** Full Specification §§3, 5, 20, 23; existing bounded resolver context and fallback behavior.
- **Implementation class:** Architectural separation inside the current monolith.
- **Test/evidence to close:** Resolver has no store dependency; model output cannot close human Gate; rejected role remains excluded; provider disagreement remains unresolved; prompt-injection artifact remains data; out-of-scope proposal is rejected; deterministic fallback preserves the same authority ceiling.
- **Client decision:** None.

### E08 — Make canonical mutation, lineage, and derived-state integrity one transaction

- **Objective:** Persist a canonical state transition, its provenance, dependency lineage, idempotency record, and audit receipt atomically.
- **Dependency:** E02–E07.
- **Applicable HELM contract:** Full Specification §§6, 10, 13, 15–19, 22; Amendment 007 additional hardening.
- **State/data affected:** Current profile aggregate, immutable mutation event, version history, `depends_on`, `valid_while`, `invalidated_by`, source versions, derived-index version/hash, and conflict status.
- **Enforcement point:** The existing Firestore transaction and equivalent in-memory test store.
- **Failure behavior:** Version mismatch returns a clear conflict; duplicate event returns the prior/current governed result without another side effect; required stale/unverifiable lineage or derived index blocks the dependent transition; lineage conflict suspends affected transitions and surfaces an authorized conflict Gate.
- **Authoritative source:** Full Specification §§6, 10, 13, 15–19, 22.
- **Implementation class:** Persistence hardening / reuse of existing CAS store.
- **Test/evidence to close:** Concurrent writers; lost-response replay; duplicate event; partial-write injection; deterministic reconstruction; stale index; missing lineage; conflicting human/source claims; unrelated profile isolation; no duplicate version/history/event.
- **Client decision:** None.

### E09 — Materialize the minimum governed military-transition path

- **Objective:** Prove one real interaction from accepted human input to a bounded, human-adjudicated next step using the hardened contracts.
- **Dependency:** E01 and E03–E08. Production activation additionally requires HG-02/HG-03.
- **Applicable HELM contract:** Full Specification §§1–7, 12–13, 18–23; client acceptance standard and interaction requirements.
- **State/data affected:** Anchor, Path target, minimum Slice projection, one active Gate at a time, reviewed evidence, candidate hypotheses, human decision, state delta, and causal receipt.
- **Enforcement point:** Existing `/api/orient`, `/api/artifact`, `/api/confirm`, `/api/decision`, recomputation, and adaptive foreground projection—behind a compatibility/feature flag until migration is validated.
- **Failure behavior:** Ambiguous input asks one smallest useful question. Contradiction surfaces a conflict Gate. Missing target role remains unresolved. No evidence silently becomes capability, qualification, or résumé truth. No action proceeds past the declared target event.
- **Authoritative source:** Full Specification control loop and core components; `CLIENT_FEEDBACK_AND_REQUIREMENTS.md`; approved Military SLICES transition Domain Pack once activated.
- **Implementation class:** Vertical integration using existing UI/backend.
- **Test/evidence to close:**
  - fresh career/résumé readiness intent satisfies the Anchor and routes to the missing target-role Gate;
  - ordinary TXT/DOCX/PDF/PNG/JPG artifact input is accepted under the existing bounded artifact contract;
  - deliberate upload is treated as authority to use that artifact for the bounded path, while extraction alone does not manufacture unsupported facts;
  - unknown/mixed input produces one clarification and zero governed writes before confirmation;
  - rejection changes later reasoning and persists through reload;
  - résumé output is server-gated by target role and grounded evidence;
  - cancel, corrupt, oversize, unsupported, stale, and replay paths behave safely;
  - no external action occurs.
- **Client decision:** HG-01 and HG-03. If thresholds remain unresolved, demonstrate with synthetic `DRAFT` rules and label the result non-production.

### E10 — Prove cross-domain subject integrity and independent Slice entry

- **Objective:** Show shared governed state can inform multiple bounded Slices without direct Slice orchestration or subject confusion.
- **Dependency:** E05–E09.
- **Applicable HELM contract:** Full Specification §§4–7, 11, 15; Amendment 008 cross-domain integrity; client independent-entry requirement.
- **State/data affected:** `planning_actor`, `military_state_subject`, governed cross-domain conclusions, and Slice-specific projections.
- **Enforcement point:** Orientation/normalization, Domain Pack rules, projection builder, and Governor.
- **Failure behavior:** If actor and military subject are unclear, ask one clarification. Never assign the service member's separation milestones to a spouse planner. Relevance to one Slice does not activate another.
- **Authoritative source:** Full Specification Slice/Gate/lineage contracts; client population includes veterans and spouses; existing spouse/PCS regression.
- **Implementation class:** Existing behavior hardening and contract proof.
- **Test/evidence to close:** Spouse/PCS fixture; veteran fixture; active-duty member fixture; mixed household fixture; Relocation-first and Education-first entry; no broad profile leakage; cross-Slice conclusion is minimum and provenance-tagged; no direct agent-to-agent call.
- **Client decision:** Exact eligibility conclusions remain Domain Pack policy under HG-03.

### E11 — Reconstitute, migrate, and audit without manufacturing history

- **Objective:** Make restart, resume, rollback, and legacy-profile handling deterministic and explainable.
- **Dependency:** E02, E04, E06, E08.
- **Applicable HELM contract:** Full Specification §§16–19, 21–22; Amendment 008 no silent reinterpretation.
- **State/data affected:** Migration status, pack pin, lineage integrity, active Gate, pending conflict, mutation history, and reconstitution receipt.
- **Enforcement point:** Store load/reconstitution before any UI projection or Resolver call.
- **Failure behavior:** Existing records become `LEGACY_VALID`, `LINEAGE_ENRICHED`, `LINEAGE_INCOMPLETE`, or `REVALIDATION_REQUIRED` based only on reproducible evidence. Missing required history reduces authority and may request revalidation; it never invents certainty.
- **Authoritative source:** Full Specification §§16–18, 22; Amendment 008 historical pinning.
- **Implementation class:** Migration / restart hardening.
- **Test/evidence to close:** Golden legacy fixtures; restart at each Gate state; deterministic byte/semantic reconstruction; missing history; retired pack; major pack upgrade; rollback to prior application revision with schema compatibility; human correction provenance survives reconstitution.
- **Client decision:** Retention and deletion behavior require HG-04 before production policy is finalized.

### E12 — Enforce dormant boundaries for external effects and HELM Probe

- **Objective:** Ensure unimplemented high-risk capabilities cannot be reached accidentally while preserving a clear implementation boundary.
- **Dependency:** E00; guard tests should land early. Full implementations are not dependencies of the first no-effect validation path.
- **Applicable HELM contract:** Full Specification §§8–9, 11, 14, 22; Amendment 007 §§2 and 4.
- **State/data affected:** Capability flags and explicit unsupported-state receipts only. No external-effect or Probe state is created in the minimum path.
- **Enforcement point:** Route registry, Governor, background-job registry, and deployment configuration.
- **Failure behavior:** Any requested external action returns a human-readable unavailable/authorization-required result and performs zero dispatches. Any autonomous dormant-state examination request is denied because no cumulative Probe budget exists.
- **Authoritative source:** Full Specification §§8–9, 11, 14; Amendment 007 §§2 and 4.
- **Implementation class:** Fail-closed guard now; feature implementation deferred.
- **Test/evidence to close:** Route/config scan; monkeypatched network client proving zero dispatch; no background scheduler; no Probe recursion; negative tests for hidden/retry paths.
- **Client decision:** HG-05. If external effects are later approved, implement the full durable ledger (`PLANNED → AUTHORIZED → DISPATCHED → EFFECT_CONFIRMED → STATE_COMMITTED`, with reconciliation states) before enabling them. If autonomous examination is later approved, implement inherited non-expandable depth/time/candidate/examination/compute budgets and flood controls first.

### E13 — Run the falsification and client-validation release Gate

- **Objective:** Attempt to disprove boundedness, authority containment, provenance integrity, persistence safety, and client usability before human validation.
- **Dependency:** E00–E12, except deferred full external-effect and Probe implementations.
- **Applicable HELM contract:** Full Specification §§23–24; BHE operating brief; client acceptance standard.
- **State/data affected:** Test/evidence artifacts only; zero-traffic candidate deployment after local validation.
- **Enforcement point:** CI, hosted candidate checks, log review, and human validation script.
- **Failure behavior:** Any contract failure blocks candidate promotion. Unknown-unknown protection is not claimed; discovered counterexamples are classified and routed under change control.
- **Authoritative source:** Full Specification §§23–24 and §26; `BHE_TO_HELM_ARCHITECT_HANDOFF.md`.
- **Implementation class:** Validation / release evidence.
- **Test/evidence to close:**
  - full legacy suite;
  - schema/migration tests;
  - property tests for Gate containment;
  - concurrency, replay, partial failure, and restart tests;
  - actor/session and second-user isolation;
  - provider disagreement and prompt injection;
  - stale/contradictory evidence and lineage;
  - pack tamper/compatibility/retirement;
  - unknown, mixed, and insufficient-context paths;
  - Career/résumé, spouse/PCS, Relocation-first, and Education-first fixtures;
  - mobile widths, keyboard/focus, native picker, and accessibility;
  - audit receipts contain sources/rules/decision/delta but no chain-of-thought;
  - production traffic unchanged and immediate rollback preserved.
- **Client decision:** Physical-device, cold-user, founder-convergence, real-second-account, and policy-acceptance Gates remain honestly human-only.

## 5. Minimum implementation path

The smallest safe path is:

1. **E00** lock and audit the existing implementation.
2. **E01** freeze a no-external-effect validation fixture and decision register.
3. **E02–E04** add the governed schema, trusted provenance, and immutable Domain Pack reference.
4. **E05–E07** enforce Slice projection, Gate containment, and Resolver/Governor separation.
5. **E08** atomically persist mutation, provenance, lineage, idempotency, and history.
6. **E09** run the career/résumé readiness vertical slice to a human-adjudicated next step.
7. **E10** prove spouse/PCS subject integrity and one independent alternate Slice entry.
8. **E11** prove migration, restart, and deterministic reconstitution.
9. **E12** keep external effects and autonomous Probe execution disabled.
10. **E13** falsify, deploy a zero-traffic candidate, and stop at the human Gates.

This path demonstrates HELM's control contracts without pretending to implement every domain or autonomous capability.

## 6. First human/client Gates

| Gate | Binary question | Required before | Default if unanswered |
|---|---|---|---|
| HG-01 Validation target | Is the first accepted client journey career/résumé readiness ending in a human-approved next step? | Final fixture acceptance | Use synthetic fixture only; no production acceptance claim |
| HG-02 Pack authority | Who is authorized to approve the exact Military Transition Domain Pack version/hash? | Domain Pack activation | `DRAFT`/`LEGACY_VALID`; no activated-policy claim |
| HG-03 Policy values | What eligibility, required evidence, approval thresholds, and consequence rules govern the chosen journey? | Production domain conclusions | Remain UNKNOWN; affected Gate stays open |
| HG-04 Retention | What are the retention/deletion periods for governed profile state, evidence text, audit events, and version history? | Production data-policy acceptance | Preserve current bounded behavior; do not promise a retention policy |
| HG-05 External effects | Does the client authorize any application submission, message, booking, or other real-world effect? | Any external action implementation | No external effects; zero dispatch |
| HG-06 Human validation | Does the zero-traffic candidate pass physical Android, native picker, cold-user comprehension, adult-tone, persistence, and real-second-account isolation? | Traffic promotion | Candidate remains at zero traffic |

## 7. Unresolved-policy boundary

Work may proceed autonomously through:

- baseline conformance evidence;
- additive schemas;
- deterministic validation and migration tooling;
- trusted session-to-provenance binding;
- Slice/Gate/Governor/lineage enforcement;
- synthetic and read-only fixtures;
- a zero-traffic candidate using a clearly non-activated `DRAFT` pack;
- fail-closed guards for external effects and Probe execution.

Work must stop before:

- activating the Military Transition Domain Pack without an authenticated approver and exact version/hash;
- inventing eligibility, required evidence, approval thresholds, or consequences;
- silently reinterpreting historical profiles under a new pack;
- dispatching any real-world effect without the complete action ledger and HG-05;
- running autonomous dormant-state examination without cumulative Probe budgets;
- promoting traffic before HG-06.

This is a **Domain Pack/client-input boundary**, not evidence of a HELM architecture gap.

## 8. Counterexample and falsification register

| Counterexample | Expected frozen-contract handling | Architecture status |
|---|---|---|
| A spouse enters a PCS date and the system treats it as the spouse's separation date | Preserve actor/subject distinction; ask if ambiguous; bind fact to relocation lineage only | Governable by current architecture; Slice/Domain Pack implementation issue |
| A résumé contains instructions to the model | Treat artifact as untrusted evidence data; Resolver cannot gain authority | Governable; security/enforcement test |
| A child Gate asks for more authority than its parent | Constructor/Governor rejects the child and all dependent transitions | Governable; Gate hardening required |
| A newer Domain Pack changes eligibility for an old profile | Historical state remains pinned; MAJOR migration/revalidation required | Governable; Domain Pack hardening required |
| Model providers disagree on a career conclusion | Persist unresolved inference/conflict; no vote and no silent fallback authority | Governable; Governor behavior required |
| A network call succeeds but acknowledgement is lost | No external call in MVP; later action ledger reconciles before retry | Governable; feature intentionally disabled |
| A required lineage index is stale | Fail closed and reconstitute/revalidate deterministically | Governable; lineage/index hardening required |
| A novel interaction falls outside all known effect dimensions | Do not claim protection; capture counterexample and route through change control | Explicit unknown-unknown limitation, not silently solved |

No counterexample found in the supplied client requirements forces a new top-level HELM concept. If implementation evidence later proves otherwise, stop only that branch and return the smallest reproducible counterexample to HELM Architect under §26 change control.

## 9. First executable engineering task

Create one failing contract-test module before runtime changes:

`tests/test_helm_governance_contract.py`

Its first tests should prove:

1. a legacy profile loads only as `LEGACY_VALID` and receives no invented provenance;
2. a Domain Pack reference with a changed payload and unchanged hash/version is rejected;
3. a child Gate cannot exceed its parent's scope or authority set;
4. a Resolver proposal cannot mutate or close a human Gate;
5. a mutation with an untrusted actor or stale source version fails closed;
6. a duplicate mutation event does not create a second state version;
7. external-effect and autonomous-Probe entry points are disabled.

Then add the minimum additive contract models needed to make those tests pass. Do not touch the primary UI in this task.

## 10. HELM Architect handoff ledger

HELM Architect should independently classify each item using the accepted protocol.

| Item | BHE intent | Suggested review focus | Architect classification |
|---|---|---|---|
| E00 | Freeze facts before change | Enforcement closure and reproducibility | Pending |
| E01 | Keep policy choices explicit | Domain Pack vs architecture boundary | Pending |
| E02 | Add governed contract spine | Canonical categories and migration semantics | Pending |
| E03 | Trust provenance only at control plane | Authenticated provenance | Pending |
| E04 | Immutable Domain Pack activation | Amendment 008 compliance | Pending |
| E05 | Minimum Slice projections | No direct cross-Slice authority | Pending |
| E06 | Gate factoring containment | Composition invariant | Pending |
| E07 | Resolver/Governor separation | Model authority ceiling | Pending |
| E08 | Atomic mutation and lineage | TOCTOU, replay, conflicts, reconstruction | Pending |
| E09 | Minimum client-visible path | Stop-at-target and human adjudication | Pending |
| E10 | Cross-domain subject integrity | Shared state without broad serialization | Pending |
| E11 | Restart/migration truthfulness | No manufactured history | Pending |
| E12 | Disable unsafe unimplemented capabilities | Action ledger and Probe budget boundary | Pending |
| E13 | Attempt falsification before promotion | Evidence sufficiency and unknown unknowns | Pending |

Allowed classifications are: `ACCEPT`, `ACCEPT WITH HARDENING`, `REORDER`, `DOMAIN PACK ISSUE`, `SLICE ISSUE`, `INFRASTRUCTURE OVERREACH`, `CONTRACT GAP`, or `POSSIBLE ARCHITECTURE GAP`.

For any non-`ACCEPT` classification, HELM Architect should state the canonical section, smallest correction, and whether downstream work may continue. Infrastructure substitutions must not be treated as conceptual HELM amendments.

## 11. Completion definition

This implementation order is complete when:

- the frozen contracts are represented and enforced at explicit boundaries;
- the chosen client journey works end to end without invented policy or authority;
- ambiguity and contradiction fail safely and visibly;
- every mutation is authenticated, version-bound, replay-safe, lineage-bearing, and reconstructable;
- the active Domain Pack is exact, immutable, approved, and historically pinned;
- model proposals remain bounded and non-authoritative;
- external effects and autonomous Probe work remain unreachable until their full contracts exist;
- automated falsification is green;
- a zero-traffic candidate is ready;
- all genuinely human-only Gates remain open until humans perform them.

Passing this milestone proves a bounded client-validation implementation. It does not prove universal safety, complete domain coverage, or protection from unknown unknowns.
