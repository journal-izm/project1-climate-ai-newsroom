import os

import pandas as pd
import streamlit as st

from src.weather_service import (
    collect_weather,
    save_weather,
)

st.set_page_config(
    page_title="Climate AI Newsroom",
    layout="wide",
)

st.title("🌤 Climate AI Newsroom")

st.caption(
    "실시간 기상 데이터 기반 AI 뉴스룸"
)

# -----------------------------------
# 데이터 수집
# -----------------------------------

st.subheader("실시간 기상 데이터")

city = st.selectbox(
    "지역 선택",
    [
        "Seoul",
        "Busan",
        "Daegu",
        "Incheon",
        "Gwangju",
        "Daejeon",
        "Ulsan",
    ],
)

if st.button(
    "최신 기상 데이터 수집",
    type="primary",
):

    try:

        weather = collect_weather(city)

        save_weather(weather)

        st.success(
            "최신 기상 데이터를 수집했습니다."
        )

        st.rerun()

    except Exception as e:

        st.error(
            f"데이터 수집 오류: {e}"
        )


# -----------------------------------
# 현재 데이터
# -----------------------------------

if os.path.exists(
    "data/weather.csv"
):

    current_df = pd.read_csv(
        "data/weather.csv"
    )

    row = current_df.iloc[0]

    st.divider()

    st.subheader(
        "현재 기상 정보"
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "현재 기온",
        f"{row['temperature']} ℃",
    )

    col2.metric(
        "체감 온도",
        f"{row['feels_like']} ℃",
    )

    col3.metric(
        "습도",
        f"{row['humidity']} %",
    )

    col4.metric(
        "풍속",
        f"{row['wind_speed']} m/s",
    )

    st.info(
        f"{row['city']} 현재 날씨: "
        f"{row['weather']}"
    )

else:

    st.warning(
        "아직 수집된 기상 데이터가 없습니다."
    )


# -----------------------------------
# 수집 이력
# -----------------------------------

if os.path.exists(
    "data/weather_history.csv"
):

    st.divider()

    st.subheader(
        "기상 데이터 변화"
    )

    history_df = pd.read_csv(
        "data/weather_history.csv"
    )

    history_df["collected_at"] = pd.to_datetime(
        history_df["collected_at"]
    )

    history_df = history_df.sort_values(
        "collected_at"
    )

    chart_df = history_df.set_index(
        "collected_at"
    )[
        [
            "temperature",
            "feels_like",
        ]
    ]

    st.line_chart(
        chart_df
    )

    st.subheader(
        "수집 이력"
    )

    st.dataframe(
        history_df.sort_values(
            "collected_at",
            ascending=False,
        ),
        use_container_width=True,
    )