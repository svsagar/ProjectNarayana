"""Core deterministic Jyotish chart analysis."""

from __future__ import annotations

from dataclasses import dataclass

from .birth_chart import JyotishBirthChart
from .graha import Graha
from .rashi import RASHI_NAMES, get_rashi_name, get_rashi_number


RASHI_LORDS: dict[str, Graha] = {
    "Mesha": Graha.MANGALA,
    "Vrishabha": Graha.SHUKRA,
    "Mithuna": Graha.BUDHA,
    "Karka": Graha.CHANDRA,
    "Simha": Graha.SURYA,
    "Kanya": Graha.BUDHA,
    "Tula": Graha.SHUKRA,
    "Vrishchika": Graha.MANGALA,
    "Dhanu": Graha.GURU,
    "Makara": Graha.SHANI,
    "Kumbha": Graha.SHANI,
    "Meena": Graha.GURU,
}


@dataclass(frozen=True)
class RashiOccupancy:
    """Grahas occupying each Rashi."""

    rashi_number: int
    rashi_name: str
    lord: Graha
    grahas: tuple[Graha, ...]


@dataclass(frozen=True)
class BhavaOccupancy:
    """Grahas occupying one Bhava."""

    bhava_number: int
    grahas: tuple[Graha, ...]


@dataclass(frozen=True)
class ChartAnalysis:
    """Deterministic structural analysis of a Jyotish birth chart."""

    ascendant_rashi_number: int
    ascendant_rashi_name: str
    ascendant_rashi_lord: Graha
    rashi_occupancy: tuple[RashiOccupancy, ...]
    bhava_occupancy: tuple[BhavaOccupancy, ...]

    def get_rashi_occupancy(
        self,
        rashi_number: int,
    ) -> RashiOccupancy:
        """Return occupancy information for a Rashi."""

        if (
            not isinstance(rashi_number, int)
            or isinstance(rashi_number, bool)
            or not 1 <= rashi_number <= 12
        ):
            raise ValueError(
                "rashi_number must be an integer between 1 and 12"
            )

        return self.rashi_occupancy[rashi_number - 1]

    def get_bhava_occupancy(
        self,
        bhava_number: int,
    ) -> BhavaOccupancy:
        """Return occupancy information for a Bhava."""

        if (
            not isinstance(bhava_number, int)
            or isinstance(bhava_number, bool)
            or not 1 <= bhava_number <= 12
        ):
            raise ValueError(
                "bhava_number must be an integer between 1 and 12"
            )

        return self.bhava_occupancy[bhava_number - 1]

    def get_rashi_lord(
        self,
        rashi_number: int,
    ) -> Graha:
        """Return the traditional lord of a Rashi."""

        return self.get_rashi_occupancy(rashi_number).lord


def get_rashi_lord(rashi_number: int) -> Graha:
    """Return the traditional lord of a 1-based Rashi."""

    if (
        not isinstance(rashi_number, int)
        or isinstance(rashi_number, bool)
        or not 1 <= rashi_number <= 12
    ):
        raise ValueError(
            "rashi_number must be an integer between 1 and 12"
        )

    return RASHI_LORDS[RASHI_NAMES[rashi_number - 1]]


def calculate_chart_analysis(
    chart: JyotishBirthChart,
) -> ChartAnalysis:
    """Calculate deterministic structural analysis for a Jyotish chart."""

    if not isinstance(chart, JyotishBirthChart):
        raise TypeError(
            "chart must be a JyotishBirthChart"
        )

    ascendant_rashi_number = get_rashi_number(
        chart.ascendant_longitude
    )
    ascendant_rashi_name = get_rashi_name(
        ascendant_rashi_number
    )
    ascendant_rashi_lord = get_rashi_lord(
        ascendant_rashi_number
    )

    rashi_groups: dict[int, list[Graha]] = {
        number: []
        for number in range(1, 13)
    }

    bhava_groups: dict[int, list[Graha]] = {
        number: []
        for number in range(1, 13)
    }

    for placement in chart.placements:
        rashi_groups[placement.rashi_number].append(
            placement.graha
        )
        bhava_groups[placement.bhava_number].append(
            placement.graha
        )

    rashi_occupancy = tuple(
        RashiOccupancy(
            rashi_number=number,
            rashi_name=get_rashi_name(number),
            lord=get_rashi_lord(number),
            grahas=tuple(rashi_groups[number]),
        )
        for number in range(1, 13)
    )

    bhava_occupancy = tuple(
        BhavaOccupancy(
            bhava_number=number,
            grahas=tuple(bhava_groups[number]),
        )
        for number in range(1, 13)
    )

    return ChartAnalysis(
        ascendant_rashi_number=ascendant_rashi_number,
        ascendant_rashi_name=ascendant_rashi_name,
        ascendant_rashi_lord=ascendant_rashi_lord,
        rashi_occupancy=rashi_occupancy,
        bhava_occupancy=bhava_occupancy,
    )