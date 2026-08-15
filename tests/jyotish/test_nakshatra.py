"""Tests for Nakshatra classification in the Project Narayana Jyotish layer."""

import pytest

from src.narayana.jyotish.nakshatra import (
    NAKSHATRA_NAMES,
    get_nakshatra_name,
    get_nakshatra_number,
    get_nakshatra_pada,
    normalize_longitude,
)


@pytest.mark.parametrize(
    "longitude,expected",
    [
        (0.0, 1),
        (13.333333333333334, 2),
        (26.666666666666668, 3),
        (39.99999, 3),
        (40.0, 4),
        (53.333333333333336, 5),
        (66.66666666666667, 6),
        (80.0, 7),
        (93.33333333333333, 8),
        (106.66666666666667, 9),
        (120.0, 10),
        (133.33333333333334, 11),
        (146.66666666666666, 12),
        (160.0, 13),
        (173.33333333333334, 14),
        (186.66666666666666, 15),
        (200.0, 16),
        (213.33333333333334, 17),
        (226.66666666666666, 18),
        (240.0, 19),
        (253.33333333333334, 20),
        (266.6666666666667, 21),
        (280.0, 22),
        (293.3333333333333, 23),
        (306.6666666666667, 24),
        (320.0, 25),
        (333.3333333333333, 26),
        (346.6666666666667, 27),
        (359.999999, 27),
    ],
)
def test_nakshatra_number(longitude, expected):
    assert get_nakshatra_number(longitude) == expected


@pytest.mark.parametrize(
    "longitude,expected",
    [
        (360.0, 1),
        (720.0, 1),
        (-0.000001, 27),
        (-13.333333333333334, 27),
        (-360.0, 1),
    ],
)
def test_nakshatra_number_wraps_longitude(longitude, expected):
    assert get_nakshatra_number(longitude) == expected


@pytest.mark.parametrize(
    "longitude,expected",
    [
        (0.0, 1),
        (3.3333333333333335, 2),
        (6.666666666666667, 3),
        (10.0, 4),
        (13.333333333333334, 1),
        (16.666666666666668, 2),
        (20.0, 3),
        (23.333333333333332, 4),
    ],
)
def test_nakshatra_pada(longitude, expected):
    assert get_nakshatra_pada(longitude) == expected


@pytest.mark.parametrize(
    "nakshatra_number,expected",
    [
        (1, "Ashwini"),
        (2, "Bharani"),
        (3, "Krittika"),
        (4, "Rohini"),
        (5, "Mrigashira"),
        (6, "Ardra"),
        (7, "Punarvasu"),
        (8, "Pushya"),
        (9, "Ashlesha"),
        (10, "Magha"),
        (11, "Purva Phalguni"),
        (12, "Uttara Phalguni"),
        (13, "Hasta"),
        (14, "Chitra"),
        (15, "Swati"),
        (16, "Vishakha"),
        (17, "Anuradha"),
        (18, "Jyeshtha"),
        (19, "Mula"),
        (20, "Purva Ashadha"),
        (21, "Uttara Ashadha"),
        (22, "Shravana"),
        (23, "Dhanishtha"),
        (24, "Shatabhisha"),
        (25, "Purva Bhadrapada"),
        (26, "Uttara Bhadrapada"),
        (27, "Revati"),
    ],
)
def test_nakshatra_name(nakshatra_number, expected):
    assert get_nakshatra_name(nakshatra_number) == expected


def test_nakshatra_names_are_complete():
    assert len(NAKSHATRA_NAMES) == 27


@pytest.mark.parametrize(
    "invalid_number",
    [0, 28, -1, 100, True, False],
)
def test_nakshatra_name_rejects_invalid_number(invalid_number):
    with pytest.raises(ValueError):
        get_nakshatra_name(invalid_number)


@pytest.mark.parametrize(
    "invalid_longitude",
    ["120.0", None, True, False],
)
def test_nakshatra_number_rejects_invalid_longitude(invalid_longitude):
    with pytest.raises(TypeError):
        get_nakshatra_number(invalid_longitude)


@pytest.mark.parametrize(
    "invalid_longitude",
    ["120.0", None, True, False],
)
def test_nakshatra_pada_rejects_invalid_longitude(invalid_longitude):
    with pytest.raises(TypeError):
        get_nakshatra_pada(invalid_longitude)


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
    ["120.0", None, True, False],
)
def test_normalize_longitude_rejects_invalid_input(invalid_longitude):
    with pytest.raises(TypeError):
        normalize_longitude(invalid_longitude)