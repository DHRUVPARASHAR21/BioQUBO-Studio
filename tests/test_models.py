from __future__ import annotations

from datetime import datetime

import pytest

from bioqubo.models import ResultEnvelope, ResultStatus
from bioqubo.provenance import DataProvenance, SourceKind
from bioqubo.validation import ValidationIssue, ValidationReport, ValidationSeverity


def test_provenance_rejects_naive_timestamp() -> None:
    with pytest.raises(ValueError, match="timezone"):
        DataProvenance(
            source_kind=SourceKind.MANUAL_ENTRY,
            source_name="test",
            identifier="test-1",
            retrieved_at=datetime(2026, 1, 1),
        )


def test_result_rejects_negative_seed() -> None:
    provenance = DataProvenance(
        source_kind=SourceKind.MANUAL_ENTRY,
        source_name="test",
        identifier="test-1",
    )
    with pytest.raises(ValueError, match="non-negative"):
        ResultEnvelope(
            workflow="test",
            status=ResultStatus.SUCCESS,
            provenance=provenance,
            configuration={},
            payload={},
            random_seed=-1,
        )


def test_validation_report_flags_errors_but_not_warnings() -> None:
    warning_only = ValidationReport(
        issues=(
            ValidationIssue(code="warn", message="notice", severity=ValidationSeverity.WARNING),
        )
    )
    error_report = ValidationReport(issues=(ValidationIssue(code="error", message="stop"),))

    assert warning_only.is_valid
    assert not error_report.is_valid
