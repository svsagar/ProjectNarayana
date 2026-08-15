"""Tests for the Astronomy Engine core models."""

from datetime import date, datetime, time, timezone
from math import inf, nan

import pytest

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


def test_birth_input_accepts_coordinate_boundaries():
    south_west = BirthInput(
        birth_date=date(1978, 8, 17),
        birth_time=time(10, 10),
        timezone="UTC",
        latitude=-90.0,
        longitude=-180.0,
    )

    north_east = BirthInput(
        birth_date=date(1978, 8, 17),
        birth_time=time(10, 10),
        timezone="UTC",
        latitude=90.0,
        longitude=180.0,
    )

    assert south_west.latitude == -90.0
    assert south_west.longitude == -180.0
    assert north_east.latitude == 90.0
    assert north_east.longitude == 180.0


def test_birth_input_rejects_invalid_latitude():
    with pytest.raises(ValueError, match="latitude"):
        BirthInput(
            birth_date=date(1978, 8, 17),
            birth_time=time(10, 10),
            timezone="Asia/Kolkata",
            latitude=90.0001,
            longitude=76.5222,
        )

    with pytest.raises(ValueError, match="latitude"):
        BirthInput(
            birth_date=date(1978, 8, 17),
            birth_time=time(10, 10),
            timezone="Asia/Kolkata",
            latitude=-90.0001,
            longitude=76.5222,
        )


def test_birth_input_rejects_invalid_longitude():
    with pytest.raises(ValueError, match="longitude"):
        BirthInput(
            birth_date=date(1978, 8, 17),
            birth_time=time(10, 10),
            timezone="Asia/Kolkata",
            latitude=9.5916,
            longitude=180.0001,
        )

    with pytest.raises(ValueError, match="longitude"):
        BirthInput(
            birth_date=date(1978, 8, 17),
            birth_time=time(10, 10),
            timezone="Asia/Kolkata",
            latitude=9.5916,
            longitude=-180.0001,
        )


def test_birth_input_rejects_empty_timezone():
    with pytest.raises(ValueError, match="timezone"):
        BirthInput(
            birth_date=date(1978, 8, 17),
            birth_time=time(10, 10),
            timezone="",
            latitude=9.5916,
            longitude=76.5222,
        )


def test_birth_input_rejects_whitespace_timezone():
    with pytest.raises(ValueError, match="timezone"):
        BirthInput(
            birth_date=date(1978, 8, 17),
            birth_time=time(10, 10),
            timezone="   ",
            latitude=9.5916,
            longitude=76.5222,
        )


def test_birth_input_rejects_non_numeric_latitude():
    with pytest.raises(TypeError, match="latitude"):
        BirthInput(
            birth_date=date(1978, 8, 17),
            birth_time=time(10, 10),
            timezone="Asia/Kolkata",
            latitude="9.5916",
            longitude=76.5222,
        )


def test_birth_input_rejects_non_numeric_longitude():
    with pytest.raises(TypeError, match="longitude"):
        BirthInput(
            birth_date=date(1978, 8, 17),
            birth_time=time(10, 10),
            timezone="Asia/Kolkata",
            latitude=9.5916,
            longitude="76.5222",
        )


def test_birth_input_rejects_boolean_coordinates():
    with pytest.raises(TypeError, match="latitude"):
        BirthInput(
            birth_date=date(1978, 8, 17),
            birth_time=time(10, 10),
            timezone="Asia/Kolkata",
            latitude=True,
            longitude=76.5222,
        )

    with pytest.raises(TypeError, match="longitude"):
        BirthInput(
            birth_date=date(1978, 8, 17),
            birth_time=time(10, 10),
            timezone="Asia/Kolkata",
            latitude=9.5916,
            longitude=False,
        )


def test_birth_input_rejects_non_finite_latitude():
    for value in (nan, inf, -inf):
        with pytest.raises(ValueError, match="latitude"):
            BirthInput(
                birth_date=date(1978, 8, 17),
                birth_time=time(10, 10),
                timezone="Asia/Kolkata",
                latitude=value,
                longitude=76.5222,
            )


def test_birth_input_rejects_non_finite_longitude():
    for value in (nan, inf, -inf):
        with pytest.raises(ValueError, match="longitude"):
            BirthInput(
                birth_date=date(1978, 8, 17),
                birth_time=time(10, 10),
                timezone="Asia/Kolkata",
                latitude=9.5916,
                longitude=value,
            )


def test_birth_input_rejects_invalid_birth_date_type():
    with pytest.raises(TypeError, match="birth_date"):
        BirthInput(
            birth_date="1978-08-17",
            birth_time=time(10, 10),
            timezone="Asia/Kolkata",
            latitude=9.5916,
            longitude=76.5222,
        )


