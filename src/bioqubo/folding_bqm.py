"""Distributed lattice-site BQM encoding for two-dimensional HP folding.

Each binary variable represents residue ``i`` occupying lattice site ``(x, y)``.
Residue/site parity is fixed, then quadratic terms encode one location per
residue, self-avoidance, chain connectivity, and non-bonded H-H contacts. This
is the distributed lattice representation described by Irbäck et al. (2022),
adapted here for small, local square-lattice experiments.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from itertools import combinations

import dimod

from bioqubo.fold_validation import Coordinate, LatticeChain, manhattan_distance
from bioqubo.hp_model import HPSequence

Variable = tuple[int, int, int]


@dataclass(frozen=True, slots=True)
class LatticeBounds:
    """Finite rectangular lattice used by the local BQM."""

    width: int
    height: int

    def __post_init__(self) -> None:
        if self.width < 1 or self.height < 1:
            raise ValueError("lattice width and height must both be positive")

    @property
    def site_count(self) -> int:
        return self.width * self.height

    def sites_for_residue(self, index: int) -> tuple[Coordinate, ...]:
        parity = index % 2
        return tuple(
            (x, y)
            for x in range(self.width)
            for y in range(self.height)
            if (x + y) % 2 == parity
        )


@dataclass(frozen=True, slots=True)
class PenaltyWeights:
    """Constraint weights from the paper's local 2D starting configuration."""

    unique_location: float = 2.0
    self_avoidance: float = 3.0
    chain_connectivity: float = 3.0

    def __post_init__(self) -> None:
        if min(self.unique_location, self.self_avoidance, self.chain_connectivity) <= 0:
            raise ValueError("all BQM penalty weights must be positive")


@dataclass(frozen=True, slots=True)
class FoldingEncoding:
    """A BQM and the metadata required to decode it safely."""

    sequence: HPSequence
    lattice: LatticeBounds
    penalties: PenaltyWeights
    bqm: dimod.BinaryQuadraticModel

    def decode(self, sample: Mapping[Variable, int]) -> LatticeChain | None:
        """Decode only samples with exactly one active site per residue."""

        coordinates: list[Coordinate] = []
        for index in range(len(self.sequence)):
            active = [
                (x, y)
                for x, y in self.lattice.sites_for_residue(index)
                if sample.get((x, y, index), 0) == 1
            ]
            if len(active) != 1:
                return None
            coordinates.append(active[0])
        return LatticeChain.from_coordinates(coordinates)


def build_folding_bqm(
    sequence: HPSequence,
    lattice: LatticeBounds,
    penalties: PenaltyWeights | None = None,
) -> FoldingEncoding:
    """Build a binary quadratic HP-folding model on a finite square lattice."""

    if len(sequence) > lattice.site_count:
        raise ValueError("lattice has fewer sites than residues")
    weights = penalties or PenaltyWeights()
    bqm = dimod.BinaryQuadraticModel.empty(dimod.BINARY)
    sites_by_index = {index: lattice.sites_for_residue(index) for index in range(len(sequence))}

    # A(sum x - 1)^2: exactly one allowed-parity site for every residue.
    for index, sites in sites_by_index.items():
        variables = [(x, y, index) for x, y in sites]
        bqm.offset += weights.unique_location
        bqm.add_linear_from((variable, -weights.unique_location) for variable in variables)
        bqm.add_quadratic_from(
            (first, second, 2 * weights.unique_location)
            for first, second in combinations(variables, 2)
        )

    # A residue pair on the same site violates self-avoidance.
    for first, second in combinations(range(len(sequence)), 2):
        if first % 2 != second % 2:
            continue
        shared = set(sites_by_index[first]).intersection(sites_by_index[second])
        bqm.add_quadratic_from(
            ((x, y, first), (x, y, second), weights.self_avoidance) for x, y in shared
        )

    # Consecutive residues must sit on neighbouring sites.
    for index in range(len(sequence) - 1):
        for first in sites_by_index[index]:
            for second in sites_by_index[index + 1]:
                if manhattan_distance(first, second) != 1:
                    bqm.add_quadratic(
                        (first[0], first[1], index),
                        (second[0], second[1], index + 1),
                        weights.chain_connectivity,
                    )

    # Favour non-bonded nearest-neighbour H-H contacts.
    hydrophobic = [index for index in range(len(sequence)) if sequence.is_hydrophobic(index)]
    for first, second in combinations(hydrophobic, 2):
        if second - first <= 1:
            continue
        for first_site in sites_by_index[first]:
            for second_site in sites_by_index[second]:
                if manhattan_distance(first_site, second_site) == 1:
                    bqm.add_quadratic(
                        (first_site[0], first_site[1], first),
                        (second_site[0], second_site[1], second),
                        -1.0,
                    )
    return FoldingEncoding(sequence, lattice, weights, bqm)
