"""Local session-history records for reproducible workflow exports."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from bioqubo.exports import ResultExports, build_result_exports
from bioqubo.models import ResultEnvelope


@dataclass(frozen=True, slots=True)
class HistoryEntry:
    """One result and its two portable export representations."""

    workflow: str
    created_at: str
    json_file_name: str
    csv_file_name: str
    exports: ResultExports


def create_history_entry(
    result: ResultEnvelope, rows: list[dict[str, Any]], file_stem: str
) -> HistoryEntry:
    """Build an in-memory local history entry from a completed workflow result."""

    exports = build_result_exports(result, rows)
    return HistoryEntry(
        workflow=result.workflow,
        created_at=result.created_at.isoformat(),
        json_file_name=f"{file_stem}.json",
        csv_file_name=f"{file_stem}.csv",
        exports=exports,
    )


def serialize_history(entries: list[HistoryEntry]) -> str:
    """Return a portable JSON bundle containing every recorded result envelope."""

    return json.dumps(
        {
            "history_schema_version": "1.0",
            "exported_at": datetime.now(tz=UTC).isoformat(),
            "results": [json.loads(entry.exports.json_text) for entry in entries],
        },
        indent=2,
        sort_keys=True,
    )
