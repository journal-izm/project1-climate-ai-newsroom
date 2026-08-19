import os

from src.rag_service import get_latest_weather


def fact_check_article(
    article: str,
    city: str,
):

    row = get_latest_weather(city)

    if row is None:
        return []

    content = f"""
수집 시각: {row['collected_at']}
도시: {city}
현재 기온: {row['temperature']}℃
체감 온도: {row['feels_like']}℃
습도: {row['humidity']}%
기압: {row['pressure']} hPa
풍속: {row['wind_speed']} m/s
날씨 상태: {row['weather']}
""".strip()

    evidence = [
        {
            "content": content,
            "metadata": {
                "source": "OpenWeather API",
                "city": city,
                "collected_at": str(
                    row["collected_at"]
                ),
            },
        }
    ]

    return evidence


def save_fact_check(
    article,
    evidence,
    path="reports/fact_check_report.md",
):

    os.makedirs(
        "reports",
        exist_ok=True,
    )

    lines = [
        "# RAG 기반 팩트체크 보고서\n",
        "## 검증 대상 기사\n",
        article,
        "\n## 검색 근거\n",
    ]

    for i, item in enumerate(
        evidence,
        start=1,
    ):

        lines.append(
            f"\n### 근거 {i}\n"
        )

        lines.append(
            item["content"]
        )

        lines.append(
            "\n출처: "
            + str(item["metadata"])
        )

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as f:

        f.write(
            "\n".join(lines)
        )