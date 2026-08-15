"""Tests for integrated Graha Rashi-Nakshatra-Bhava placement."""

import pytest

from src.narayana.jyotish.graha import Graha
from src.narayana.jyotish.integration import (
    GrahaBhavaPlacement,
    calculate_graha_bhava_placement,
)


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


def test_complete_sun_placement():
    placement = calculate_graha_bhava_placement(
        Graha.SURYA,
        0.0,
        CUSPS,
    )

    assert isinstance(placement, GrahaBhavaPlacement)
    assert placement.graha is Graha.SURYA
    assert placement.longitude == 0.0

    assert placement.rashi_number == 1
    assert placement.rashi_name == "Mesha"

    assert placement.nakshatra_number == 1
    assert placement.nakshatra_name == "Ashwini"
    assert placement.nakshatra_pada == 1

    assert placement.bhava_number == 1


def test_complete_moon_placement():
    placement = calculate_graha_bhava_placement(
        Graha.CHANDRA,
        30.0,
        CUSPS,
    )

    assert placement.graha is Graha.CHANDRA
    assert placement.longitude == 30.0

    assert placement.rashi_number == 2
    assert placement.rashi_name == "Vrishabha"

    assert placement.nakshatra_number == 3
    assert placement.nakshatra_name == "Krittika"

    assert placement.bhava_number == 2


@pytest.mark.parametrize(
    "longitude,expected_rashi,expected_nakshatra,expected_bhava",
    [
        (0.0, 1, 1, 1),
        (29.999999, 1, 3, 1),
        (30.0, 2, 3, 2),
        (60.0, 3, 5, 3),
        (90.0, 4, 7, 4),
        (120.0, 5, 10, 5),
        (180.0, 7, 14, 7),
        (240.0, 9, 19, 9),
        (300.0, 11, 23, 11),
        (330.0, 12, 25, 12),
        (359.999999, 12, 27, 12),
    ],
)
def test_integrated_boundary_values(
    longitude,
    expected_rashi,
    expected_nakshatra,
    expected_bhava,
):
    placement = calculate_graha_bhava_placement(
        Graha.SURYA,
        longitude,
        CUSPS,
    )

    assert placement.rashi_number == expected_rashi
    assert placement.nakshatra_number == expected_nakshatra
    assert placement.bhava_number == expected_bhava


def test_longitude_is_normalized():
    placement = calculate_graha_bhava_placement(
        Graha.GURU,
        360.0,
        CUSPS,
    )

    assert placement.longitude == 0.0
    assert placement.rashi_number == 1
    assert placement.nakshatra_number == 1
    assert placement.bhava_number == 1


def test_negative_longitude_is_normalized():
    placement = calculate_graha_bhava_placement(
        Graha.SHUKRA,
        -30.0,
        CUSPS,
    )

    assert placement.longitude == 330.0
    assert placement.rashi_number == 12
    assert placement.nakshatra_number == 25
    assert placement.bhava_number == 12


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
def test_invalid_graha_rejected(invalid_graha):
    with pytest.raises(TypeError, match="graha must be a Graha"):
        calculate_graha_bhava_placement(
            invalid_graha,
            120.0,
            CUSPS,
        )


@pytest.mark.parametrize(
    "invalid_longitude",
    [
        "120.0",
        None,
        True,
        False,
    ],
)
def test_invalid_longitude_rejected(invalid_longitude):
    with pytest.raises(TypeError, match="longitude must be a number"):
        calculate_graha_bhava_placement(
            Graha.SURYA,
            invalid_longitude,
            CUSPS,
        )


def test_invalid_cusps_are_rejected():
    with pytest.raises(ValueError, match="exactly 12"):
        calculate_graha_bhava_placement(
            Graha.SURYA,
            120.0,
            CUSPS[:11],
        )


def test_result_is_immutable():
    placement = calculate_graha_bhava_placement(
        Graha.SURYA,
        120.0,
        CUSPS,
    )

    with pytest.raises(AttributeError):
        placement.bhava_number = 6