from __future__ import annotations

from copy import deepcopy
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from military_slices.agent_runtime import Resolver
from military_slices.app import COOKIE_NAME, create_app
from military_slices.control import lens_projections
from military_slices.engine import apply_confirmed_input, apply_revalidation, new_state, orient, recompute_state
from military_slices.models import (
    Authority,
    CanonicalState,
    Fact,
    FreshnessClass,
    FreshnessStatus,
    SliceName,
    utc_now,
)
from military_slices.security import verify_session
from military_slices.store import MemoryStore
from military_slices.temporal import (
    ExternalFactUpdate,
    current_impact,
    evaluate_elapsed_freshness,
    propagate_temporal_changes,
)


def employment_state(profile_id: str = "temporal-test") -> CanonicalState:
    state = new_state(profile_id)
    state.human_anchor = "Find civilian work"
    state.current_goal = state.human_anchor
    state.career_target = "Program Management"
    state.transition_date = "2027-06-01"
    state.facts.append(
        Fact(
            id="relocation-fact",
            statement="I will stay local.",
            value="NO",
            authority=Authority.HUMAN,
            affected_slices=[SliceName.LOCATION],
            field_key="relocation_willingness",
            freshness_class=FreshnessClass.SLOW,
        )
    )
    return recompute_state(state)


def test_front_door_preserves_ordinary_local_only_language() -> None:
    oriented = orient("I want civilian work. I will stay local.")

    local = next(item for item in oriented.statements if "stay local" in item.text)
    assert SliceName.LOCATION in local.affected_slices


def test_career_target_marks_only_mapped_location_assumption_stale() -> None:
    before = employment_state()
    before.facts.append(
        Fact(
            id="degree-fact",
            statement="Completed a bachelor's degree.",
            value="bachelor's degree",
            authority=Authority.HUMAN,
            affected_slices=[SliceName.EDUCATION],
            field_key="historical_achievement",
            freshness_class=FreshnessClass.STABLE,
        )
    )
    after = deepcopy(before)
    after.career_target = "Defense Aerospace Program Management"

    updated = propagate_temporal_changes(before, after)

    relocation = next(fact for fact in updated.facts if fact.id == "relocation-fact")
    degree = next(fact for fact in updated.facts if fact.id == "degree-fact")
    assert relocation.status == FreshnessStatus.STALE
    assert degree.status == FreshnessStatus.VALID
    assert len(updated.impacts) == 1
    assert updated.impacts[0].affected_slice == SliceName.LOCATION
    assert updated.impacts[0].question == "Still planning to stay local?"
    assert updated.telemetry.temporal_dependencies_evaluated == 2
    assert updated.telemetry.temporal_fields_marked_stale == 1
    assert updated.telemetry.temporal_freshness_model_calls == 0
    assert updated.telemetry.temporal_full_rebuilds == 0
    assert all(lens.may_have_changed == (lens.name == SliceName.LOCATION) for lens in lens_projections(updated))


def test_explicit_human_career_target_change_runs_temporal_propagation() -> None:
    before = employment_state()

    updated = apply_confirmed_input(
        before,
        orient("My career target is Defense Aerospace Program Management."),
        idempotency_key="temporal-career-target-0001",
    )

    assert updated.career_target == "Defense Aerospace Program Management"
    assert [item.title for item in updated.career_hypotheses if item.status == "accepted"] == [
        "Defense Aerospace Program Management"
    ]
    assert next(fact for fact in updated.facts if fact.id == "relocation-fact").status == FreshnessStatus.STALE
    assert current_impact(updated) is not None
    assert updated.telemetry.temporal_freshness_model_calls == 0


def test_compensation_change_does_not_activate_education() -> None:
    before = employment_state()
    before.facts.append(
        Fact(
            id="compensation-fact",
            statement="My minimum compensation is $90,000.",
            value="90000",
            authority=Authority.HUMAN,
            affected_slices=[SliceName.CAREER],
            field_key="compensation_floor",
            freshness_class=FreshnessClass.SLOW,
        )
    )
    after = deepcopy(before)
    next(fact for fact in after.facts if fact.id == "compensation-fact").value = "100000"

    updated = propagate_temporal_changes(before, after)

    assert not updated.impacts
    assert updated.telemetry.temporal_dependencies_evaluated == 0
    education = next(lens for lens in lens_projections(updated) if lens.name == SliceName.EDUCATION)
    assert not education.may_have_changed


