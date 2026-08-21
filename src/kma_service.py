from __future__ import annotations

from datetime import timedelta
from typing import Any

import requests

from src.config import SUPPORTED_CITIES, Settings
from src.models import AlertRecord
from src.time_utils import compact_kma_time, iso_seoul, now_seoul


def _items_from_response(payload: dict[str, Any]) -> list[dict[str, Any]]:
    body = payload.get("response", {}).get("body", {})
    items = body.get("items", {})
    if isinstance(items, dict):
        items = items.get("item", [])
    if isinstance(items, dict):
        return [items]
    return items if isinstance(items, list) else []


def _first(item: dict[str, Any], *keys: str, default: str = "") -> str:
    for key in keys:
        value = item.get(key)
        if value not in (None, ""):
            return str(value)
    return default


def _classify_alert(text: str) -> tuple[str, str]:
    types = ("폭염", "호우", "강풍", "풍랑", "대설", "한파", "태풍", "건조", "황사")
    alert_type = next((name for name in types if name in text), "기상특보")
    level = "경보" if "경보" in text else "주의보" if "주의보" in text else "정보"
    return f"{alert_type}{level}" if alert_type != "기상특보" and level != "정보" else alert_type, level


def collect_kma_alerts(city: str, settings: Settings | None = None) -> list[AlertRecord]:
    settings = settings or Settings()
    if not settings.kma_service_key:
        raise ValueError("KMA_SERVICE_KEY가 설정되지 않았습니다.")
    if city not in SUPPORTED_CITIES:
        raise ValueError(f"지원하지 않는 지역입니다: {city}")

    end = now_seoul()
    start = end - timedelta(days=2)
    params = {
        "serviceKey": settings.kma_service_key,
        "pageNo": 1,
        "numOfRows": 100,
        "dataType": "JSON",
        "fromTmFc": compact_kma_time(start),
        "toTmFc": compact_kma_time(end),
        "stnId": "108",
    }
    response = requests.get(settings.kma_alert_api_url, params=params, timeout=15)
    response.raise_for_status()
    items = _items_from_response(response.json())
    region_name = SUPPORTED_CITIES[city]
    results: list[AlertRecord] = []
    for item in items:
        region = _first(item, "t6", "regName", "areaName", "stnName", default="전국")
        content = _first(item, "t7", "wrnCont", "content", "title")
        if region_name not in f"{region} {content}" and "전국" not in f"{region} {content}":
            continue
        issued = _first(item, "tmFc", "issuedAt", default=iso_seoul())
        effective = _first(item, "tmEf", "effectiveAt", default=issued)
        title = _first(item, "title")
        classified_type, classified_level = _classify_alert(f"{title} {content}")
        results.append(
            AlertRecord(
                collected_at=iso_seoul(),
                region=region,
                alert_type=_first(item, "t1", "wrnType", "alertType", default=classified_type),
                level=_first(item, "t2", "wrnLevel", "level", default=classified_level),
                issued_at=iso_seoul(issued),
                effective_at=iso_seoul(effective),
                content=content or title or "기상청 특보가 발표되었습니다.",
                mode="live",
                source_url=settings.kma_alert_api_url,
            )
        )
    return results
