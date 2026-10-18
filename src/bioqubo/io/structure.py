"""Local PDB/mmCIF parsing with residue-level coordinates and provenance."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Literal

from Bio.PDB import MMCIFParser, PDBParser

from bioqubo.provenance import DataProvenance, SourceKind

StructureFormat = Literal["pdb", "mmcif"]


@dataclass(frozen=True, slots=True)
class ResidueCoordinate:
    """A standard amino-acid residue represented by its alpha-carbon coordinate."""

    chain_id: str
    residue_name: str
    residue_number: int
    insertion_code: str
    coordinate: tuple[float, float, float]


@dataclass(frozen=True, slots=True)
class ParsedStructure:
    """First-model standard residues with alpha-carbon positions from a local structure file."""

    structure_id: str
    format: StructureFormat
    residues: tuple[ResidueCoordinate, ...]
    provenance: DataProvenance

    @property
    def chain_ids(self) -> tuple[str, ...]:
        return tuple(sorted({residue.chain_id for residue in self.residues}))


def _detect_format(source_name: str) -> StructureFormat:
    suffix = Path(source_name).suffix.lower()
    if suffix in {".pdb", ".ent"}:
        return "pdb"
    if suffix in {".cif", ".mmcif"}:
        return "mmcif"
    raise ValueError("Structure format must be PDB (.pdb/.ent) or mmCIF (.cif/.mmcif)")


def parse_structure_text(text: str, source_name: str) -> ParsedStructure:
    """Parse local PDB or mmCIF text, retaining standard residues with CA atoms."""

    file_format = _detect_format(source_name)
    parser = PDBParser(QUIET=True) if file_format == "pdb" else MMCIFParser(QUIET=True)
    try:
        structure = parser.get_structure(Path(source_name).stem, StringIO(text))
    except Exception as error:
        raise ValueError(f"Could not parse {file_format.upper()} structure: {error}") from error
    models = list(structure.get_models())
    if not models:
        raise ValueError("Structure contains no models")
    residues: list[ResidueCoordinate] = []
    for chain in models[0]:
        for residue in chain:
            hetero_flag, residue_number, insertion_code = residue.id
            if hetero_flag.strip() or "CA" not in residue:
                continue
            coordinate = residue["CA"].coord
            residues.append(
                ResidueCoordinate(
                    chain_id=chain.id or "_",
                    residue_name=residue.resname.strip(),
                    residue_number=int(residue_number),
                    insertion_code=insertion_code.strip(),
                    coordinate=(float(coordinate[0]), float(coordinate[1]), float(coordinate[2])),
                )
            )
    if not residues:
        raise ValueError(
            "No standard residues with alpha-carbon atoms were found in the first model"
        )
    data = text.encode("utf-8")
    return ParsedStructure(
        structure_id=Path(source_name).stem,
        format=file_format,
        residues=tuple(residues),
        provenance=DataProvenance(
            source_kind=SourceKind.LOCAL_FILE,
            source_name=source_name,
            identifier=Path(source_name).name,
            checksum=f"sha256:{hashlib.sha256(data).hexdigest()}",
            notes=(
                "Parsed locally from a user-supplied structure file; no network retrieval was used."
            ),
        ),
    )


def parse_structure_file(path: Path) -> ParsedStructure:
    """Read and parse a local PDB or mmCIF structure file."""

    if not path.is_file():
        raise ValueError(f"Structure file does not exist: {path}")
    return parse_structure_text(path.read_text(encoding="utf-8"), source_name=path.name)
