"""Swiss Ephemeris backend for the Narayana Astronomy Engine."""

from __future__ import annotations

from dataclasses import dataclass

import swisseph as swe


@dataclass(frozen=True)
class EphemerisPosition:
    """Canonical position returned by Swiss Ephemeris."""

    body: str
    longitude: float
    latitude: float
    distance: float
    speed_longitude: float


class SwissEphemerisBackend:
    """Astronomical backend boundary around Swiss Ephemeris."""

    _BODY_MAP = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mars": swe.MARS,
        "Mercury": swe.MERCURY,
        "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS,
        "Saturn": swe.SATURN,
        "Mean Node": swe.MEAN_NODE,
        "True Node": swe.TRUE_NODE,
    }

    _AYANAMSA_MAP = {
        "lahiri": swe.SIDM_LAHIRI,
    }

    def __init__(self) -> None:
        self.version = swe.version

    def calculate_position(
        self,
        julian_day_ut: float,
        body: str,
        *,
        zodiac: str = "tropical",
        ayanamsa: str | None = None,
    ) -> EphemerisPosition:
        """Calculate one celestial body's position for a Julian Day.

        Tropical calculations do not require an ayanamsa.
        Sidereal calculations require an explicit ayanamsa.
        """

        if body not in self._BODY_MAP:
            raise ValueError(f"Unsupported celestial body: {body}")

        if zodiac not in {"tropical", "sidereal"}:
            raise ValueError(f"Unsupported zodiac: {zodiac}")

        if zodiac == "sidereal":
            if ayanamsa is None:
                raise ValueError(
                    "ayanamsa must be specified for sidereal calculations"
                )

            if ayanamsa not in self._AYANAMSA_MAP:
                raise ValueError(f"Unsupported ayanamsa: {ayanamsa}")

            swe.set_sid_mode(self._AYANAMSA_MAP[ayanamsa])
            flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL
        else:
            flags = swe.FLG_SWIEPH | swe.FLG_SPEED

        result, _flags = swe.calc_ut(
            julian_day_ut,
            self._BODY_MAP[body],
            flags,
        )

        return EphemerisPosition(
            body=body,
            longitude=result[0],
            latitude=result[1],
            distance=result[2],
            speed_longitude=result[3],
        )

    def calculate_ascendant(
        self,
        julian_day_ut: float,
        latitude: float,
        longitude: float,
        *,
        zodiac: str = "tropical",
        ayanamsa: str | None = None,
    ) -> float:
        """Calculate the Ascendant longitude for a Julian Day."""

        if zodiac not in {"tropical", "sidereal"}:
            raise ValueError(f"Unsupported zodiac: {zodiac}")

        if zodiac == "sidereal":
            if ayanamsa is None:
                raise ValueError(
                    "ayanamsa must be specified for sidereal calculations"
                )

            if ayanamsa not in self._AYANAMSA_MAP:
                raise ValueError(f"Unsupported ayanamsa: {ayanamsa}")

            swe.set_sid_mode(self._AYANAMSA_MAP[ayanamsa])
            flags = swe.FLG_SIDEREAL
        else:
            flags = 0

        houses = swe.houses_ex(
            julian_day_ut,
            latitude,
            longitude,
            b"P",
            flags,
        )

        ascendant = houses[1][0]

        return ascendant % 360.0

    def calculate_houses(
        self,
        julian_day_ut: float,
        latitude: float,
        longitude: float,
        *,
        zodiac: str = "tropical",
        ayanamsa: str | None = None,
    ) -> tuple[float, ...]:
        """Calculate the 12 house cusp longitudes for a Julian Day."""

        if zodiac not in {"tropical", "sidereal"}:
            raise ValueError(f"Unsupported zodiac: {zodiac}")

        if zodiac == "sidereal":
            if ayanamsa is None:
                raise ValueError(
                    "ayanamsa must be specified for sidereal calculations"
                )

            if ayanamsa not in self._AYANAMSA_MAP:
                raise ValueError(f"Unsupported ayanamsa: {ayanamsa}")

            swe.set_sid_mode(self._AYANAMSA_MAP[ayanamsa])
            flags = swe.FLG_SIDEREAL
        else:
            flags = 0

        houses = swe.houses_ex(
            julian_day_ut,
            latitude,
            longitude,
            b"P",
            flags,
        )

        cusps = houses[0]

        return tuple(cusp % 360.0 for cusp in cusps)