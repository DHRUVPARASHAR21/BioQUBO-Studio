from __future__ import annotations

from bioqubo.offline_demo import run_offline_check
from bioqubo.provenance import SourceKind


def test_offline_check_reads_the_bundled_fixture() -> None:
    result = run_offline_check()

    assert result.workflow == "offline_foundation_check"
    assert result.provenance.source_kind is SourceKind.BUNDLED_EXAMPLE
    assert result.payload["record_count"] == 1
    assert result.configuration["network_access"] is False
    assert result.random_seed == 2026


def test_offline_result_is_json_compatible() -> None:
    payload = run_offline_check().to_dict()

    assert payload["status"] == "success"
    assert payload["provenance"]["identifier"] == "offline-foundation-v1"
    assert payload["configuration"]["network_access"] is False
