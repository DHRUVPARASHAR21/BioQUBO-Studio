from __future__ import annotations

import dimod
import pytest

from bioqubo.fold_validation import LatticeChain
from bioqubo.inverse_design import (
    build_sequence_design_bqm,
    design_sequences,
    evaluate_target_energy,
    refold_candidates,
)
from bioqubo.target_fold import TargetFold, parse_target_coordinates


def _u_target() -> TargetFold:
    return TargetFold(LatticeChain.from_coordinates([(0, 0), (1, 0), (1, 1), (0, 1)]))


def test_target_parser_and_contacts() -> None:
    target = TargetFold(parse_target_coordinates("0, 0\n1 0\n1,1\n0 1 # close U"))

    assert target.length == 4
    assert target.contacts == ((0, 3),)


def test_target_fold_rejects_disconnected_coordinates() -> None:
    with pytest.raises(ValueError, match="Invalid target fold"):
        TargetFold(LatticeChain.from_coordinates([(0, 0), (2, 0)]))


def test_design_bqm_exact_ground_state_matches_target_contact_energy() -> None:
    encoding = build_sequence_design_bqm(_u_target(), hydrophobic_count=2)
    record = next(iter(dimod.ExactSolver().sample(encoding.bqm).data(fields=["sample", "energy"])))
    sequence = encoding.decode(dict(record.sample))

    assert sequence is not None
    assert sequence.residues == "HPPH"
    assert evaluate_target_energy(sequence, encoding.target).energy == -1
    assert record.energy == pytest.approx(-1.0)


@pytest.mark.parametrize("solver", ["neal", "tabu"])
def test_local_design_adapters_return_target_optimised_sequence(solver: str) -> None:
    result = design_sequences(
        build_sequence_design_bqm(_u_target(), hydrophobic_count=2),
        solver=solver,  # type: ignore[arg-type]
        reads=30,
        seed=7,
    )

    assert result.invalid_samples == 0
    assert result.candidates[0].sequence.residues == "HPPH"
    assert result.candidates[0].target_evaluation.energy == -1


def test_refolding_records_target_recovery_evidence() -> None:
    designs = design_sequences(
        build_sequence_design_bqm(_u_target(), hydrophobic_count=2), reads=30, seed=7
    )
    evidence = refold_candidates(_u_target(), designs.candidates[:1], reads=30, seed=7)

    assert len(evidence) == 1
    assert evidence[0].folding_result is not None
    assert evidence[0].target_recovered


def test_shape_matching_accepts_rotated_target() -> None:
    target = _u_target()
    rotated = LatticeChain.from_coordinates([(0, 0), (0, 1), (-1, 1), (-1, 0)])

    assert target.matches_shape(rotated)
