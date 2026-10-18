"""Local SMILES parsing and lightweight descriptor calculation with RDKit."""

from __future__ import annotations

from dataclasses import dataclass

from rdkit import Chem
from rdkit.Chem import Descriptors, Lipinski


@dataclass(frozen=True, slots=True)
class Molecule:
    identifier: str
    smiles: str
    molecular_weight: float
    logp: float
    hbd: int
    hba: int


def parse_smiles_lines(text: str) -> tuple[Molecule, ...]:
    """Parse local whitespace-delimited SMILES and optional identifiers."""
    molecules = []
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        fields = line.split()
        mol = Chem.MolFromSmiles(fields[0])
        if mol is None:
            raise ValueError(f"Invalid SMILES on line {number}")
        molecules.append(
            Molecule(
                fields[1] if len(fields) > 1 else f"molecule_{number}",
                fields[0],
                round(Descriptors.MolWt(mol), 3),
                round(Descriptors.MolLogP(mol), 3),
                Lipinski.NumHDonors(mol),
                Lipinski.NumHAcceptors(mol),
            )
        )
    if not molecules:
        raise ValueError("No molecules found")
    return tuple(molecules)


def filter_molecules(
    molecules: tuple[Molecule, ...], max_weight: float = 500, max_logp: float = 5
) -> tuple[Molecule, ...]:
    return tuple(m for m in molecules if m.molecular_weight <= max_weight and m.logp <= max_logp)
