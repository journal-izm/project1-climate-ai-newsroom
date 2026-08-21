from __future__ import annotations

from typing import Any

from src.config import Settings


def demo_article(weather: dict[str, Any], alerts: list[dict[str, Any]]) -> str:
    city = weather.get("city_ko", weather.get("city", "해당 지역"))
    alert_text = "현재 확인된 기상특보는 없다."
    if alerts:
        first = alerts[0]
        alert_text = f"{first['region']}에는 {first['alert_type']}가 발표됐다. {first['content']}"
    return (
        f"# {city}, {weather['weather']}…기상특보와 안전정보 확인 필요\n\n"
        f"{city}의 현재 기온은 {weather['temperature']}℃, 체감온도는 {weather['feels_like']}℃다. "
        f"습도는 {weather['humidity']}%, 풍속은 초속 {weather['wind_speed']}m로 관측됐다. "
        f"{alert_text} 시민들은 최신 기상정보와 재난 안내를 계속 확인해야 한다.\n\n"
        f"> 현재 날씨 출처: {weather.get('source', '')} | 수집 시각: {weather.get('collected_at', '')}"
    )


def generate_article(weather: dict[str, Any], alerts: list[dict[str, Any]], evidence: list[dict[str, Any]], settings: Settings | None = None) -> tuple[str, str]:
    settings = settings or Settings()
    if not settings.openai_api_key:
        return demo_article(weather, alerts), "demo"
    from openai import OpenAI
    client = OpenAI(api_key=settings.openai_api_key)
    prompt = f"""다음 관측자료와 공식 근거만 이용해 500자 안팎의 한국어 기상 뉴스 기사를 작성하라.
제목을 포함하고 확인되지 않은 예보나 과장된 표현을 넣지 마라. 기사 끝에 출처와 수집 시각을 표시하라.
[현재 날씨]\n{weather}\n[특보]\n{alerts}\n[검색 근거]\n{evidence}"""
    response = client.chat.completions.create(model=settings.chat_model, messages=[{"role": "system", "content": "너는 출처 중심의 데이터 저널리스트다."}, {"role": "user", "content": prompt}], temperature=0.2)
    return response.choices[0].message.content or "", "openai"


def generate_news_script(article: str, city: str) -> str:
    return (
        f"[앵커]\n{city} 기상 상황을 전해드립니다.\n\n[리포트]\n{article.replace('#', '').strip()}\n\n"
        "[데이터 화면]\n현재 기상 지표와 특보 발효 시각, 출처를 화면에 표시합니다.\n\n"
        "[앵커 클로징]\n기상 상황은 달라질 수 있으므로 기상청의 최신 발표를 확인하시기 바랍니다.\n"
        "[고지]\n이 대본은 AI가 초안을 작성하고 사람이 최종 검수했습니다."
    )
