"""Local Ocean sampler adapters that independently validate decoded folds."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import dimod
import neal
import tabu

from bioqubo.fold_energy import ContactEvaluation, evaluate_hp_energy
from bioqubo.fold_validation import LatticeChain
from bioqubo.folding_bqm import FoldingEncoding

SolverName = Literal["neal", "tabu"]


@dataclass(frozen=True, slots=True)
class FoldingResult:
    """The best independently validated fold returned by a local sampler."""

    solver: SolverName
    chain: LatticeChain
    evaluation: ContactEvaluation
    bqm_energy: float
    valid_samples: int
    invalid_samples: int


def _sample(
    encoding: FoldingEncoding, solver: SolverName, reads: int, seed: int | None
) -> dimod.SampleSet:
    if reads < 1:
        raise ValueError("reads must be at least 1")
    if solver == "neal":
        return neal.SimulatedAnnealingSampler().sample(encoding.bqm, num_reads=reads, seed=seed)
    if solver == "tabu":
        return tabu.TabuSampler().sample(encoding.bqm, num_reads=reads, seed=seed)
    raise ValueError(f"Unknown local solver: {solver}")


def solve_folding(
    encoding: FoldingEncoding,
    solver: SolverName = "neal",
    reads: int = 100,
    seed: int | None = 123,
) -> FoldingResult | None:
    """Sample, decode, validate, and rank folds by independent HP energy."""

    samples = _sample(encoding, solver, reads, seed)
    valid: list[tuple[ContactEvaluation, float, LatticeChain]] = []
    invalid = 0
    for record in samples.data(fields=["sample", "energy"]):
        chain = encoding.decode(record.sample)
        if chain is None or not chain.validate(expected_length=len(encoding.sequence)).is_valid:
            invalid += 1
            continue
        valid.append((evaluate_hp_energy(encoding.sequence, chain), float(record.energy), chain))
    if not valid:
        return None
    valid.sort(key=lambda item: (item[0].energy, item[1], item[2].coordinates))
    evaluation, bqm_energy, chain = valid[0]
    return FoldingResult(solver, chain, evaluation, bqm_energy, len(valid), invalid)
