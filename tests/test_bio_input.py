from __future__ import annotations

import pytest

from bioqubo.io.fasta import parse_fasta_text
from bioqubo.io.structure import parse_structure_text
from bioqubo.provenance import SourceKind

PDB_TEXT = """HEADER    TEST STRUCTURE
ATOM      1  N   GLY A   1       0.000   0.000   0.000  1.00 20.00           N
ATOM      2  CA  GLY A   1       1.000   0.000   0.000  1.00 20.00           C
ATOM      3  N   ALA A   2       2.000   0.000   0.000  1.00 20.00           N
ATOM      4  CA  ALA A   2       3.000   0.000   0.000  1.00 20.00           C
HETATM    5  O   HOH A   3       4.000   0.000   0.000  1.00 20.00           O
END
"""


def test_fasta_parser_returns_validated_local_records() -> None:
    records = parse_fasta_text(
        ">protein_a useful fixture\nACD\nEF\n>protein_b\nMNPQ\n", "fixture.fasta"
    )

    assert [record.identifier for record in records] == ["protein_a", "protein_b"]
    assert records[0].sequence == "ACDEF"
    assert records[0].provenance.source_kind is SourceKind.LOCAL_FILE
    assert records[0].provenance.checksum is not None


def test_fasta_parser_rejects_invalid_residues() -> None:
    with pytest.raises(ValueError, match="invalid residues"):
        parse_fasta_text(">bad\nAC*\n")


def test_pdb_parser_keeps_standard_residue_alpha_carbons() -> None:
    parsed = parse_structure_text(PDB_TEXT, "fixture.pdb")

    assert parsed.format == "pdb"
    assert parsed.chain_ids == ("A",)
    assert [(item.residue_name, item.residue_number) for item in parsed.residues] == [
        ("GLY", 1),
        ("ALA", 2),
    ]
    assert parsed.residues[1].coordinate == (3.0, 0.0, 0.0)


def test_structure_parser_rejects_unknown_format() -> None:
    with pytest.raises(ValueError, match="PDB"):
        parse_structure_text(PDB_TEXT, "fixture.xyz")
