"""Canonical data models for Project Narayana Astronomy Engine."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Optional


@dataclass(frozen=True)
class BirthInput:
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
    zodiac: str = "sidereal"
    ayanamsa: str = "lahiri"
    node: str = "mean"
    ephemeris: str = "swiss_ephemeris"
    house_system: str = "placidus"


@dataclass(frozen=True)
class CelestialPosition:
    body: str
    longitude: float
    latitude: float
    distance: float
    speed_longitude: float


@dataclass(frozen=True)
class AscendantPosition:
    longitude: float


@dataclass(frozen=True)
class HouseCusps:
    cusps: tuple[float, ...]


@dataclass(frozen=True)
class PanchangaData:
    tithi: int
    nakshatra: int
    nakshatra_pada: int
    yoga: int
    karana: int
    vara: Optional[int] = None


@dataclass(frozen=True)
class CalculationMetadata:
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
    ayanamsa: str
    node_mode: str


@dataclass(frozen=True)
class AstronomyResult:
    birth_input: BirthInput
    calculation_config: CalculationConfig
    calculation_metadata: CalculationMetadata
    positions: tuple[CelestialPosition, ...]
    ascendant: AscendantPosition
    houses: HouseCusps
    panchanga: Optional[PanchangaData] = None