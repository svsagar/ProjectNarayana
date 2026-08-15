"""Panchanga calculations for Project Narayana."""

from __future__ import annotations

from datetime import datetime

from .models import CelestialPosition, PanchangaData


NAKSHATRA_COUNT = 27
DEGREES_PER_NAKSHATRA = 360.0 / NAKSHATRA_COUNT

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
    "Dhanishta",
    "Shatabhisha",
    "Purva Bhadrapada",
    "Uttara Bhadrapada",
    "Revati",
)

PADA_COUNT = 4
DEGREES_PER_PADA = DEGREES_PER_NAKSHATRA / PADA_COUNT

TITHI_COUNT = 30

TITHI_NAMES = (
    "Pratipada",
    "Dvitiya",
    "Tritiya",
    "Chaturthi",
    "Panchami",
    "Shashthi",
    "Saptami",
    "Ashtami",
    "Navami",
    "Dashami",
    "Ekadashi",
    "Dwadashi",
    "Trayodashi",
    "Chaturdashi",
    "Purnima",
    "Pratipada",
    "Dvitiya",
    "Tritiya",
    "Chaturthi",
    "Panchami",
    "Shashthi",
    "Saptami",
    "Ashtami",
    "Navami",
    "Dashami",
    "Ekadashi",
    "Dwadashi",
    "Trayodashi",
    "Chaturdashi",
    "Amavasya",
)

YOGA_COUNT = 27
DEGREES_PER_YOGA = 360.0 / YOGA_COUNT

YOGA_NAMES = (
    "Vishkambha",
    "Priti",
    "Ayushman",
    "Saubhagya",
    "Shobhana",
    "Atiganda",
    "Sukarma",
    "Dhriti",
    "Shula",
    "Ganda",
    "Vriddhi",
    "Dhruva",
    "Vyaghata",
    "Harshana",
    "Vajra",
    "Siddhi",
    "Vyatipata",
    "Variyana",
    "Parigha",
    "Shiva",
    "Siddha",
    "Sadhya",
    "Shubha",
    "Shukla",
    "Brahma",
    "Indra",
    "Vaidhriti",
)

DEGREES_PER_KARANA = 6.0
KARANA_COUNT = 60

RECURRING_KARANA_NAMES = (
    "Bava",
    "Balava",
    "Kaulava",
    "Taitila",
    "Garaja",
    "Vanija",
    "Vishti",
)

FIXED_KARANA_NAMES = (
    "Shakuni",
    "Chatushpada",
    "Naga",
    "Kimstughna",
)


def calculate_tithi(
    sun: CelestialPosition,
    moon: CelestialPosition,
) -> int:
    """Calculate the current Tithi from Sun and Moon longitudes."""

    elongation = (moon.longitude - sun.longitude) % 360.0
    return int(elongation // 12.0) + 1


def get_tithi_name(tithi: int) -> str:
    """Return the canonical name for a Tithi number, 1 through 30."""

    if not 1 <= tithi <= TITHI_COUNT:
        raise ValueError(
            f"Tithi must be between 1 and {TITHI_COUNT}"
        )

    return TITHI_NAMES[tithi - 1]


def get_tithi_paksha(tithi: int) -> str:
    """Return the Paksha for a Tithi number."""

    if not 1 <= tithi <= TITHI_COUNT:
        raise ValueError(
            f"Tithi must be between 1 and {TITHI_COUNT}"
        )

    return "Shukla" if tithi <= 15 else "Krishna"


def calculate_nakshatra(moon: CelestialPosition) -> int:
    """Calculate the Moon's Nakshatra number, 1 through 27."""

    longitude = moon.longitude % 360.0
    return int(longitude // DEGREES_PER_NAKSHATRA) + 1


def get_nakshatra_name(nakshatra: int) -> str:
    """Return the canonical name for a Nakshatra number, 1 through 27."""

    if not 1 <= nakshatra <= NAKSHATRA_COUNT:
        raise ValueError(
            f"Nakshatra must be between 1 and {NAKSHATRA_COUNT}"
        )

    return NAKSHATRA_NAMES[nakshatra - 1]


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


def get_yoga_name(yoga: int) -> str:
    """Return the canonical name for a Yoga number, 1 through 27."""

    if not 1 <= yoga <= YOGA_COUNT:
        raise ValueError(
            f"Yoga must be between 1 and {YOGA_COUNT}"
        )

    return YOGA_NAMES[yoga - 1]


def calculate_karana(
    sun: CelestialPosition,
    moon: CelestialPosition,
) -> int:
    """Calculate the six-degree Karana segment, 1 through 60."""

    elongation = (moon.longitude - sun.longitude) % 360.0
    return int(elongation // DEGREES_PER_KARANA) + 1


def get_karana_name(karana: int) -> str:
    """Return the traditional name for a Karana position, 1 through 60.

    The first seven positions follow the traditional fixed opening
    sequence. Positions 8 through 57 repeat the seven movable Karanas.
    Positions 58 through 60 are the final fixed Karanas.
    """

    if not 1 <= karana <= KARANA_COUNT:
        raise ValueError(
            f"Karana must be between 1 and {KARANA_COUNT}"
        )

    if karana == 1:
        return "Kimstughna"

    if 2 <= karana <= 57:
        return RECURRING_KARANA_NAMES[(karana - 2) % 7]

    return FIXED_KARANA_NAMES[karana - 58]


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
        tithi_name=get_tithi_name(tithi),
        tithi_paksha=get_tithi_paksha(tithi),
    )