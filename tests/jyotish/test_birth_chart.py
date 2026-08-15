"""Tests for AstronomyResult to Jyotish birth-chart conversion."""

from datetime import date, datetime, time

import pytest

from src.narayana.astronomy.models import (
    AscendantPosition,
    AstronomyResult,
    BirthInput,
    CalculationConfig,
    CalculationMetadata,
    CelestialPosition,
    HouseCusps,
)

from src.narayana.jyotish.birth_chart import (
    JyotishBirthChart,
    calculate_birth_chart,
)
from src.narayana.jyotish.graha import GRAHAS, Graha


CUSPS = (
    0.0,
    30.0,
    60.0,
    90.0,
    120.0,
    150.0,
    180.0,
    210.0,
    240.0,
    270.0,
    300.0,
    330.0,
)


def make_astronomy_result() -> AstronomyResult:
    """Create a deterministic AstronomyResult for unit tests."""

    birth_input = BirthInput(
        birth_date=date(1978, 8, 17),
        birth_time=time(10, 10),
        timezone="Asia/Kolkata",
        latitude=9.5916,
        longitude=76.5222,
    )

    calculation_config = CalculationConfig()

    metadata = CalculationMetadata(
        local_datetime=datetime(
            1978,
            8,
            17,
            10,
            10,
        ),
        timezone_name="Asia/Kolkata",
        utc_datetime=datetime(
            1978,
            8,
            17,
            4,
            40,
        ),
        latitude=9.5916,
        longitude=76.5222,
        coordinate_source="test",
        coordinate_precision=6,
        julian_day_ut=2443737.694444,
        ephemeris_implementation="Swiss Ephemeris",
        ephemeris_version="test",
        ayanamsa=calculation_config.ayanamsa,
        node_mode=calculation_config.node,
    )

    positions = (
        CelestialPosition(
            body="Sun",
            longitude=0.0,
            latitude=0.0,
            distance=1.0,
            speed_longitude=1.0,
        ),
        CelestialPosition(
            body="Moon",
            longitude=30.0,
            latitude=0.0,
            distance=1.0,
            speed_longitude=13.0,
        ),
        CelestialPosition(
            body="Mars",
            longitude=60.0,
            latitude=0.0,
            distance=1.0,
            speed_longitude=0.5,
        ),
        CelestialPosition(
            body="Mercury",
            longitude=90.0,
            latitude=0.0,
            distance=1.0,
            speed_longitude=1.0,
        ),
        CelestialPosition(
            body="Jupiter",
            longitude=120.0,
            latitude=0.0,
            distance=1.0,
            speed_longitude=0.1,
        ),
        CelestialPosition(
            body="Venus",
            longitude=150.0,
            latitude=0.0,
            distance=1.0,
            speed_longitude=1.0,
        ),
        CelestialPosition(
            body="Saturn",
            longitude=180.0,
            latitude=0.0,
            distance=1.0,
            speed_longitude=0.1,
        ),
        CelestialPosition(
            body="Rahu",
            longitude=210.0,
            latitude=0.0,
            distance=1.0,
            speed_longitude=-0.1,
        ),
        CelestialPosition(
            body="Ketu",
            longitude=30.0,
            latitude=0.0,
            distance=1.0,
            speed_longitude=-0.1,
        ),
    )

    return AstronomyResult(
        birth_input=birth_input,
        calculation_config=calculation_config,
        calculation_metadata=metadata,
        positions=positions,
        ascendant=AscendantPosition(
            longitude=15.0,
        ),
        houses=HouseCusps(
            cusps=CUSPS,
        ),
        panchanga=None,
    )


def test_calculate_birth_chart_returns_chart():
    result = calculate_birth_chart(
        make_astronomy_result()
    )

    assert isinstance(result, JyotishBirthChart)
    assert len(result.placements) == 9


def test_birth_chart_contains_all_grahas():
    result = calculate_birth_chart(
        make_astronomy_result()
    )

    assert tuple(
        placement.graha
        for placement in result.placements
    ) == GRAHAS


