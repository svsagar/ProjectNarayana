"""Integration of Graha, Rashi, Nakshatra, and Bhava placement."""

from __future__ import annotations

from dataclasses import dataclass

from .bhava import get_bhava_number
from .graha import Graha
from .nakshatra import (
    get_nakshatra_name,
    get_nakshatra_number,
    get_nakshatra_pada,
)
from .rashi import get_rashi_name, get_rashi_number


@dataclass(frozen=True)
class GrahaBhavaPlacement:
    """Complete Jyotish placement of a Graha."""

    graha: Graha
    longitude: float
    rashi_number: int
    rashi_name: str
    nakshatra_number: int
    nakshatra_name: str
    nakshatra_pada: int
    bhava_number: int


def calculate_graha_bhava_placement(
    graha: Graha,
    longitude: float,
    cusps: tuple[float, ...],
) -> GrahaBhavaPlacement:
    """Calculate complete Rashi, Nakshatra, and Bhava placement."""

    if not isinstance(graha, Graha):
        raise TypeError("graha must be a Graha")

    if not isinstance(longitude, (int, float)) or isinstance(longitude, bool):
        raise TypeError("longitude must be a number")

    normalized_longitude = float(longitude) % 360.0

    rashi_number = get_rashi_number(normalized_longitude)
    rashi_name = get_rashi_name(rashi_number)

    nakshatra_number = get_nakshatra_number(normalized_longitude)
    nakshatra_name = get_nakshatra_name(nakshatra_number)
    nakshatra_pada = get_nakshatra_pada(normalized_longitude)

    bhava_number = get_bhava_number(
        normalized_longitude,
        cusps,
    )

    return GrahaBhavaPlacement(
        graha=graha,
        longitude=normalized_longitude,
        rashi_number=rashi_number,
        rashi_name=rashi_name,
        nakshatra_number=nakshatra_number,
        nakshatra_name=nakshatra_name,
        nakshatra_pada=nakshatra_pada,
        bhava_number=bhava_number,
    )