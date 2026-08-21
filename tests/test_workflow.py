import pytest

import src.data_service as data_service
from src.article_service import generate_news_script
from src.workflow_service import approve_article, attach_factcheck, create_article_record, review_article


@pytest.fixture(autouse=True)
def isolated_article_store(tmp_path, monkeypatch):
    monkeypatch.setattr(data_service, "ARTICLE_STORE", tmp_path / "articles.json")


def test_approval_requires_human_review():
    record = create_article_record("기사", "서울", "demo")
    with pytest.raises(ValueError):
        approve_article(record, "대본")


def test_full_approval_flow():
    record = create_article_record("기사", "서울", "demo")
    fact = {"status": "사람 검토 대기", "reason": "검증 완료"}
    record = attach_factcheck(record, fact)
    record = review_article(record, "수정 기사", "사람이 확인함")
    record = approve_article(record, generate_news_script(record["content"], record["city"]))
    assert record["status"] == "approved"
    assert record["approved_at"]
    assert "AI가 초안을 작성" in record["script"]
