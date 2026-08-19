import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")

CITY = "Seoul"

URL = "https://api.openweathermap.org/data/2.5/weather"

params = {
    "q": CITY,
    "appid": API_KEY,
    "units": "metric",
    "lang": "kr"
}

response = requests.get(
    URL,
    params=params,
    timeout=10
)

print("상태 코드:", response.status_code)
# print(response.json())

if response.status_code != 200:
    print("API 호출 실패")
    print(response.json())
    raise SystemExit

data = response.json()

weather = {
    "city": data["name"],
    "temperature": data["main"]["temp"],
    "feels_like": data["main"]["feels_like"],
    "humidity": data["main"]["humidity"],
    "pressure": data["main"]["pressure"],
    "wind_speed": data["wind"]["speed"],
    "weather": data["weather"][0]["description"],
}

df = pd.DataFrame([weather])

print("\n수집 결과")
print(df)

os.makedirs("data", exist_ok=True)

df.to_csv(
    "data/weather.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\ndata/weather.csv 저장 완료")