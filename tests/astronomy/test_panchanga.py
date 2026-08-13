"""Tests for Panchanga calculations."""

from datetime import date, time

from src.narayana.astronomy.calculator import calculate
from src.narayana.astronomy.models import BirthInput, CalculationConfig
from src.narayana.astronomy.panchanga import calculate_panchanga


VALIDATION_BIRTH = BirthInput(
    birth_date=date(1978, 8, 17),
    birth_time=time(10, 10),
    timezone="Asia/Kolkata",
    latitude=9.5916,
    longitude=76.5222,
)


def test_panchanga_calculation():
    config = CalculationConfig(
        zodiac="sidereal",
        ayanamsa="lahiri",
        node="mean",
    )

    astronomy_result = calculate(
        VALIDATION_BIRTH,
        config,
        bodies=("Sun", "Moon"),
    )

    panchanga = calculate_panchanga(astronomy_result)

    assert panchanga.tithi == 14
    assert panchanga.nakshatra == 0.0
    assert panchanga.yoga == 0.0
    assert panchanga.karana == 0.0
    assert panchanga.vara == 0