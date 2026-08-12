"""Core data models for the Narayana Astronomy Engine."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
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
    coordinate_source: Optional[str] = None
    coordinate_precision: Optional[str] = None


@dataclass(frozen=True)
class CalculationConfig:
    """Explicit configuration controlling an astronomy calculation."""

    zodiac: str
    ayanamsa: Optional[str]
    node: Optional[str]
    ephemeris: str = "swiss_ephemeris"


@dataclass(frozen=True)
class CelestialPosition:
    """Canonical position calculated for a celestial body."""

    body: str
    longitude: float
    latitude: float
    distance: float
    speed_longitude: float


@dataclass(frozen=True)
class AscendantPosition:
    """Canonical Ascendant position calculated for a birth input."""

    longitude: float


@dataclass(frozen=True)
class CalculationMetadata:
    """Metadata required to reproduce and audit a calculation."""

    local_datetime: datetime
    timezone_name: str
    utc_datetime: datetime
    latitude: float
    longitude: float
    coordinate_source: Optional[str]
    coordinate_precision: Optional[str]
    julian_day_ut: float
    ephemeris_implementation: str
    ephemeris_version: str
    ayanamsa: Optional[str]
    node_mode: Optional[str]
    time_scale: str = "UT"
    calculation_mode: str = "geocentric"


@dataclass(frozen=True)
class AstronomyResult:
    """Canonical result produced by the Astronomy Engine."""

    birth_input: BirthInput
    calculation_config: CalculationConfig
    calculation_metadata: CalculationMetadata
    positions: tuple[CelestialPosition, ...]
    ascendant: AscendantPosition