def test_birth_input_rejects_invalid_birth_time_type():
    with pytest.raises(TypeError, match="birth_time"):
        BirthInput(
            birth_date=date(1978, 8, 17),
            birth_time="10:10",
            timezone="Asia/Kolkata",
            latitude=9.5916,
            longitude=76.5222,
        )


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
        tithi=14,
        nakshatra=23,
        nakshatra_pada=1,
        yoga=4,
        karana=28,
        vara=4,
    )

    assert panchanga.tithi == 14
    assert panchanga.nakshatra == 23
    assert panchanga.nakshatra_pada == 1
    assert panchanga.yoga == 4
    assert panchanga.karana == 28
    assert panchanga.vara == 4
    """BirthInput validation tests"""

from datetime import date, time

import pytest

from src.narayana.astronomy.models import BirthInput


def test_invalid_birth_date_type():
    with pytest.raises(TypeError):
        BirthInput(
            birth_date="2026-08-14",  # type: ignore[arg-type]
            birth_time=time(12, 0),
            timezone="UTC",
            latitude=10.0,
            longitude=76.0,
        )


def test_invalid_birth_time_type():
    with pytest.raises(TypeError):
        BirthInput(
            birth_date=date(2026, 8, 14),
            birth_time="12:00:00",  # type: ignore[arg-type]
            timezone="UTC",
            latitude=10.0,
            longitude=76.0,
        )


@pytest.mark.parametrize("invalid_tz", ["", "   ", None, 123])
def test_invalid_timezone(invalid_tz):
    with pytest.raises((TypeError, ValueError)):
        BirthInput(
            birth_date=date(2026, 8, 14),
            birth_time=time(12, 0),
            timezone=invalid_tz,  # type: ignore[arg-type]
            latitude=10.0,
            longitude=76.0,
        )


@pytest.mark.parametrize("invalid_lat", ["10.0", None])
def test_non_numeric_latitude(invalid_lat):
    with pytest.raises(TypeError):
        BirthInput(
            birth_date=date(2026, 8, 14),
            birth_time=time(12, 0),
            timezone="UTC",
            latitude=invalid_lat,  # type: ignore[arg-type]
            longitude=76.0,
        )


@pytest.mark.parametrize(
    "out_of_bounds_lat",
    [-91.0, 91.0, -150.0, 200.0],
)
def test_latitude_out_of_bounds(out_of_bounds_lat):
    with pytest.raises(ValueError):
        BirthInput(
            birth_date=date(2026, 8, 14),
            birth_time=time(12, 0),
            timezone="UTC",
            latitude=out_of_bounds_lat,
            longitude=76.0,
        )


@pytest.mark.parametrize("invalid_lon", ["76.0", None])
def test_non_numeric_longitude(invalid_lon):
    with pytest.raises(TypeError):
        BirthInput(
            birth_date=date(2026, 8, 14),
            birth_time=time(12, 0),
            timezone="UTC",
            latitude=10.0,
            longitude=invalid_lon,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "out_of_bounds_lon",
    [-181.0, 181.0, -200.0, 250.0],
)
def test_longitude_out_of_bounds(out_of_bounds_lon):
    with pytest.raises(ValueError):
        BirthInput(
            birth_date=date(2026, 8, 14),
            birth_time=time(12, 0),
            timezone="UTC",
            latitude=10.0,
            longitude=out_of_bounds_lon,
        )


@pytest.mark.parametrize(
    "lat,lon",
    [
        (90.0, 180.0),
        (-90.0, -180.0),
        (90.0, -180.0),
        (-90.0, 180.0),
    ],
)
def test_valid_boundary_coordinates(lat, lon):
    birth = BirthInput(
        birth_date=date(2026, 8, 14),
        birth_time=time(12, 0),
        timezone="UTC",
        latitude=lat,
        longitude=lon,
    )

    assert birth.latitude == lat
    assert birth.longitude == lon


@pytest.mark.parametrize("val", [True, False])
def test_boolean_rejection_for_coordinates(val):
    with pytest.raises(TypeError):
        BirthInput(
            birth_date=date(2026, 8, 14),
            birth_time=time(12, 0),
            timezone="UTC",
            latitude=val,  # type: ignore[arg-type]
            longitude=76.0,
        )

    with pytest.raises(TypeError):
        BirthInput(
            birth_date=date(2026, 8, 14),
            birth_time=time(12, 0),
            timezone="UTC",
            latitude=10.0,
            longitude=val,  # type: ignore[arg-type]
        )