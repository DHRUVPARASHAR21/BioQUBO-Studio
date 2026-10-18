"""Independent HP contact and energy calculations.

This module deliberately has no dependency on the BQM encoder or a sampler.
"""

from __future__ import annotations

from dataclasses import dataclass

from bioqubo.fold_validation import LatticeChain, manhattan_distance
from bioqubo.hp_model import HPSequence


@dataclass(frozen=True, slots=True)
class ContactEvaluation:
    """Validated H-H contacts and their HP-model energy."""

    contacts: tuple[tuple[int, int], ...]

    @property
    def energy(self) -> int:
        return -len(self.contacts)


def evaluate_hp_energy(sequence: HPSequence, chain: LatticeChain) -> ContactEvaluation:
    """Evaluate ``E_HP = -N_HH`` for a valid square-lattice chain.

    Consecutive residues are covalently bonded and are never counted as contacts.
    """

    report = chain.validate(expected_length=len(sequence))
    if not report.is_valid:
        detail = "; ".join(issue.message for issue in report.issues)
        raise ValueError(f"Cannot evaluate an invalid lattice chain: {detail}")
    contacts: list[tuple[int, int]] = []
    for first in range(len(sequence)):
        if not sequence.is_hydrophobic(first):
            continue
        for second in range(first + 2, len(sequence)):
            if sequence.is_hydrophobic(second) and manhattan_distance(
                chain.coordinates[first], chain.coordinates[second]
            ) == 1:
                contacts.append((first, second))
    return ContactEvaluation(tuple(contacts))
