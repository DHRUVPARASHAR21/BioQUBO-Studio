"""Local inverse HP lattice-protein design and re-folding evidence.

The first stage follows the sequence-space optimization in Irbäck et al.
(2024): binary variables select H/P at each target-fold position, a fixed H
count prevents the all-H trivial solution, and target H-H contacts are favoured.
The second stage re-folds candidates with the local folding model.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Literal

import dimod
import neal
import tabu

from bioqubo.fold_energy import ContactEvaluation
from bioqubo.folding_bqm import LatticeBounds, build_folding_bqm
from bioqubo.hp_model import HPSequence
from bioqubo.solvers import FoldingResult, SolverName, solve_folding
from bioqubo.target_fold import TargetFold

DesignSolverName = Literal["neal", "tabu"]


@dataclass(frozen=True, slots=True)
class SequenceDesignEncoding:
    """A fixed-composition target-contact BQM over one binary variable per residue."""

    target: TargetFold
    hydrophobic_count: int
    composition_strength: float
    bqm: dimod.BinaryQuadraticModel

    def decode(self, sample: dict[int, int]) -> HPSequence | None:
        """Decode samples only when they satisfy the requested H count."""

        residues = "".join(
            "H" if sample.get(index, 0) else "P" for index in range(self.target.length)
        )
        if residues.count("H") != self.hydrophobic_count:
            return None
        return HPSequence(residues)


@dataclass(frozen=True, slots=True)
class DesignedSequence:
    """A sequence ranked by its independently calculated target-fold energy."""

    sequence: HPSequence
    target_evaluation: ContactEvaluation
    bqm_energy: float


@dataclass(frozen=True, slots=True)
class DesignSearchResult:
    """Unique valid design candidates produced by one local sampler run."""

    solver: DesignSolverName
    candidates: tuple[DesignedSequence, ...]
    valid_samples: int
    invalid_samples: int


@dataclass(frozen=True, slots=True)
class RecoveryEvidence:
    """Evidence from a separate re-folding run for one designed sequence."""

    candidate: DesignedSequence
    folding_result: FoldingResult | None
    target_recovered: bool


def evaluate_target_energy(sequence: HPSequence, target: TargetFold) -> ContactEvaluation:
    """Independently calculate H-H contacts on the fixed target structure."""

    if len(sequence) != target.length:
        raise ValueError("sequence length must match the target-fold length")
    contacts = tuple(
        (first, second)
        for first, second in target.contacts
        if sequence.is_hydrophobic(first) and sequence.is_hydrophobic(second)
    )
    return ContactEvaluation(contacts)


def build_sequence_design_bqm(
    target: TargetFold, hydrophobic_count: int, composition_strength: float = 4.0
) -> SequenceDesignEncoding:
    """Build a target-contact BQM with an exact hydrophobic-residue count."""

    if not 1 <= hydrophobic_count < target.length:
        raise ValueError("hydrophobic count must be between 1 and target length minus 1")
    if composition_strength <= 0:
        raise ValueError("composition strength must be positive")
    bqm = dimod.BinaryQuadraticModel.empty(dimod.BINARY)
    indices = range(target.length)
    # A(sum_i h_i - N_H)^2: prohibit the all-H shortcut and fix composition.
    bqm.offset += composition_strength * hydrophobic_count**2
    bqm.add_linear_from(
        (index, composition_strength * (1 - 2 * hydrophobic_count)) for index in indices
    )
    bqm.add_quadratic_from(
        (first, second, 2 * composition_strength) for first, second in combinations(indices, 2)
    )
    bqm.add_quadratic_from((first, second, -1.0) for first, second in target.contacts)
    return SequenceDesignEncoding(target, hydrophobic_count, composition_strength, bqm)


def _sample_design(
    encoding: SequenceDesignEncoding, solver: DesignSolverName, reads: int, seed: int | None
) -> dimod.SampleSet:
    if reads < 1:
        raise ValueError("reads must be at least 1")
    if solver == "neal":
        return neal.SimulatedAnnealingSampler().sample(encoding.bqm, num_reads=reads, seed=seed)
    if solver == "tabu":
        return tabu.TabuSampler().sample(encoding.bqm, num_reads=reads, seed=seed)
    raise ValueError(f"Unknown local solver: {solver}")


def design_sequences(
    encoding: SequenceDesignEncoding,
    solver: DesignSolverName = "neal",
    reads: int = 100,
    seed: int | None = 123,
    max_candidates: int = 10,
) -> DesignSearchResult:
    """Sample target-optimised sequences and deduplicate valid candidates."""

    if max_candidates < 1:
        raise ValueError("max_candidates must be at least 1")
    samples = _sample_design(encoding, solver, reads, seed)
    candidates: dict[str, DesignedSequence] = {}
    invalid = 0
    valid = 0
    for record in samples.data(fields=["sample", "energy"]):
        sequence = encoding.decode(dict(record.sample))
        if sequence is None:
            invalid += 1
            continue
        valid += 1
        candidate = DesignedSequence(
            sequence=sequence,
            target_evaluation=evaluate_target_energy(sequence, encoding.target),
            bqm_energy=float(record.energy),
        )
        existing = candidates.get(sequence.residues)
        if existing is None or candidate.bqm_energy < existing.bqm_energy:
            candidates[sequence.residues] = candidate
    ordered = sorted(
        candidates.values(),
        key=lambda item: (item.target_evaluation.energy, item.sequence.residues),
    )
    return DesignSearchResult(solver, tuple(ordered[:max_candidates]), valid, invalid)


def refold_candidates(
    target: TargetFold,
    candidates: tuple[DesignedSequence, ...],
    solver: SolverName = "neal",
    reads: int = 100,
    seed: int | None = 123,
) -> tuple[RecoveryEvidence, ...]:
    """Re-fold candidates and record exact target-shape recovery evidence."""

    xs = [x for x, _ in target.chain.coordinates]
    ys = [y for _, y in target.chain.coordinates]
    lattice = LatticeBounds(max(xs) - min(xs) + 3, max(ys) - min(ys) + 3)
    evidence: list[RecoveryEvidence] = []
    for index, candidate in enumerate(candidates):
        result = solve_folding(
            build_folding_bqm(candidate.sequence, lattice),
            solver=solver,
            reads=reads,
            seed=None if seed is None else seed + index,
        )
        recovered = result is not None and target.matches_shape(result.chain)
        evidence.append(RecoveryEvidence(candidate, result, recovered))
    return tuple(evidence)
