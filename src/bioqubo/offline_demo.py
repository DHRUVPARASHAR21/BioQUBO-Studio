"""Offline-only Milestone 0 verification workflow."""

from __future__ import annotations

import json
from importlib.metadata import PackageNotFoundError, version
from importlib.resources import files
from pathlib import Path

from bioqubo.models import ResultEnvelope, ResultStatus
from bioqubo.provenance import DataProvenance, SourceKind

SAMPLE_RESOURCE = files("bioqubo").joinpath("data", "offline_foundation_sample.json")


def software_version() -> str:
    """Return the installed distribution version or the source-tree fallback."""

    try:
        return version("bioqubo-studio")
    except PackageNotFoundError:
        return "0.1.0+source"


def run_offline_check(sample_path: Path | None = None) -> ResultEnvelope:
    """Read the bundled fixture and wrap it in a reproducible result envelope."""

    resource = sample_path if sample_path is not None else SAMPLE_RESOURCE
    sample = json.loads(resource.read_text(encoding="utf-8"))
    provenance = DataProvenance(
        source_kind=SourceKind.BUNDLED_EXAMPLE,
        source_name="BioQUBO Studio bundled offline foundation sample",
        identifier=sample["id"],
        source_url=None,
        license_name="MIT",
        checksum=sample["checksum"],
        notes="Non-biological fixture used to verify local provenance and result serialization.",
    )
    return ResultEnvelope(
        workflow="offline_foundation_check",
        status=ResultStatus.SUCCESS,
        provenance=provenance,
        configuration={"network_access": False, "sample_path": str(resource)},
        payload={"message": sample["message"], "record_count": sample["record_count"]},
        random_seed=sample["random_seed"],
        software_version=software_version(),
    )


def main() -> None:
    """Run the offline verification from the command line."""

    print(json.dumps(run_offline_check().to_dict(), indent=2))


if __name__ == "__main__":
    main()
