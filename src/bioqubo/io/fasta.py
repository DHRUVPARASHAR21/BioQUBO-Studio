"""Strict, local FASTA parsing with source provenance."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from bioqubo.provenance import DataProvenance, SourceKind

_AMINO_ACIDS = frozenset("ACDEFGHIKLMNPQRSTVWYBXZJUO")


@dataclass(frozen=True, slots=True)
class FastaRecord:
    """One validated protein sequence and its FASTA metadata."""

    identifier: str
    description: str
    sequence: str
    provenance: DataProvenance


def _provenance(name: str, data: bytes) -> DataProvenance:
    return DataProvenance(
        source_kind=SourceKind.LOCAL_FILE,
        source_name=name,
        identifier=name,
        checksum=f"sha256:{hashlib.sha256(data).hexdigest()}",
        notes="Parsed locally from a user-supplied FASTA file; no network retrieval was used.",
    )


def parse_fasta_text(text: str, source_name: str = "manual.fasta") -> tuple[FastaRecord, ...]:
    """Parse one or more protein FASTA records without network access."""

    data = text.encode("utf-8")
    records: list[FastaRecord] = []
    header: str | None = None
    sequence_lines: list[str] = []

    def finish_record() -> None:
        if header is None:
            return
        fields = header.split(maxsplit=1)
        identifier = fields[0] if fields else ""
        sequence = "".join(sequence_lines).upper()
        if not identifier:
            raise ValueError("FASTA header must include an identifier")
        if not sequence:
            raise ValueError(f"FASTA record {identifier!r} has no sequence")
        invalid = sorted(set(sequence) - _AMINO_ACIDS)
        if invalid:
            raise ValueError(
                f"FASTA record {identifier!r} has invalid residues: {''.join(invalid)}"
            )
        records.append(
            FastaRecord(
                identifier=identifier,
                description=fields[1] if len(fields) == 2 else "",
                sequence=sequence,
                provenance=_provenance(source_name, data),
            )
        )

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith(">"):
            finish_record()
            header = line[1:].strip()
            sequence_lines = []
        elif header is None:
            raise ValueError(f"Expected a FASTA header starting with '>' before line {line_number}")
        else:
            sequence_lines.append("".join(line.split()))
    finish_record()
    if not records:
        raise ValueError("No FASTA records found")
    return tuple(records)


def parse_fasta_file(path: Path) -> tuple[FastaRecord, ...]:
    """Read and parse a local UTF-8 FASTA file."""

    if not path.is_file():
        raise ValueError(f"FASTA file does not exist: {path}")
    return parse_fasta_text(path.read_text(encoding="utf-8"), source_name=path.name)
