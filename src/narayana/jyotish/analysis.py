"""Core deterministic Jyotish chart analysis."""

from __future__ import annotations

from dataclasses import dataclass

from .birth_chart import JyotishBirthChart
from .bhava import get_bhava_number
from .dignity import Dignity, get_dignity, get_dignity_score
from .graha import Graha
from .integration import GrahaBhavaPlacement
from .placement import GrahaPlacement
from .rashi import (
    RASHI_NAMES,
    get_rashi_name,
    get_rashi_number,
)


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
class GrahaAnalysis:
    """Consolidated analysis of one Graha placement."""

    placement: GrahaPlacement
    dignity: Dignity
    dignity_score: int


def analyze_graha(
    placement: GrahaPlacement,
) -> GrahaAnalysis:
    """Analyze the dignity and strength of one Graha placement."""

    if not isinstance(placement, GrahaPlacement):
        raise TypeError(
            "placement must be a GrahaPlacement"
        )

    dignity = get_dignity(
        placement.graha,
        placement.rashi_number,
    )

    dignity_score = get_dignity_score(
        placement.graha,
        placement.rashi_number,
    )

    return GrahaAnalysis(
        placement=placement,
        dignity=dignity,
        dignity_score=dignity_score,
    )


@dataclass(frozen=True)
class ChartGrahaAnalysis:
    """Structural analysis of one Graha in a complete birth chart."""

    placement: GrahaBhavaPlacement
    dignity: Dignity
    dignity_score: int


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
class BhavaAnalysis:
    """Structural analysis of one Bhava."""

    bhava_number: int
    rashi_number: int
    rashi_name: str
    lord: Graha
    grahas: tuple[Graha, ...]
    lord_bhava_number: int | None


@dataclass(frozen=True)
class BhavaLordRelationship:
    """Deterministic relationship between a Bhava and its lord."""

    bhava_number: int
    source_bhava: int
    rashi_number: int
    rashi_name: str
    source_rashi_number: int
    source_rashi_name: str
    lord: Graha
    lord_is_present: bool
    lord_bhava_number: int | None
    lord_rashi_number: int | None
    lord_rashi_name: str | None
    lord_dignity: Dignity | None
    lord_dignity_score: int | None
    house_distance: int | None
    is_same_bhava: bool
    relationship_types: tuple[str, ...]


@dataclass(frozen=True)
class ChartAnalysis:
    """Deterministic structural analysis of a Jyotish birth chart."""

    ascendant_rashi_number: int
    ascendant_rashi_name: str
    ascendant_rashi_lord: Graha
    rashi_occupancy: tuple[RashiOccupancy, ...]
    bhava_occupancy: tuple[BhavaOccupancy, ...]
    bhava_analysis: tuple[BhavaAnalysis, ...]
    graha_analysis: tuple[ChartGrahaAnalysis, ...] = ()
    bhava_lord_relationships: tuple[
        BhavaLordRelationship, ...
    ] = ()

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
        """Return occupancy information for one Bhava."""

        if (
            not isinstance(bhava_number, int)
            or isinstance(bhava_number, bool)
            or not 1 <= bhava_number <= 12
        ):
            raise ValueError(
                "bhava_number must be an integer between 1 and 12"
            )

        return self.bhava_occupancy[bhava_number - 1]

    def get_bhava_analysis(
        self,
        bhava_number: int,
    ) -> BhavaAnalysis:
        """Return structural analysis for one Bhava."""

        if (
            not isinstance(bhava_number, int)
            or isinstance(bhava_number, bool)
            or not 1 <= bhava_number <= 12
        ):
            raise ValueError(
                "bhava_number must be an integer between 1 and 12"
            )

        return self.bhava_analysis[bhava_number - 1]

    def get_graha_analysis(
        self,
        graha: Graha,
    ) -> ChartGrahaAnalysis:
        """Return structural analysis for one Graha."""

        if not isinstance(graha, Graha):
            raise TypeError(
                "graha must be a Graha"
            )

        for analysis in self.graha_analysis:
            if analysis.placement.graha is graha:
                return analysis

        raise ValueError(
            f"No analysis found for {graha.value}"
        )

    def get_bhava_lord_relationship(
        self,
        bhava_number: int,
    ) -> BhavaLordRelationship:
        """Return the relationship between a Bhava and its lord."""

        if (
            not isinstance(bhava_number, int)
            or isinstance(bhava_number, bool)
            or not 1 <= bhava_number <= 12
        ):
            raise ValueError(
                "bhava_number must be an integer between 1 and 12"
            )

        return self.bhava_lord_relationships[
            bhava_number - 1
        ]

    def get_rashi_lord(
        self,
        rashi_number: int,
    ) -> Graha:
        """Return the traditional lord of a Rashi."""

        return self.get_rashi_occupancy(rashi_number).lord

    def get_bhava_lord(
        self,
        bhava_number: int,
    ) -> Graha:
        """Return the lord of a Bhava."""

        return self.get_bhava_analysis(bhava_number).lord


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

    return RASHI_LORDS[
        RASHI_NAMES[rashi_number - 1]
    ]


