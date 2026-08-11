"""Swiss Ephemeris backend for the Narayana Astronomy Engine."""

from __future__ import annotations

from dataclasses import dataclass

import swisseph as swe


@dataclass(frozen=True)
class EphemerisPosition:
    """Raw canonical position returned by Swiss Ephemeris."""

    body: str
    longitude: float
    latitude: float
    distance: float
    speed_longitude: float


class SwissEphemerisBackend:
    """Astronomical backend boundary around Swiss Ephemeris."""

    def __init__(self) -> None:
        self.version = swe.version

    def calculate_position(
        self,
        julian_day_ut: float,
        body: str,
    ) -> EphemerisPosition:
        """Calculate one celestial body's position for a Julian Day."""

        body_map = {
            "Sun": swe.SUN,
            "Moon": swe.MOON,
            "Mean Node": swe.MEAN_NODE,
            "True Node": swe.TRUE_NODE,
        }

        if body not in body_map:
            raise ValueError(f"Unsupported celestial body: {body}")

        result, _flags = swe.calc_ut(
            julian_day_ut,
            body_map[body],
            swe.FLG_SWIEPH | swe.FLG_SPEED,
        )

        return EphemerisPosition(
            body=body,
            longitude=result[0],
            latitude=result[1],
            distance=result[2],
            speed_longitude=result[3],
        )
