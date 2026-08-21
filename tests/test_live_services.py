from src.config import Settings
from src.kma_service import collect_kma_alerts
from src.weather_service import collect_weather


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_openweather_live_response(monkeypatch):
    payload = {
        "main": {"temp": 28.1, "feels_like": 30.2, "humidity": 77, "pressure": 1008},
        "wind": {"speed": 2.5},
        "weather": [{"description": "흐림"}],
    }
    monkeypatch.setattr("src.weather_service.requests.get", lambda *args, **kwargs: FakeResponse(payload))
    record = collect_weather("Seoul", Settings(app_mode="live", openweather_api_key="test"))
    assert record.mode == "live"
    assert record.temperature == 28.1
    assert record.collected_at.endswith("+09:00")


def test_kma_alert_response(monkeypatch):
    payload = {"response": {"body": {"items": {"item": [{"title": "서울 폭염주의보 발표", "tmFc": "202608201100", "t6": "서울", "t7": "온열질환에 유의"}]}}}}
    monkeypatch.setattr("src.kma_service.requests.get", lambda *args, **kwargs: FakeResponse(payload))
    alerts = collect_kma_alerts("Seoul", Settings(app_mode="live", kma_api_hub_key="test"))
    assert len(alerts) == 1
    assert alerts[0].alert_type == "폭염주의보"
    assert alerts[0].issued_at == "2026-08-20T11:00:00+09:00"
