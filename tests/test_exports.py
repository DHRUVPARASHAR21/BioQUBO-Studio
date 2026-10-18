from __future__ import annotations

import csv
import json
from io import StringIO

from bioqubo.exports import build_result_exports
from bioqubo.models import ResultEnvelope, ResultStatus
from bioqubo.provenance import DataProvenance, SourceKind


def _result() -> ResultEnvelope:
    return ResultEnvelope(
        workflow="hp_lattice_folding",
        status=ResultStatus.SUCCESS,
        provenance=DataProvenance(
            source_kind=SourceKind.MANUAL_ENTRY,
            source_name="Manual HP sequence",
            identifier="manual-hp-sequence",
            checksum="sha256:test",
        ),
        configuration={"solver": "neal", "reads": 20, "network_access": False},
        payload={"coordinates": ((0, 0), (1, 0)), "independent_energy": -1},
        random_seed=7,
        software_version="0.1.0-test",
    )


def test_shared_exports_keep_complete_result_metadata_in_json_and_csv() -> None:
    exports = build_result_exports(
        _result(), [{"residue_index": 0, "coordinate": (0, 0)}]
    )

    document = json.loads(exports.json_text)
    row = next(csv.DictReader(StringIO(exports.csv_text)))

    assert document["provenance"]["checksum"] == "sha256:test"
    assert document["configuration"]["solver"] == "neal"
    assert document["random_seed"] == 7
    assert document["software_version"] == "0.1.0-test"
    assert json.loads(row["provenance_json"])["identifier"] == "manual-hp-sequence"
    assert json.loads(row["configuration_json"])["reads"] == 20
    assert json.loads(row["payload_json"])["independent_energy"] == -1
    assert row["random_seed"] == "7"
    assert row["software_version"] == "0.1.0-test"
    assert json.loads(row["coordinate"]) == [0, 0]


def test_shared_csv_has_header_when_result_has_no_data_rows() -> None:
    exports = build_result_exports(_result(), [])

    reader = csv.DictReader(StringIO(exports.csv_text))

    assert reader.fieldnames is not None
    assert "payload_json" in reader.fieldnames
    assert list(reader) == []
