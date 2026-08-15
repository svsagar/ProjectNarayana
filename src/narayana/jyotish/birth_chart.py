"""Birth-chart conversion from AstronomyResult to Jyotish structures."""

from __future__ import annotations

from dataclasses import dataclass

from src.narayana.astronomy.models import AstronomyResult

from .graha import Graha
from .integration import (
    GrahaBhavaPlacement,
    calculate_graha_bhava_placement,
)


ASTRONOMY_TO_GRAHA: dict[str, Graha] = {
    "Sun": Graha.SURYA,
    "Moon": Graha.CHANDRA,
    "Mars": Graha.MANGALA,
    "Mercury": Graha.BUDHA,
    "Jupiter": Graha.GURU,
    "Venus": Graha.SHUKRA,
    "Saturn": Graha.SHANI,
    "Rahu": Graha.RAHU,
    "Ketu": Graha.KETU,
}


@dataclass(frozen=True)
class JyotishBirthChart:
    """Complete Jyotish chart derived from an AstronomyResult."""

    placements: tuple[GrahaBhavaPlacement, ...]
    ascendant_longitude: float
    bhava_cusps: tuple[float, ...]
    astronomy_result: AstronomyResult

    def get_placement(self, graha: Graha) -> GrahaBhavaPlacement:
        """Return the complete placement for one Graha."""

        if not isinstance(graha, Graha):
            raise TypeError("graha must be a Graha")

        for placement in self.placements:
            if placement.graha is graha:
                return placement

        raise ValueError(f"No placement found for {graha.value}")


def calculate_birth_chart(
    astronomy_result: AstronomyResult,
) -> JyotishBirthChart:
    """Convert a canonical AstronomyResult into a Jyotish birth chart."""

    if not isinstance(astronomy_result, AstronomyResult):
        raise TypeError(
            "astronomy_result must be an AstronomyResult"
        )

    positions = astronomy_result.positions

    position_map = {
        position.body: position
        for position in positions
    }

    missing_bodies = [
        body
        for body in ASTRONOMY_TO_GRAHA
        if body not in position_map
    ]

    if missing_bodies:
        missing = ", ".join(missing_bodies)
        raise ValueError(
            f"AstronomyResult is missing required Graha positions: {missing}"
        )

    cusps = tuple(astronomy_result.houses.cusps)

    placements = tuple(
        calculate_graha_bhava_placement(
            graha,
            position_map[body].longitude,
            cusps,
        )
        for body, graha in ASTRONOMY_TO_GRAHA.items()
    )

    return JyotishBirthChart(
        placements=placements,
        ascendant_longitude=astronomy_result.ascendant.longitude,
        bhava_cusps=cusps,
        astronomy_result=astronomy_result,
    )