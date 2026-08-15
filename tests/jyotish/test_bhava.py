"""Tests for Bhava placement classification."""

import pytest

from src.narayana.jyotish.bhava import (
    BhavaPlacement,
    calculate_bhava_placement,
    get_bhava_number,
    normalize_cusps,
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


def test_bhava_at_first_cusp():
    assert get_bhava_number(0.0, CUSPS) == 1


def test_bhava_at_second_cusp():
    assert get_bhava_number(30.0, CUSPS) == 2


def test_bhava_at_last_cusp():
    assert get_bhava_number(330.0, CUSPS) == 12


@pytest.mark.parametrize(
    "longitude,expected",
    [
        (0.0, 1),
        (29.999999, 1),
        (30.0, 2),
        (59.999999, 2),
        (60.0, 3),
        (89.999999, 3),
        (90.0, 4),
        (119.999999, 4),
        (120.0, 5),
        (149.999999, 5),
        (150.0, 6),
        (179.999999, 6),
        (180.0, 7),
        (209.999999, 7),
        (210.0, 8),
        (239.999999, 8),
        (240.0, 9),
        (269.999999, 9),
        (270.0, 10),
        (299.999999, 10),
        (300.0, 11),
        (329.999999, 11),
        (330.0, 12),
        (359.999999, 12),
    ],
)
def test_all_bhava_boundaries(longitude, expected):
    assert get_bhava_number(longitude, CUSPS) == expected


def test_longitude_wraps_at_360():
    assert get_bhava_number(360.0, CUSPS) == 1


def test_negative_longitude_is_normalized():
    assert get_bhava_number(-30.0, CUSPS) == 12


def test_bhava_placement_returns_dataclass():
    placement = calculate_bhava_placement(
        45.0,
        CUSPS,
    )

    assert isinstance(placement, BhavaPlacement)
    assert placement.longitude == 45.0
    assert placement.bhava_number == 2


def test_bhava_placement_normalizes_longitude():
    placement = calculate_bhava_placement(
        405.0,
        CUSPS,
    )

    assert placement.longitude == 45.0
    assert placement.bhava_number == 2


def test_cusps_are_normalized():
    cusps = normalize_cusps(
        (
            360.0,
            390.0,
            420.0,
            450.0,
            480.0,
            510.0,
            540.0,
            570.0,
            600.0,
            630.0,
            660.0,
            690.0,
        )
    )

    assert cusps == CUSPS


@pytest.mark.parametrize(
    "invalid_cusps",
    [
        None,
        [],
        [0.0] * 12,
        CUSPS[:11],
        CUSPS + (0.0,),
    ],
)
def test_invalid_cusps_rejected(invalid_cusps):
    with pytest.raises((TypeError, ValueError)):
        normalize_cusps(invalid_cusps)


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
        get_bhava_number(
            invalid_longitude,
            CUSPS,
        )


def test_invalid_cusp_value_rejected():
    cusps = (
        0.0,
        30.0,
        "60.0",
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

    with pytest.raises(TypeError, match="longitude must be a number"):
        normalize_cusps(cusps)


def test_bhava_placement_is_immutable():
    placement = calculate_bhava_placement(
        45.0,
        CUSPS,
    )

    with pytest.raises(AttributeError):
        placement.longitude = 50.0