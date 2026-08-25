from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import UTC, date, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal, cast

from military_slices.models import (
    ActiveTask,
    Authority,
    CanonicalState,
    ExecutionState,
    ExecutionStatus,
    FreshnessStatus,
    GateState,
    OrientationResult,
    ServiceName,
    SliceName,
    utc_now,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
PACK_VERSION = "2026-08-24-v2-shadow-tested"

SERVICE_ALIASES: dict[ServiceName, tuple[str, ...]] = {
    ServiceName.ARMY: ("army", "soldier", "ets", "refrad"),
    ServiceName.NAVY: ("navy", "sailor", "eaos", "fleet reserve", "mynavy"),
    ServiceName.MARINE_CORPS: ("marine corps", "marine", " eas ", "trp", "trs"),
    ServiceName.AIR_FORCE: ("air force", "airman", "afsc"),
    ServiceName.SPACE_FORCE: ("space force", "guardian", "ussf"),
    ServiceName.COAST_GUARD: ("coast guard", "coast guardsman", "uscg"),
}

SERVICE_DISPLAY = {
    ServiceName.ARMY: "Army",
    ServiceName.NAVY: "Navy",
    ServiceName.MARINE_CORPS: "Marine Corps",
    ServiceName.AIR_FORCE: "Air Force",
    ServiceName.SPACE_FORCE: "Space Force",
    ServiceName.COAST_GUARD: "Coast Guard",
}

SERVICE_PATH_TASKS: dict[ServiceName, dict[str, str]] = {
    ServiceName.ARMY: {
        "early": "Begin Army TAP and Individualized Initial Counseling (IIC)",
        "prepare": "Complete the Army TAP preparation work required for the active route",
        "final": "Complete Army TAP Capstone and verify Career Readiness Standards",
    },
    ServiceName.NAVY: {
        "early": "Begin Navy Initial Counseling through FFSC or the Command Career Counselor",
        "prepare": "Complete the Navy TAP preparation work required for the active route",
        "final": "Complete Navy CAPSTONE and verify Career Readiness Standards",
    },
    ServiceName.MARINE_CORPS: {
        "early": "Begin the Transition Readiness Program and prepare for TRS with the UTC",
        "prepare": "Complete the Marine Corps TRP preparation work required for the active route",
        "final": "Complete Capstone Review and Commander's Verification",
    },
    ServiceName.AIR_FORCE: {
        "early": "Begin DAF TAP with the Military & Family Readiness Center",
        "prepare": "Complete the DAF TAP preparation work required for the active route",
        "final": "Complete DAF TAP Capstone and verify Career Readiness Standards",
    },
    ServiceName.SPACE_FORCE: {
        "early": "Begin DAF TAP with the Military & Family Readiness Center",
        "prepare": "Complete the DAF TAP preparation work required for the active route",
        "final": "Complete DAF TAP Capstone and verify Career Readiness Standards",
    },
    ServiceName.COAST_GUARD: {
        "early": "Begin Coast Guard TAP with the Transition/Relocation Manager",
        "prepare": "Complete the Coast Guard TAP and DHS Transition Day work required for the active route",
        "final": "Complete Coast Guard CAPSTONE and verify Career Readiness Standards",
    },
}

ANCHOR_OPTIONS = {
    "Find civilian work": "Find civilian work",
    "Choose education or training": "Choose an education or training path",
    "Plan where to live": "Make a post-service location decision",
    "Improve a résumé for a specific goal": "Make my résumé ready for a specific target",
    "I am still deciding": "Choose the post-service direction worth pursuing first",
}


@lru_cache(maxsize=1)
def path_boundaries() -> dict[str, Any]:
    payload = json.loads((DATA_DIR / "service_path_boundaries.json").read_text(encoding="utf-8"))
    if payload.get("version") != PACK_VERSION:
        raise ValueError("The installed transition path pack has an unexpected version.")
    return cast(dict[str, Any], payload)


def detect_service(text: str) -> ServiceName | None:
    padded = f" {text.casefold()} "
    for service, aliases in SERVICE_ALIASES.items():
        if any(alias in padded for alias in aliases):
            return service
    return None


def detect_separation_type(text: str) -> Literal["separation", "retirement"] | None:
    lower = text.casefold()
    if any(term in lower for term in ("retire", "retirement", "fleet reserve")):
        return "retirement"
    if any(term in lower for term in ("separate", "separation", "eaos", "eas", "ets", "refrad", "dos")):
        return "separation"
    return None


@dataclass(frozen=True)
class AnchorResolution:
    anchor: str | None
    candidate_count: int
    selected_class: str | None
    reason_code: str


def _anchor_clauses(orientation: OrientationResult) -> list[str]:
    clauses: list[str] = []
    for statement in orientation.statements:
        if not statement.affected_slices:
            continue
        pieces = re.split(r"\s*(?:;|\bbut\b|\band\b)\s*", statement.text, flags=re.IGNORECASE)
        clauses.extend(piece.strip(" ,.-") for piece in pieces if piece.strip(" ,.-"))
    return clauses


def _anchor_candidate(clause: str) -> tuple[int, int, str, str] | None:
    lower = clause.casefold()
    domain = anchor_domain(clause)
    if domain in (None, "general"):
        return None
    domain = cast(str, domain)
    constraint = any(
        term in lower
        for term in (
            "stay local",
            "remain local",
            "cannot move",
            "can't move",
            "will not move",
            "won't move",
            "predictable hours",
            "remote work",
            "remote only",
            "hybrid",
            "commute",
            "travel limit",
            "cannot relocate",
            "can't relocate",
            "won't relocate",
            "will not relocate",
            "prefer remote",
            "shift work",
            "steady work",
            "stable work",
            "prefer ",
            "do not want",
            "don't want",
        )
    )
    explicit_target = bool(
        re.search(r"\b(?:my\s+)?(?:career|job|education|location|resume|résumé)?\s*target\s*(?:is|:)", lower)
        or re.search(r"\bmy\s+(?:anchor|goal)\s+(?:is|:)", lower)
    )
    explicit_objective = bool(
        explicit_target
        or re.search(r"\bi\s+(?:want|need|plan|hope)\s+to\b", lower)
        or re.search(r"\bi\s+(?:want|need)\s+[^.!?]{0,40}\b(?:civilian\s+)?(?:work|employment|job)\b", lower)
        or re.search(r"\bwe\s+(?:want|need|plan)\s+to\b", lower)
    )
    explicit_task = bool(
        re.search(r"\bhelp\s+(?:me|us)\b", lower)
        or re.search(r"\b(?:update|rewrite|compare|prepare|plan|make)\s+(?:my|our|this|these)\b", lower)
        or re.search(r"\bcompare\s+(?:civilian\s+)?(?:career|job|role)\b", lower)
    )
    milestone = bool(
        re.search(
            r"\b(?:before|by)\s+(?:i|we|my|our|january|february|march|april|may|june|july|august|"
            r"september|october|november|december|20\d{2})\b",
            lower,
        )
        and any(term in lower for term in ("job", "work", "move", "education", "school", "resume", "résumé", "ready"))
    )
    objective_noun = bool(
        re.search(
            r"\b(?:civilian\s+(?:work|employment|job)|civilian\s+role|"
            r"(?:remote|hybrid|steady|stable)\s+work|become\s+an?\s+\w+|"
            r"choose\s+(?:an?\s+)?education|prepare\s+for\s+(?:our|a)\s+(?:pcs|move))\b",
            lower,
        )
        or any(term in lower for term in ("my career target", "my job target", "my resume target", "my résumé target"))
    )
    if explicit_objective and not (constraint and not explicit_target and not objective_noun):
        specificity = 3 if explicit_target else 2
        return (1, specificity, "explicit_objective", domain)
    if explicit_task:
        return (2, 2, "explicit_task", domain)
    if milestone:
        return (3, 1, "milestone", domain)
    if constraint:
        return (4, 1, "constraint", domain)
    return None


def _canonical_anchor(clause: str, candidate_class: str, domain: str) -> str:
    lower = clause.casefold()
    if domain == "employment":
        return "Find civilian work"
    if domain == "education" and "resume" not in lower and "résumé" not in lower:
        return "Choose an education or training path"
    if domain == "location":
        return "Make a post-service location decision"
    if domain == "undecided":
        return "Choose the post-service direction worth pursuing first"
    if domain == "resume":
        match = re.search(r"(?:submission-ready|ready)\s+for\s+(.+)$", clause, flags=re.IGNORECASE)
        if match and resume_target_specificity(clause) == "concrete":
            return f"Make my résumé submission-ready for {match.group(1).strip(' .')}"
        return "Make my résumé ready for a specific target"
    return clause.strip()


def resolve_human_anchor(orientation: OrientationResult) -> AnchorResolution:
    meaningful = [item for item in orientation.statements if item.affected_slices]
    if not meaningful:
        return AnchorResolution(None, 0, None, "no_decision_relevant_statement")
    lower = orientation.reviewed_input.casefold()
    if any(term in lower for term in ("don't know what i want", "do not know what i want", "not sure what i want")):
        return AnchorResolution(
            "Choose the post-service direction worth pursuing first",
            1,
            "explicit_uncertainty",
            "explicit_uncertainty",
        )
    candidates = [
        (clause, classified)
        for clause in _anchor_clauses(orientation)
        if (classified := _anchor_candidate(clause)) is not None
    ]
    if not candidates:
        return AnchorResolution(None, 0, None, "no_authorized_objective")
    highest_priority = min(item[1][0] for item in candidates)
    highest_specificity = max(item[1][1] for item in candidates if item[1][0] == highest_priority)
    finalists = [
        item for item in candidates if item[1][0] == highest_priority and item[1][1] == highest_specificity
    ]
    domains = {item[1][3] for item in finalists}
    if len(domains) > 1:
        return AnchorResolution(None, len(candidates), None, "ambiguous_equal_authority_objectives")
    clause, (_, _, selected_class, domain) = min(finalists, key=lambda item: item[0].casefold())
    return AnchorResolution(
        _canonical_anchor(clause, selected_class, domain),
        len(candidates),
        selected_class,
        f"semantic_precedence_{selected_class}",
    )


def extract_human_anchor(orientation: OrientationResult) -> str | None:
    return resolve_human_anchor(orientation).anchor


def anchor_domain(anchor: str | None) -> str | None:
    if not anchor:
        return None
    lower = anchor.casefold()
    if any(term in lower for term in ("resume", "résumé", "cv", "submission-ready")):
        return "resume"
    if any(term in lower for term in ("school", "degree", "education", "training", "credential", "certification")):
        return "education"
    if any(term in lower for term in ("relocat", "move", "location", "where to live")):
        return "location"
    if any(term in lower for term in ("job", "career", "work", "employ", "civilian role")):
        return "employment"
    if re.search(r"\bbecome\s+(?:a|an)\s+[a-z][a-z -]{2,60}\b", lower):
        return "employment"
    if any(term in lower for term in ("direction", "deciding", "decide")):
        return "undecided"
    return "general"


GENERIC_RESUME_TARGETS = {
    "a specific target",
    "a specific goal",
    "a declared target",
    "target role",
    "specific role",
    "desired job",
    "career target",
    "the role",
    "some role",
    "a future job",
    "a role",
    "a job",
    "a target role",
}


def resume_target_specificity(text: str) -> Literal["concrete", "generic", "negated", "absent"]:
    lower = re.sub(r"\s+", " ", text.casefold()).strip()
    if not any(term in lower for term in ("resume", "résumé", "cv", "target role", "job posting", "job description")):
        return "absent"
    if any(
        term in lower
        for term in (
            "don't have a target",
            "do not have a target",
            "haven't chosen",
            "have not chosen",
            "not named",
            "still deciding",
            "need to decide",
            "no target role",
            "without a target",
            "remove my target",
            "clear my target",
        )
    ):
        return "negated"
    posted_target_signals = (
        "this uploaded job posting",
        "this job posting",
        "explicit job description",
        "this job description",
    )
    if any(term in lower for term in posted_target_signals):
        return "concrete"
    match = re.search(
        r"(?:submission-ready|ready|resume|résumé|cv|target role|job target)\s+(?:for|is|to|:)\s+([^.!?\n]{2,120})",
        text,
        flags=re.IGNORECASE,
    )
    if not match:
        return "generic"
    target = re.sub(r"\s+", " ", match.group(1).casefold()).strip(" .,:;-")
    unresolved = any(term in target for term in ("not named", "not chosen", "still deciding"))
    if target in GENERIC_RESUME_TARGETS or unresolved:
        return "generic"
    meaningful = [
        word
        for word in re.findall(r"[a-z0-9+#.-]+", target)
        if word not in {"a", "an", "the", "this", "that"}
    ]
    return "concrete" if meaningful else "generic"


def transition_window_id(transition_date: str | None, *, today: date | None = None) -> str:
    if not transition_date:
        return "PATH_IDENTITY"
    target = date.fromisoformat(transition_date)
    current = today or datetime.now(UTC).date()
    days = (target - current).days
    if days < 0:
        return "H"
    if days <= 30:
        return "G"
    if days <= 90:
        return "F"
    if days <= 180:
        return "E"
    if days <= 274:
        return "D"
    if days <= 365:
        return "C"
    if days <= 548:
        return "B"
    return "A"


def _window(window_id: str) -> dict[str, Any]:
    return next(item for item in path_boundaries()["windows"] if item["id"] == window_id)


def _title(task: str) -> str:
    return task[:1].upper() + task[1:].rstrip(".") + "."


def _task_slices(domain: str | None) -> list[SliceName]:
    return {
        "resume": [SliceName.RESUME, SliceName.CAREER],
        "employment": [SliceName.CAREER, SliceName.RESUME],
        "education": [SliceName.EDUCATION],
        "location": [SliceName.LOCATION],
    }.get(domain or "", [])


def _task_matches(domain: str, task: str) -> bool:
    lower = task.casefold()
    signals = {
        "employment": ("employment", "career", "job", "resume", "occupation", "skillbridge", "csp"),
        "resume": ("resume", "evidence", "occupation", "career crosswalk", "job applications"),
        "education": ("education", "training", "credential", "certification", "licensure", "school"),
        "location": ("relocation", "move", "family/location"),
        "undecided": ("direction", "self-assessment", "transition target"),
        "general": ("transition target", "self-assessment", "itp", "core transition"),
    }
    return any(term in lower for term in signals.get(domain, ()))


def _resume_tasks(anchor: str) -> list[str]:
    if resume_target_specificity(anchor) != "concrete":
        return ["Name the role or use this résumé should support"]
    return [
        "Preserve only evidence relevant to the declared résumé target",
        "Identify the highest-value missing proof for that target",
        "Compare the résumé against the declared role",
    ]


def _anchor_fingerprint(anchor: str | None) -> str | None:
    if not anchor:
        return None
    return hashlib.sha256(re.sub(r"\s+", " ", anchor.casefold()).strip().encode()).hexdigest()[:16]


def _material_slices_for_anchor(state: CanonicalState) -> set[SliceName]:
    return {
        "employment": {SliceName.CAREER, SliceName.LOCATION, SliceName.RESUME},
        "resume": {SliceName.RESUME, SliceName.CAREER},
        "education": {SliceName.EDUCATION},
        "location": {SliceName.LOCATION},
        "undecided": {SliceName.CAREER, SliceName.EDUCATION, SliceName.LOCATION},
    }.get(anchor_domain(state.human_anchor) or "", set())


def _anchor_satisfied(state: CanonicalState) -> bool:
    domain = anchor_domain(state.human_anchor)
    if domain in (None, "undecided", "general"):
        return False
    domain = cast(str, domain)
    common = (
        "current goal is complete",
        "this goal is complete",
        "target is satisfied",
        "finished this goal",
    )
    signals = {
        "employment": ("accepted a civilian job", "started my civilian job", "now employed as"),
        "resume": (
            "resume is submission-ready",
            "résumé is submission-ready",
            "finalized my resume",
            "finalized my résumé",
        ),
        "education": ("chosen my education path", "selected my education path", "enrolled in the program"),
        "location": ("location decision is made", "decided where to live", "move is complete"),
    }.get(domain, ())
    return any(
        fact.status == FreshnessStatus.VALID
        and fact.authority == Authority.HUMAN
        and any(term in fact.statement.casefold() for term in (*common, *signals))
        for fact in state.facts
    )


def _validated_conflict(state: CanonicalState, gate_id: str) -> bool:
    usable = " ".join(
        fact.statement.casefold()
        for fact in state.facts
        if fact.status == FreshnessStatus.VALID
    )
    if gate_id == "priority-first-six-months":
        income = any(term in usable for term in ("immediate income", "need income", "work right away"))
        education = any(term in usable for term in ("full-time education", "full-time school", "school full time"))
        return income and education
    return False


def derive_execution_state(
    state: CanonicalState,
    *,
    previous: ExecutionStatus | None = None,
    resolving_authority: Authority | None = None,
) -> CanonicalState:
    prior = previous or state.execution
    fingerprint = _anchor_fingerprint(state.human_anchor)
    before = prior.state
    material_slices = _material_slices_for_anchor(state)
    conflicted = [
        gate
        for gate in state.gates
        if gate.state == GateState.CONFLICTED
        and bool(material_slices.intersection(gate.affected_slices))
        and _validated_conflict(state, gate.id)
    ]
    blocking_gate = max(conflicted, key=lambda item: item.value_score, default=None)
    next_task = state.active_tasks[0] if state.active_tasks else None

    if blocking_gate is not None and next_task is not None:
        execution = ExecutionStatus(
            state=ExecutionState.PARALYZED,
            blocked_transition=next_task.id,
            blocking_gate_id=blocking_gate.id,
            reason_code="validated_material_conflict_blocks_next_transition",
            derived_from_version=state.version,
            anchor_fingerprint=fingerprint,
        )
    elif _anchor_satisfied(state) or (
        prior.state == ExecutionState.COMPLETE
        and prior.anchor_fingerprint is not None
        and prior.anchor_fingerprint == fingerprint
    ):
        execution = ExecutionStatus(
            state=ExecutionState.COMPLETE,
            reason_code="human_authoritative_anchor_satisfaction",
            derived_from_version=state.version,
            anchor_fingerprint=fingerprint,
            resolving_authority=(
                resolving_authority
                if prior.state == ExecutionState.PARALYZED
                else prior.resolving_authority or Authority.HUMAN
            ),
        )
        state.active_tasks = []
    else:
        execution = ExecutionStatus(
            state=ExecutionState.ACTIVE,
            reason_code=(
                "material_conflict_resolved"
                if prior.state == ExecutionState.PARALYZED
                else "anchor_or_next_transition_available"
            ),
            derived_from_version=state.version,
            anchor_fingerprint=fingerprint,
            resolving_authority=resolving_authority if prior.state == ExecutionState.PARALYZED else None,
        )

    if execution.model_dump(exclude={"updated_at"}) == prior.model_dump(exclude={"updated_at"}):
        execution.updated_at = prior.updated_at
    else:
        execution.updated_at = utc_now()
    state.execution = execution
    state.telemetry.execution_state_before = before
    state.telemetry.execution_state_after = execution.state
    state.telemetry.blocked_transition = execution.blocked_transition
    state.telemetry.blocking_gate_id = execution.blocking_gate_id
    return state


def _service_path_task(service: ServiceName | None, window_id: str) -> str | None:
    if service is None:
        return None
    if window_id in ("A", "B"):
        phase = "early"
    elif window_id in ("C", "D", "E"):
        phase = "prepare"
    elif window_id in ("F", "G"):
        phase = "final"
    else:
        return None
    return SERVICE_PATH_TASKS[service][phase]


def _domain_fallback(domain: str) -> str:
    return {
        "employment": "Define the civilian employment direction enough to choose the next route",
        "education": "Define the education outcome enough to compare relevant programs",
        "location": "Identify the location condition that materially shapes the declared target",
        "undecided": "Choose one post-service direction to examine without committing permanently",
        "general": "Confirm the next action that materially advances the declared target",
    }[domain]


def refresh_path_state(state: CanonicalState, *, today: date | None = None) -> CanonicalState:
    text = " ".join([*(fact.statement for fact in state.facts[-30:]), *state.original_intents[-5:]])
    state.service = state.service or detect_service(text)
    detected_type = detect_separation_type(text)
    if state.separation_type is None and detected_type in ("separation", "retirement"):
        state.separation_type = detected_type
    artifact_only = bool(state.original_intents) and all(
        intent == "Shared a document to update my transition plan." for intent in state.original_intents
    )
    if state.human_anchor is None and state.current_goal and not artifact_only:
        state.human_anchor = state.current_goal
    if state.human_anchor is None and artifact_only:
        state.current_goal = None
    state.current_goal = state.human_anchor

    domain = anchor_domain(state.human_anchor)
    window_id = transition_window_id(state.transition_date, today=today)
    state.current_timeline_window = window_id
    if window_id == "H":
        state.stage = "STABILIZE"
    elif window_id in ("F", "G"):
        state.stage = "TRANSITION"
    elif window_id in ("D", "E"):
        state.stage = "SEPARATE"
    elif window_id in ("A", "B", "C"):
        state.stage = "PREPARE"
    else:
        state.stage = "TODAY"

    if domain is None:
        state.path_target_state = "PATH_IDENTIFIED"
        tasks = ["Choose what this transition plan should help accomplish next"]
    elif domain == "resume":
        state.path_target_state = "PREPARATION_BASELINE_READY"
        tasks = _resume_tasks(state.human_anchor or "")
    elif window_id == "PATH_IDENTITY":
        state.path_target_state = "PATH_IDENTIFIED"
        tasks = ["Confirm the working transition date or date range"]
    else:
        window = _window(window_id)
        state.path_target_state = str(window["target_state"])
        tasks = []
        service_task = _service_path_task(state.service, window_id)
        if service_task:
            tasks.append(service_task)
        tasks.extend(task for task in window["candidate_tasks"] if _task_matches(domain, task))
        if len(tasks) < 2:
            tasks.append(_domain_fallback(domain))
        tasks = list(dict.fromkeys(tasks))[:3]

    slices = _task_slices(domain)
    state.active_tasks = [
        ActiveTask(
            id=f"path-{window_id.lower()}-{index}",
            title=_title(task),
            reason="It advances the current target inside the active service-aware path.",
            source=f"transition-pack:{PACK_VERSION}:{window_id}",
            affected_slices=slices,
        )
        for index, task in enumerate(tasks[:3], start=1)
    ]
    active_slices = set(slices)
    state.latent_fact_count = sum(
        1 for fact in state.facts if active_slices and not active_slices.intersection(fact.affected_slices)
    )
    state.transition_pack_version = PACK_VERSION
    return state


def normalize_service_choice(value: str) -> ServiceName:
    lower = value.casefold().replace(" ", "_")
    aliases = {"marine_corps": ServiceName.MARINE_CORPS, "marines": ServiceName.MARINE_CORPS}
    if lower in aliases:
        return aliases[lower]
    try:
        return ServiceName(lower)
    except ValueError as exc:
        raise ValueError("Choose one of the listed military services.") from exc


def service_display(service: ServiceName | None) -> str | None:
    return SERVICE_DISPLAY.get(service) if service else None
