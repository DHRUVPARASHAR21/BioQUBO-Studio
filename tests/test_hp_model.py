from __future__ import annotations

import pytest

from bioqubo.hp_model import HPSequenceError, parse_hp_sequence


def test_parse_hp_sequence_accepts_fasta_like_text_and_whitespace() -> None:
    sequence = parse_hp_sequence(">short benchmark\n h p\tP\nH \n")

    assert sequence.residues == "HPPH"
    assert sequence.is_hydrophobic(0)
    assert not sequence.is_hydrophobic(1)


def test_parse_hp_sequence_rejects_non_hp_symbols() -> None:
    with pytest.raises(HPSequenceError, match="only H and P"):
        parse_hp_sequence("HAP")
