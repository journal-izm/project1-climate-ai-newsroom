from src.article_service import demo_article
from src.demo_service import load_demo_alerts, load_demo_weather
from src.rule_check_service import rule_check_article


def test_demo_article_passes_rule_check():
    weather = load_demo_weather("Seoul").to_dict()
    alerts = [item.to_dict() for item in load_demo_alerts("Seoul")]
    result = rule_check_article(demo_article(weather, alerts), weather, alerts)
    assert result["status"] == "사실"
    assert all(item["passed"] for item in result["checks"])


def test_wrong_temperature_fails_rule_check():
    weather = load_demo_weather("Seoul").to_dict()
    alerts = [item.to_dict() for item in load_demo_alerts("Seoul")]
    article = demo_article(weather, alerts).replace("29.2℃", "10.0℃")
    result = rule_check_article(article, weather, alerts)
    assert result["status"] == "불일치"
