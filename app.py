import os

import pandas as pd
import streamlit as st

from src.weather_service import (
    collect_weather,
    save_weather,
)
from src.article_service import (
    generate_article,
)
from src.rag_service import (
    build_vector_db,
)
from src.factcheck_service import (
    fact_check_article,
    save_fact_check,
)

st.set_page_config(
    page_title="Climate AI Newsroom",
    layout="wide",
)

# -----------------------------------
# Session State 초기화
# -----------------------------------
if "article" not in st.session_state:
    st.session_state.article = None

if "factcheck_evidence" not in st.session_state:
    st.session_state.factcheck_evidence = None

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

        # 최신 history 기준으로 Vector DB 재생성
        build_vector_db()

        # st.session_state.factcheck_result = None  # LLM 판정 결과 초기화
        st.session_state.factcheck_evidence = None

        st.success(
            "최신 기상 데이터를 수집하고 "
            "Vector DB를 갱신했습니다."
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

    # 문자열 → datetime 변환
    history_df["collected_at"] = pd.to_datetime(
        history_df["collected_at"],
        errors="coerce",
    )

    # -----------------------------------
    # 그래프용: 오래된 순 → 최신순
    # -----------------------------------
    chart_history_df = (
        history_df
        .sort_values(
            "collected_at",
            ascending=True,
        )
        .copy()
    )

    chart_df = chart_history_df.set_index(
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

    # -----------------------------------
    # 표 출력용: 최신순 → 오래된 순
    # -----------------------------------
    table_history_df = (
        history_df
        .sort_values(
            "collected_at",
            ascending=False,
        )
        .reset_index(drop=True)
        .copy()
    )

    st.subheader(
        "수집 이력"
    )

    st.dataframe(
        table_history_df,
        width="stretch",
    )
    
# -----------------------------------
# AI 기사 생성
# -----------------------------------
if st.button("AI 기사 생성"):

    article = generate_article(row)

    st.session_state.article = article

    # st.session_state.factcheck_result = None # LLM 판정 결과 초기화
    st.session_state.factcheck_evidence = None

    os.makedirs(
        "articles",
        exist_ok=True,
    )

    with open(
        "articles/news_article.md",
        "w",
        encoding="utf-8",
    ) as f:
        f.write(article)
if st.session_state.article:

    st.divider()

    st.subheader("AI 생성 기사")

    st.markdown(
        st.session_state.article
    )

# -----------------------------------
# RAG 팩트체크 실행
# -----------------------------------
if st.button("RAG 팩트체크 실행"):

    article = st.session_state.article

    if not article:
        st.warning("먼저 AI 기사를 생성하세요.")

    else:

        target_city = str(row["city"]).strip()

        st.write(
            "팩트체크 대상 도시:",
            target_city
        )

        evidence = fact_check_article(
            article,
            city=row["city"],
        )

        st.write(
            "RAG 검색 결과:",
            len(evidence),
            "건"
        )

        st.session_state.factcheck_evidence = evidence

        save_fact_check(
            article,
            evidence,
        )

        st.success("팩트체크 완료")

# -----------------------------------
# RAG 팩트체크 결과
# -----------------------------------
evidence = st.session_state.get(
    "factcheck_evidence"
)

if evidence is not None:

    st.divider()
    st.subheader("실시간 관측 데이터 근거")

    if len(evidence) == 0:
        st.warning("검증 가능한 관측 데이터가 없습니다.")

    else:
        item = evidence[0]

        st.success(
            f"{row['city']} 최신 관측 데이터 확인 완료"
        )

        with st.expander(
            "최신 관측 근거 보기",
            expanded=True,
        ):
            st.text(item["content"])

            st.caption(
                f"출처: {item['metadata']['source']} | "
                f"수집시각: {item['metadata']['collected_at']}"
            )

# -----------------------------------
# RAG 팩트체크 결과 - LLM 판정
# -----------------------------------
result = st.session_state.get(
    "factcheck_result"
)
if result:
    st.divider()

    st.subheader(
        "팩트체크 결과"
    )

    status = result.get(
        "status",
        "근거 부족"
    )

    if status == "사실":
        st.success(
            f"판정: {status}"
        )

    elif status == "불일치":
        st.error(
            f"판정: {status}"
        )

    else:
        st.warning(
            f"판정: {status}"
        )

    st.write(
        result.get(
            "reason",
            ""
        )
    )

    mismatches = result.get(
        "mismatches",
        []
    )

    if mismatches:

        st.subheader(
            "불일치 항목"
        )

        for i, item in enumerate(
            mismatches,
            start=1,
        ):

            with st.expander(
                f"불일치 {i}"
            ):

                st.write(
                    "기사 주장:",
                    item["claim"],
                )

                st.write(
                    "실제 데이터:",
                    item["evidence"],
                )

                st.write(
                    "설명:",
                    item["explanation"],
                )