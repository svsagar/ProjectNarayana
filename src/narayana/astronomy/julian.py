"""Julian Day conversion for the Narayana Astronomy Engine."""

from __future__ import annotations

from datetime import datetime, timezone

import swisseph as swe


def utc_to_julian_day(utc_datetime: datetime) -> float:
    """Convert a timezone-aware UTC datetime to Julian Day UT."""

    if utc_datetime.tzinfo is None:
        raise ValueError("utc_datetime must be timezone-aware")

    utc_datetime = utc_datetime.astimezone(timezone.utc)

    hour = (
        utc_datetime.hour
        + utc_datetime.minute / 60.0
        + utc_datetime.second / 3600.0
        + utc_datetime.microsecond / 3_600_000_000.0
    )

    return swe.julday(
        utc_datetime.year,
        utc_datetime.month,
        utc_datetime.day,
        hour,
        swe.GREG_CAL,
    )