def test_sun_is_mapped_to_surya():
    result = calculate_birth_chart(
        make_astronomy_result()
    )

    placement = result.get_placement(Graha.SURYA)

    assert placement.graha is Graha.SURYA
    assert placement.longitude == 0.0
    assert placement.rashi_number == 1
    assert placement.rashi_name == "Mesha"
    assert placement.nakshatra_number == 1
    assert placement.nakshatra_name == "Ashwini"
    assert placement.bhava_number == 1


def test_moon_is_mapped_to_chandra():
    result = calculate_birth_chart(
        make_astronomy_result()
    )

    placement = result.get_placement(Graha.CHANDRA)

    assert placement.graha is Graha.CHANDRA
    assert placement.longitude == 30.0
    assert placement.rashi_number == 2
    assert placement.rashi_name == "Vrishabha"
    assert placement.nakshatra_number == 3
    assert placement.nakshatra_name == "Krittika"
    assert placement.bhava_number == 2


@pytest.mark.parametrize(
    "graha,expected_longitude,expected_bhava",
    [
        (Graha.SURYA, 0.0, 1),
        (Graha.CHANDRA, 30.0, 2),
        (Graha.MANGALA, 60.0, 3),
        (Graha.BUDHA, 90.0, 4),
        (Graha.GURU, 120.0, 5),
        (Graha.SHUKRA, 150.0, 6),
        (Graha.SHANI, 180.0, 7),
        (Graha.RAHU, 210.0, 8),
        (Graha.KETU, 30.0, 2),
    ],
)
def test_all_grahas_are_converted(
    graha,
    expected_longitude,
    expected_bhava,
):
    result = calculate_birth_chart(
        make_astronomy_result()
    )

    placement = result.get_placement(graha)

    assert placement.longitude == expected_longitude
    assert placement.bhava_number == expected_bhava


def test_ascendant_is_preserved():
    result = calculate_birth_chart(
        make_astronomy_result()
    )

    assert result.ascendant_longitude == 15.0


def test_bhava_cusps_are_preserved():
    result = calculate_birth_chart(
        make_astronomy_result()
    )

    assert result.bhava_cusps == CUSPS


def test_original_astronomy_result_is_preserved():
    astronomy_result = make_astronomy_result()

    result = calculate_birth_chart(
        astronomy_result
    )

    assert result.astronomy_result is astronomy_result


@pytest.mark.parametrize(
    "invalid_value",
    [
        None,
        123,
        {},
        "AstronomyResult",
    ],
)
def test_invalid_astronomy_result_is_rejected(
    invalid_value,
):
    with pytest.raises(
        TypeError,
        match="astronomy_result must be an AstronomyResult",
    ):
        calculate_birth_chart(invalid_value)


def test_missing_required_body_is_rejected():
    astronomy_result = make_astronomy_result()

    reduced_positions = tuple(
        position
        for position in astronomy_result.positions
        if position.body != "Mars"
    )

    reduced_result = AstronomyResult(
        birth_input=astronomy_result.birth_input,
        calculation_config=astronomy_result.calculation_config,
        calculation_metadata=astronomy_result.calculation_metadata,
        positions=reduced_positions,
        ascendant=astronomy_result.ascendant,
        houses=astronomy_result.houses,
        panchanga=astronomy_result.panchanga,
    )

    with pytest.raises(
        ValueError,
        match="missing required Graha positions: Mars",
    ):
        calculate_birth_chart(reduced_result)


@pytest.mark.parametrize(
    "invalid_graha",
    [
        "Sun",
        "Surya",
        1,
        None,
        True,
    ],
)
def test_get_placement_rejects_invalid_graha(
    invalid_graha,
):
    chart = calculate_birth_chart(
        make_astronomy_result()
    )

    with pytest.raises(
        TypeError,
        match="graha must be a Graha",
    ):
        chart.get_placement(invalid_graha)


def test_chart_is_immutable():
    chart = calculate_birth_chart(
        make_astronomy_result()
    )

    with pytest.raises(AttributeError):
        chart.ascendant_longitude = 20.0


def test_placements_are_immutable():
    chart = calculate_birth_chart(
        make_astronomy_result()
    )

    with pytest.raises(AttributeError):
        chart.placements = ()