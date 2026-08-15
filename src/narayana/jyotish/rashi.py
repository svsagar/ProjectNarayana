"""Rashi (zodiac sign) classification for the Project Narayana Jyotish layer."""

from __future__ import annotations


RASHI_NAMES = (
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

RASHI_COUNT = 12
DEGREES_PER_RASHI = 30.0
FULL_CIRCLE = 360.0


def normalize_longitude(longitude: float) -> float:
    """Normalize longitude into the canonical [0, 360) interval."""

    if not isinstance(longitude, (int, float)) or isinstance(longitude, bool):
        raise TypeError("longitude must be a number")

    return float(longitude) % FULL_CIRCLE


def get_rashi_number(longitude: float) -> int:
    """Return the 1-based Rashi number for a celestial longitude.

    Each Rashi occupies exactly 30 degrees:

        0°   <= Mesha      < 30°
        30°  <= Vrishabha  < 60°
        ...
        330° <= Meena      < 360°

    Longitudes outside the canonical 0–360 degree interval are normalized.
    """

    normalized = normalize_longitude(longitude)

    return int(normalized // DEGREES_PER_RASHI) + 1


def get_rashi_name(rashi_number: int) -> str:
    """Return the canonical name for a 1-based Rashi number."""

    if (
        not isinstance(rashi_number, int)
        or isinstance(rashi_number, bool)
        or not 1 <= rashi_number <= RASHI_COUNT
    ):
        raise ValueError("rashi_number must be an integer between 1 and 12")

    return RASHI_NAMES[rashi_number - 1]