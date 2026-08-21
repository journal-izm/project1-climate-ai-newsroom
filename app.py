from __future__ import annotations

import pandas as pd
import streamlit as st

from src.article_service import generate_article, generate_news_script
from src.config import SUPPORTED_CITIES, Settings, ensure_runtime_dirs
from src.data_service import load_alert_history, load_weather_history, save_alerts, save_weather
from src.demo_service import load_demo_alerts
from src.export_service import build_factcheck_report, export_powerbi_csv, save_factcheck_report
from src.factcheck_service import combine_checks, llm_review_article
from src.kma_service import collect_kma_alerts
from src.rag_service import build_vector_db, search_weather
from src.rule_check_service import rule_check_article
from src.weather_service import collect_weather
from src.workflow_service import approve_article, attach_factcheck, create_article_record, review_article

st.set_page_config(page_title="Climate AI Newsroom", page_icon="🌤️", layout="wide")
ensure_runtime_dirs()


def init_state() -> None:
    defaults = {"weather": None, "alerts": [], "evidence": [], "article_record": None, "last_error": None}
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_news_state() -> None:
    st.session_state.evidence = []
    st.session_state.article_record = None


def status_label(status: str) -> str:
    return {"draft": "초안", "fact_checked": "팩트체크 완료", "reviewed": "사람 검토 완료", "approved": "최종 승인"}.get(status, status)


init_state()
settings = Settings()

st.title("🌤 Climate AI Newsroom")
st.caption("프로젝트 1. 실시간 기상 특보 뉴스룸 — 데이터 수집부터 사람 승인까지")

with st.sidebar:
    st.header("실행 설정")
    mode = st.radio("데이터 모드", ["demo", "live"], index=0 if settings.demo_mode else 1, format_func=lambda value: "교육용 데모" if value == "demo" else "실시간 API")
    city = st.selectbox("지역", list(SUPPORTED_CITIES), format_func=lambda value: SUPPORTED_CITIES[value])
    effective_settings = Settings(app_mode=mode, openweather_api_key=settings.openweather_api_key, kma_api_hub_key=settings.kma_api_hub_key, kma_alert_api_url=settings.kma_alert_api_url, openai_api_key=settings.openai_api_key, chat_model=settings.chat_model, embedding_model=settings.embedding_model)
    if mode == "live" and not settings.openweather_api_key:
        st.warning("OpenWeather 키가 없어 현재 날씨는 데모 데이터를 사용합니다.")
    if mode == "live" and not settings.kma_api_hub_key:
        st.warning("기상청 키가 없어 특보는 데모 데이터를 사용합니다.")
    st.caption(f"AI 기사/검토: {'OpenAI' if settings.openai_api_key else '데모 기사·규칙 검증'}")

tab_collect, tab_rag, tab_news, tab_export = st.tabs(["① 수집·시각화", "② RAG 근거", "③ 기사·팩트체크·승인", "④ 내보내기"])

with tab_collect:
    st.subheader("현재 기상정보와 기상특보")
    if st.button("기상 데이터 수집", type="primary"):
        reset_news_state()
        errors: list[str] = []
        try:
            weather = collect_weather(city, effective_settings)
            save_weather(weather)
            st.session_state.weather = weather.to_dict()
        except Exception as exc:
            errors.append(f"현재 날씨 수집 실패: {exc}")
        try:
            if mode == "live" and settings.kma_api_hub_key:
                alerts = collect_kma_alerts(city, effective_settings)
            else:
                alerts = load_demo_alerts(city)
            save_alerts(alerts)
            st.session_state.alerts = [item.to_dict() for item in alerts]
        except Exception as exc:
            errors.append(f"특보 수집 실패: {exc}")
        if errors:
            st.warning(" / ".join(errors))
        if st.session_state.weather:
            st.success("수집·저장을 완료했습니다. 각 단계는 독립 처리되어 일부 API 실패가 기존 데이터를 손상시키지 않습니다.")

    weather = st.session_state.weather
    if weather:
        cols = st.columns(5)
        cols[0].metric("기온", f"{weather['temperature']} ℃")
        cols[1].metric("체감온도", f"{weather['feels_like']} ℃")
        cols[2].metric("습도", f"{weather['humidity']} %")
        cols[3].metric("풍속", f"{weather['wind_speed']} m/s")
        cols[4].metric("특보", len(st.session_state.alerts))
        st.caption(f"출처: {weather['source']} | 수집시각: {weather['collected_at']} | 모드: {weather['mode']}")
        for item in st.session_state.alerts:
            st.warning(f"{item['region']} · {item['alert_type']}({item['level']}) — {item['content']}")
    else:
        st.info("지역을 선택하고 기상 데이터를 수집하세요.")

    history = load_weather_history(descending=True)
    if not history.empty:
        st.subheader("수집 이력 — 최신순")
        st.dataframe(history, use_container_width=True, hide_index=True)
        chart = history.copy()
        chart["collected_at"] = pd.to_datetime(chart["collected_at"])
        chart = chart.sort_values("collected_at").set_index("collected_at")
        st.line_chart(chart[["temperature", "feels_like"]])

