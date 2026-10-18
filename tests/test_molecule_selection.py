from __future__ import annotations

from bioqubo.chemistry import parse_smiles_lines
from bioqubo.molecule_selection_bqm import build_molecule_selection_bqm, solve_molecule_selection


def test_fixed_size_local_diverse_shortlist() -> None:
    molecules = parse_smiles_lines("CCO ethanol\nc1ccccc1 benzene\nCCCC butane\n")
    encoding = build_molecule_selection_bqm(molecules, 2)
    result = solve_molecule_selection(encoding, reads=20, seed=7)
    assert result is not None
    assert len(result) == 2
    assert set(result).issubset(set(molecules))