def _analyze_chart_graha(
    placement: GrahaBhavaPlacement,
) -> ChartGrahaAnalysis:
    """Create deterministic structural analysis for one chart Graha."""

    dignity = get_dignity(
        placement.graha,
        placement.rashi_number,
    )

    dignity_score = get_dignity_score(
        placement.graha,
        placement.rashi_number,
    )

    return ChartGrahaAnalysis(
        placement=placement,
        dignity=dignity,
        dignity_score=dignity_score,
    )


def _classify_bhava_relationship(
    house_distance: int,
) -> tuple[str, ...]:
    """Classify a Bhava lord by its relative house distance."""

    relationship_types: list[str] = []

    if house_distance == 1:
        relationship_types.append("same_bhava")

    if house_distance in (1, 4, 7, 10):
        relationship_types.append("kendra")

    if house_distance in (1, 5, 9):
        relationship_types.append("trikona")

    if house_distance in (3, 6, 10, 11):
        relationship_types.append("upachaya")

    if house_distance in (6, 8, 12):
        relationship_types.append("dusthana")

    if not relationship_types:
        relationship_types.append("other")

    return tuple(relationship_types)


def _build_bhava_lord_relationship(
    bhava: BhavaAnalysis,
    graha_bhava_map: dict[Graha, int],
    graha_placement_map: dict[
        Graha,
        GrahaBhavaPlacement,
    ],
) -> BhavaLordRelationship:
    """Build deterministic relationship data for one Bhava."""

    lord_bhava_number = graha_bhava_map.get(
        bhava.lord
    )

    lord_is_present = (
        lord_bhava_number is not None
    )

    if not lord_is_present:
        return BhavaLordRelationship(
            bhava_number=bhava.bhava_number,
            source_bhava=bhava.bhava_number,
            rashi_number=bhava.rashi_number,
            rashi_name=bhava.rashi_name,
            source_rashi_number=bhava.rashi_number,
            source_rashi_name=bhava.rashi_name,
            lord=bhava.lord,
            lord_is_present=False,
            lord_bhava_number=None,
            lord_rashi_number=None,
            lord_rashi_name=None,
            lord_dignity=None,
            lord_dignity_score=None,
            house_distance=None,
            is_same_bhava=False,
            relationship_types=("unplaced",),
        )

    placement = graha_placement_map[
        bhava.lord
    ]

    house_distance = (
        (
            lord_bhava_number
            - bhava.bhava_number
        ) % 12
    ) + 1

    is_same_bhava = (
        lord_bhava_number
        == bhava.bhava_number
    )

    return BhavaLordRelationship(
        bhava_number=bhava.bhava_number,
        source_bhava=bhava.bhava_number,
        rashi_number=bhava.rashi_number,
        rashi_name=bhava.rashi_name,
        source_rashi_number=bhava.rashi_number,
        source_rashi_name=bhava.rashi_name,
        lord=bhava.lord,
        lord_is_present=True,
        lord_bhava_number=lord_bhava_number,
        lord_rashi_number=placement.rashi_number,
        lord_rashi_name=placement.rashi_name,
        lord_dignity=get_dignity(
            placement.graha,
            placement.rashi_number,
        ),
        lord_dignity_score=get_dignity_score(
            placement.graha,
            placement.rashi_number,
        ),
        house_distance=house_distance,
        is_same_bhava=is_same_bhava,
        relationship_types=_classify_bhava_relationship(
            house_distance
        ),
    )


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

    graha_bhava_map: dict[Graha, int] = {}

    graha_placement_map: dict[
        Graha,
        GrahaBhavaPlacement,
    ] = {}

    for placement in chart.placements:
        rashi_groups[
            placement.rashi_number
        ].append(placement.graha)

        bhava_number = get_bhava_number(
            placement.longitude,
            chart.bhava_cusps,
        )

        bhava_groups[
            bhava_number
        ].append(placement.graha)

        graha_bhava_map[
            placement.graha
        ] = bhava_number

        graha_placement_map[
            placement.graha
        ] = GrahaBhavaPlacement(
            graha=placement.graha,
            longitude=placement.longitude,
            rashi_number=placement.rashi_number,
            rashi_name=placement.rashi_name,
            nakshatra_number=placement.nakshatra_number,
            nakshatra_name=placement.nakshatra_name,
            nakshatra_pada=placement.nakshatra_pada,
            bhava_number=bhava_number,
        )

    rashi_occupancy = tuple(
        RashiOccupancy(
            rashi_number=number,
            rashi_name=get_rashi_name(number),
            lord=get_rashi_lord(number),
            grahas=tuple(
                rashi_groups[number]
            ),
        )
        for number in range(1, 13)
    )

    bhava_occupancy = tuple(
        BhavaOccupancy(
            bhava_number=number,
            grahas=tuple(
                bhava_groups[number]
            ),
        )
        for number in range(1, 13)
    )

    bhava_analysis_items: list[
        BhavaAnalysis
    ] = []

    for bhava_number in range(1, 13):
        rashi_number = (
            (
                ascendant_rashi_number
                + bhava_number
                - 2
            ) % 12
        ) + 1

        rashi_name = get_rashi_name(
            rashi_number
        )

        lord = get_rashi_lord(
            rashi_number
        )

        bhava_analysis_items.append(
            BhavaAnalysis(
                bhava_number=bhava_number,
                rashi_number=rashi_number,
                rashi_name=rashi_name,
                lord=lord,
                grahas=tuple(
                    bhava_groups[
                        bhava_number
                    ]
                ),
                lord_bhava_number=graha_bhava_map.get(
                    lord
                ),
            )
        )

    bhava_analysis = tuple(
        bhava_analysis_items
    )

    graha_analysis = tuple(
        _analyze_chart_graha(
            graha_placement_map[
                placement.graha
            ]
        )
        for placement in chart.placements
    )

    bhava_lord_relationships = tuple(
        _build_bhava_lord_relationship(
            bhava,
            graha_bhava_map,
            graha_placement_map,
        )
        for bhava in bhava_analysis
    )

    return ChartAnalysis(
        ascendant_rashi_number=ascendant_rashi_number,
        ascendant_rashi_name=ascendant_rashi_name,
        ascendant_rashi_lord=ascendant_rashi_lord,
        rashi_occupancy=rashi_occupancy,
        bhava_occupancy=bhava_occupancy,
        bhava_analysis=bhava_analysis,
        graha_analysis=graha_analysis,
        bhava_lord_relationships=(
            bhava_lord_relationships
        ),
    )