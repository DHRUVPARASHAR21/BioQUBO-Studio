"""Dependency-free SVG rendering of a validated lattice fold."""

from __future__ import annotations

from html import escape

from bioqubo.fold_energy import ContactEvaluation
from bioqubo.fold_validation import LatticeChain
from bioqubo.hp_model import HPSequence


def fold_svg(sequence: HPSequence, chain: LatticeChain, evaluation: ContactEvaluation) -> str:
    """Return a small SVG showing the chain and independently evaluated contacts."""

    report = chain.validate(expected_length=len(sequence))
    if not report.is_valid:
        raise ValueError("only validated folds can be visualized")
    spacing, margin = 56, 42
    xs = [point[0] for point in chain.coordinates]
    ys = [point[1] for point in chain.coordinates]
    min_x, min_y = min(xs), min(ys)
    width = (max(xs) - min_x) * spacing + 2 * margin
    height = (max(ys) - min_y) * spacing + 2 * margin

    def point(index: int) -> tuple[int, int]:
        x, y = chain.coordinates[index]
        return margin + (x - min_x) * spacing, margin + (max(ys) - y) * spacing

    bonds = "".join(
        (
            f'<line x1="{point(index)[0]}" y1="{point(index)[1]}" '
            f'x2="{point(index + 1)[0]}" y2="{point(index + 1)[1]}" class="bond"/>'
        )
        for index in range(len(sequence) - 1)
    )
    contacts = "".join(
        (
            f'<line x1="{point(first)[0]}" y1="{point(first)[1]}" '
            f'x2="{point(second)[0]}" y2="{point(second)[1]}" class="contact"/>'
        )
        for first, second in evaluation.contacts
    )
    residues = "".join(
        f'<circle cx="{point(index)[0]}" cy="{point(index)[1]}" r="15" class="{residue}"/>'
        f'<text x="{point(index)[0]}" y="{point(index)[1] + 4}" class="label">{index}</text>'
        for index, residue in enumerate(sequence.residues)
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'role="img" aria-label="{escape(sequence.residues)} HP lattice fold">'
        "<style>.bond{stroke:#475569;stroke-width:5;stroke-linecap:round}"
        ".contact{stroke:#ea580c;stroke-width:3;stroke-dasharray:6 4}.H{fill:#ef4444}"
        ".P{fill:#38bdf8}.label{font:12px sans-serif;text-anchor:middle;fill:#0f172a}</style>"
        f"{bonds}{contacts}{residues}</svg>"
    )
