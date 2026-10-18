"""Immutable, serializable result models shared by future workflows."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from bioqubo.provenance import DataProvenance


class ResultStatus(StrEnum):
    """Lifecycle states for a locally generated workflow result."""

    SUCCESS = "success"
    FAILED = "failed"


def _utc_now() -> datetime:
    return datetime.now(tz=UTC)


def _json_safe(value: Any) -> Any:
    """Convert supported immutable model values into JSON-compatible values."""

    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, DataProvenance):
        return value.to_dict()
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    return value


@dataclass(frozen=True, slots=True)
class ResultEnvelope:
    """A versioned result with provenance and reproducibility metadata."""

    workflow: str
    status: ResultStatus
    provenance: DataProvenance
    configuration: Mapping[str, Any]
    payload: Mapping[str, Any]
    random_seed: int | None = None
    created_at: datetime = field(default_factory=_utc_now)
    schema_version: str = "1.0"
    software_version: str = "0.1.0"

    def __post_init__(self) -> None:
        if not self.workflow.strip():
            raise ValueError("workflow must not be blank")
        if self.created_at.tzinfo is None:
            raise ValueError("created_at must include a timezone")
        if self.random_seed is not None and self.random_seed < 0:
            raise ValueError("random_seed must be non-negative")

    def to_dict(self) -> dict[str, Any]:
        """Return a portable, JSON-compatible representation."""

        return {
            "schema_version": self.schema_version,
            "workflow": self.workflow,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "software_version": self.software_version,
            "random_seed": self.random_seed,
            "provenance": self.provenance.to_dict(),
            "configuration": _json_safe(self.configuration),
            "payload": _json_safe(self.payload),
        }
