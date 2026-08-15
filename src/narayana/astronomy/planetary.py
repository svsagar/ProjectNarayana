"""Planetary classification primitives for Project Narayana."""

from __future__ import annotations

from dataclasses import dataclass

from .models import CelestialPosition
from .zodiac import ZodiacPosition, classify_zodiac


@dataclass(frozen=True)
class PlanetaryClassification:
    """Derived astrological classification of a celestial position."""

    body: str
    longitude: float
    zodiac: ZodiacPosition
    nakshatra: int
    nakshatra_pada: int
    retrograde: bool


def get_nakshatra_number(longitude: float) -> int:
    """Return the Nakshatra number (1-27) for a longitude."""

    normalized = float(longitude) % 360.0

    nakshatra_span = 360.0 / 27.0

    return int(normalized // nakshatra_span) + 1


def get_nakshatra_pada(longitude: float) -> int:
    """Return the Nakshatra Pada (1-4) for a longitude."""

    normalized = float(longitude) % 360.0

    pada_span = 360.0 / 108.0

    return int(normalized // pada_span) % 4 + 1


def is_retrograde(position: CelestialPosition) -> bool:
    """Return True when the body's longitudinal motion is retrograde."""

    return position.speed_longitude < 0.0


def classify_planetary_position(
    position: CelestialPosition,
) -> PlanetaryClassification:
    """Classify a celestial position into zodiac, Nakshatra and motion."""

    zodiac = classify_zodiac(position.longitude)

    return PlanetaryClassification(
        body=position.body,
        longitude=position.longitude,
        zodiac=zodiac,
        nakshatra=get_nakshatra_number(position.longitude),
        nakshatra_pada=get_nakshatra_pada(position.longitude),
        retrograde=is_retrograde(position),
    )