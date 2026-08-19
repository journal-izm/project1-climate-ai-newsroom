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


def search_weather(query, k=3):
    """
    생성한 FAISS DB에서
    질문과 관련된 기상 데이터를 검색한다.
    """

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    vector_store = FAISS.load_local(
        VECTOR_DB_PATH,
        embeddings,
        allow_dangerous_deserialization=True,
    )

    results = vector_store.similarity_search(
        query,
        k=k,
    )

    return results