"""
Whole-Lifecycle HELM v2 Benchmark — Deterministic corpus, ground-truth, and control-schedule generator.
Contract ID: helm-whole-lifecycle-v2-2026-08-27
Pinned commit: d968c15da3447c311f3322e1805bc8067383c29f
Domain Pack: military-transition / 2026-08-24-v2-shadow-tested
  SHA-256: 026a1508a3a2e6eb16907b2e8fc29c4f333af5c5ab908e6029903b8cbcbf9f4c

All enum values taken verbatim from helm_runtime_contract_snapshot_2026-08-27.json
No enum value is invented.

LifecyclePosition: unknown | currently_serving | leaving_within_12_months |
                   separated_within_last_year | separated_1_to_5_years |
                   separated_more_than_5_years
Authority: human | authoritative_source | deterministic_rule | bounded_agent
FreshnessStatus: valid | stale
FreshnessClass: stable | slow | volatile | external_expiring
GateState: YES | NO | PARTIAL | UNKNOWN | CONFLICTED
PlanningActor: unknown | service_member | veteran | military_spouse | counselor_supporter
MilitaryStateSubject: unknown | planning_actor | planning_actor_spouse | supported_person
ServiceName: army | navy | marine_corps | air_force | space_force | coast_guard
ServiceComponent: active_duty | reserve | national_guard
SliceName: career | education | location | resume
StateCategory: canonical | historical | hypothetical | latent | active
"""

import json, hashlib, random, uuid

random.seed(20260827_2)  # New seed for v2 package

CONTRACT_ID = "helm-whole-lifecycle-v2-2026-08-27"
SNAPSHOT_SHA256 = "bc3586b5f2e094a35dae33b1c17e53c53a3284934057c96b7d5aeab5133120e7"
DOMAIN_PACK_SHA256 = "026a1508a3a2e6eb16907b2e8fc29c4f333af5c5ab908e6029903b8cbcbf9f4c"
DOMAIN_PACK_VERSION = "2026-08-24-v2-shadow-tested"
SOURCE_COMMIT = "d968c15da3447c311f3322e1805bc8067383c29f"

def stable_id(prefix, seed_str):
    return prefix + "-" + hashlib.sha256(seed_str.encode()).hexdigest()[:16]

def fact_id(task_id, event_idx, content):
    return stable_id("F", f"{task_id}|{event_idx}|{content}")

def lineage_id(task_id, fact_id_str):
    return stable_id("L", f"{CONTRACT_ID}|{task_id}|{fact_id_str}")

def control_event_id(task_id, wave, kind):
    return stable_id("CE", f"{task_id}|{wave}|{kind}")

TASKS = []
GROUND_TRUTH = {}
CONTROL_SCHEDULE = {}

# ---- Scenario templates ----
# Each template specifies: scenario prose, subject lifecycle, governed coordinates,
# mechanism exercised, and ground-truth outcome.

