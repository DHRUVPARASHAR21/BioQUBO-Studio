"""Core types and parsing for the two-dimensional HP lattice model.

The HP model used here is the coarse-grained model described by Irbäck et al.
(2022).  ``H`` and ``P`` are model bead types, not atomistic amino acids.
"""

from __future__ import annotations

from dataclasses import dataclass


class HPSequenceError(ValueError):
    """Raised when text cannot be interpreted as one HP sequence."""


@dataclass(frozen=True, slots=True)
class HPSequence:
    """An immutable sequence of hydrophobic (H) and polar (P) beads."""

    residues: str

    def __post_init__(self) -> None:
        if not self.residues:
            raise HPSequenceError("HP sequence must contain at least one residue")
        invalid = sorted(set(self.residues) - {"H", "P"})
        if invalid:
            raise HPSequenceError(
                f"HP sequence may contain only H and P; found: {''.join(invalid)}"
            )

    def __len__(self) -> int:
        return len(self.residues)

    def is_hydrophobic(self, index: int) -> bool:
        return self.residues[index] == "H"


def parse_hp_sequence(text: str) -> HPSequence:
    """Parse whitespace-separated HP text or a single-record FASTA-like input.

    Header lines beginning with ``>`` are ignored.  All remaining non-whitespace
    characters must be H or P, case-insensitively.
    """

    if not text.strip():
        raise HPSequenceError("Provide an HP sequence containing H and P residues")
    residues = "".join(
        "".join(line.split()) for line in text.splitlines() if not line.lstrip().startswith(">")
    )
    return HPSequence(residues.upper())
