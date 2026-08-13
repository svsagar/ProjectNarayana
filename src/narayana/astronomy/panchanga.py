"""Panchanga calculations for Project Narayana."""

from __future__ import annotations

from datetime import datetime

from .models import CelestialPosition, PanchangaData


NAKSHATRA_COUNT = 27
DEGREES_PER_NAKSHATRA = 360.0 / NAKSHATRA_COUNT

PADA_COUNT = 4
DEGREES_PER_PADA = DEGREES_PER_NAKSHATRA / PADA_COUNT

YOGA_COUNT = 27
DEGREES_PER_YOGA = 360.0 / YOGA_COUNT

DEGREES_PER_KARANA = 6.0


def calculate_tithi(
    sun: CelestialPosition,
    moon: CelestialPosition,
) -> int:
    """Calculate the current Tithi from Sun and Moon longitudes."""

    elongation = (moon.longitude - sun.longitude) % 360.0
    return int(elongation // 12.0) + 1


def calculate_nakshatra(moon: CelestialPosition) -> int:
    """Calculate the Moon's Nakshatra number, 1 through 27."""

    longitude = moon.longitude % 360.0
    return int(longitude // DEGREES_PER_NAKSHATRA) + 1


def calculate_nakshatra_pada(moon: CelestialPosition) -> int:
    """Calculate the Moon's Nakshatra Pada number, 1 through 4."""

    longitude = moon.longitude % 360.0

    position_within_nakshatra = (
        longitude % DEGREES_PER_NAKSHATRA
    )

    return int(
        position_within_nakshatra // DEGREES_PER_PADA
    ) + 1


def calculate_yoga(
    sun: CelestialPosition,
    moon: CelestialPosition,
) -> int:
    """Calculate the Yoga number from Sun and Moon longitudes."""

    combined_longitude = (
        sun.longitude + moon.longitude
    ) % 360.0

    return int(combined_longitude // DEGREES_PER_YOGA) + 1


def calculate_karana(
    sun: CelestialPosition,
    moon: CelestialPosition,
) -> int:
    """Calculate the six-degree Karana segment."""

    elongation = (moon.longitude - sun.longitude) % 360.0
    return int(elongation // DEGREES_PER_KARANA) + 1


def calculate_vara(value: datetime) -> int:
    """Calculate Vara as the weekday number.

    Monday = 1 through Sunday = 7.
    """

    return value.isoweekday()


def calculate_panchanga(
    sun: CelestialPosition,
    moon: CelestialPosition,
    local_datetime: datetime | None = None,
) -> PanchangaData:
    """Calculate the supported Panchanga elements."""

    tithi = calculate_tithi(sun, moon)
    nakshatra = calculate_nakshatra(moon)
    nakshatra_pada = calculate_nakshatra_pada(moon)
    yoga = calculate_yoga(sun, moon)
    karana = calculate_karana(sun, moon)

    vara = None

    if local_datetime is not None:
        vara = calculate_vara(local_datetime)

    return PanchangaData(
        tithi=tithi,
        nakshatra=nakshatra,
        nakshatra_pada=nakshatra_pada,
        yoga=yoga,
        karana=karana,
        vara=vara,
    )