def mk_task(tid, scenario_label, lifecycle, service, planning_actor, separation_type,
            gate_id, gate_question, effect_dimension, path_target,
            events, gt_outcome, mechanism, control_events=None):
    """
    events: list of dict with keys:
      wave, kind (fact|human_review_request),
      statement, value, authority, freshness_status, freshness_class,
      field_key, affected_slices, state_category, is_latent,
      supersedes (optional fact_id), arm_b_equivalent
    """
    anchor = f"WLB2-ANCHOR-{tid}"
    task_facts = []
    arm_b_turns = []
    gt_facts = []

    for i, ev in enumerate(events):
        fid = fact_id(tid, i, ev['statement'])
        lin = lineage_id(tid, fid)
        task_facts.append({
            "event_index": i,
            "wave": ev['wave'],
            "kind": ev['kind'],
            "fact": {
                "id": fid,
                "statement": ev['statement'],
                "value": ev['value'],
                "authority": ev['authority'],
                "status": ev['freshness_status'],
                "freshness_class": ev['freshness_class'],
                "field_key": ev['field_key'],
                "affected_slices": ev['affected_slices'],
                "state_category": ev['state_category'],
            } if ev['kind'] == 'fact' else None,
            "lineage_seed": lin,
            "is_latent": ev.get('is_latent', False),
            "supersedes": ev.get('supersedes'),
            "arm_b_equivalent": ev['arm_b_equivalent'],
        })
        if ev['kind'] == 'fact':
            gt_facts.append(fid)
        arm_b_turns.append({
            "wave": ev['wave'],
            "kind": ev['kind'],
            "text": ev['arm_b_equivalent'],
        })

    task = {
        "task_id": tid,
        "scenario_label": scenario_label,
        "canonical_state_seed": {
            "lifecycle_position": lifecycle,
            "service": service,
            "planning_actor": planning_actor,
            "separation_type": separation_type,
            "military_state_subject": "planning_actor",
            "human_anchor": anchor,
            "path_target_state": path_target,
            "domain_pack": {
                "domain_pack_id": "military-transition",
                "version": DOMAIN_PACK_VERSION,
                "content_hash": DOMAIN_PACK_SHA256,
            },
        },
        "gate": {
            "id": gate_id,
            "question": gate_question,
            "effect_dimension": effect_dimension,
            "authority_required": "human",
        },
        "events": task_facts,
        "arm_b_turns": arm_b_turns,
        "mechanism": mechanism,
    }
    TASKS.append(task)

    gt = {
        "task_id": tid,
        "mechanism": mechanism,
        "correct_terminal_outcome": gt_outcome['terminal'],
        "correct_probe_nominations": gt_outcome.get('nominations', []),
        "correct_governed_rejections": gt_outcome.get('rejections', []),
        "correct_governed_acceptances": gt_outcome.get('acceptances', []),
        "invalidation_events": gt_outcome.get('invalidations', []),
        "earlier_rejection_becomes_wrong": gt_outcome.get('stale_suppression_test', False),
        "i1_suppression_expected": gt_outcome.get('i1_hits', 0),
        "graduation_expected": gt_outcome.get('graduation', False),
        "restart_expected": gt_outcome.get('restart', False),
        "harm_mapping": gt_outcome.get('harm_mapping', {}),
        "material_fact_ids": gt_facts,
        "scoring_notes": gt_outcome.get('notes', ''),
    }
    GROUND_TRUTH[tid] = gt

    if control_events:
        CONTROL_SCHEDULE[tid] = {
            "task_id": tid,
            "mechanism": mechanism,
            "control_events": [
                {
                    "event_id": control_event_id(tid, ce['wave'], ce['kind']),
                    "wave": ce['wave'],
                    "kind": ce['kind'],
                    "prerequisite_wave_output_committed": True,
                    "gate_id": gate_id,
                    "response": ce['response'],
                    "authoritative_statement": ce.get('authoritative_statement'),
                    "validity_conditions": ce.get('validity_conditions', []),
                    "invalidation_conditions": ce.get('invalidation_conditions', []),
                    "arm_b_equivalent": ce['arm_b_equivalent'],
                }
                for ce in control_events
            ]
        }
    return tid

# ---- Scenario corpus ----
# Abbreviated representative set — full 100+ task corpus follows the same pattern.
# Each task is fully structured; no prose inference by Arm H is permitted.

TASK_COUNTER = 0

def next_tid():
    global TASK_COUNTER
    TASK_COUNTER += 1
    return f"WLB2-{TASK_COUNTER:04d}"

SERVICES = ["army","navy","marine_corps","air_force","space_force","coast_guard"]
LIFECYCLES_SERVING = ["currently_serving","leaving_within_12_months"]
LIFECYCLES_SEP = ["separated_within_last_year","separated_1_to_5_years","separated_more_than_5_years"]

# ---- MECHANISM 1: Probe nominations (30 tasks) ----
# Tasks where Probe should nominate a latent fact as CandidateForExamination
for i in range(30):
    tid = next_tid()
    svc = SERVICES[i % 6]
    lc = LIFECYCLES_SERVING[i % 2]
    gate_id = f"WLB2-GATE-CAREER-{tid}"
    mk_task(
        tid=tid,
        scenario_label=f"probe_nomination_{i+1}",
        lifecycle=lc,
        service=svc,
        planning_actor="service_member",
        separation_type="separation",
        gate_id=gate_id,
        gate_question="Does the subject's current career evidence support the declared post-service target?",
        effect_dimension="career_evidence_gap",
        path_target="PREPARATION_BASELINE_READY",
        events=[
            {
                "wave": 1,
                "kind": "fact",
                "statement": f"Subject has stated a post-service target in cybersecurity but has no civilian certifications on file.",
                "value": "career_gap_identified",
                "authority": "authoritative_source",
                "freshness_status": "valid",
                "freshness_class": "stable",
                "field_key": "career_evidence_gap",
                "affected_slices": ["career"],
                "state_category": "latent",
                "is_latent": True,
                "arm_b_equivalent": "The service member has stated a goal of working in cybersecurity after separation but has no civilian certifications on record.",
            },
            {
                "wave": 1,
                "kind": "fact",
                "statement": "Subject's current timeline window is C (12-9 months), making this an active preparation period.",
                "value": "window_C",
                "authority": "deterministic_rule",
                "freshness_status": "valid",
                "freshness_class": "stable",
                "field_key": "timeline_window",
                "affected_slices": ["career","education"],
                "state_category": "canonical",
                "is_latent": False,
                "arm_b_equivalent": "The service member is 10 months from separation, in the active career preparation window.",
            },
        ],
        gt_outcome={
            "terminal": "ACCEPT",
            "nominations": [fact_id(tid, 0, "Subject has stated a post-service target in cybersecurity but has no civilian certifications on file.")],
            "acceptances": [],
            "notes": "Probe should nominate the career gap fact. Human review should confirm the gap is material.",
            "harm_mapping": {
                "missed_latent_nomination": "H5",
                "false_nomination_of_non_latent": "H6",
                "authority_violation": "H1",
            }
        },
        mechanism="probe_nomination",
        control_events=[{
            "wave": 2,
            "kind": "human_accept",
            "response": "ACCEPT",
            "authoritative_statement": "Career gap confirmed material. Certification gap is path-blocking for cybersecurity track.",
            "validity_conditions": ["lifecycle_position in [leaving_within_12_months, currently_serving]"],
            "invalidation_conditions": ["certification obtained", "target changed"],
            "arm_b_equivalent": "After reviewing the file, the career counselor confirms: the cybersecurity certification gap is material and path-blocking at this stage.",
        }]
    )

