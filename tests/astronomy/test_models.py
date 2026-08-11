"""Tests for the Astronomy Engine core models."""

from datetime import date, time

from src.narayana.astronomy.models import (
    AstronomyResult,
    BirthInput,
    CalculationConfig,
    CelestialPosition,
)


def test_birth_input():
    birth = BirthInput(
        birth_date=date(1978, 8, 17),
        birth_time=time(10, 10),
        timezone="Asia/Kolkata",
        latitude=9.5916,
        longitude=76.5222,
        place_name="Kottayam",
    )

    assert birth.birth_date == date(1978, 8, 17)
    assert birth.birth_time == time(10, 10)
    assert birth.timezone == "Asia/Kolkata"
    assert birth.latitude == 9.5916
    assert birth.longitude == 76.5222
    assert birth.place_name == "Kottayam"


def test_calculation_config():
    config = CalculationConfig(
        zodiac="sidereal",
        ayanamsa="lahiri",
        node="mean",
    )

    assert config.zodiac == "sidereal"
    assert config.ayanamsa == "lahiri"
    assert config.node == "mean"
    assert config.ephemeris == "swiss_ephemeris"


def test_celestial_position():
    position = CelestialPosition(
        body="Sun",
        longitude=120.5,
        latitude=0.0,
        distance=1.0,
        speed_longitude=0.95,
    )

    assert position.body == "Sun"
    assert position.longitude == 120.5


def test_astronomy_result():
    birth = BirthInput(
        birth_date=date(1978, 8, 17),
        birth_time=time(10, 10),
        timezone="Asia/Kolkata",
        latitude=9.5916,
        longitude=76.5222,
    )

    config = CalculationConfig(
        zodiac="sidereal",
        ayanamsa="lahiri",
        node="mean",
    )

    position = CelestialPosition(
        body="Sun",
        longitude=120.5,
        latitude=0.0,
        distance=1.0,
        speed_longitude=0.95,
    )

    result = AstronomyResult(
        birth_input=birth,
        calculation_config=config,
        julian_day_ut=2443742.6875,
        positions=(position,),
    )

    assert result.julian_day_ut == 2443742.6875
    assert len(result.positions) == 1
    assert result.positions[0].body == "Sun"
