from __future__ import annotations

import json

from bioqubo.models import ResultEnvelope, ResultStatus
from bioqubo.provenance import DataProvenance, SourceKind
from bioqubo.result_history import create_history_entry, serialize_history


def _result(workflow: str) -> ResultEnvelope:
    return ResultEnvelope(
        workflow=workflow,
        status=ResultStatus.SUCCESS,
        provenance=DataProvenance(
            source_kind=SourceKind.MANUAL_ENTRY,
            source_name="test input",
            identifier="test-input",
        ),
        configuration={"solver": "neal"},
        payload={"score": 2},
        random_seed=12,
        software_version="0.1.0-test",
    )


def test_history_bundle_preserves_complete_result_envelopes() -> None:
    entry = create_history_entry(_result("hp_lattice_folding"), [{"residue_index": 0}], "fold")

    document = json.loads(serialize_history([entry]))

    assert entry.json_file_name == "fold.json"
    assert entry.csv_file_name == "fold.csv"
    assert document["history_schema_version"] == "1.0"
    assert document["results"][0]["workflow"] == "hp_lattice_folding"
    assert document["results"][0]["configuration"]["solver"] == "neal"
    assert document["results"][0]["random_seed"] == 12
