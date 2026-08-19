import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from src.rag_service import get_latest_weather

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def fact_check_article(
    article: str,
    city: str,
):
    """
    AI 기사와 최신 실제 기상 데이터를 비교하여
    사실 / 불일치 / 근거 부족으로 판정한다.
    """

    row = get_latest_weather(city)

    if row is None:
        return {
            "status": "근거 부족",
            "reason": f"{city}의 최신 관측 데이터가 없습니다.",
            "mismatches": [],
            "evidence": None,
        }

    evidence_text = f"""
수집 시각: {row['collected_at']}
도시: {city}
현재 기온: {row['temperature']}℃
체감 온도: {row['feels_like']}℃
습도: {row['humidity']}%
기압: {row['pressure']} hPa
풍속: {row['wind_speed']} m/s
날씨 상태: {row['weather']}
""".strip()

    prompt = f"""
너는 데이터 저널리즘 팩트체커다.

아래 AI 생성 기사와 실제 기상 관측 데이터를 비교하여
기사에 포함된 사실 주장이 실제 데이터와 일치하는지 판정하라.

[AI 생성 기사]
{article}

[실제 기상 관측 데이터]
{evidence_text}

판정 기준은 다음과 같다.

1. 사실
- 기사에 포함된 수치 및 날씨 상태가 실제 데이터와 일치함

2. 불일치
- 기사에 실제 데이터와 다른 수치 또는 사실이 포함됨

3. 근거 부족
- 기사에 언급된 내용이 제공된 실제 데이터만으로 검증할 수 없음

중요 규칙:
- 기사에 실제 데이터에 없는 예보, 건강 조언, 미래 전망 등이 있으면
  해당 내용은 근거 부족으로 판단할 수 있다.
- 숫자가 실제 값과 다르면 불일치로 판정한다.
- 전체 기사 판정은 가장 중요한 오류를 기준으로 판단한다.

반드시 아래 JSON 형식으로만 응답하라.

{{
  "status": "사실 | 불일치 | 근거 부족",
  "reason": "전체 판정 이유",
  "mismatches": [
    {{
      "claim": "기사의 주장",
      "evidence": "실제 관측 데이터",
      "explanation": "판정 설명"
    }}
  ]
}}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "너는 사실 검증만 수행하는 데이터 저널리즘 팩트체커다.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        response_format={
            "type": "json_object"
        },
        temperature=0,
    )

    result = json.loads(
        response.choices[0].message.content
    )

    result["evidence"] = {
        "content": evidence_text,
        "metadata": {
            "source": "OpenWeather API",
            "city": city,
            "collected_at": str(row["collected_at"]),
        },
    }

    return result