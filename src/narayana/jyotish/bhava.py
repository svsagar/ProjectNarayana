"""Bhava (house) placement classification for Project Narayana Jyotish."""

from __future__ import annotations

from dataclasses import dataclass


BHAVA_COUNT = 12
FULL_CIRCLE = 360.0


@dataclass(frozen=True)
class BhavaPlacement:
    """Canonical Bhava placement of a celestial longitude."""

    longitude: float
    bhava_number: int


def normalize_longitude(longitude: float) -> float:
    """Normalize longitude into the canonical [0, 360) interval."""

    if not isinstance(longitude, (int, float)) or isinstance(longitude, bool):
        raise TypeError("longitude must be a number")

    return float(longitude) % FULL_CIRCLE


def normalize_cusps(cusps: tuple[float, ...]) -> tuple[float, ...]:
    """Validate and normalize the twelve Bhava cusp longitudes."""

    if not isinstance(cusps, tuple):
        raise TypeError("cusps must be a tuple")

    if len(cusps) != BHAVA_COUNT:
        raise ValueError("cusps must contain exactly 12 values")

    normalized = tuple(normalize_longitude(cusp) for cusp in cusps)

    return normalized


def get_bhava_number(
    longitude: float,
    cusps: tuple[float, ...],
) -> int:
    """Return the 1-based Bhava containing a celestial longitude.

    Each cusp marks the beginning of its corresponding Bhava.
    The interval extends from that cusp up to, but not including,
    the following cusp, proceeding cyclically through 360 degrees.
    """

    normalized_longitude = normalize_longitude(longitude)
    normalized_cusps = normalize_cusps(cusps)

    for index, cusp in enumerate(normalized_cusps):
        next_cusp = normalized_cusps[(index + 1) % BHAVA_COUNT]

        if cusp < next_cusp:
            in_bhava = cusp <= normalized_longitude < next_cusp
        else:
            in_bhava = (
                normalized_longitude >= cusp
                or normalized_longitude < next_cusp
            )

        if in_bhava:
            return index + 1

    # A valid ordered cusp system should always classify the longitude.
    raise ValueError("longitude could not be assigned to a Bhava")


def calculate_bhava_placement(
    longitude: float,
    cusps: tuple[float, ...],
) -> BhavaPlacement:
    """Calculate the Bhava placement of a celestial longitude."""

    normalized_longitude = normalize_longitude(longitude)

    return BhavaPlacement(
        longitude=normalized_longitude,
        bhava_number=get_bhava_number(
            normalized_longitude,
            cusps,
        ),
    )