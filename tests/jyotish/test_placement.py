"""Tests for Graha placement classification."""

import pytest

from src.narayana.jyotish.graha import Graha
from src.narayana.jyotish.placement import (
    GrahaPlacement,
    calculate_graha_placement,
)


def test_sun_placement_at_zero_degrees():
    placement = calculate_graha_placement(
        Graha.SURYA,
        0.0,
    )

    assert isinstance(placement, GrahaPlacement)
    assert placement.graha is Graha.SURYA
    assert placement.longitude == 0.0
    assert placement.rashi_number == 1
    assert placement.rashi_name == "Mesha"
    assert placement.nakshatra_number == 1
    assert placement.nakshatra_name == "Ashwini"
    assert placement.nakshatra_pada == 1


def test_moon_placement_at_thirty_degrees():
    placement = calculate_graha_placement(
        Graha.CHANDRA,
        30.0,
    )

    assert placement.graha is Graha.CHANDRA
    assert placement.longitude == 30.0
    assert placement.rashi_number == 2
    assert placement.rashi_name == "Vrishabha"
    assert placement.nakshatra_number == 3
    assert placement.nakshatra_name == "Krittika"


def test_placement_at_sixty_degrees():
    placement = calculate_graha_placement(
        Graha.MANGALA,
        60.0,
    )

    assert placement.rashi_number == 3
    assert placement.rashi_name == "Mithuna"


def test_placement_at_three_hundred_thirty_degrees():
    placement = calculate_graha_placement(
        Graha.SHANI,
        330.0,
    )

    assert placement.rashi_number == 12
    assert placement.rashi_name == "Meena"


def test_longitude_is_normalized():
    placement = calculate_graha_placement(
        Graha.GURU,
        360.0,
    )

    assert placement.longitude == 0.0
    assert placement.rashi_number == 1
    assert placement.rashi_name == "Mesha"
    assert placement.nakshatra_number == 1
    assert placement.nakshatra_name == "Ashwini"


def test_negative_longitude_is_normalized():
    placement = calculate_graha_placement(
        Graha.SHUKRA,
        -30.0,
    )

    assert placement.longitude == 330.0
    assert placement.rashi_number == 12
    assert placement.rashi_name == "Meena"


@pytest.mark.parametrize(
    "longitude,expected_rashi,expected_name",
    [
        (0.0, 1, "Mesha"),
        (29.999999, 1, "Mesha"),
        (30.0, 2, "Vrishabha"),
        (59.999999, 2, "Vrishabha"),
        (60.0, 3, "Mithuna"),
        (89.999999, 3, "Mithuna"),
        (90.0, 4, "Karka"),
        (119.999999, 4, "Karka"),
        (120.0, 5, "Simha"),
        (149.999999, 5, "Simha"),
        (150.0, 6, "Kanya"),
        (179.999999, 6, "Kanya"),
        (180.0, 7, "Tula"),
        (209.999999, 7, "Tula"),
        (210.0, 8, "Vrishchika"),
        (239.999999, 8, "Vrishchika"),
        (240.0, 9, "Dhanu"),
        (269.999999, 9, "Dhanu"),
        (270.0, 10, "Makara"),
        (299.999999, 10, "Makara"),
        (300.0, 11, "Kumbha"),
        (329.999999, 11, "Kumbha"),
        (330.0, 12, "Meena"),
        (359.999999, 12, "Meena"),
    ],
)
def test_all_rashi_boundaries(
    longitude,
    expected_rashi,
    expected_name,
):
    placement = calculate_graha_placement(
        Graha.SURYA,
        longitude,
    )

    assert placement.rashi_number == expected_rashi
    assert placement.rashi_name == expected_name


@pytest.mark.parametrize(
    "longitude,expected_nakshatra,expected_pada",
    [
        (0.0, 1, 1),
        (3.333333, 1, 1),
        (3.333334, 1, 2),
        (10.0, 1, 4),
        (13.333333333333334, 2, 1),
        (26.666666666666668, 3, 1),
        (359.999999, 27, 4),
    ],
)
def test_nakshatra_and_pada(
    longitude,
    expected_nakshatra,
    expected_pada,
):
    placement = calculate_graha_placement(
        Graha.CHANDRA,
        longitude,
    )

    assert placement.nakshatra_number == expected_nakshatra
    assert placement.nakshatra_pada == expected_pada


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
        calculate_graha_placement(
            invalid_graha,
            120.0,
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
        calculate_graha_placement(
            Graha.SURYA,
            invalid_longitude,
        )


def test_placement_is_immutable():
    placement = calculate_graha_placement(
        Graha.SURYA,
        120.0,
    )

    with pytest.raises(AttributeError):
        placement.longitude = 121.0