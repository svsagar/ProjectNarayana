"""Tests for planetary classification."""

import pytest

from src.narayana.astronomy.models import CelestialPosition
from src.narayana.astronomy.planetary import (
    classify_planetary_position,
    get_nakshatra_number,
    get_nakshatra_pada,
    is_retrograde,
)


@pytest.mark.parametrize(
    "longitude,expected",
    [
        (0.0, 1),
        (13.333333333333334, 2),
        (26.666666666666668, 3),
        (359.999999, 27),
    ],
)
def test_nakshatra_number(longitude, expected):
    assert get_nakshatra_number(longitude) == expected


def test_nakshatra_number_wraps_longitude():
    assert get_nakshatra_number(360.0) == 1
    assert get_nakshatra_number(-0.001) == 27


@pytest.mark.parametrize(
    "longitude,expected",
    [
        (0.0, 1),
        (3.333333333333334, 2),
        (6.666666666666667, 3),
        (9.999999, 3),
        (10.0000001, 4),
        (13.333333333333334, 1),
    ],
)
def test_nakshatra_pada(longitude, expected):
    assert get_nakshatra_pada(longitude) == expected


def test_retrograde():
    position = CelestialPosition(
        body="Saturn",
        longitude=250.0,
        latitude=0.0,
        distance=9.0,
        speed_longitude=-0.05,
    )

    assert is_retrograde(position) is True


def test_direct_motion():
    position = CelestialPosition(
        body="Jupiter",
        longitude=250.0,
        latitude=0.0,
        distance=5.0,
        speed_longitude=0.08,
    )

    assert is_retrograde(position) is False


def test_classify_planetary_position():
    position = CelestialPosition(
        body="Saturn",
        longitude=285.5,
        latitude=0.0,
        distance=9.0,
        speed_longitude=-0.05,
    )

    result = classify_planetary_position(position)

    assert result.body == "Saturn"
    assert result.longitude == 285.5

    assert result.zodiac.sign_number == 10
    assert result.zodiac.sign_name == "Makara"
    assert result.zodiac.degrees_in_sign == pytest.approx(15.5)

    assert result.nakshatra == 22
    assert result.nakshatra_pada == 2
    assert result.retrograde is True