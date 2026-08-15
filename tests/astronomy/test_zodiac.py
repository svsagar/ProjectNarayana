"""Tests for zodiac / Rāśi classification."""

import pytest

from src.narayana.astronomy.zodiac import (
    classify_zodiac,
    get_degrees_in_sign,
    get_zodiac_sign_name,
    get_zodiac_sign_number,
    normalize_longitude,
)


def test_normalize_longitude():
    assert normalize_longitude(0.0) == 0.0
    assert normalize_longitude(360.0) == 0.0
    assert normalize_longitude(720.0) == 0.0
    assert normalize_longitude(-1.0) == pytest.approx(359.0)


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
def test_zodiac_sign_number(longitude, expected):
    assert get_zodiac_sign_number(longitude) == expected


def test_zodiac_sign_number_wraps_longitude():
    assert get_zodiac_sign_number(360.0) == 1
    assert get_zodiac_sign_number(-0.1) == 12


@pytest.mark.parametrize(
    "sign_number,expected",
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
def test_zodiac_sign_name(sign_number, expected):
    assert get_zodiac_sign_name(sign_number) == expected


@pytest.mark.parametrize("invalid", [0, 13, -1])
def test_zodiac_sign_name_rejects_invalid_number(invalid):
    with pytest.raises(ValueError):
        get_zodiac_sign_name(invalid)


@pytest.mark.parametrize(
    "longitude,expected",
    [
        (0.0, 0.0),
        (29.5, 29.5),
        (30.0, 0.0),
        (45.25, 15.25),
        (120.0, 0.0),
        (359.5, 29.5),
    ],
)
def test_degrees_in_sign(longitude, expected):
    assert get_degrees_in_sign(longitude) == pytest.approx(expected)


def test_classify_zodiac():
    result = classify_zodiac(285.5)

    assert result.sign_number == 10
    assert result.sign_name == "Makara"
    assert result.degrees_in_sign == pytest.approx(15.5)


@pytest.mark.parametrize("invalid", ["120.0", None, True, False])
def test_longitude_rejects_invalid_type(invalid):
    with pytest.raises(TypeError):
        normalize_longitude(invalid)