from src.time_utils import iso_seoul, to_seoul_datetime


def test_naive_time_is_localized_to_seoul():
    value = iso_seoul("2026-08-21 09:30:00")
    assert value == "2026-08-21T09:30:00+09:00"


def test_utc_time_is_converted_to_seoul():
    converted = to_seoul_datetime("2026-08-21T00:30:00+00:00")
    assert converted.hour == 9
    assert str(converted.tzinfo) == "Asia/Seoul"
