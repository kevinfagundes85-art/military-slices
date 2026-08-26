from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict

from military_slices.models import CanonicalState, SliceName
from military_slices.temporal import fact_is_usable


class SliceManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: SliceName
    version: str
    permitted_fields: tuple[str, ...]
    permitted_gate_ids: tuple[str, ...]
    emitted_candidate_types: tuple[str, ...]
    governed_interfaces: tuple[str, ...]


MANIFESTS: dict[SliceName, SliceManifest] = {
    SliceName.CAREER: SliceManifest(
        name=SliceName.CAREER,
        version="1.0.0",
        permitted_fields=(
            "human_anchor",
            "path_target_state",
            "current_timeline_window",
            "active_tasks",
            "confirmed_statements",
            "transition_date",
            "rejected_roles",
            "conflicts",
        ),
        permitted_gate_ids=("next-work-preferences", "career-direction", "resume-target-role"),
        emitted_candidate_types=("career_hypothesis",),
        governed_interfaces=("confirmed_transition_timing", "confirmed_work_preferences"),
    ),
    SliceName.RESUME: SliceManifest(
        name=SliceName.RESUME,
        version="1.0.0",
        permitted_fields=("human_anchor", "career_target", "confirmed_statements", "transition_date"),
        permitted_gate_ids=("resume-target-role",),
        emitted_candidate_types=("resume_evidence_candidate",),
        governed_interfaces=("confirmed_career_target",),
    ),
    SliceName.EDUCATION: SliceManifest(
        name=SliceName.EDUCATION,
        version="1.0.0",
        permitted_fields=("human_anchor", "confirmed_statements", "transition_date", "conflicts"),
        permitted_gate_ids=("education-outcome", "priority-first-six-months"),
        emitted_candidate_types=("education_path_candidate",),
        governed_interfaces=("confirmed_transition_timing",),
    ),
    SliceName.LOCATION: SliceManifest(
        name=SliceName.LOCATION,
        version="1.0.0",
        permitted_fields=("human_anchor", "confirmed_statements", "pcs_relocation_date", "conflicts"),
        permitted_gate_ids=("location-priority",),
        emitted_candidate_types=("location_condition_candidate",),
        governed_interfaces=("confirmed_household_move_timing",),
    ),
}


def slice_manifest(name: SliceName) -> SliceManifest:
    return MANIFESTS[name]


def project_slice_context(state: CanonicalState, name: SliceName) -> dict[str, Any]:
    manifest = slice_manifest(name)
    statements = [
        fact.statement
        for fact in state.facts
        if name in fact.affected_slices and fact_is_usable(fact)
    ][-12:]
    relevant_tasks = [
        task.title for task in state.active_tasks if name in task.affected_slices
    ]
    available: dict[str, Any] = {
        "human_anchor": state.human_anchor,
        "career_target": state.career_target,
        "path_target_state": state.path_target_state,
        "current_timeline_window": state.current_timeline_window,
        "active_tasks": relevant_tasks,
        "confirmed_statements": statements,
        "transition_date": state.transition_date,
        "pcs_relocation_date": state.pcs_relocation_date,
        "rejected_roles": state.rejected_roles[-12:],
        "conflicts": state.conflicts[-5:],
    }
    return {field: available[field] for field in manifest.permitted_fields}
