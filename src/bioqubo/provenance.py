"""Source provenance models for local data and generated artifacts."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class SourceKind(StrEnum):
    """How input data reached the local application."""

    BUNDLED_EXAMPLE = "bundled_example"
    LOCAL_FILE = "local_file"
    MANUAL_ENTRY = "manual_entry"
    EXPLICIT_RETRIEVAL = "explicit_retrieval"


def _utc_now() -> datetime:
    return datetime.now(tz=UTC)


@dataclass(frozen=True, slots=True)
class DataProvenance:
    """Immutable source record stored with every input and result."""

    source_kind: SourceKind
    source_name: str
    identifier: str
    retrieved_at: datetime = field(default_factory=_utc_now)
    source_url: str | None = None
    license_name: str | None = None
    checksum: str | None = None
    notes: str | None = None
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.source_name.strip():
            raise ValueError("source_name must not be blank")
        if not self.identifier.strip():
            raise ValueError("identifier must not be blank")
        if self.retrieved_at.tzinfo is None:
            raise ValueError("retrieved_at must include a timezone")
        if self.source_url is not None and not self.source_url.startswith(("https://", "file://")):
            raise ValueError("source_url must use https:// or file://")

    def to_dict(self) -> dict[str, Any]:
        """Return a portable, JSON-compatible representation."""

        return {
            "source_kind": self.source_kind.value,
            "source_name": self.source_name,
            "identifier": self.identifier,
            "retrieved_at": self.retrieved_at.isoformat(),
            "source_url": self.source_url,
            "license_name": self.license_name,
            "checksum": self.checksum,
            "notes": self.notes,
            "attributes": dict(self.attributes),
        }
