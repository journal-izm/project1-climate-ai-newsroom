from pathlib import Path

from src.config import Settings
from src.demo_service import load_demo_alerts
from src.weather_service import collect_weather


def test_demo_weather_supports_seven_cities():
    for city in ("Seoul", "Busan", "Daegu", "Incheon", "Gwangju", "Daejeon", "Ulsan"):
        record = collect_weather(city, Settings(app_mode="demo"))
        assert record.city == city
        assert record.mode == "demo"
        assert record.collected_at.endswith("+09:00")


def test_demo_alert_has_source_and_timezone():
    alerts = load_demo_alerts("Seoul")
    assert alerts
    assert alerts[0].source
    assert alerts[0].issued_at.endswith("+09:00")