def test_quick_revalidation_is_one_tap_persistent_and_idempotent() -> None:
    before = employment_state()
    changed = deepcopy(before)
    changed.career_target = "Defense Aerospace Program Management"
    stale = propagate_temporal_changes(before, changed)
    impact = current_impact(stale)
    assert impact is not None
    old_validated = next(fact for fact in stale.facts if fact.id == impact.fact_id).last_validated_at

    confirmed, wrote = apply_revalidation(
        stale,
        impact_id=impact.id,
        action="confirm",
        value=None,
        idempotency_key="temporal-confirm-0001",
    )
    assert wrote
    fact = next(item for item in confirmed.facts if item.id == impact.fact_id)
    assert fact.status == FreshnessStatus.VALID
    assert fact.last_validated_at >= old_validated
    assert not confirmed.impacts
    assert confirmed.version == stale.version + 1
    assert confirmed.telemetry.temporal_one_tap_confirmations == 1
    assert confirmed.telemetry.model_calls == stale.telemetry.model_calls

    replay, replay_wrote = apply_revalidation(
        confirmed,
        impact_id=impact.id,
        action="confirm",
        value=None,
        idempotency_key="temporal-confirm-0001",
    )
    assert not replay_wrote
    assert replay.version == confirmed.version
    assert len(replay.receipt_deltas) == len(confirmed.receipt_deltas)

    second_key, second_key_wrote = apply_revalidation(
        confirmed,
        impact_id=impact.id,
        action="confirm",
        value=None,
        idempotency_key="temporal-confirm-0002",
    )
    assert not second_key_wrote
    assert second_key.version == confirmed.version


def test_nonblocking_impact_can_be_deferred_without_validating_the_fact() -> None:
    before = employment_state()
    changed = deepcopy(before)
    changed.career_target = "Defense Aerospace Program Management"
    stale = propagate_temporal_changes(before, changed)
    impact = current_impact(stale)
    assert impact is not None and not impact.blocking

    dismissed, wrote = apply_revalidation(
        stale,
        impact_id=impact.id,
        action="dismiss",
        value=None,
        idempotency_key="temporal-dismiss-0001",
    )

    assert wrote
    assert not dismissed.impacts
    assert next(fact for fact in dismissed.facts if fact.id == impact.fact_id).status == FreshnessStatus.STALE
    assert dismissed.receipt_deltas[-1].operation == "remove"


def test_stale_relocation_cannot_ground_conflict_or_paralysis() -> None:
    before = employment_state()
    before.conflicts.append("The role requires relocation but the plan says stay local.")
    after = deepcopy(before)
    after.career_target = "Role requiring relocation"

    updated = recompute_state(propagate_temporal_changes(before, after))

    relocation = next(fact for fact in updated.facts if fact.id == "relocation-fact")
    assert relocation.status == FreshnessStatus.STALE
    assert not updated.conflicts
    assert all(gate.state.value != "CONFLICTED" for gate in updated.gates)
    assert updated.path_target_state != "PARALYZED"


def test_separation_date_fanout_refreshes_machine_state_and_queues_human_state() -> None:
    before = employment_state()
    validated = utc_now() - timedelta(days=1)
    before.facts.extend(
        [
            Fact(
                id="application-timing",
                statement="Applications begin six months before separation.",
                value="six months before",
                authority=Authority.DETERMINISTIC_RULE,
                affected_slices=[SliceName.CAREER],
                field_key="application_timing",
                freshness_class=FreshnessClass.VOLATILE,
                last_validated_at=validated,
            ),
            Fact(
                id="resume-deadline",
                statement="Résumé ready three months before separation.",
                value="three months before",
                authority=Authority.HUMAN,
                affected_slices=[SliceName.RESUME],
                field_key="resume_readiness_deadline",
                freshness_class=FreshnessClass.VOLATILE,
                last_validated_at=validated,
            ),
        ]
    )
    after = deepcopy(before)
    after.transition_date = "2027-03-01"

    updated = propagate_temporal_changes(before, after)

    machine = next(fact for fact in updated.facts if fact.id == "application-timing")
    human = next(fact for fact in updated.facts if fact.id == "resume-deadline")
    assert machine.status == FreshnessStatus.VALID
    assert machine.last_validated_at > validated
    assert human.status == FreshnessStatus.STALE
    assert updated.telemetry.temporal_dependencies_evaluated == 4
    assert updated.telemetry.temporal_fields_silently_refreshed == 1
    assert len(updated.impacts) == 1
    assert current_impact(updated) == updated.impacts[0]


def test_elapsed_volatile_human_fact_uses_central_ttl_without_turn_counting() -> None:
    state = employment_state()
    state.facts.append(
        Fact(
            id="active-application",
            statement="My current application is awaiting an interview.",
            value="awaiting interview",
            authority=Authority.HUMAN,
            affected_slices=[SliceName.CAREER],
            field_key="active_application",
            freshness_class=FreshnessClass.VOLATILE,
            last_validated_at=utc_now() - timedelta(days=15),
        )
    )

    updated = evaluate_elapsed_freshness(state)

    application = next(fact for fact in updated.facts if fact.id == "active-application")
    assert application.status == FreshnessStatus.STALE
    assert current_impact(updated) is not None
    assert updated.telemetry.temporal_freshness_model_calls == 0


