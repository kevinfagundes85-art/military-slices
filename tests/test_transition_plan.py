from __future__ import annotations

from fastapi.testclient import TestClient

from military_slices.agent_runtime import Resolver
from military_slices.app import create_app
from military_slices.models import (
    Authority,
    CanonicalState,
    CareerHypothesis,
    Decision,
    Fact,
    FeedbackEvent,
    Gate,
    GateState,
    ServiceName,
    SliceName,
    SurfaceType,
)
from military_slices.plan import build_transition_plan, render_plan_html
from military_slices.store import MemoryStore


def developed_state(profile_id: str = "plan-persona") -> CanonicalState:
    return CanonicalState(
        profile_id=profile_id,
        version=8,
        starting_vector_complete=True,
        service=ServiceName.NAVY,
        transition_month="2027-05",
        human_anchor="Build a stable civilian life while finding work that helps people.",
        current_goal="Build a stable civilian life while finding work that helps people.",
        original_intents=[
            "I am separating and I am not sure what I want to do.",
            (
                "For my next test of the Logistics analyst work direction: "
                "Ask a recently separated veteran to use my program dashboard."
            ),
            (
                "While testing the Logistics analyst work direction, I learned: "
                "The veteran only understood it after I talked through it, so direct support fits me better."
            ),
            (
                "For my next test of the Veteran services coordinator work direction: "
                "Interview two veterans about where transition support breaks down."
            ),
            (
                "While testing the Veteran services coordinator work direction, I learned: "
                "Both veterans needed help comparing training programs."
            ),
            (
                "For my next test of the Veteran services coordinator work direction: "
                "Compare two approved training programs before June 15."
            ),
        ],
        facts=[
            Fact(
                id="fact-location",
                statement="I need to stay within an hour of Tacoma because my partner is in school.",
                value="Tacoma area",
                authority=Authority.HUMAN,
                affected_slices=[SliceName.LOCATION],
                field_key="relocation_willingness",
            ),
            Fact(
                id="fact-education",
                statement="I can use education benefits, but I do not want a four-year program right now.",
                value="Short program preferred",
                authority=Authority.HUMAN,
                affected_slices=[SliceName.EDUCATION],
                field_key="education_priority",
            ),
            Fact(
                id="fact-experience",
                statement="I led a six-person maintenance team and planned weekly work.",
                value="Team leadership",
                authority=Authority.HUMAN,
                affected_slices=[SliceName.CAREER, SliceName.RESUME],
                field_key="historical_achievement",
            ),
            Fact(
                id="fact-deadline",
                statement="I want to apply for training by June 15, 2027.",
                value="2027-06-15",
                authority=Authority.HUMAN,
                affected_slices=[SliceName.EDUCATION],
                field_key="application_timing",
                effective_at="2027-06-15",
            ),
        ],
        career_hypotheses=[
            CareerHypothesis(
                id="direction-current",
                title="Veteran services coordinator",
                rationale="It connects team leadership with helping people navigate complicated steps.",
                evidence=["O*NET 21-1093.00"],
                capability_matches=["Team leadership", "Planning work"],
                possible_gaps=["Confirm whether local roles require a credential"],
                first_experiment="Talk with one veteran services coordinator.",
                status="accepted",
            ),
            CareerHypothesis(
                id="direction-alt",
                title="Operations coordinator",
                rationale="A related alternative.",
                status="candidate",
            ),
        ],
        gates=[
            Gate(
                id="education-choice",
                title="Choose a training route",
                question="Which short training option fits your timeline and benefits?",
                why="The training choice affects cost and application timing.",
                state=GateState.PARTIAL,
                surface=SurfaceType.TEXT,
                affected_slices=[SliceName.EDUCATION],
                authority_required=Authority.HUMAN,
            )
        ],
        decisions=[
            Decision(id="decision-old-direction", gate_id="career-direction", value="explore:Logistics analyst"),
            Decision(id="decision-old-test", gate_id="path-task_old", value="Build a dashboard for one veteran."),
            Decision(
                id="decision-current-direction",
                gate_id="career-direction",
                value="explore:Veteran services coordinator",
            ),
            Decision(id="decision-why", gate_id="path-task_reason", value="I want work that directly helps veterans."),
            Decision(id="decision-check", gate_id="path-task_check", value="Ask a coordinator what the work requires."),
            Decision(
                id="decision-current-test",
                gate_id="path-task_test",
                value="Compare two approved training programs before June 15.",
            ),
        ],
        feedback=[
            FeedbackEvent(
                id="feedback-change",
                headline="Your location plan changed.",
                consequences=["Remote work is no longer required; Tacoma-area work is now acceptable."],
            )
        ],
    )


def test_complete_plan_projects_only_human_useful_governed_state() -> None:
    plan = build_transition_plan(developed_state())

    assert plan.objective == "Build a stable civilian life while finding work that helps people."
    assert plan.direction is not None
    assert plan.direction.title == "Veteran services coordinator"
    assert plan.direction.status == "Exploring"
    assert plan.direction.alternatives == ["Operations coordinator"]
    assert any(item.detail == "Team leadership" for item in plan.what_i_bring)
    assert any("Tacoma" in (item.detail or "") for item in plan.what_matters_to_me)
    assert any(
        item.title == "Compare two approved training programs before June 15." for item in plan.active_experiments
    )
    assert "Build a dashboard for one veteran." not in plan.direction.why
    assert any(item.decision == "Working direction: Veteran services coordinator" for item in plan.decisions)
    old_test = next(item for item in plan.decisions if item.decision == "Build a dashboard for one veteran.")
    assert old_test.current is False
    assert any("Both veterans" in (item.detail or "") for item in plan.completed_experiments)
    assert any(
        item.title == "Ask a recently separated veteran to use my program dashboard."
        and "direct support fits me better" in (item.detail or "")
        for item in plan.completed_experiments
    )
    assert any(item.title == "Your location plan changed." for item in plan.changes)
    assert any("Which short training option" in item.title for item in plan.unresolved)
    assert any(item.date == "2027-05" and item.date_kind == "veteran_target" for item in plan.timeline)
    assert any(item.date == "2027-06-15" for item in plan.timeline)


def test_export_stands_alone_without_internal_runtime_language() -> None:
    document = render_plan_html(build_transition_plan(developed_state()))

    for heading in (
        "My objective",
        "My direction",
        "What I bring",
        "What matters to me",
        "Decisions I’ve made",
        "What I’m testing",
        "What I learned",
        "What changed my plan",
        "What I still need to figure out",
        "What I need to do next",
        "Timeline",
    ):
        assert heading in document
    assert "Veteran services coordinator" in document
    assert "Tacoma" in document
    assert "CanonicalState" not in document
    assert "LineageRecord" not in document
    assert "Gate version" not in document
    assert "chain-of-thought" not in document


def test_plan_api_and_download_use_the_same_projection() -> None:
    store = MemoryStore()
    app = create_app(store=store, resolver=Resolver(mode="deterministic"))
    client = TestClient(app)
    initial = client.get("/api/state").json()["state"]
    state = developed_state(initial["profile_id"])
    store.save(state, expected_version=0)

    plan_response = client.get("/api/plan")
    export_response = client.get("/api/plan/export")

    assert plan_response.status_code == 200
    assert plan_response.json()["direction"]["title"] == "Veteran services coordinator"
    assert export_response.status_code == 200
    assert "attachment" in export_response.headers["content-disposition"]
    assert "Veteran services coordinator" in export_response.text
    assert export_response.headers["cache-control"] == "no-store"
