import os
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")

URL = "https://api.openweathermap.org/data/2.5/weather"


def collect_weather(city="Seoul"):
    if not API_KEY:
        raise ValueError(
            "OPENWEATHER_API_KEY가 설정되지 않았습니다."
        )

    params = {
        "q": city,
        "appid": API_KEY,
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

    weather = {
        "collected_at": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "city": data["name"],
        "temperature": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],
        "wind_speed": data["wind"]["speed"],
        "weather": data["weather"][0]["description"],
    }

    return weather


def save_weather(weather):
    os.makedirs(
        "data",
        exist_ok=True,
    )

    new_df = pd.DataFrame(
        [weather]
    )

    current_path = "data/weather.csv"
    history_path = "data/weather_history.csv"

    # 최신 데이터 저장
    new_df.to_csv(
        current_path,
        index=False,
        encoding="utf-8-sig",
    )

    # 이력 데이터 누적
    if os.path.exists(history_path):

        history_df = pd.read_csv(
            history_path
        )

        history_df = pd.concat(
            [
                history_df,
                new_df,
            ],
            ignore_index=True,
        )

    else:

        history_df = new_df

    history_df.to_csv(
        history_path,
        index=False,
        encoding="utf-8-sig",
    )

    return history_df