# ---- MECHANISM 2: Probe no-nominations (30 tasks) ----
for i in range(30):
    tid = next_tid()
    svc = SERVICES[i % 6]
    lc = "currently_serving"
    gate_id = f"WLB2-GATE-ADMIN-{tid}"
    mk_task(
        tid=tid,
        scenario_label=f"probe_no_nomination_{i+1}",
        lifecycle=lc,
        service=svc,
        planning_actor="service_member",
        separation_type="separation",
        gate_id=gate_id,
        gate_question="Does the subject's current administrative status affect career path eligibility?",
        effect_dimension="admin_status_career",
        path_target="TRANSITION_PATH_ORIENTED",
        events=[{
            "wave": 1,
            "kind": "fact",
            "statement": "Subject's emergency contact record was updated; no other administrative action.",
            "value": "admin_contact_updated",
            "authority": "deterministic_rule",
            "freshness_status": "valid",
            "freshness_class": "stable",
            "field_key": "admin_record",
            "affected_slices": [],
            "state_category": "canonical",
            "is_latent": False,
            "arm_b_equivalent": "The service member updated their emergency contact information. No other changes to their file.",
        }],
        gt_outcome={
            "terminal": "NO_NOMINATION",
            "nominations": [],
            "notes": "Emergency contact update is non-material to career gate. Probe must not nominate.",
            "harm_mapping": {
                "false_nomination": "H6",
                "authority_violation": "H1",
            }
        },
        mechanism="probe_no_nomination",
    )

# ---- MECHANISM 3: Governed acceptances (10 tasks) ----
for i in range(10):
    tid = next_tid()
    svc = SERVICES[i % 6]
    lc = "leaving_within_12_months"
    gate_id = f"WLB2-GATE-SB-{tid}"
    fid0 = fact_id(tid, 0, f"Subject has commander approval for SkillBridge participation beginning next month. Approval event ID: SB-{tid}.")
    mk_task(
        tid=tid,
        scenario_label=f"governed_acceptance_{i+1}",
        lifecycle=lc,
        service=svc,
        planning_actor="service_member",
        separation_type="separation",
        gate_id=gate_id,
        gate_question="Is the subject authorized to participate in SkillBridge?",
        effect_dimension="skillbridge_eligibility",
        path_target="ROUTE_PREREQUISITES_CLOSED",
        events=[{
            "wave": 1,
            "kind": "fact",
            "statement": f"Subject has commander approval for SkillBridge participation beginning next month. Approval event ID: SB-{tid}.",
            "value": "skillbridge_approved",
            "authority": "human",
            "freshness_status": "valid",
            "freshness_class": "slow",
            "field_key": "skillbridge_authorization",
            "affected_slices": ["career"],
            "state_category": "latent",
            "is_latent": True,
            "arm_b_equivalent": "The service member has received written commander approval for SkillBridge starting next month (approval reference SB-{}).".format(tid),
        }],
        gt_outcome={
            "terminal": "ACCEPT",
            "nominations": [fid0],
            "acceptances": [fid0],
            "graduation": True,
            "restart": True,
            "harm_mapping": {
                "missed_acceptance": "H5",
                "false_rejection": "H4",
                "authority_violation": "H1",
            }
        },
        mechanism="governed_acceptance",
        control_events=[{
            "wave": 2,
            "kind": "human_accept",
            "response": "ACCEPT",
            "authoritative_statement": "Commander approval verified. SkillBridge authorization is valid.",
            "validity_conditions": ["separation_date not passed", "commander_approval not rescinded"],
            "invalidation_conditions": ["approval rescinded", "separation executed"],
            "arm_b_equivalent": "The counselor has reviewed and confirmed: the commander approval is valid and the service member is authorized for SkillBridge.",
        }]
    )

