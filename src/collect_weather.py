import os
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")

CITY = "Seoul"

URL = "https://api.openweathermap.org/data/2.5/weather"

params = {
    "q": CITY,
    "appid": API_KEY,
    "units": "metric",
    "lang": "kr",
}

response = requests.get(
    URL,
    params=params,
    timeout=10,
)

print("상태 코드:", response.status_code)

if response.status_code != 200:
    print("API 호출 실패")
    print(response.json())
    raise SystemExit

data = response.json()

weather = {
    "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "city": data["name"],
    "temperature": data["main"]["temp"],
    "feels_like": data["main"]["feels_like"],
    "humidity": data["main"]["humidity"],
    "pressure": data["main"]["pressure"],
    "wind_speed": data["wind"]["speed"],
    "weather": data["weather"][0]["description"],
}

new_df = pd.DataFrame([weather])

os.makedirs("data", exist_ok=True)

current_path = "data/weather.csv"
history_path = "data/weather_history.csv"

# 최신 데이터 1건 저장
new_df.to_csv(
    current_path,
    index=False,
    encoding="utf-8-sig",
)

# 이력 데이터 누적 저장
if os.path.exists(history_path):
    history_df = pd.read_csv(history_path)

    history_df = pd.concat(
        [history_df, new_df],
        ignore_index=True,
    )
else:
    history_df = new_df

history_df.to_csv(
    history_path,
    index=False,
    encoding="utf-8-sig",
)

print("\n현재 수집 데이터")
print(new_df)

print(
    f"\nweather_history.csv 누적 건수: {len(history_df)}"
)