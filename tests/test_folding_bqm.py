from __future__ import annotations

import dimod
import pytest

from bioqubo.fold_energy import evaluate_hp_energy
from bioqubo.folding_bqm import LatticeBounds, build_folding_bqm
from bioqubo.hp_model import parse_hp_sequence
from bioqubo.solvers import solve_folding


def _benchmark_encoding():
    return build_folding_bqm(parse_hp_sequence("HPPH"), LatticeBounds(3, 3))


def test_bqm_exact_ground_state_matches_independent_short_benchmark_energy() -> None:
    """HPPH has a one-contact U-shaped ground state with E_HP = -1."""

    encoding = _benchmark_encoding()
    samples = dimod.ExactSolver().sample(encoding.bqm)
    first = next(iter(samples.data(fields=["sample", "energy"])))
    chain = encoding.decode(first.sample)

    assert chain is not None
    assert chain.validate(expected_length=4).is_valid
    assert evaluate_hp_energy(encoding.sequence, chain).energy == -1
    assert first.energy == pytest.approx(-1.0)


@pytest.mark.parametrize("solver", ["neal", "tabu"])
def test_local_solver_adapters_return_independently_validated_benchmark_fold(solver: str) -> None:
    result = solve_folding(_benchmark_encoding(), solver=solver, reads=30, seed=7)  # type: ignore[arg-type]

    assert result is not None
    assert result.chain.validate(expected_length=4).is_valid
    assert result.evaluation.energy == -1
    assert result.invalid_samples == 0


def test_bqm_rejects_lattice_smaller_than_sequence() -> None:
    with pytest.raises(ValueError, match="fewer sites"):
        build_folding_bqm(parse_hp_sequence("HPPH"), LatticeBounds(1, 3))
