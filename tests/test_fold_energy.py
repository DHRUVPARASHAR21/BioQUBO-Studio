from __future__ import annotations

import pytest

from bioqubo.fold_energy import evaluate_hp_energy
from bioqubo.fold_validation import LatticeChain
from bioqubo.hp_model import parse_hp_sequence


def test_evaluator_counts_only_nonbonded_hydrophobic_contacts() -> None:
    sequence = parse_hp_sequence("HPPH")
    chain = LatticeChain.from_coordinates([(0, 0), (1, 0), (1, 1), (0, 1)])

    result = evaluate_hp_energy(sequence, chain)

    assert result.contacts == ((0, 3),)
    assert result.energy == -1


def test_validation_detects_overlaps_and_disconnected_bonds() -> None:
    chain = LatticeChain.from_coordinates([(0, 0), (1, 0), (0, 0), (3, 0)])

    report = chain.validate(expected_length=4)

    assert not report.is_valid
    assert {issue.code for issue in report.issues} == {"overlap", "disconnected_chain"}


def test_energy_evaluator_refuses_invalid_chains() -> None:
    with pytest.raises(ValueError, match="invalid lattice chain"):
        evaluate_hp_energy(parse_hp_sequence("HH"), LatticeChain.from_coordinates([(0, 0), (2, 0)]))
