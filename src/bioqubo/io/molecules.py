"""Offline CSV and SDF molecular-library import with checksum provenance."""

from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from io import BytesIO, StringIO

from rdkit import Chem

from bioqubo.chemistry import Molecule, parse_smiles_lines
from bioqubo.provenance import DataProvenance, SourceKind

_SMILES_COLUMNS = ("smiles", "canonical_smiles", "isomeric_smiles")
_IDENTIFIER_COLUMNS = ("identifier", "id", "name", "molecule_chembl_id")


@dataclass(frozen=True, slots=True)
class ImportedMoleculeLibrary:
    """A locally parsed library and the evidence required to reproduce its input."""

    molecules: tuple[Molecule, ...]
    provenance: DataProvenance


def _provenance(source_name: str, data: bytes, file_format: str) -> DataProvenance:
    return DataProvenance(
        source_kind=SourceKind.LOCAL_FILE,
        source_name=source_name,
        identifier=source_name,
        checksum=f"sha256:{hashlib.sha256(data).hexdigest()}",
        notes=(
            f"Parsed locally from a user-supplied {file_format} file; "
            "no network retrieval was used."
        ),
    )


def _column(fieldnames: list[str] | None, choices: tuple[str, ...], label: str) -> str:
    normalized = {name.strip().lower(): name for name in fieldnames or []}
    for candidate in choices:
        if candidate in normalized:
            return normalized[candidate]
    expected = ", ".join(choices)
    raise ValueError(f"CSV needs a {label} column (accepted names: {expected})")


def parse_csv_library(data: bytes, source_name: str = "library.csv") -> ImportedMoleculeLibrary:
    """Parse a UTF-8 CSV with a SMILES column and optional identifier column."""

    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError("CSV must be UTF-8 encoded") from error
    reader = csv.DictReader(StringIO(text))
    smiles_column = _column(reader.fieldnames, _SMILES_COLUMNS, "SMILES")
    identifier_column: str | None
    try:
        identifier_column = _column(reader.fieldnames, _IDENTIFIER_COLUMNS, "identifier")
    except ValueError:
        identifier_column = None
    lines: list[str] = []
    for row_number, row in enumerate(reader, start=2):
        smiles = (row.get(smiles_column) or "").strip()
        if not smiles:
            raise ValueError(f"CSV row {row_number} has no SMILES value")
        identifier = (row.get(identifier_column) or "").strip() if identifier_column else ""
        lines.append(f"{smiles} {identifier or f'molecule_{row_number}'}")
    return ImportedMoleculeLibrary(
        molecules=parse_smiles_lines("\n".join(lines)),
        provenance=_provenance(source_name, data, "CSV"),
    )


def parse_sdf_library(data: bytes, source_name: str = "library.sdf") -> ImportedMoleculeLibrary:
    """Parse an SDF from bytes, using its title or ID property as an identifier."""

    molecules: list[Molecule] = []
    supplier = Chem.ForwardSDMolSupplier(BytesIO(data), sanitize=True, removeHs=True)
    for number, mol in enumerate(supplier, start=1):
        if mol is None:
            raise ValueError(f"SDF record {number} could not be parsed")
        identifier = mol.GetProp("_Name").strip() if mol.HasProp("_Name") else ""
        if not identifier and mol.HasProp("ID"):
            identifier = mol.GetProp("ID").strip()
        smiles = Chem.MolToSmiles(mol, isomericSmiles=True)
        molecules.extend(parse_smiles_lines(f"{smiles} {identifier or f'molecule_{number}'}"))
    if not molecules:
        raise ValueError("No molecules found in SDF")
    return ImportedMoleculeLibrary(
        molecules=tuple(molecules),
        provenance=_provenance(source_name, data, "SDF"),
    )
