"""Nakshatra classification for the Project Narayana Jyotish layer."""

from __future__ import annotations


NAKSHATRA_NAMES = (
    "Ashwini",
    "Bharani",
    "Krittika",
    "Rohini",
    "Mrigashira",
    "Ardra",
    "Punarvasu",
    "Pushya",
    "Ashlesha",
    "Magha",
    "Purva Phalguni",
    "Uttara Phalguni",
    "Hasta",
    "Chitra",
    "Swati",
    "Vishakha",
    "Anuradha",
    "Jyeshtha",
    "Mula",
    "Purva Ashadha",
    "Uttara Ashadha",
    "Shravana",
    "Dhanishtha",
    "Shatabhisha",
    "Purva Bhadrapada",
    "Uttara Bhadrapada",
    "Revati",
)

NAKSHATRA_COUNT = 27
NAKSHATRA_DEGREES = 360.0 / NAKSHATRA_COUNT
PADA_COUNT = 4
PADA_DEGREES = NAKSHATRA_DEGREES / PADA_COUNT
FULL_CIRCLE = 360.0


def normalize_longitude(longitude: float) -> float:
    """Normalize longitude into the canonical [0, 360) interval."""

    if not isinstance(longitude, (int, float)) or isinstance(longitude, bool):
        raise TypeError("longitude must be a number")

    return float(longitude) % FULL_CIRCLE


def get_nakshatra_number(longitude: float) -> int:
    """Return the 1-based Nakshatra number for a celestial longitude."""

    normalized = normalize_longitude(longitude)

    # Use a tiny tolerance at exact mathematical boundaries so that
    # decimal representations immediately below a boundary do not
    # unexpectedly classify into the preceding Nakshatra.
    boundary = 1e-9

    index = int((normalized + boundary) / NAKSHATRA_DEGREES)

    if index >= NAKSHATRA_COUNT:
        index = NAKSHATRA_COUNT - 1

    return index + 1


def get_nakshatra_name(nakshatra_number: int) -> str:
    """Return the canonical name for a 1-based Nakshatra number."""

    if (
        not isinstance(nakshatra_number, int)
        or isinstance(nakshatra_number, bool)
        or not 1 <= nakshatra_number <= NAKSHATRA_COUNT
    ):
        raise ValueError(
            "nakshatra_number must be an integer between 1 and 27"
        )

    return NAKSHATRA_NAMES[nakshatra_number - 1]


def get_nakshatra_pada(longitude: float) -> int:
    """Return the 1-based Pada number within the Nakshatra."""

    normalized = normalize_longitude(longitude)

    boundary = 1e-9
    position = normalized % NAKSHATRA_DEGREES

    pada = int((position + boundary) / PADA_DEGREES) + 1

    if pada > PADA_COUNT:
        pada = PADA_COUNT

    return pada