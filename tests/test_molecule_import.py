from __future__ import annotations

from importlib.resources import files
from pathlib import Path

import pytest

from bioqubo.io.molecules import parse_csv_library, parse_sdf_library
from bioqubo.provenance import SourceKind
from bioqubo.ui.molecule_prioritization import _read_library


def test_csv_import_retains_identifier_and_checksum() -> None:
    library = parse_csv_library(b"identifier,smiles\nethanol,CCO\nbenzene,c1ccccc1\n", "test.csv")

    assert [m.identifier for m in library.molecules] == ["ethanol", "benzene"]
    assert library.provenance.source_kind is SourceKind.LOCAL_FILE
    assert library.provenance.checksum and library.provenance.checksum.startswith("sha256:")


def test_csv_without_smiles_column_is_rejected() -> None:
    with pytest.raises(ValueError, match="SMILES column"):
        parse_csv_library(b"identifier,name\n1,ethanol\n")


def test_sdf_import_uses_title_as_identifier() -> None:
    data = Path(__file__).parent / "fixtures" / "ethanol.sdf"
    library = parse_sdf_library(data.read_bytes(), data.name)

    assert library.molecules[0].identifier == "ethanol"
    assert library.molecules[0].smiles == "CCO"


def test_bundled_demo_is_importable_with_attributed_provenance() -> None:
    assert files("bioqubo.data").joinpath("demo", "hiv1_protease_chembl_subset.json").is_file()

    library = _read_library("Bundled HIV-1 protease demo", "", None)

    assert len(library.molecules) == 4
    assert library.provenance.source_kind is SourceKind.BUNDLED_EXAMPLE
    assert library.provenance.license_name == "CC BY-SA 3.0"
