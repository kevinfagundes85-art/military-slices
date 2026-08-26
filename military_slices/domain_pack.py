from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from military_slices.governance import validate_domain_pack
from military_slices.models import DomainPackRef, DomainPackStatus
from military_slices.path_runtime import PACK_VERSION

DATA_DIR = Path(__file__).resolve().parent / "data"
DOMAIN_PACK_ID = "military-transition"


@lru_cache(maxsize=1)
def installed_domain_pack_payload() -> dict[str, Any]:
    return {
        "version": PACK_VERSION,
        "service_path_boundaries": json.loads(
            (DATA_DIR / "service_path_boundaries.json").read_text(encoding="utf-8")
        ),
        "source_manifest": json.loads((DATA_DIR / "source_manifest.json").read_text(encoding="utf-8")),
    }


@lru_cache(maxsize=1)
def installed_domain_pack_ref() -> DomainPackRef:
    """Return the exact installed pack identity without manufacturing approval."""
    return DomainPackRef.for_payload(
        domain_pack_id=DOMAIN_PACK_ID,
        version=PACK_VERSION,
        payload=installed_domain_pack_payload(),
        status=DomainPackStatus.LEGACY_VALID,
    )


def validate_installed_domain_pack(reference: DomainPackRef | None = None) -> DomainPackRef:
    governed = reference or installed_domain_pack_ref()
    validate_domain_pack(governed, installed_domain_pack_payload())
    return governed
