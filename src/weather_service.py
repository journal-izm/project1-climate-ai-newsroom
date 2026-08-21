import requests
from src.config import SUPPORTED_CITIES, Settings
from src.demo_service import load_demo_weather
from src.models import WeatherRecord
from src.time_utils import iso_seoul

URL = "https://api.openweathermap.org/data/2.5/weather"


def collect_weather(city: str = "Seoul", settings: Settings | None = None) -> WeatherRecord:
    settings = settings or Settings()
    if city not in SUPPORTED_CITIES:
        raise ValueError(f"지원하지 않는 지역입니다: {city}")
    if settings.demo_mode or not settings.openweather_api_key:
        return load_demo_weather(city)

    params = {
        "q": city,
        "appid": settings.openweather_api_key,
        "units": "metric",
        "lang": "kr",
    }

    response = requests.get(
        URL,
        params=params,
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()

    return WeatherRecord(
        collected_at=iso_seoul(),
        city=city,
        city_ko=SUPPORTED_CITIES[city],
        temperature=float(data["main"]["temp"]),
        feels_like=float(data["main"]["feels_like"]),
        humidity=int(data["main"]["humidity"]),
        pressure=int(data["main"]["pressure"]),
        wind_speed=float(data["wind"]["speed"]),
        weather=str(data["weather"][0]["description"]),
        source="OpenWeather API",
        source_url=URL,
        mode="live",
    )
