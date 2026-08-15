"""Tests for Rashi classification in the Project Narayana Jyotish layer."""

import pytest

from src.narayana.jyotish.rashi import (
    RASHI_NAMES,
    get_rashi_name,
    get_rashi_number,
    normalize_longitude,
)


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
def test_rashi_number_boundaries(longitude, expected):
    assert get_rashi_number(longitude) == expected


@pytest.mark.parametrize(
    "longitude,expected",
    [
        (360.0, 1),
        (720.0, 1),
        (-0.000001, 12),
        (-30.0, 12),
        (-60.0, 11),
        (-360.0, 1),
    ],
)
def test_rashi_number_normalizes_longitude(longitude, expected):
    assert get_rashi_number(longitude) == expected


@pytest.mark.parametrize(
    "rashi_number,expected",
    [
        (1, "Mesha"),
        (2, "Vrishabha"),
        (3, "Mithuna"),
        (4, "Karka"),
        (5, "Simha"),
        (6, "Kanya"),
        (7, "Tula"),
        (8, "Vrishchika"),
        (9, "Dhanu"),
        (10, "Makara"),
        (11, "Kumbha"),
        (12, "Meena"),
    ],
)
def test_rashi_name(rashi_number, expected):
    assert get_rashi_name(rashi_number) == expected


def test_rashi_names_are_complete():
    assert len(RASHI_NAMES) == 12


@pytest.mark.parametrize("invalid_number", [0, 13, -1, 100, True, False])
def test_rashi_name_rejects_invalid_number(invalid_number):
    with pytest.raises(ValueError):
        get_rashi_name(invalid_number)


@pytest.mark.parametrize(
    "invalid_longitude",
    ["120.0", None, True, False],
)
def test_rashi_number_rejects_invalid_longitude(invalid_longitude):
    with pytest.raises(TypeError):
        get_rashi_number(invalid_longitude)


@pytest.mark.parametrize(
    "longitude,expected",
    [
        (0.0, 0.0),
        (360.0, 0.0),
        (720.0, 0.0),
        (-1.0, 359.0),
        (-30.0, 330.0),
        (361.5, 1.5),
    ],
)
def test_normalize_longitude(longitude, expected):
    assert normalize_longitude(longitude) == pytest.approx(expected)


@pytest.mark.parametrize(
    "invalid_longitude",
    ["0.0", None, True, False],
)
def test_normalize_longitude_rejects_invalid_input(invalid_longitude):
    with pytest.raises(TypeError):
        normalize_longitude(invalid_longitude)