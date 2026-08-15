"""Zodiac / Rāśi classification primitives for Project Narayana."""

from __future__ import annotations

from dataclasses import dataclass


ZODIAC_SIGNS = (
    "Mesha",
    "Vrishabha",
    "Mithuna",
    "Karka",
    "Simha",
    "Kanya",
    "Tula",
    "Vrishchika",
    "Dhanu",
    "Makara",
    "Kumbha",
    "Meena",
)


@dataclass(frozen=True)
class ZodiacPosition:
    """Canonical zodiac classification of a celestial longitude."""

    sign_number: int
    sign_name: str
    degrees_in_sign: float


def normalize_longitude(longitude: float) -> float:
    """Normalize a celestial longitude to the range [0, 360)."""

    if not isinstance(longitude, (int, float)) or isinstance(longitude, bool):
        raise TypeError("longitude must be a number")

    return float(longitude) % 360.0


def get_zodiac_sign_number(longitude: float) -> int:
    """Return the zodiac sign number (1-12) for a longitude."""

    normalized = normalize_longitude(longitude)

    return int(normalized // 30.0) + 1


def get_zodiac_sign_name(sign_number: int) -> str:
    """Return the Sanskrit Rāśi name for a sign number (1-12)."""

    if not isinstance(sign_number, int) or isinstance(sign_number, bool):
        raise TypeError("sign_number must be an integer")

    if not 1 <= sign_number <= 12:
        raise ValueError("sign_number must be between 1 and 12")

    return ZODIAC_SIGNS[sign_number - 1]


def get_degrees_in_sign(longitude: float) -> float:
    """Return degrees within the current zodiac sign."""

    normalized = normalize_longitude(longitude)

    return normalized % 30.0


def classify_zodiac(longitude: float) -> ZodiacPosition:
    """Classify a celestial longitude into its Rāśi and degree position."""

    sign_number = get_zodiac_sign_number(longitude)

    return ZodiacPosition(
        sign_number=sign_number,
        sign_name=get_zodiac_sign_name(sign_number),
        degrees_in_sign=get_degrees_in_sign(longitude),
    )