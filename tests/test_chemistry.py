from __future__ import annotations

import pytest

from bioqubo.chemistry import filter_molecules, parse_smiles_lines


def test_parse_and_filter_local_smiles() -> None:
    molecules = parse_smiles_lines("CCO ethanol\nCC(=O)O acetate\n")
    assert len(molecules) == 2
    assert molecules[0].molecular_weight == pytest.approx(46.069, abs=0.01)
    assert [m.identifier for m in filter_molecules(molecules, max_logp=0)] == ["ethanol"]


def test_invalid_smiles_is_rejected() -> None:
    with pytest.raises(ValueError, match="Invalid"):
        parse_smiles_lines("not-a-smiles bad")
