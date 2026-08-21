from __future__ import annotations

import re
from typing import Any

from src.models import RuleCheckResult


def _contains_number(article: str, value: object, tolerance: float = 0.11) -> bool:
    target = float(value)
    return any(abs(float(item) - target) <= tolerance for item in re.findall(r"-?\d+(?:\.\d+)?", article))


def rule_check_article(article: str, weather: dict[str, Any], alerts: list[dict[str, Any]]) -> dict[str, Any]:
    city_ko = str(weather.get("city_ko", weather.get("city", "")))
    checks = [{"field": "지역", "expected": city_ko, "passed": city_ko in article}]
    for field, label in (("temperature", "기온"), ("feels_like", "체감온도"), ("humidity", "습도"), ("wind_speed", "풍속")):
        checks.append({"field": label, "expected": weather[field], "passed": _contains_number(article, weather[field])})
    for alert in alerts:
        checks.append({"field": "특보", "expected": alert["alert_type"], "passed": str(alert["alert_type"]) in article})
    failed = [check for check in checks if not check["passed"]]
    evidence = [{"content": f"{city_ko} {weather['temperature']}℃, 체감 {weather['feels_like']}℃, 습도 {weather['humidity']}%, 풍속 {weather['wind_speed']}m/s", "source": weather.get("source"), "collected_at": weather.get("collected_at")}] + [{"content": f"{item['region']} {item['alert_type']} {item['content']}", "source": item.get("source"), "collected_at": item.get("issued_at")} for item in alerts]
    return RuleCheckResult(status="사실" if not failed else "불일치", reason="지역·수치·특보가 수집 데이터와 일치합니다." if not failed else "기사에서 일치하지 않거나 누락된 핵심 데이터가 발견됐습니다.", checks=checks, evidence=evidence).to_dict()
