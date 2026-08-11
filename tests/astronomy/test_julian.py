"""Tests for Astronomy Engine Julian Day conversion."""

from datetime import datetime, timezone

import pytest

from src.narayana.astronomy.julian import utc_to_julian_day


def test_kottayam_validation_julian_day():
    utc_datetime = datetime(
        1978,
        8,
        17,
        4,
        40,
        tzinfo=timezone.utc,
    )

    result = utc_to_julian_day(utc_datetime)

    assert result == pytest.approx(2443737.6944444445)


def test_naive_datetime_is_rejected():
    with pytest.raises(ValueError):
        utc_to_julian_day(datetime(1978, 8, 17, 4, 40))
