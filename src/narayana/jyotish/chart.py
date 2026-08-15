"""Complete Graha chart structure for Project Narayana Jyotish."""

from __future__ import annotations

from dataclasses import dataclass

from .graha import GRAHAS, Graha
from .placement import GrahaPlacement, calculate_graha_placement


@dataclass(frozen=True)
class GrahaChart:
    """Canonical collection of the nine Graha placements."""

    placements: tuple[GrahaPlacement, ...]

    def get_placement(self, graha: Graha) -> GrahaPlacement:
        """Return the placement for one Graha."""

        if not isinstance(graha, Graha):
            raise TypeError("graha must be a Graha")

        for placement in self.placements:
            if placement.graha is graha:
                return placement

        raise ValueError(f"No placement found for {graha.value}")


def calculate_graha_chart(
    longitudes: dict[Graha, float],
) -> GrahaChart:
    """Calculate the complete nine-Graha chart from longitudes."""

    if not isinstance(longitudes, dict):
        raise TypeError("longitudes must be a dictionary")

    expected_grahas = set(GRAHAS)
    supplied_grahas = set(longitudes)

    missing = expected_grahas - supplied_grahas
    unexpected = supplied_grahas - expected_grahas

    if missing:
        missing_names = ", ".join(
            graha.value for graha in GRAHAS if graha in missing
        )
        raise ValueError(
            f"Missing Graha longitudes: {missing_names}"
        )

    if unexpected:
        unexpected_names = ", ".join(
            str(graha) for graha in unexpected
        )
        raise ValueError(
            f"Unexpected Graha longitudes: {unexpected_names}"
        )

    placements = tuple(
        calculate_graha_placement(
            graha,
            longitudes[graha],
        )
        for graha in GRAHAS
    )

    return GrahaChart(placements=placements)