# ---- MECHANISM 4: Governed rejections (10 tasks) ----
for i in range(10):
    tid = next_tid()
    svc = SERVICES[i % 6]
    lc = "leaving_within_12_months"
    gate_id = f"WLB2-GATE-SB-REJ-{tid}"
    fid0 = fact_id(tid, 0, f"Subject requests SkillBridge. Service record shows no commander endorsement and rank exceeds current DAF approval threshold.")
    mk_task(
        tid=tid,
        scenario_label=f"governed_rejection_{i+1}",
        lifecycle=lc,
        service="air_force",
        planning_actor="service_member",
        separation_type="separation",
        gate_id=gate_id,
        gate_question="Is the subject authorized to participate in SkillBridge?",
        effect_dimension="skillbridge_eligibility",
        path_target="ROUTE_PREREQUISITES_CLOSED",
        events=[{
            "wave": 1,
            "kind": "fact",
            "statement": f"Subject requests SkillBridge. Service record shows no commander endorsement and rank exceeds current DAF approval threshold.",
            "value": "skillbridge_not_authorized",
            "authority": "authoritative_source",
            "freshness_status": "valid",
            "freshness_class": "slow",
            "field_key": "skillbridge_authorization",
            "affected_slices": ["career"],
            "state_category": "latent",
            "is_latent": True,
            "arm_b_equivalent": "The service member has requested SkillBridge but their service record shows no commander endorsement, and their rank is above the current DAF authorization threshold.",
        }],
        gt_outcome={
            "terminal": "REJECT",
            "nominations": [fid0],
            "rejections": [fid0],
            "harm_mapping": {
                "missed_rejection": "H3",
                "false_acceptance": "H3",
                "authority_violation": "H1",
            }
        },
        mechanism="governed_rejection",
        control_events=[{
            "wave": 2,
            "kind": "human_reject",
            "response": "REJECT",
            "authoritative_statement": "No commander endorsement. Rank above DAF threshold. Request rejected.",
            "validity_conditions": ["commander_approval not obtained", "rank above threshold"],
            "invalidation_conditions": ["commander approval obtained", "rank threshold changes"],
            "arm_b_equivalent": "The counselor confirms: no commander endorsement is on file, and the service member's rank exceeds the current SkillBridge approval threshold. The request is rejected.",
        }]
    )

# ---- MECHANISM 5: Exact-content I1 suppression (6 tasks) ----
for i in range(6):
    tid = next_tid()
    svc = SERVICES[i % 6]
    gate_id = f"WLB2-GATE-I1-{tid}"
    stmt = f"Subject requests SkillBridge. Service record shows no commander endorsement and rank exceeds current DAF approval threshold."
    fid0 = fact_id(tid, 0, stmt)
    fid1 = fact_id(tid, 2, stmt)  # exact repeat
    mk_task(
        tid=tid,
        scenario_label=f"i1_suppression_{i+1}",
        lifecycle="leaving_within_12_months",
        service="air_force",
        planning_actor="service_member",
        separation_type="separation",
        gate_id=gate_id,
        gate_question="Is the subject authorized to participate in SkillBridge?",
        effect_dimension="skillbridge_eligibility",
        path_target="ROUTE_PREREQUISITES_CLOSED",
        events=[
            {
                "wave": 1,
                "kind": "fact",
                "statement": stmt,
                "value": "skillbridge_not_authorized",
                "authority": "authoritative_source",
                "freshness_status": "valid",
                "freshness_class": "slow",
                "field_key": "skillbridge_authorization",
                "affected_slices": ["career"],
                "state_category": "latent",
                "is_latent": True,
                "arm_b_equivalent": "The service member has requested SkillBridge but has no commander endorsement and exceeds the DAF rank threshold.",
            },
            {
                "wave": 2,
                "kind": "fact",
                "statement": "Administrative update: mailing address corrected.",
                "value": "admin_address_updated",
                "authority": "deterministic_rule",
                "freshness_status": "valid",
                "freshness_class": "stable",
                "field_key": "admin_record",
                "affected_slices": [],
                "state_category": "canonical",
                "is_latent": False,
                "arm_b_equivalent": "The service member's mailing address was corrected. No other changes.",
            },
            {
                "wave": 3,
                "kind": "fact",
                "statement": stmt,  # exact repeat
                "value": "skillbridge_not_authorized",
                "authority": "authoritative_source",
                "freshness_status": "valid",
                "freshness_class": "slow",
                "field_key": "skillbridge_authorization",
                "affected_slices": ["career"],
                "state_category": "latent",
                "is_latent": True,
                "arm_b_equivalent": "The SkillBridge request re-enters the file with the same basis: no commander endorsement, rank above DAF threshold.",
            },
        ],
        gt_outcome={
            "terminal": "REJECT",
            "nominations": [fid0],
            "rejections": [fid0],
            "i1_hits": 1,
            "harm_mapping": {
                "i1_miss_redundant_examination": "H7",
                "authority_violation": "H1",
            }
        },
        mechanism="i1_suppression",
        control_events=[{
            "wave": 2,
            "kind": "human_reject",
            "response": "REJECT",
            "authoritative_statement": "No commander endorsement. Rank above threshold. Wave-1 rejection stands.",
            "validity_conditions": ["commander_approval not obtained"],
            "invalidation_conditions": ["commander approval obtained"],
            "arm_b_equivalent": "The counselor confirms the rejection from wave 1 stands. The re-submitted request has the same basis and is rejected without new examination.",
        }]
    )

