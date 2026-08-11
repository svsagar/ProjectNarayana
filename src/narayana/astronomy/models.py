"""Core data models for the Narayana Astronomy Engine."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time
from typing import Optional


@dataclass(frozen=True)
class BirthInput:
    """Validated civil birth information supplied to the astronomy engine."""

    birth_date: date
    birth_time: time
    timezone: str
    latitude: float
    longitude: float
    place_name: Optional[str] = None


@dataclass(frozen=True)
class CalculationConfig:
    """Configuration controlling an astronomy calculation."""

    zodiac: str = "sidereal"
    ayanamsa: str = "lahiri"
    node: str = "mean"
    ephemeris: str = "swiss_ephemeris"


@dataclass(frozen=True)
class CelestialPosition:
    """Canonical position data for a calculated celestial body."""

    body: str
    longitude: float
    latitude: float
    distance: float
    speed_longitude: float


@dataclass(frozen=True)
class AstronomyResult:
    """Canonical result produced by the Astronomy Engine."""

    birth_input: BirthInput
    calculation_config: CalculationConfig
    julian_day_ut: float
    positions: tuple[CelestialPosition, ...]