with tab_rag:
    st.subheader("기상·특보 근거 검색")
    default_query = f"{SUPPORTED_CITIES[city]} 현재 날씨 특보와 재난 대응요령"
    query = st.text_input("검색 질문", value=default_query)
    c1, c2 = st.columns(2)
    if c1.button("근거 검색"):
        st.session_state.evidence = search_weather(query, city=SUPPORTED_CITIES[city], k=5)
    if c2.button("RAG 인덱스 갱신"):
        try:
            result = build_vector_db(effective_settings)
            st.success(f"{result['backend']} 검색 기반을 갱신했습니다: {result['count']}건")
        except Exception as exc:
            st.error(f"RAG 갱신 실패: {exc}")
    for index, item in enumerate(st.session_state.evidence, 1):
        with st.expander(f"근거 {index} · {item['metadata'].get('source', '')}", expanded=index == 1):
            st.text(item["content"])
            st.caption(str(item["metadata"]))

with tab_news:
    st.subheader("AI 기사 제작과 편집 승인")
    if not st.session_state.weather:
        st.info("먼저 ① 수집·시각화에서 데이터를 수집하세요.")
    else:
        if st.button("AI 기사 초안 생성", type="primary"):
            if not st.session_state.evidence:
                st.session_state.evidence = search_weather(default_query, city=SUPPORTED_CITIES[city], k=5)
            try:
                content, generator = generate_article(st.session_state.weather, st.session_state.alerts, st.session_state.evidence, effective_settings)
                st.session_state.article_record = create_article_record(content, SUPPORTED_CITIES[city], generator)
                st.success("기사 초안을 생성했습니다.")
            except Exception as exc:
                st.error(f"기사 생성 실패: {exc}")

    record = st.session_state.article_record
    if record:
        st.markdown(f"**현재 상태:** {status_label(record['status'])}")
        st.markdown(record["content"])
        if record["status"] == "draft" and st.button("규칙·LLM 팩트체크 실행"):
            rule = rule_check_article(record["content"], st.session_state.weather, st.session_state.alerts)
            llm = llm_review_article(record["content"], rule["evidence"], effective_settings)
            record = attach_factcheck(record, combine_checks(rule, llm))
            st.session_state.article_record = record
            st.rerun()

        if record.get("factcheck"):
            fact = record["factcheck"]
            if fact["status"] == "사람 검토 필요":
                st.warning(f"{fact['status']}: {fact['reason']}")
            else:
                st.info(f"{fact['status']}: {fact['reason']}")
            st.write("규칙 판정", fact["rule"])
            st.write("LLM 문맥 검토", fact["llm"])

        if record["status"] == "fact_checked":
            edited = st.text_area("사람 검토·수정", value=record["content"], height=260)
            note = st.text_input("검토 메모", value="출처와 수치를 확인함")
            if st.button("사람 검토 완료"):
                st.session_state.article_record = review_article(record, edited, note)
                st.rerun()

        if record["status"] == "reviewed":
            st.warning("최종 승인하면 승인 기사와 뉴스 대본이 생성됩니다.")
            if st.button("최종 승인", type="primary"):
                script = generate_news_script(record["content"], record["city"])
                record = approve_article(record, script)
                save_factcheck_report(record)
                st.session_state.article_record = record
                st.rerun()

        if record["status"] == "approved":
            st.success(f"최종 승인 완료 · {record['approved_at']}")
            st.subheader("승인 기사")
            st.markdown(record["content"])
            st.subheader("뉴스 대본")
            st.text(record["script"])
            st.download_button("승인 기사 다운로드", record["content"], file_name=f"approved_article_{record['id']}.md", mime="text/markdown")
            st.download_button("뉴스 대본 다운로드", record["script"], file_name=f"news_script_{record['id']}.txt", mime="text/plain")

with tab_export:
    st.subheader("Power BI 및 보고서 출력")
    if st.button("Power BI 연계 CSV 생성"):
        paths = export_powerbi_csv()
        st.success(f"생성 완료: {paths['weather'].name}, {paths['alerts'].name}")
    weather_export = load_weather_history(descending=True)
    alert_export = load_alert_history(descending=True)
    if not weather_export.empty:
        st.download_button("기상 이력 CSV 다운로드", weather_export.to_csv(index=False).encode("utf-8-sig"), "weather_history_powerbi.csv", "text/csv")
    if not alert_export.empty:
        st.download_button("특보 이력 CSV 다운로드", alert_export.to_csv(index=False).encode("utf-8-sig"), "weather_alerts_powerbi.csv", "text/csv")
    if st.session_state.article_record:
        report = build_factcheck_report(st.session_state.article_record)
        st.download_button("팩트체크 보고서 다운로드", report, file_name=f"fact_check_{st.session_state.article_record['id']}.md", mime="text/markdown")
