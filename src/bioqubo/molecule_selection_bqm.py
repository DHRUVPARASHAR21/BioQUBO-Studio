"""Local fixed-cardinality, fingerprint-diverse molecular prioritization BQM."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Literal

import dimod
import neal
import tabu
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem

from bioqubo.chemistry import Molecule

SelectionSolver = Literal["neal", "tabu"]


@dataclass(frozen=True, slots=True)
class MoleculeSelectionEncoding:
    molecules: tuple[Molecule, ...]
    shortlist_size: int
    bqm: dimod.BinaryQuadraticModel

    def decode(self, sample: dict[int, int]) -> tuple[Molecule, ...] | None:
        selected = tuple(
            molecule for index, molecule in enumerate(self.molecules) if sample.get(index, 0)
        )
        return selected if len(selected) == self.shortlist_size else None


def _similarity(first: Molecule, second: Molecule) -> float:
    first_fp = AllChem.GetMorganFingerprintAsBitVect(
        Chem.MolFromSmiles(first.smiles), 2, nBits=1024
    )
    second_fp = AllChem.GetMorganFingerprintAsBitVect(
        Chem.MolFromSmiles(second.smiles), 2, nBits=1024
    )
    return float(DataStructs.TanimotoSimilarity(first_fp, second_fp))


def build_molecule_selection_bqm(
    molecules: tuple[Molecule, ...], shortlist_size: int, diversity_weight: float = 1.0
) -> MoleculeSelectionEncoding:
    """Select exactly k molecules while penalizing fingerprint-similar pairs."""
    if not 1 <= shortlist_size <= len(molecules):
        raise ValueError("shortlist size must be between 1 and number of eligible molecules")
    strength = 10.0
    bqm = dimod.BinaryQuadraticModel.empty(dimod.BINARY)
    bqm.offset += strength * shortlist_size**2
    bqm.add_linear_from((i, strength * (1 - 2 * shortlist_size)) for i in range(len(molecules)))
    bqm.add_quadratic_from((i, j, 2 * strength) for i, j in combinations(range(len(molecules)), 2))
    bqm.add_quadratic_from(
        (i, j, diversity_weight * _similarity(molecules[i], molecules[j]))
        for i, j in combinations(range(len(molecules)), 2)
    )
    return MoleculeSelectionEncoding(molecules, shortlist_size, bqm)


def solve_molecule_selection(
    encoding: MoleculeSelectionEncoding,
    solver: SelectionSolver = "neal",
    reads: int = 100,
    seed: int = 123,
) -> tuple[Molecule, ...] | None:
    sampler = neal.SimulatedAnnealingSampler() if solver == "neal" else tabu.TabuSampler()
    samples = sampler.sample(encoding.bqm, num_reads=reads, seed=seed)
    for record in samples.data(fields=["sample", "energy"]):
        selected = encoding.decode(dict(record.sample))
        if selected is not None:
            return selected
    return None
