import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv(
        "OPENAI_API_KEY"
    )
)


def generate_article(weather):

    prompt = f"""
다음 기상 정보를 이용하여 뉴스 기사를 작성하시오.

도시: {weather['city']}

기온: {weather['temperature']}℃

체감온도: {weather['feels_like']}℃

습도: {weather['humidity']}%

풍속: {weather['wind_speed']}m/s

날씨: {weather['weather']}

조건

- 뉴스 기사 형식
- 제목 포함
- 300자 이내
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response.choices[0].message.content