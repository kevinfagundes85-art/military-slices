from __future__ import annotations

import pytest

from military_slices.engine import new_state
from military_slices.security import (
    TokenError,
    issue_orientation,
    issue_session,
    verify_orientation,
    verify_session,
)
from military_slices.store import MemoryStore, VersionConflictError


def test_session_signature_and_isolation() -> None:
    first_id, first_token = issue_session()
    second_id, second_token = issue_session()
    assert first_id != second_id
    assert verify_session(first_token) == first_id
    assert verify_session(second_token) == second_id
    assert verify_session(first_token + "x") is None


def test_orientation_token_binds_exact_reviewed_text() -> None:
    text = "I want work near home."
    token = issue_orientation(text)
    verify_orientation(token, text)
    with pytest.raises(TokenError):
        verify_orientation(token, text + " changed")


def test_memory_store_enforces_optimistic_concurrency() -> None:
    store = MemoryStore()
    state = new_state("ms-one")
    state.version = 1
    store.save(state, expected_version=0)
    stale = new_state("ms-one")
    stale.version = 1
    with pytest.raises(VersionConflictError):
        store.save(stale, expected_version=0)


def test_memory_store_separates_profiles() -> None:
    store = MemoryStore()
    first = store.get("ms-first")
    first.current_goal = "first"
    first.version = 1
    store.save(first, expected_version=0)
    assert store.get("ms-first").current_goal == "first"
    assert store.get("ms-second").current_goal is None
