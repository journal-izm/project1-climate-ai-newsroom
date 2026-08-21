"""수동 RAG 확인 스크립트. 자동 테스트는 tests/test_rag.py를 사용합니다."""

from src.rag_service import build_vector_db, search_weather


def main() -> None:
    result = build_vector_db()
    print(f"RAG 검색 기반 갱신: {result}")
    for index, item in enumerate(search_weather("서울의 현재 기온과 특보는?", k=3), 1):
        print(f"\n[{index}] {item['content']}")
        print("metadata:", item["metadata"])


if __name__ == "__main__":
    main()