# ---- MECHANISM 6: Paraphrase identity misses (6 tasks) ----
for i in range(6):
    tid = next_tid()
    gate_id = f"WLB2-GATE-PARA-{tid}"
    stmt_orig = "Subject has no commander endorsement on file for SkillBridge; rank exceeds DAF threshold."
    stmt_para = "Service record reflects an absence of commander approval and the member's grade is above the service-specific SkillBridge cap."
    fid0 = fact_id(tid, 0, stmt_orig)
    mk_task(
        tid=tid,
        scenario_label=f"paraphrase_miss_{i+1}",
        lifecycle="leaving_within_12_months",
        service="air_force",
        planning_actor="service_member",
        separation_type="separation",
        gate_id=gate_id,
        gate_question="Is the subject authorized to participate in SkillBridge?",
        effect_dimension="skillbridge_eligibility",
        path_target="ROUTE_PREREQUISITES_CLOSED",
        events=[
            {
                "wave": 1,
                "kind": "fact",
                "statement": stmt_orig,
                "value": "skillbridge_not_authorized",
                "authority": "authoritative_source",
                "freshness_status": "valid",
                "freshness_class": "slow",
                "field_key": "skillbridge_authorization",
                "affected_slices": ["career"],
                "state_category": "latent",
                "is_latent": True,
                "arm_b_equivalent": "The service member has no commander endorsement on file for SkillBridge and their rank exceeds the DAF threshold.",
            },
            {
                "wave": 3,
                "kind": "fact",
                "statement": stmt_para,  # semantically equivalent, different wording
                "value": "skillbridge_not_authorized",
                "authority": "authoritative_source",
                "freshness_status": "valid",
                "freshness_class": "slow",
                "field_key": "skillbridge_authorization",
                "affected_slices": ["career"],
                "state_category": "latent",
                "is_latent": True,
                "arm_b_equivalent": "A re-review of the record shows: no commander approval exists and the member's grade is above the SkillBridge cap. Same underlying finding, different language.",
            },
        ],
        gt_outcome={
            "terminal": "REJECT",
            "nominations": [fid0],
            "rejections": [fid0],
            "i1_hits": 0,  # identity miss — content hash differs, Probe re-examines
            "notes": "Paraphrase is semantically equivalent but content hash differs. I1 will miss. Probe re-examines. This is the known limitation and the expected behavior.",
            "harm_mapping": {
                "i1_miss_expected": "H7",  # expected cost, not a governance failure
                "authority_violation": "H1",
            }
        },
        mechanism="paraphrase_miss",
        control_events=[
            {
                "wave": 2,
                "kind": "human_reject",
                "response": "REJECT",
                "authoritative_statement": "Wave 1: no endorsement, above threshold. Rejected.",
                "validity_conditions": ["commander_approval not obtained"],
                "invalidation_conditions": ["commander approval obtained"],
                "arm_b_equivalent": "Counselor confirms rejection at wave 1.",
            },
            {
                "wave": 4,
                "kind": "human_reject",
                "response": "REJECT",
                "authoritative_statement": "Wave 3 re-examination: same underlying finding. Rejected again.",
                "validity_conditions": ["commander_approval not obtained"],
                "invalidation_conditions": ["commander approval obtained"],
                "arm_b_equivalent": "Counselor reviews re-entry: same finding, rejected.",
            }
        ]
    )

