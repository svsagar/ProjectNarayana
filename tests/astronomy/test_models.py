"""Tests for the Astronomy Engine core models."""

from datetime import date, datetime, time, timezone

from src.narayana.astronomy.models import (
    AscendantPosition,
    AstronomyResult,
    BirthInput,
    CalculationConfig,
    CalculationMetadata,
    CelestialPosition,
    HouseCusps,
    PanchangaData,
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
    assert config.house_system == "placidus"
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

    metadata = CalculationMetadata(
        local_datetime=datetime(
            1978,
            8,
            17,
            10,
            10,
            tzinfo=timezone.utc,
        ),
        timezone_name="Asia/Kolkata",
        utc_datetime=datetime(
            1978,
            8,
            17,
            4,
            40,
            tzinfo=timezone.utc,
        ),
        latitude=9.5916,
        longitude=76.5222,
        coordinate_source=None,
        coordinate_precision=None,
        julian_day_ut=2443742.6875,
        ephemeris_implementation="swiss_ephemeris",
        ephemeris_version="2.10.03",
        ayanamsa="lahiri",
        node_mode="mean",
    )

    position = CelestialPosition(
        body="Sun",
        longitude=120.5,
        latitude=0.0,
        distance=1.0,
        speed_longitude=0.95,
    )

    ascendant = AscendantPosition(
        longitude=185.25,
    )

    houses = HouseCusps(
        cusps=(
            185.25,
            215.25,
            245.25,
            275.25,
            305.25,
            335.25,
            5.25,
            35.25,
            65.25,
            95.25,
            125.25,
            155.25,
        ),
    )

    result = AstronomyResult(
        birth_input=birth,
        calculation_config=config,
        calculation_metadata=metadata,
        positions=(position,),
        ascendant=ascendant,
        houses=houses,
    )

    assert result.calculation_metadata.julian_day_ut == 2443742.6875
    assert result.calculation_metadata.timezone_name == "Asia/Kolkata"
    assert result.calculation_metadata.utc_datetime == datetime(
        1978,
        8,
        17,
        4,
        40,
        tzinfo=timezone.utc,
    )
    assert result.calculation_metadata.ephemeris_implementation == "swiss_ephemeris"
    assert result.calculation_metadata.ephemeris_version == "2.10.03"
    assert result.calculation_metadata.ayanamsa == "lahiri"
    assert result.calculation_metadata.node_mode == "mean"
    assert len(result.positions) == 1
    assert result.positions[0].body == "Sun"
    assert result.ascendant.longitude == 185.25
    assert len(result.houses.cusps) == 12
    assert result.houses.cusps[0] == 185.25
def test_panchanga_data():
    panchanga = PanchangaData(
        tithi=1.0,
        nakshatra=5.0,
        yoga=10.0,
        karana=2.0,
        vara=3,
    )

    assert panchanga.tithi == 1.0
    assert panchanga.nakshatra == 5.0
    assert panchanga.yoga == 10.0
    assert panchanga.karana == 2.0
    assert panchanga.vara == 3