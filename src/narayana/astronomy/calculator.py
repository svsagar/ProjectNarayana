"""Canonical astronomy calculation orchestration for Project Narayana."""

from __future__ import annotations

from datetime import datetime

from .ephemeris import SwissEphemerisBackend
from .julian import utc_to_julian_day
from .models import AstronomyResult, BirthInput, CalculationConfig, CelestialPosition
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

    julian_day_ut = utc_to_julian_day(resolved_time.utc_datetime)

    backend = SwissEphemerisBackend()

    positions = []

    for body in bodies:
        ephemeris_body = body

        if body == "Rahu":
            ephemeris_body = "Mean Node"

        position = backend.calculate_position(
            julian_day_ut,
            ephemeris_body,
            zodiac=calculation_config.zodiac,
            ayanamsa=calculation_config.ayanamsa,
        )

        positions.append(
            CelestialPosition(
                body=body,
                longitude=position.longitude,
                latitude=position.latitude,
                distance=position.distance,
                speed_longitude=position.speed_longitude,
            )
        )

    return AstronomyResult(
        birth_input=birth_input,
        calculation_config=calculation_config,
        julian_day_ut=julian_day_ut,
        positions=tuple(positions),
    )
