"""Panchanga calculations for Project Narayana."""

from __future__ import annotations

from .models import AstronomyResult, PanchangaData


def calculate_tithi(result: AstronomyResult) -> int:
    """Calculate the Vedic Tithi from the Sun and Moon longitudes."""

    sun = next(
        position
        for position in result.positions
        if position.body == "Sun"
    )

    moon = next(
        position
        for position in result.positions
        if position.body == "Moon"
    )

    elongation = (moon.longitude - sun.longitude) % 360.0

    return int(elongation // 12.0) + 1


def calculate_panchanga(result: AstronomyResult) -> PanchangaData:
    """Calculate the currently supported Panchanga values."""

    return PanchangaData(
        tithi=calculate_tithi(result),
        nakshatra=0.0,
        yoga=0.0,
        karana=0.0,
        vara=0,
    )