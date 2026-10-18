"""Portable JSON and CSV exports for reproducible local workflow results."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from io import StringIO
from typing import Any

from bioqubo.models import ResultEnvelope


@dataclass(frozen=True, slots=True)
class ResultExports:
    """The paired export formats for one versioned result envelope."""

    json_text: str
    csv_text: str


def _json_cell(value: Any) -> str:
    """Encode structured CSV values consistently and without losing their shape."""

    return json.dumps(value, default=str, sort_keys=True, separators=(",", ":"))


def build_result_exports(
    result: ResultEnvelope, rows: list[dict[str, Any]]
) -> ResultExports:
    """Create paired exports with complete reproducibility metadata in both formats.

    JSON is the complete result envelope. CSV repeats envelope metadata on each data
    row so the file can be moved independently of its JSON companion. Structured
    provenance, configuration, and payload fields are canonical JSON strings.
    """

    document = result.to_dict()
    metadata = {
        "schema_version": document["schema_version"],
        "workflow": document["workflow"],
        "status": document["status"],
        "created_at": document["created_at"],
        "software_version": document["software_version"],
        "random_seed": document["random_seed"],
        "provenance_json": _json_cell(document["provenance"]),
        "configuration_json": _json_cell(document["configuration"]),
        "payload_json": _json_cell(document["payload"]),
    }
    row_columns = list(dict.fromkeys(column for row in rows for column in row))
    output = StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=[*metadata, *row_columns])
    writer.writeheader()
    for row in rows:
        writer.writerow(
            {
                **metadata,
                **{
                    key: _json_cell(value)
                    if isinstance(value, (dict, list, tuple))
                    else value
                    for key, value in row.items()
                },
            }
        )
    return ResultExports(
        json_text=json.dumps(document, indent=2, sort_keys=True),
        csv_text=output.getvalue(),
    )
