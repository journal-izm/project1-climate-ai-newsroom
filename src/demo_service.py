from __future__ import annotations

import pandas as pd

from src.config import SAMPLE_DIR, SUPPORTED_CITIES
from src.models import AlertRecord, WeatherRecord
from src.time_utils import iso_seoul


def load_demo_weather(city: str) -> WeatherRecord:
    df = pd.read_csv(SAMPLE_DIR / "current_weather.csv", encoding="utf-8-sig")
    selected = df[df["city"].astype(str).str.casefold() == city.casefold()]
    if selected.empty:
        raise ValueError(f"지원하지 않는 데모 지역입니다: {city}")
    row = selected.iloc[0]
    return WeatherRecord(
        collected_at=iso_seoul(),
        city=city,
        city_ko=SUPPORTED_CITIES[city],
        temperature=float(row["temperature"]),
        feels_like=float(row["feels_like"]),
        humidity=int(row["humidity"]),
        pressure=int(row["pressure"]),
        wind_speed=float(row["wind_speed"]),
        weather=str(row["weather"]),
        source="교육용 샘플 데이터",
        source_url="data/sample/current_weather.csv",
        mode="demo",
    )


def load_demo_alerts(city: str) -> list[AlertRecord]:
    df = pd.read_csv(SAMPLE_DIR / "weather_alerts.csv", encoding="utf-8-sig")
    city_ko = SUPPORTED_CITIES[city]
    selected = df[df["region"].astype(str).str.contains(city_ko, regex=False)]
    return [
        AlertRecord(
            collected_at=iso_seoul(),
            region=str(row["region"]),
            alert_type=str(row["alert_type"]),
            level=str(row["level"]),
            issued_at=iso_seoul(row["issued_at"]),
            effective_at=iso_seoul(row["effective_at"]),
            content=str(row["content"]),
            mode="demo",
            source="교육용 기상특보 샘플",
            source_url="data/sample/weather_alerts.csv",
        )
        for _, row in selected.iterrows()
    ]
