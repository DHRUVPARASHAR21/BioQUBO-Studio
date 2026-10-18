"""Fixed-cardinality residue-network selection BQM for local exploration."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Literal

import dimod
import neal
import tabu

from bioqubo.residue_network import ResidueNetwork

SelectionSolver = Literal["neal", "tabu"]


@dataclass(frozen=True, slots=True)
class ResidueSelectionEncoding:
    network: ResidueNetwork
    selection_count: int
    cardinality_strength: float
    bqm: dimod.BinaryQuadraticModel

    def decode(self, sample: dict[int, int]) -> tuple[int, ...] | None:
        selected = tuple(
            index for index in range(len(self.network.residues)) if sample.get(index, 0)
        )
        return selected if len(selected) == self.selection_count else None


@dataclass(frozen=True, slots=True)
class ResidueSelectionResult:
    solver: SelectionSolver
    selected_indices: tuple[int, ...]
    objective_score: int
    bqm_energy: float
    valid_samples: int
    invalid_samples: int


def evaluate_selection(network: ResidueNetwork, selected_indices: tuple[int, ...]) -> int:
    """Return the sum of graph degrees for an independently valid selection."""

    if len(set(selected_indices)) != len(selected_indices):
        raise ValueError("residue selection contains duplicates")
    if any(index < 0 or index >= len(network.residues) for index in selected_indices):
        raise ValueError("residue selection contains an out-of-range index")
    return sum(network.degree(index) for index in selected_indices)


def build_residue_selection_bqm(
    network: ResidueNetwork, selection_count: int, cardinality_strength: float = 10.0
) -> ResidueSelectionEncoding:
    """Maximise contact-network degree while selecting exactly ``selection_count`` residues."""

    size = len(network.residues)
    if not 1 <= selection_count <= size:
        raise ValueError("selection count must be between 1 and the number of residues")
    bqm = dimod.BinaryQuadraticModel.empty(dimod.BINARY)
    bqm.offset += cardinality_strength * selection_count**2
    bqm.add_linear_from(
        (index, cardinality_strength * (1 - 2 * selection_count) - network.degree(index))
        for index in range(size)
    )
    bqm.add_quadratic_from(
        (first, second, 2 * cardinality_strength) for first, second in combinations(range(size), 2)
    )
    return ResidueSelectionEncoding(network, selection_count, cardinality_strength, bqm)


def solve_residue_selection(
    encoding: ResidueSelectionEncoding,
    solver: SelectionSolver = "neal",
    reads: int = 100,
    seed: int | None = 123,
) -> ResidueSelectionResult | None:
    """Run one local sampler and independently verify the selected cardinality and score."""

    if reads < 1:
        raise ValueError("reads must be at least 1")
    sampler = neal.SimulatedAnnealingSampler() if solver == "neal" else tabu.TabuSampler()
    if solver not in {"neal", "tabu"}:
        raise ValueError(f"Unknown local solver: {solver}")
    samples = sampler.sample(encoding.bqm, num_reads=reads, seed=seed)
    valid: list[tuple[int, float, tuple[int, ...]]] = []
    invalid = 0
    for record in samples.data(fields=["sample", "energy"]):
        selected = encoding.decode(dict(record.sample))
        if selected is None:
            invalid += 1
            continue
        valid.append(
            (evaluate_selection(encoding.network, selected), float(record.energy), selected)
        )
    if not valid:
        return None
    valid.sort(key=lambda item: (-item[0], item[1], item[2]))
    score, energy, selected = valid[0]
    return ResidueSelectionResult(solver, selected, score, energy, len(valid), invalid)
