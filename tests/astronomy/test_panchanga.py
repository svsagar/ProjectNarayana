"""Tests for Panchanga calculations."""

from datetime import date, datetime, time

import pytest

from src.narayana.astronomy.calculator import calculate
from src.narayana.astronomy.models import BirthInput, CalculationConfig
from src.narayana.astronomy.panchanga import (
    calculate_karana,
    calculate_nakshatra,
    calculate_nakshatra_pada,
    calculate_panchanga,
    calculate_tithi,
    calculate_vara,
    calculate_yoga,
    get_nakshatra_name,
)


VALIDATION_BIRTH = BirthInput(
    birth_date=date(1978, 8, 17),
    birth_time=time(10, 10),
    timezone="Asia/Kolkata",
    latitude=9.5916,
    longitude=76.5222,
)


def test_tithi_calculation():
    config = CalculationConfig(
        zodiac="sidereal",
        ayanamsa="lahiri",
        node="mean",
    )

    result = calculate(
        VALIDATION_BIRTH,
        config,
        bodies=("Sun", "Moon"),
    )

    sun = result.positions[0]
    moon = result.positions[1]

    tithi = calculate_tithi(sun, moon)

    assert tithi == 14


def test_nakshatra_calculation():
    config = CalculationConfig(
        zodiac="sidereal",
        ayanamsa="lahiri",
        node="mean",
    )

    result = calculate(
        VALIDATION_BIRTH,
        config,
        bodies=("Sun", "Moon"),
    )

    moon = result.positions[1]

    nakshatra = calculate_nakshatra(moon)

    assert nakshatra == 22


def test_nakshatra_pada_calculation():
    config = CalculationConfig(
        zodiac="sidereal",
        ayanamsa="lahiri",
        node="mean",
    )

    result = calculate(
        VALIDATION_BIRTH,
        config,
        bodies=("Sun", "Moon"),
    )

    moon = result.positions[1]

    pada = calculate_nakshatra_pada(moon)

    assert pada == 1


def test_nakshatra_name():
    assert get_nakshatra_name(1) == "Ashwini"
    assert get_nakshatra_name(22) == "Shravana"
    assert get_nakshatra_name(27) == "Revati"


def test_nakshatra_name_rejects_invalid_number():
    with pytest.raises(ValueError):
        get_nakshatra_name(0)

    with pytest.raises(ValueError):
        get_nakshatra_name(28)


def test_panchanga_calculation():
    config = CalculationConfig(
        zodiac="sidereal",
        ayanamsa="lahiri",
        node="mean",
    )

    result = calculate(
        VALIDATION_BIRTH,
        config,
        bodies=("Sun", "Moon"),
    )

    sun = result.positions[0]
    moon = result.positions[1]

    panchanga = calculate_panchanga(
        sun,
        moon,
        result.calculation_metadata.local_datetime,
    )

    assert panchanga.tithi == 14
    assert panchanga.nakshatra == 22
    assert panchanga.nakshatra_pada == 1
    assert panchanga.yoga == 4
    assert panchanga.karana == 28
    assert panchanga.vara == 4


def test_yoga_calculation():
    config = CalculationConfig(
        zodiac="sidereal",
        ayanamsa="lahiri",
        node="mean",
    )

    result = calculate(
        VALIDATION_BIRTH,
        config,
        bodies=("Sun", "Moon"),
    )

    sun = result.positions[0]
    moon = result.positions[1]

    yoga = calculate_yoga(sun, moon)

    assert yoga == 4


def test_karana_calculation():
    config = CalculationConfig(
        zodiac="sidereal",
        ayanamsa="lahiri",
        node="mean",
    )

    result = calculate(
        VALIDATION_BIRTH,
        config,
        bodies=("Sun", "Moon"),
    )

    sun = result.positions[0]
    moon = result.positions[1]

    karana = calculate_karana(sun, moon)

    assert karana == 28


def test_vara_calculation():
    value = datetime(2026, 8, 10, 10, 10)

    assert calculate_vara(value) == 1