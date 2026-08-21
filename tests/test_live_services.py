from src.config import Settings
from src.kma_service import collect_kma_alerts
from src.weather_service import collect_weather


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload
        self.content = payload.encode("utf-8") if isinstance(payload, str) else b""

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
    payload = """#START7777
# REG_UP REG_UP_KO REG_ID REG_KO TM_FC TM_EF WRN LVL CMD
L1010000 서울특별시 L1010100 서울동북권 202608201100 202608201200 H 2 1
#7777END
"""
    monkeypatch.setattr("src.kma_service.requests.get", lambda *args, **kwargs: FakeResponse(payload))
    alerts = collect_kma_alerts("Seoul", Settings(app_mode="live", kma_api_hub_key="test"))
    assert len(alerts) == 1
    assert alerts[0].alert_type == "폭염주의보"
    assert alerts[0].issued_at == "2026-08-20T11:00:00+09:00"


def test_kma_alert_filters_other_city_and_released_alert(monkeypatch):
    payload = """#START7777
L1010000 서울특별시 L1010100 서울동북권 202608201100 202608201200 H 2 3
L1020000 부산광역시 L1020100 부산광역시 202608201300 202608201400 R 3 1
#7777END
"""
    monkeypatch.setattr("src.kma_service.requests.get", lambda *args, **kwargs: FakeResponse(payload))
    settings = Settings(app_mode="live", kma_api_hub_key="test")
    assert collect_kma_alerts("Seoul", settings) == []
    alerts = collect_kma_alerts("Busan", settings)
    assert len(alerts) == 1
    assert alerts[0].alert_type == "호우경보"


def test_kma_no_active_alert_is_valid_empty_result(monkeypatch):
    payload = """#START7777
# REG_UP REG_UP_KO REG_ID REG_KO TM_FC TM_EF WRN LVL CMD
#7777END
"""
    monkeypatch.setattr("src.kma_service.requests.get", lambda *args, **kwargs: FakeResponse(payload))
    settings = Settings(app_mode="live", kma_api_hub_key="test")
    assert collect_kma_alerts("Seoul", settings) == []


def test_kma_alerts_are_sorted_by_issued_time_descending(monkeypatch):
    payload = """#START7777
L1010000 서울특별시 L1010100 서울동북권 202608201100 202608201200 H 2 1
L1010000 서울특별시 L1010200 서울서북권 202608201300 202608201400 R 3 1
#7777END
"""
    monkeypatch.setattr("src.kma_service.requests.get", lambda *args, **kwargs: FakeResponse(payload))
    settings = Settings(app_mode="live", kma_api_hub_key="test")
    alerts = collect_kma_alerts("Seoul", settings)
    assert [item.alert_type for item in alerts] == ["호우경보", "폭염주의보"]
