from __future__ import annotations

import dimod

from bioqubo.io.structure import parse_structure_text
from bioqubo.residue_network import build_residue_network
from bioqubo.residue_selection_bqm import (
    build_residue_selection_bqm,
    evaluate_selection,
    solve_residue_selection,
)

PDB_TEXT = """ATOM      1  CA  GLY A   1       0.000   0.000   0.000  1.00 20.00           C
ATOM      2  CA  ALA A   3       3.000   0.000   0.000  1.00 20.00           C
ATOM      3  CA  SER A   5       6.000   0.000   0.000  1.00 20.00           C
END
"""


def _network():
    return build_residue_network(parse_structure_text(PDB_TEXT, "network.pdb"), cutoff_angstrom=4.0)


def test_contact_network_and_exact_selection() -> None:
    network = _network()
    encoding = build_residue_selection_bqm(network, selection_count=1)
    record = next(iter(dimod.ExactSolver().sample(encoding.bqm).data(fields=["sample"])))
    selected = encoding.decode(dict(record.sample))

    assert network.edges == ((0, 1), (1, 2))
    assert selected == (1,)
    assert evaluate_selection(network, selected) == 2


def test_local_selection_solver_independently_obeys_count() -> None:
    result = solve_residue_selection(build_residue_selection_bqm(_network(), 2), reads=20, seed=7)

    assert result is not None
    assert len(result.selected_indices) == 2
    assert result.objective_score == evaluate_selection(_network(), result.selected_indices)
