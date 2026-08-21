from __future__ import annotations

import re
from typing import Any

import pandas as pd

from src.config import SAMPLE_DIR, Settings, VECTOR_DB_DIR
from src.data_service import load_alert_history, load_weather_history


def _document(content: str, source: str, **metadata: Any) -> dict[str, Any]:
    return {"content": content.strip(), "metadata": {"source": source, **metadata}}


def create_weather_documents() -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    weather = load_weather_history(descending=True)
    for _, row in weather.iterrows():
        content = (
            f"수집 시각: {row['collected_at']}\n지역: {row.get('city_ko', row['city'])}\n"
            f"기온: {row['temperature']}℃\n체감온도: {row['feels_like']}℃\n"
            f"습도: {row['humidity']}%\n풍속: {row['wind_speed']}m/s\n날씨: {row['weather']}"
        )
        documents.append(_document(content, str(row.get("source", "기상 데이터")), city=row["city"], collected_at=row["collected_at"], kind="observation"))

    alerts = load_alert_history(descending=True)
    for _, row in alerts.iterrows():
        content = f"특보 발표 시각: {row['issued_at']}\n지역: {row['region']}\n특보: {row['alert_type']} ({row['level']})\n내용: {row['content']}"
        documents.append(_document(content, str(row.get("source", "기상청")), region=row["region"], collected_at=row["issued_at"], kind="alert"))

    for filename, kind in (("weather_terms.csv", "term"), ("disaster_guidelines.csv", "guideline")):
        path = SAMPLE_DIR / filename
        if not path.exists():
            continue
        df = pd.read_csv(path, encoding="utf-8-sig")
        for _, row in df.iterrows():
            content = f"기상 용어: {row['term']}\n설명: {row['description']}" if kind == "term" else f"특보 유형: {row['alert_type']}\n재난 대응요령: {row['guideline']}"
            documents.append(_document(content, str(row["source"]), kind=kind))
    return documents


def _tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"[0-9A-Za-z가-힣]+", text.casefold()) if len(token) > 1}


def search_weather(query: str, city: str | None = None, k: int = 5) -> list[dict[str, Any]]:
    query_tokens = _tokens(query)
    scored: list[tuple[int, str, dict[str, Any]]] = []
    for doc in create_weather_documents():
        metadata = doc["metadata"]
        city_text = f"{metadata.get('city', '')} {metadata.get('region', '')} {doc['content']}"
        if city and city.casefold() not in city_text.casefold() and metadata.get("kind") not in {"term", "guideline"}:
            continue
        scored.append((len(query_tokens & _tokens(doc["content"])), str(metadata.get("collected_at", "")), doc))
    scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
    matched = [item[2] for item in scored if item[0] > 0]
    return (matched or [item[2] for item in scored])[:k]


def build_vector_db(settings: Settings | None = None) -> dict[str, Any]:
    settings = settings or Settings()
    documents = create_weather_documents()
    if not settings.openai_api_key or not documents:
        return {"backend": "keyword", "count": len(documents), "path": None}
    from langchain_community.vectorstores import FAISS
    from langchain_core.documents import Document
    from langchain_openai import OpenAIEmbeddings
    lc_documents = [Document(page_content=d["content"], metadata=d["metadata"]) for d in documents]
    vector_store = FAISS.from_documents(lc_documents, OpenAIEmbeddings(model=settings.embedding_model, api_key=settings.openai_api_key))
    VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
    vector_store.save_local(str(VECTOR_DB_DIR))
    return {"backend": "faiss", "count": len(documents), "path": str(VECTOR_DB_DIR)}
