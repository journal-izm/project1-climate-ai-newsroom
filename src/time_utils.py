from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd

SEOUL_TZ = ZoneInfo("Asia/Seoul")


def now_seoul() -> datetime:
    return datetime.now(SEOUL_TZ)


def to_seoul_datetime(value: object) -> datetime:
    parsed = pd.to_datetime(value, errors="raise")
    if parsed.tzinfo is None:
        parsed = parsed.tz_localize(SEOUL_TZ)
    else:
        parsed = parsed.tz_convert(SEOUL_TZ)
    return parsed.to_pydatetime()


def iso_seoul(value: object | None = None) -> str:
    dt = now_seoul() if value is None else to_seoul_datetime(value)
    return dt.isoformat(timespec="seconds")


def compact_kma_time(value: object | None = None) -> str:
    dt = now_seoul() if value is None else to_seoul_datetime(value)
    return dt.strftime("%Y%m%d%H%M")
