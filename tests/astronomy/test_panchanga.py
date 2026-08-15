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
    get_karana_name,
    get_nakshatra_name,
    get_tithi_name,
    get_tithi_paksha,
    get_yoga_name,
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


def test_tithi_name():
    assert get_tithi_name(14) == "Chaturdashi"


def test_tithi_name_rejects_invalid_number():
    with pytest.raises(ValueError):
        get_tithi_name(0)

    with pytest.raises(ValueError):
        get_tithi_name(31)


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

    nakshatra_pada = calculate_nakshatra_pada(moon)

    assert nakshatra_pada == 1


def test_nakshatra_name():
    assert get_nakshatra_name(22) == "Shravana"


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
    assert panchanga.tithi_name == "Chaturdashi"
    assert panchanga.tithi_paksha == "Shukla"
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


def test_yoga_name():
    assert get_yoga_name(1) == "Vishkambha"
    assert get_yoga_name(14) == "Harshana"
    assert get_yoga_name(27) == "Vaidhriti"


def test_yoga_name_rejects_invalid_number():
    with pytest.raises(ValueError):
        get_yoga_name(0)

    with pytest.raises(ValueError):
        get_yoga_name(28)


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


def test_karana_name():
    assert get_karana_name(1) == "Kimstughna"
    assert get_karana_name(2) == "Bava"
    assert get_karana_name(3) == "Balava"
    assert get_karana_name(8) == "Vishti"
    assert get_karana_name(57) == "Vishti"
    assert get_karana_name(58) == "Shakuni"
    assert get_karana_name(59) == "Chatushpada"
    assert get_karana_name(60) == "Naga"
def test_all_karana_positions():
    expected = [
        "Kimstughna",
        "Bava",
        "Balava",
        "Kaulava",
        "Taitila",
        "Garaja",
        "Vanija",
        "Vishti",
        "Bava",
        "Balava",
        "Kaulava",
        "Taitila",
        "Garaja",
        "Vanija",
        "Vishti",
        "Bava",
        "Balava",
        "Kaulava",
        "Taitila",
        "Garaja",
        "Vanija",
        "Vishti",
        "Bava",
        "Balava",
        "Kaulava",
        "Taitila",
        "Garaja",
        "Vanija",
        "Vishti",
        "Bava",
        "Balava",
        "Kaulava",
        "Taitila",
        "Garaja",
        "Vanija",
        "Vishti",
        "Bava",
        "Balava",
        "Kaulava",
        "Taitila",
        "Garaja",
        "Vanija",
        "Vishti",
        "Bava",
        "Balava",
        "Kaulava",
        "Taitila",
        "Garaja",
        "Vanija",
        "Vishti",
        "Bava",
        "Balava",
        "Kaulava",
        "Taitila",
        "Garaja",
        "Vanija",
        "Vishti",
        "Shakuni",
        "Chatushpada",
        "Naga",
    ]

    actual = [
        get_karana_name(position)
        for position in range(1, 61)
    ]

    assert actual == expected

def test_karana_name_rejects_invalid_number():
    with pytest.raises(ValueError):
        get_karana_name(0)

    with pytest.raises(ValueError):
        get_karana_name(61)


def test_vara_calculation():
    value = datetime(2026, 8, 10, 10, 10)

    assert calculate_vara(value) == 1


def test_tithi_paksha():
    assert get_tithi_paksha(1) == "Shukla"
    assert get_tithi_paksha(15) == "Shukla"
    assert get_tithi_paksha(16) == "Krishna"
    assert get_tithi_paksha(30) == "Krishna"


def test_tithi_paksha_rejects_invalid_number():
    with pytest.raises(ValueError):
        get_tithi_paksha(0)

    with pytest.raises(ValueError):
        get_tithi_paksha(31)