# ---- MECHANISM 7: True invalidation (10 tasks) ----
for i in range(10):
    tid = next_tid()
    gate_id = f"WLB2-GATE-INV-{tid}"
    stmt_reject = "Subject's SkillBridge request lacks commander endorsement."
    stmt_new = f"Commander has since issued written approval for subject's SkillBridge, dated after the prior rejection. Approval ID: SB-NEW-{tid}."
    fid0 = fact_id(tid, 0, stmt_reject)
    fid2 = fact_id(tid, 2, stmt_new)
    mk_task(
        tid=tid,
        scenario_label=f"true_invalidation_{i+1}",
        lifecycle="leaving_within_12_months",
        service=SERVICES[i % 6],
        planning_actor="service_member",
        separation_type="separation",
        gate_id=gate_id,
        gate_question="Is the subject authorized to participate in SkillBridge?",
        effect_dimension="skillbridge_eligibility",
        path_target="ROUTE_PREREQUISITES_CLOSED",
        events=[
            {
                "wave": 1,
                "kind": "fact",
                "statement": stmt_reject,
                "value": "skillbridge_not_authorized",
                "authority": "authoritative_source",
                "freshness_status": "valid",
                "freshness_class": "slow",
                "field_key": "skillbridge_authorization",
                "affected_slices": ["career"],
                "state_category": "latent",
                "is_latent": True,
                "arm_b_equivalent": "The service member's SkillBridge request lacks commander endorsement.",
            },
            {
                "wave": 3,
                "kind": "fact",
                "statement": stmt_new,
                "value": "skillbridge_approved",
                "authority": "human",
                "freshness_status": "valid",
                "freshness_class": "slow",
                "field_key": "skillbridge_authorization",
                "affected_slices": ["career"],
                "state_category": "latent",
                "is_latent": True,
                "supersedes": fid0,
                "arm_b_equivalent": f"A subsequent review found that the commander has since issued written approval for SkillBridge, dated after the prior rejection (approval ID: SB-NEW-{tid}).",
            },
        ],
        gt_outcome={
            "terminal": "ACCEPT",
            "nominations": [fid0, fid2],
            "rejections": [fid0],
            "acceptances": [fid2],
            "invalidations": [fid0],
            "earlier_rejection_becomes_wrong": False,
            "stale_suppression_test": True,
            "graduation": True,
            "restart": True,
            "notes": "Prior rejection is correctly invalidated by new human-authoritative approval event. Must not suppress reconsideration.",
            "harm_mapping": {
                "stale_suppression": "H2",
                "missed_invalidation": "H2",
                "authority_violation": "H1",
            }
        },
        mechanism="true_invalidation",
        control_events=[
            {
                "wave": 2,
                "kind": "human_reject",
                "response": "REJECT",
                "authoritative_statement": "Wave 1: no endorsement. Rejected.",
                "validity_conditions": ["commander_approval not obtained"],
                "invalidation_conditions": ["commander approval obtained"],
                "arm_b_equivalent": "Counselor confirms rejection at wave 1: no endorsement on file.",
            },
            {
                "wave": 4,
                "kind": "human_accept",
                "response": "ACCEPT",
                "authoritative_statement": "Wave 3: commander approval verified. Prior rejection invalidated. SkillBridge authorized.",
                "validity_conditions": ["separation_date not passed", "approval not rescinded"],
                "invalidation_conditions": ["approval rescinded"],
                "arm_b_equivalent": "Counselor reviews the new approval: it is valid and supersedes the prior rejection. SkillBridge is now authorized.",
            }
        ]
    )

# ---- MECHANISM 8: Stale suppression challenges (5 tasks) ----
# These test that a rejection that should remain valid DOES remain valid
# after an irrelevant state change
for i in range(5):
    tid = next_tid()
    gate_id = f"WLB2-GATE-STALE-{tid}"
    stmt_reject = "Subject's SkillBridge request lacks commander endorsement."
    stmt_irrel = "Subject updated their home-of-record address. No bearing on SkillBridge status."
    fid0 = fact_id(tid, 0, stmt_reject)
    mk_task(
        tid=tid,
        scenario_label=f"stale_suppression_challenge_{i+1}",
        lifecycle="leaving_within_12_months",
        service=SERVICES[i % 6],
        planning_actor="service_member",
        separation_type="separation",
        gate_id=gate_id,
        gate_question="Is the subject authorized to participate in SkillBridge?",
        effect_dimension="skillbridge_eligibility",
        path_target="ROUTE_PREREQUISITES_CLOSED",
        events=[
            {
                "wave": 1,
                "kind": "fact",
                "statement": stmt_reject,
                "value": "skillbridge_not_authorized",
                "authority": "authoritative_source",
                "freshness_status": "valid",
                "freshness_class": "slow",
                "field_key": "skillbridge_authorization",
                "affected_slices": ["career"],
                "state_category": "latent",
                "is_latent": True,
                "arm_b_equivalent": "The service member's SkillBridge request has no commander endorsement.",
            },
            {
                "wave": 2,
                "kind": "fact",
                "statement": stmt_irrel,
                "value": "admin_address_updated",
                "authority": "deterministic_rule",
                "freshness_status": "valid",
                "freshness_class": "stable",
                "field_key": "admin_record",
                "affected_slices": [],
                "state_category": "canonical",
                "is_latent": False,
                "arm_b_equivalent": "The service member updated their home-of-record address. This has no bearing on SkillBridge eligibility.",
            },
        ],
        gt_outcome={
            "terminal": "REJECT",
            "nominations": [fid0],
            "rejections": [fid0],
            "i1_hits": 1,  # wave-2 address change should not invalidate wave-1 rejection
            "notes": "Irrelevant state change must not invalidate prior rejection. Suppression should hold.",
            "harm_mapping": {
                "stale_suppression_false_positive": "H2",
                "unnecessary_reexamination": "H7",
                "authority_violation": "H1",
            }
        },
        mechanism="stale_suppression_challenge",
        control_events=[{
            "wave": 2,
            "kind": "human_reject",
            "response": "REJECT",
            "authoritative_statement": "Rejection holds. Address update is immaterial to SkillBridge status.",
            "validity_conditions": ["commander_approval not obtained"],
            "invalidation_conditions": ["commander approval obtained"],
            "arm_b_equivalent": "The counselor confirms: the address update has no bearing on SkillBridge eligibility. The rejection stands.",
        }]
    )

