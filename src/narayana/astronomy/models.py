"""Canonical data models for Project Narayana Astronomy Engine."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Optional


def validate_birth_input(
    birth_date: date,
    birth_time: time,
    timezone: str,
    latitude: float,
    longitude: float,
) -> None:
    """Validate birth input fields with clear domain boundaries."""

    if not isinstance(birth_date, date) or isinstance(birth_date, bool):
        raise TypeError("birth_date must be a date instance")

    if not isinstance(birth_time, time) or isinstance(birth_time, bool):
        raise TypeError("birth_time must be a time instance")

    if not isinstance(timezone, str) or not timezone.strip():
        raise ValueError("timezone must be a non-empty string")

    if not isinstance(latitude, (int, float)) or isinstance(latitude, bool):
        raise TypeError("latitude must be a number")

    if not (-90.0 <= latitude <= 90.0):
        raise ValueError("latitude must be between -90 and 90 degrees")

    if not isinstance(longitude, (int, float)) or isinstance(longitude, bool):
        raise TypeError("longitude must be a number")

    if not (-180.0 <= longitude <= 180.0):
        raise ValueError("longitude must be between -180 and 180 degrees")


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

    def __post_init__(self) -> None:
        validate_birth_input(
            self.birth_date,
            self.birth_time,
            self.timezone,
            self.latitude,
            self.longitude,
        )


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
    tithi_name: Optional[str] = None
    tithi_paksha: Optional[str] = None


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