def test_blocking_dependency_makes_revalidation_primary_without_adding_a_gate() -> None:
    before = employment_state()
    primary = max(before.gates, key=lambda item: item.value_score)
    primary.dependencies.append("relocation_willingness")
    gate_ids = [gate.id for gate in before.gates]
    after = deepcopy(before)
    after.career_target = "Role requiring relocation"

    updated = propagate_temporal_changes(before, after)

    impact = current_impact(updated)
    assert impact is not None and impact.blocking
    assert [gate.id for gate in updated.gates] == gate_ids
    assert len(updated.active_tasks) <= 3


def test_blocking_impact_cannot_be_dismissed() -> None:
    before = employment_state()
    primary = max(before.gates, key=lambda item: item.value_score)
    primary.dependencies.append("relocation_willingness")
    after = deepcopy(before)
    after.career_target = "Role requiring relocation"
    updated = propagate_temporal_changes(before, after)

    with pytest.raises(ValueError, match="Confirm or update"):
        apply_revalidation(
            updated,
            impact_id=updated.impacts[0].id,
            action="dismiss",
            value=None,
            idempotency_key="blocking-dismiss",
        )


def test_external_expiring_fact_refreshes_from_authoritative_source_without_prompt() -> None:
    state = employment_state()
    state.facts.append(
        Fact(
            id="skillbridge-policy",
            statement="Current SkillBridge policy version A.",
            value="A",
            authority=Authority.AUTHORITATIVE_SOURCE,
            evidence_ids=["policy-a"],
            affected_slices=[SliceName.CAREER],
            field_key="skillbridge_policy",
            freshness_class=FreshnessClass.EXTERNAL_EXPIRING,
            last_validated_at=utc_now() - timedelta(days=2),
        )
    )

    refreshed = evaluate_elapsed_freshness(
        state,
        external_refresher=lambda _: ExternalFactUpdate(
            value="B",
            statement="Current SkillBridge policy version B.",
            evidence_id="policy-b",
        ),
    )

    policy = next(fact for fact in refreshed.facts if fact.id == "skillbridge-policy")
    assert policy.status == FreshnessStatus.VALID
    assert policy.value == "B"
    assert "policy-b" in policy.evidence_ids
    assert not refreshed.impacts
    assert refreshed.telemetry.temporal_fields_silently_refreshed == 1
    assert refreshed.telemetry.temporal_freshness_model_calls == 0


def test_resume_scope_change_does_not_activate_unmapped_slices() -> None:
    before = employment_state()
    before.human_anchor = "Make my résumé submission-ready for Program Management"
    before.current_goal = before.human_anchor
    after = deepcopy(before)
    after.facts.append(
        Fact(
            id="cyber-resume-fact",
            statement="Led cyber operations.",
            value="Led cyber operations.",
            authority=Authority.HUMAN,
            affected_slices=[SliceName.RESUME, SliceName.CAREER],
        )
    )

    updated = propagate_temporal_changes(before, after)

    assert not updated.impacts
    assert updated.telemetry.temporal_dependencies_evaluated == 0
    assert not any(lens.may_have_changed for lens in lens_projections(updated))


def test_revalidation_http_write_survives_reload_and_replay() -> None:
    store = MemoryStore()
    app = create_app(store=store, resolver=Resolver(mode="deterministic"))
    client = TestClient(app)
    assert client.get("/api/state").status_code == 200
    profile_id = verify_session(client.cookies.get(COOKIE_NAME))
    assert profile_id is not None
    before = employment_state(profile_id)
    changed = deepcopy(before)
    changed.career_target = "Defense Aerospace Program Management"
    stale = propagate_temporal_changes(before, changed)
    stale.version = 1
    store.save(stale, expected_version=0)
    impact = current_impact(stale)
    assert impact is not None
    body = {
        "impact_id": impact.id,
        "action": "confirm",
        "expected_version": 1,
        "idempotency_key": "temporal-http-confirm-0001",
    }

    first = client.post("/api/revalidate", json=body)
    replay = client.post("/api/revalidate", json=body)
    reload = client.get("/api/state")

    assert first.status_code == replay.status_code == reload.status_code == 200, (
        first.text,
        replay.text,
        reload.text,
    )
    assert first.json()["state"]["version"] == replay.json()["state"]["version"] == 2
    assert reload.json()["state"]["version"] == 2
    assert reload.json()["impact"] is None
    fact = next(item for item in reload.json()["state"]["facts"] if item["id"] == "relocation-fact")
    assert fact["status"] == "valid"
    assert reload.json()["state"]["telemetry"]["temporal_one_tap_confirmations"] == 1
