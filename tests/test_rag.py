from src.data_service import save_alerts, save_weather
from src.demo_service import load_demo_alerts, load_demo_weather
from src.rag_service import search_weather


def test_rag_returns_alert_or_guideline():
    save_weather(load_demo_weather("Seoul"))
    save_alerts(load_demo_alerts("Seoul"))
    results = search_weather("서울 폭염주의보 대응요령", city="서울", k=5)
    assert results
    text = " ".join(item["content"] for item in results)
    assert "폭염" in text
