import os

import pandas as pd
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS


load_dotenv()

VECTOR_DB_PATH = "vector_db/weather"


def create_weather_documents():
    """
    weather_history.csv의 각 행을
    LangChain Document 객체로 변환한다.
    """

    history_path = "data/weather_history.csv"

    if not os.path.exists(history_path):
        raise FileNotFoundError(
            "data/weather_history.csv 파일이 없습니다."
        )

    df = pd.read_csv(history_path)

    documents = []

    for _, row in df.iterrows():

        content = f"""
수집 시각: {row['collected_at']}
도시: {row['city']}
현재 기온: {row['temperature']}℃
체감 온도: {row['feels_like']}℃
습도: {row['humidity']}%
기압: {row['pressure']} hPa
풍속: {row['wind_speed']} m/s
날씨 상태: {row['weather']}
""".strip()

        document = Document(
            page_content=content,
            metadata={
                "source": "OpenWeather API",
                "city": row["city"],
                "collected_at": row["collected_at"],
            },
        )

        documents.append(document)

    return documents


def build_vector_db():
    """
    기상 데이터를 임베딩하여
    FAISS Vector DB를 생성한다.
    """

    documents = create_weather_documents()

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    vector_store = FAISS.from_documents(
        documents,
        embeddings,
    )

    os.makedirs(
        "vector_db",
        exist_ok=True,
    )

    vector_store.save_local(
        VECTOR_DB_PATH
    )

    return len(documents)


def search_weather(
    query,
    city=None,
    k=3,
):

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    vector_store = FAISS.load_local(
        VECTOR_DB_PATH,
        embeddings,
        allow_dangerous_deserialization=True,
    )

    # 우선 넉넉하게 검색
    results = vector_store.similarity_search(
        query,
        k=20,
    )

    # 도시가 지정되면 Python에서 직접 필터
    if city:

        target_city = str(city).strip().lower()

        results = [
            doc
            for doc in results
            if str(
                doc.metadata.get(
                    "city",
                    ""
                )
            ).strip().lower()
            == target_city
        ]

    if results:

        results = sorted(
            results,
            key=lambda doc: pd.to_datetime(
                doc.metadata.get(
                    "collected_at"
                )
            ),
            reverse=True,
        )
    # 최종 반환 개수 제한
    return results[:k]

def get_latest_weather(city):
    """
    weather_history.csv에서
    지정 도시의 가장 최근 관측값 1건을 반환한다.
    """

    history_path = "data/weather_history.csv"

    if not os.path.exists(history_path):
        return None

    df = pd.read_csv(history_path)

    df["city"] = (
        df["city"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    target_city = str(city).strip().lower()

    city_df = df[
        df["city"] == target_city
    ].copy()

    if city_df.empty:
        return None

    city_df["collected_at"] = pd.to_datetime(
        city_df["collected_at"]
    )

    city_df = city_df.sort_values(
        "collected_at",
        ascending=False,
    )

    return city_df.iloc[0]