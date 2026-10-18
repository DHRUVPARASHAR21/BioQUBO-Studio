"""Residue-contact networks derived locally from alpha-carbon coordinates."""

from __future__ import annotations

from dataclasses import dataclass
from math import dist

from bioqubo.io.structure import ParsedStructure, ResidueCoordinate


@dataclass(frozen=True, slots=True)
class ResidueNetwork:
    """An undirected CA-distance contact network for one parsed structure."""

    residues: tuple[ResidueCoordinate, ...]
    edges: tuple[tuple[int, int], ...]
    cutoff_angstrom: float

    def degree(self, index: int) -> int:
        return sum(index in edge for edge in self.edges)


def build_residue_network(
    structure: ParsedStructure, cutoff_angstrom: float = 8.0
) -> ResidueNetwork:
    """Create non-sequential CA contacts at or below the selected cutoff."""

    if cutoff_angstrom <= 0:
        raise ValueError("contact cutoff must be positive")
    edges: list[tuple[int, int]] = []
    for first, first_residue in enumerate(structure.residues):
        for second in range(first + 1, len(structure.residues)):
            second_residue = structure.residues[second]
            sequential = (
                first_residue.chain_id == second_residue.chain_id
                and second_residue.residue_number - first_residue.residue_number == 1
            )
            if (
                not sequential
                and dist(first_residue.coordinate, second_residue.coordinate) <= cutoff_angstrom
            ):
                edges.append((first, second))
    return ResidueNetwork(structure.residues, tuple(edges), cutoff_angstrom)
