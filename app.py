import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Climate AI Newsroom",
    layout="wide",
)

st.title("🌤 Climate AI Newsroom")

current_df = pd.read_csv("data/weather.csv")
row = current_df.iloc[0]

st.subheader("현재 기상 정보")

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

st.write(
    f"현재 {row['city']}의 날씨는 "
    f"**{row['weather']}** 입니다."
)

st.divider()

st.subheader("기상 데이터 변화")

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

st.line_chart(chart_df)

st.subheader("수집 데이터")

st.dataframe(
    history_df.sort_values(
        "collected_at",
        ascending=False,
    ),
    use_container_width=True,
)