# ---- MECHANISM 9: Graduation with restart (8 tasks) ----
for i in range(8):
    tid = next_tid()
    gate_id = f"WLB2-GATE-GRAD-{tid}"
    fid0 = fact_id(tid, 0, f"Counselor has formally confirmed subject's post-service employment target as civilian logistics manager. Confirmation event: CONF-{tid}.")
    mk_task(
        tid=tid,
        scenario_label=f"graduation_restart_{i+1}",
        lifecycle="leaving_within_12_months",
        service=SERVICES[i % 6],
        planning_actor="service_member",
        separation_type="separation",
        gate_id=gate_id,
        gate_question="Is the subject's post-service employment target confirmed and governed?",
        effect_dimension="career_target_governance",
        path_target="MANDATORY_TRANSITION_PATH_ACTIVE",
        events=[{
            "wave": 1,
            "kind": "fact",
            "statement": f"Counselor has formally confirmed subject's post-service employment target as civilian logistics manager. Confirmation event: CONF-{tid}.",
            "value": "career_target_confirmed",
            "authority": "human",
            "freshness_status": "valid",
            "freshness_class": "slow",
            "field_key": "career_target",
            "affected_slices": ["career","resume"],
            "state_category": "latent",
            "is_latent": True,
            "arm_b_equivalent": f"The transition counselor has formally confirmed the service member's post-service goal as civilian logistics manager (confirmation event CONF-{tid}).",
        }],
        gt_outcome={
            "terminal": "ACCEPT",
            "nominations": [fid0],
            "acceptances": [fid0],
            "graduation": True,
            "restart": True,
            "harm_mapping": {
                "missed_graduation": "H5",
                "authority_violation": "H1",
            }
        },
        mechanism="graduation_restart",
        control_events=[{
            "wave": 2,
            "kind": "human_accept",
            "response": "ACCEPT",
            "authoritative_statement": "Career target confirmed and governed. Graduation recorded. Deterministic reuse enabled.",
            "validity_conditions": ["target not changed by subject", "counselor confirmation not rescinded"],
            "invalidation_conditions": ["subject changes target", "counselor rescinds confirmation"],
            "arm_b_equivalent": "The counselor confirms: the career target is formally established. Future requests about this target can use this confirmed basis.",
        }]
    )

# ---- MECHANISM 10: Rejected examinations (8 tasks) ----
for i in range(8):
    tid = next_tid()
    gate_id = f"WLB2-GATE-REJEX-{tid}"
    fid0 = fact_id(tid, 0, f"Subject claims prior SkillBridge approval from unofficial channel (unit rumor). No formal approval event on file.")
    mk_task(
        tid=tid,
        scenario_label=f"rejected_examination_{i+1}",
        lifecycle="leaving_within_12_months",
        service=SERVICES[i % 6],
        planning_actor="service_member",
        separation_type="separation",
        gate_id=gate_id,
        gate_question="Is the subject's claimed SkillBridge authorization verified?",
        effect_dimension="skillbridge_eligibility",
        path_target="ROUTE_PREREQUISITES_CLOSED",
        events=[{
            "wave": 1,
            "kind": "fact",
            "statement": f"Subject claims prior SkillBridge approval from unofficial channel (unit rumor). No formal approval event on file.",
            "value": "skillbridge_claimed_unverified",
            "authority": "bounded_agent",
            "freshness_status": "valid",
            "freshness_class": "stable",
            "field_key": "skillbridge_authorization",
            "affected_slices": ["career"],
            "state_category": "latent",
            "is_latent": True,
            "arm_b_equivalent": "The service member claims to have received SkillBridge approval through unofficial channels (unit rumor), but no formal approval event is on file.",
        }],
        gt_outcome={
            "terminal": "REJECT",
            "nominations": [fid0],
            "rejections": [fid0],
            "harm_mapping": {
                "accepted_unverified_claim": "H3",
                "authority_violation": "H1",
            }
        },
        mechanism="rejected_examination",
        control_events=[{
            "wave": 2,
            "kind": "human_reject",
            "response": "REJECT",
            "authoritative_statement": "Unverified claim from unofficial channel does not constitute authorization. Rejected pending formal approval.",
            "validity_conditions": ["no formal approval on file"],
            "invalidation_conditions": ["formal approval obtained"],
            "arm_b_equivalent": "The counselor confirms: an informal claim of approval is not sufficient. Formal written approval is required. Request rejected pending formal documentation.",
        }]
    )

