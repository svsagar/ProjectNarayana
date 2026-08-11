"""Time resolution for the Narayana Astronomy Engine."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class ResolvedTime:
    """Resolved civil birth time retained for astronomical calculations."""

    local_datetime: datetime
    timezone_name: str
    utc_datetime: datetime


def resolve_local_time(
    local_datetime: datetime,
    timezone_name: str,
) -> ResolvedTime:
    """Resolve a local civil datetime into UTC using IANA timezone rules."""

    if local_datetime.tzinfo is not None:
        raise ValueError("local_datetime must be timezone-naive")

    zone = ZoneInfo(timezone_name)
    localized = local_datetime.replace(tzinfo=zone)
    utc_datetime = localized.astimezone(timezone.utc)

    return ResolvedTime(
        local_datetime=localized,
        timezone_name=timezone_name,
        utc_datetime=utc_datetime,
    )
