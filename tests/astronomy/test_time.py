"""Tests for Astronomy Engine time resolution."""

from datetime import datetime, timezone

import pytest

from src.narayana.astronomy.time import ResolvedTime, resolve_local_time


def test_resolve_historical_kottayam_time():
    result = resolve_local_time(
        datetime(1978, 8, 17, 10, 10),
        "Asia/Kolkata",
    )

    assert isinstance(result, ResolvedTime)
    assert result.local_datetime.isoformat() == "1978-08-17T10:10:00+05:30"
    assert result.timezone_name == "Asia/Kolkata"
    assert result.utc_datetime.isoformat() == "1978-08-17T04:40:00+00:00"


def test_utc_datetime_is_timezone_aware():
    result = resolve_local_time(
        datetime(1978, 8, 17, 10, 10),
        "Asia/Kolkata",
    )

    assert result.utc_datetime.tzinfo == timezone.utc


def test_local_datetime_must_be_naive():
    aware_datetime = datetime(
        1978,
        8,
        17,
        10,
        10,
        tzinfo=timezone.utc,
    )

    with pytest.raises(ValueError):
        resolve_local_time(aware_datetime, "Asia/Kolkata")
