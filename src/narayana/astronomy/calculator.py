"""Canonical astronomy calculation orchestration for Project Narayana."""

from __future__ import annotations

from datetime import datetime

from .ephemeris import SwissEphemerisBackend
from .julian import utc_to_julian_day
from .models import (
    AscendantPosition,
    AstronomyResult,
    BirthInput,
    CalculationConfig,
    CalculationMetadata,
    CelestialPosition,
)
from .time import resolve_local_time


SUPPORTED_BODIES = (
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
    "Mean Node",
)


def calculate(
    birth_input: BirthInput,
    calculation_config: CalculationConfig,
    *,
    bodies: tuple[str, ...] = SUPPORTED_BODIES,
) -> AstronomyResult:
    """Calculate canonical astronomical positions for a birth input."""

    local_datetime = datetime.combine(
        birth_input.birth_date,
        birth_input.birth_time,
    )

    resolved_time = resolve_local_time(
        local_datetime,
        birth_input.timezone,
    )

    julian_day_ut = utc_to_julian_day(
        resolved_time.utc_datetime,
    )

    backend = SwissEphemerisBackend()

    node_body = {
        "mean": "Mean Node",
        "true": "True Node",
    }.get(calculation_config.node)

    if node_body is None:
        raise ValueError(
            f"Unsupported node mode: {calculation_config.node}"
        )

    positions = []
    ascendant_longitude = backend.calculate_ascendant(
        julian_day_ut,
        birth_input.latitude,
        birth_input.longitude,
        zodiac=calculation_config.zodiac,
        ayanamsa=calculation_config.ayanamsa,
    )

    for body in bodies:
        ephemeris_body = body

        if body in {"Rahu", "Ketu"}:
            ephemeris_body = node_body

        position = backend.calculate_position(
            julian_day_ut,
            ephemeris_body,
            zodiac=calculation_config.zodiac,
            ayanamsa=calculation_config.ayanamsa,
        )

        longitude = position.longitude

        if body == "Ketu":
            longitude = (longitude + 180.0) % 360.0

        positions.append(
            CelestialPosition(
                body=body,
                longitude=longitude,
                latitude=position.latitude,
                distance=position.distance,
                speed_longitude=position.speed_longitude,
            )
        )

    calculation_metadata = CalculationMetadata(
        local_datetime=resolved_time.local_datetime,
        timezone_name=resolved_time.timezone_name,
        utc_datetime=resolved_time.utc_datetime,
        latitude=birth_input.latitude,
        longitude=birth_input.longitude,
        coordinate_source=birth_input.coordinate_source,
        coordinate_precision=birth_input.coordinate_precision,
        julian_day_ut=julian_day_ut,
        ephemeris_implementation=calculation_config.ephemeris,
        ephemeris_version=backend.version,
        ayanamsa=calculation_config.ayanamsa,
        node_mode=calculation_config.node,
    )

    ascendant = AscendantPosition(
        longitude=ascendant_longitude,
    )

    return AstronomyResult(
        birth_input=birth_input,
        calculation_config=calculation_config,
        calculation_metadata=calculation_metadata,
        positions=tuple(positions),
        ascendant=ascendant,
    )