from __future__ import annotations

import threading
from copy import deepcopy
from typing import Any, Protocol

from military_slices.engine import new_state
from military_slices.models import CanonicalState


class VersionConflictError(RuntimeError):
    pass


class StateStore(Protocol):
    def get(self, profile_id: str) -> CanonicalState: ...

    def save(self, state: CanonicalState, expected_version: int) -> CanonicalState: ...

    def history(self, profile_id: str) -> list[CanonicalState]: ...

    def get_version(self, profile_id: str, version: int) -> CanonicalState | None: ...


class MemoryStore:
    def __init__(self) -> None:
        self._states: dict[str, CanonicalState] = {}
        self._history: dict[str, dict[int, CanonicalState]] = {}
        self._lock = threading.RLock()

    def get(self, profile_id: str) -> CanonicalState:
        with self._lock:
            state = self._states.get(profile_id)
            if state is None:
                state = new_state(profile_id)
                self._states[profile_id] = state
            return deepcopy(state)

    def save(self, state: CanonicalState, expected_version: int) -> CanonicalState:
        with self._lock:
            current = self._states.get(state.profile_id)
            current_version = current.version if current else 0
            if current_version != expected_version:
                raise VersionConflictError(f"State changed from version {expected_version} to {current_version}.")
            if current is None:
                current = new_state(state.profile_id)
            self._history.setdefault(state.profile_id, {})[current.version] = deepcopy(current)
            self._states[state.profile_id] = deepcopy(state)
            return deepcopy(state)

    def history(self, profile_id: str) -> list[CanonicalState]:
        with self._lock:
            current = self.get(profile_id)
            versions = self._history.get(profile_id, {})
            result = [deepcopy(versions[key]) for key in sorted(versions)]
            if not result or result[-1].version != current.version:
                result.append(current)
            return result

    def get_version(self, profile_id: str, version: int) -> CanonicalState | None:
        with self._lock:
            current = self.get(profile_id)
            if current.version == version:
                return current
            state = self._history.get(profile_id, {}).get(version)
            return deepcopy(state) if state else None


class FirestoreStore:
    def __init__(self, project: str | None = None) -> None:
        from google.cloud import firestore

        self._firestore = firestore
        self._client = firestore.Client(project=project)
        self._collection = self._client.collection("military_slices_profiles")

    def get(self, profile_id: str) -> CanonicalState:
        snapshot = self._collection.document(profile_id).get()
        if not snapshot.exists:
            return new_state(profile_id)
        return CanonicalState.model_validate(snapshot.to_dict())

    def save(self, state: CanonicalState, expected_version: int) -> CanonicalState:
        reference = self._collection.document(state.profile_id)
        transaction = self._client.transaction()

        @self._firestore.transactional
        def write(transaction: Any) -> None:
            snapshot = reference.get(transaction=transaction)
            current_version = snapshot.get("version") if snapshot.exists else 0
            if current_version != expected_version:
                raise VersionConflictError(f"State changed from version {expected_version} to {current_version}.")
            previous = (
                CanonicalState.model_validate(snapshot.to_dict())
                if snapshot.exists
                else new_state(state.profile_id)
            )
            history_reference = reference.collection("versions").document(f"{previous.version:08d}")
            transaction.set(history_reference, previous.model_dump(mode="json"))
            transaction.set(reference, state.model_dump(mode="json"))

        write(transaction)
        return state

    def history(self, profile_id: str) -> list[CanonicalState]:
        reference = self._collection.document(profile_id)
        snapshots = reference.collection("versions").stream()
        result = [CanonicalState.model_validate(snapshot.to_dict()) for snapshot in snapshots]
        current = self.get(profile_id)
        by_version = {state.version: state for state in result}
        by_version[current.version] = current
        return [by_version[key] for key in sorted(by_version)]

    def get_version(self, profile_id: str, version: int) -> CanonicalState | None:
        current = self.get(profile_id)
        if current.version == version:
            return current
        snapshot = self._collection.document(profile_id).collection("versions").document(f"{version:08d}").get()
        if not snapshot.exists:
            return None
        return CanonicalState.model_validate(snapshot.to_dict())
