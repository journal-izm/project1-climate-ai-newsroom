import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Climate AI Newsroom",
    layout="wide"
)

st.title("🌤 Climate AI Newsroom")

df = pd.read_csv("data/weather.csv")

row = df.iloc[0]

st.subheader("현재 기상 정보")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "현재 기온",
    f"{row['temperature']} ℃"
)

col2.metric(
    "체감 온도",
    f"{row['feels_like']} ℃"
)

col3.metric(
    "습도",
    f"{row['humidity']} %"
)

col4.metric(
    "풍속",
    f"{row['wind_speed']} m/s"
)

st.divider()

st.subheader("기상 상태")

st.write(
    f"현재 {row['city']}의 날씨는 **{row['weather']}** 입니다."
)