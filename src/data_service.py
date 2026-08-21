from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from src.config import PROCESSED_DIR, ensure_runtime_dirs
from src.models import AlertRecord, WeatherRecord
from src.time_utils import to_seoul_datetime

WEATHER_CURRENT = PROCESSED_DIR / "weather_current.csv"
WEATHER_HISTORY = PROCESSED_DIR / "weather_history.csv"
ALERT_HISTORY = PROCESSED_DIR / "weather_alerts.csv"
ARTICLE_STORE = PROCESSED_DIR / "articles.json"


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig") if path.exists() else pd.DataFrame()


def _normalize_time(df: pd.DataFrame, column: str) -> pd.DataFrame:
    if df.empty or column not in df.columns:
        return df
    result = df.copy()
    result[column] = result[column].map(lambda value: to_seoul_datetime(value).isoformat(timespec="seconds"))
    return result


def save_weather(record: WeatherRecord) -> pd.DataFrame:
    ensure_runtime_dirs()
    new_df = pd.DataFrame([record.to_dict()])
    new_df.to_csv(WEATHER_CURRENT, index=False, encoding="utf-8-sig")
    history = pd.concat([_read_csv(WEATHER_HISTORY), new_df], ignore_index=True)
    history = _normalize_time(history, "collected_at")
    history = history.drop_duplicates(
        subset=["collected_at", "city", "temperature", "weather"], keep="last"
    ).sort_values("collected_at", ascending=True)
    history.to_csv(WEATHER_HISTORY, index=False, encoding="utf-8-sig")
    return history


def save_alerts(records: Iterable[AlertRecord]) -> pd.DataFrame:
    ensure_runtime_dirs()
    rows = [record.to_dict() for record in records]
    if not rows:
        return _read_csv(ALERT_HISTORY)
    history = pd.concat([_read_csv(ALERT_HISTORY), pd.DataFrame(rows)], ignore_index=True)
    for column in ("collected_at", "issued_at", "effective_at"):
        history = _normalize_time(history, column)
    history = history.drop_duplicates(
        subset=["region", "alert_type", "issued_at", "content"], keep="last"
    ).sort_values("issued_at", ascending=True)
    history.to_csv(ALERT_HISTORY, index=False, encoding="utf-8-sig")
    return history


def load_weather_history(descending: bool = True) -> pd.DataFrame:
    df = _normalize_time(_read_csv(WEATHER_HISTORY), "collected_at")
    return df.sort_values("collected_at", ascending=not descending).reset_index(drop=True) if not df.empty else df


def load_alert_history(descending: bool = True) -> pd.DataFrame:
    df = _normalize_time(_read_csv(ALERT_HISTORY), "issued_at")
    return df.sort_values("issued_at", ascending=not descending).reset_index(drop=True) if not df.empty else df


def get_latest_weather(city: str) -> dict[str, Any] | None:
    df = load_weather_history(descending=True)
    if df.empty:
        return None
    selected = df[df["city"].astype(str).str.casefold() == city.casefold()]
    return None if selected.empty else selected.iloc[0].to_dict()


def load_articles() -> list[dict[str, Any]]:
    if not ARTICLE_STORE.exists():
        return []
    return json.loads(ARTICLE_STORE.read_text(encoding="utf-8"))


def save_article_record(record: dict[str, Any]) -> dict[str, Any]:
    ensure_runtime_dirs()
    records = load_articles()
    records = [item for item in records if item.get("id") != record.get("id")]
    records.append(record)
    ARTICLE_STORE.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    return record
