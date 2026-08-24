from __future__ import annotations

import json
from datetime import UTC, date, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal, cast

from military_slices.models import ActiveTask, CanonicalState, OrientationResult, ServiceName, SliceName

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


def extract_human_anchor(orientation: OrientationResult) -> str | None:
    meaningful = [item for item in orientation.statements if item.affected_slices]
    if not meaningful:
        return None
    lower = orientation.reviewed_input.casefold()
    domain_signal = any(
        term in lower
        for term in (
            "job",
            "career",
            "work",
            "employ",
            "resume",
            "résumé",
            "school",
            "degree",
            "education",
            "training",
            "relocat",
            "move",
            "location",
        )
    )
    if any(term in lower for term in ("don't know what i want", "do not know what i want", "not sure what i want")):
        return "Choose the post-service direction worth pursuing first"
    candidates = [item.text for item in meaningful if item.kind in ("goal", "preference")]
    if candidates:
        return candidates[0]
    return orientation.reviewed_input if domain_signal else None


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
    if any(term in lower for term in ("direction", "deciding", "decide")):
        return "undecided"
    return "general"


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
    lower = anchor.casefold()
    generic_targets = ("for a specific target", "for a specific goal", "for a declared target")
    target_known = (
        " role" in lower
        or "job description" in lower
        or ("submission-ready for " in lower and not any(term in lower for term in generic_targets))
    )
    if not target_known:
        return ["Name the role or use this résumé should support"]
    return [
        "Preserve only evidence relevant to the declared résumé target",
        "Identify the highest-value missing proof for that target",
        "Compare the résumé against the declared role",
    ]


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
