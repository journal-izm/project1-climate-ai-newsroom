from src.rag_service import (
    build_vector_db,
    search_weather,
)


count = build_vector_db()

print(
    f"\nVector DB 생성 완료: {count}건"
)

print("\n--- 검색 테스트 ---")

query = "서울의 현재 기온과 습도는?"

results = search_weather(
    query,
    k=3,
)

for i, doc in enumerate(
    results,
    start=1,
):
    print(
        f"\n[{i}번째 검색 결과]"
    )

    print(
        doc.page_content
    )

    print(
        "metadata:",
        doc.metadata,
    )