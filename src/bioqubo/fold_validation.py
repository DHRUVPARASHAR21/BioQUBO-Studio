"""Independent geometric validation for 2D square-lattice HP folds."""

from __future__ import annotations

from dataclasses import dataclass

from bioqubo.validation import ValidationIssue, ValidationReport

Coordinate = tuple[int, int]


def manhattan_distance(first: Coordinate, second: Coordinate) -> int:
    """Return square-lattice graph distance between two coordinates."""

    return abs(first[0] - second[0]) + abs(first[1] - second[1])


@dataclass(frozen=True, slots=True)
class LatticeChain:
    """An ordered coordinate assignment for a chain on a square lattice."""

    coordinates: tuple[Coordinate, ...]

    @classmethod
    def from_coordinates(
        cls, coordinates: list[Coordinate] | tuple[Coordinate, ...]
    ) -> LatticeChain:
        return cls(tuple((int(x), int(y)) for x, y in coordinates))

    def validate(self, expected_length: int | None = None) -> ValidationReport:
        """Check length, self-avoidance, and nearest-neighbour chain bonds."""

        issues: list[ValidationIssue] = []
        if expected_length is not None and len(self.coordinates) != expected_length:
            issues.append(
                ValidationIssue(
                    code="length_mismatch",
                    message=(
                        f"Expected {expected_length} coordinates, received {len(self.coordinates)}."
                    ),
                )
            )
        seen: dict[Coordinate, int] = {}
        for index, coordinate in enumerate(self.coordinates):
            previous = seen.get(coordinate)
            if previous is not None:
                issues.append(
                    ValidationIssue(
                        code="overlap",
                        message=f"Residues {previous} and {index} occupy {coordinate}.",
                    )
                )
            else:
                seen[coordinate] = index
        for index, (first, second) in enumerate(zip(self.coordinates, self.coordinates[1:])):
            if manhattan_distance(first, second) != 1:
                issues.append(
                    ValidationIssue(
                        code="disconnected_chain",
                        message=f"Residues {index} and {index + 1} are not lattice neighbours.",
                    )
                )
        return ValidationReport(tuple(issues))
