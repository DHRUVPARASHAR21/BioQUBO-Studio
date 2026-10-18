"""Validated target folds and shape comparison for inverse HP design."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from bioqubo.fold_validation import Coordinate, LatticeChain, manhattan_distance


def parse_target_coordinates(text: str) -> LatticeChain:
    """Parse one integer ``x, y`` coordinate pair per non-empty line."""

    coordinates: list[Coordinate] = []
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.split("#", maxsplit=1)[0].strip()
        if not line:
            continue
        fields = line.replace(",", " ").split()
        if len(fields) != 2:
            raise ValueError(f"Line {line_number} must contain exactly two coordinates: x, y")
        try:
            coordinates.append((int(fields[0]), int(fields[1])))
        except ValueError as error:
            raise ValueError(f"Line {line_number} coordinates must be integers") from error
    if not coordinates:
        raise ValueError("Provide at least one target-fold coordinate")
    return LatticeChain.from_coordinates(coordinates)


def _canonical_coordinates(chain: LatticeChain) -> tuple[Coordinate, ...]:
    """Canonicalize translations, rotations, and reflections while preserving residue order."""

    coordinates = chain.coordinates
    transforms = (
        lambda x, y: (x, y),
        lambda x, y: (x, -y),
        lambda x, y: (-x, y),
        lambda x, y: (-x, -y),
        lambda x, y: (y, x),
        lambda x, y: (y, -x),
        lambda x, y: (-y, x),
        lambda x, y: (-y, -x),
    )
    variants: list[tuple[Coordinate, ...]] = []
    for transform in transforms:
        transformed = [transform(x, y) for x, y in coordinates]
        minimum_x = min(x for x, _ in transformed)
        minimum_y = min(y for _, y in transformed)
        variants.append(tuple((x - minimum_x, y - minimum_y) for x, y in transformed))
    return min(variants)


@dataclass(frozen=True, slots=True)
class TargetFold:
    """A validated 2D self-avoiding target conformation for sequence design."""

    chain: LatticeChain

    def __post_init__(self) -> None:
        report = self.chain.validate()
        if not report.is_valid:
            detail = "; ".join(issue.message for issue in report.issues)
            raise ValueError(f"Invalid target fold: {detail}")

    @property
    def length(self) -> int:
        return len(self.chain.coordinates)

    @property
    def contacts(self) -> tuple[tuple[int, int], ...]:
        """All non-bonded lattice contacts in the target, independent of sequence."""

        return tuple(
            (first, second)
            for first, second in combinations(range(self.length), 2)
            if second - first > 1
            and manhattan_distance(
                self.chain.coordinates[first], self.chain.coordinates[second]
            )
            == 1
        )

    def matches_shape(self, candidate: LatticeChain) -> bool:
        """Test target recovery up to translation, rotation, and reflection."""

        return candidate.validate(expected_length=self.length).is_valid and (
            _canonical_coordinates(self.chain) == _canonical_coordinates(candidate)
        )