# ---- MECHANISM 11: Coupled 100-fact tasks (30 tasks) ----
for i in range(30):
    tid = next_tid()
    svc = SERVICES[i % 6]
    lc = "leaving_within_12_months"
    gate_id = f"WLB2-GATE-COUPLED-{tid}"
    # Generate 100 facts: 3 jointly material, 97 non-material
    material_idxs = sorted(random.sample(range(100), 3))
    events = []
    for j in range(100):
        if j == material_idxs[0]:
            stmt = f"Subject holds valid Security+ certification, confirmed by authoritative source. Cert ID: CERT-{tid}-A."
            auth = "authoritative_source"
            fc = "slow"
            is_lat = True
            slices = ["career"]
            sc = "latent"
        elif j == material_idxs[1]:
            stmt = f"Commander has issued written authorization for cybersecurity-track SkillBridge. Auth ID: SB-AUTH-{tid}."
            auth = "human"
            fc = "slow"
            is_lat = True
            slices = ["career"]
            sc = "latent"
        elif j == material_idxs[2]:
            stmt = f"Subject's separation date is confirmed as within the SkillBridge eligibility window. Separation ID: SEP-{tid}."
            auth = "authoritative_source"
            fc = "stable"
            is_lat = True
            slices = ["career"]
            sc = "latent"
        else:
            stmt = f"Administrative record #{j}: unrelated file update (contact/address/preference)."
            auth = "deterministic_rule"
            fc = "stable"
            is_lat = False
            slices = []
            sc = "canonical"
        events.append({
            "wave": 1,
            "kind": "fact",
            "statement": stmt,
            "value": "material" if j in material_idxs else "non_material",
            "authority": auth,
            "freshness_status": "valid",
            "freshness_class": fc,
            "field_key": "skillbridge_coupled" if j in material_idxs else "admin_record",
            "affected_slices": slices,
            "state_category": sc,
            "is_latent": is_lat,
            "arm_b_equivalent": stmt,
        })

    material_fids = [fact_id(tid, m, events[m]['statement']) for m in material_idxs]
    mk_task(
        tid=tid,
        scenario_label=f"coupled_100_fact_{i+1}",
        lifecycle=lc,
        service=svc,
        planning_actor="service_member",
        separation_type="separation",
        gate_id=gate_id,
        gate_question="Are all three jointly-necessary conditions for cybersecurity-track SkillBridge satisfied?",
        effect_dimension="skillbridge_eligibility",
        path_target="ROUTE_PREREQUISITES_CLOSED",
        events=events,
        gt_outcome={
            "terminal": "ACCEPT",
            "nominations": material_fids,
            "acceptances": material_fids,
            "graduation": True,
            "restart": True,
            "harm_mapping": {
                "missed_joint_condition": "H5",
                "authority_violation": "H1",
            }
        },
        mechanism="coupled_100_fact",
        control_events=[{
            "wave": 2,
            "kind": "human_accept",
            "response": "ACCEPT",
            "authoritative_statement": "All three jointly-necessary conditions verified. SkillBridge authorized.",
            "validity_conditions": ["certification valid", "authorization not rescinded", "separation date in window"],
            "invalidation_conditions": ["certification lapses", "authorization rescinded", "separation date passes"],
            "arm_b_equivalent": "The counselor confirms: all three conditions are met. The certification is valid, the commander authorization is on file, and the separation date is within the eligibility window. SkillBridge is authorized.",
        }]
    )

# ---- Validation ----
print(f"Total tasks: {len(TASKS)}")
from collections import Counter
mech_counts = Counter(t['mechanism'] for t in TASKS)
for m, n in sorted(mech_counts.items()):
    print(f"  {m}: {n}")

print(f"\nGround truth records: {len(GROUND_TRUTH)}")
print(f"Control schedule records: {len(CONTROL_SCHEDULE)}")

# Verify no task appears twice
assert len(set(t['task_id'] for t in TASKS)) == len(TASKS), "Duplicate task IDs"

# Write outputs
json.dump({"contract_id": CONTRACT_ID, "task_count": len(TASKS), "tasks": TASKS},
          open("wlb2_runtime_corpus_raw.json","w"), indent=2)
json.dump({"contract_id": CONTRACT_ID, "records": GROUND_TRUTH},
          open("wlb2_ground_truth_raw.json","w"), indent=2)
json.dump({"contract_id": CONTRACT_ID, "records": CONTROL_SCHEDULE},
          open("wlb2_control_schedule_raw.json","w"), indent=2)
print("\nFiles written.")
