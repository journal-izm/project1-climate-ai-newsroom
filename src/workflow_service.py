from __future__ import annotations

from typing import Any
from uuid import uuid4

from src.data_service import save_article_record
from src.time_utils import iso_seoul

VALID_TRANSITIONS = {"draft": {"fact_checked"}, "fact_checked": {"reviewed"}, "reviewed": {"approved", "draft"}, "approved": set()}


def create_article_record(article: str, city: str, generator: str) -> dict[str, Any]:
    return save_article_record({"id": uuid4().hex, "city": city, "content": article, "status": "draft", "generator": generator, "created_at": iso_seoul(), "updated_at": iso_seoul(), "factcheck": None, "review_note": "", "approved_at": None, "script": None})


def transition(record: dict[str, Any], new_status: str, **updates: Any) -> dict[str, Any]:
    current = str(record.get("status"))
    if new_status not in VALID_TRANSITIONS.get(current, set()):
        raise ValueError(f"허용되지 않은 상태 변경입니다: {current} → {new_status}")
    result = {**record, **updates, "status": new_status, "updated_at": iso_seoul()}
    if new_status == "approved":
        result["approved_at"] = iso_seoul()
    return save_article_record(result)


def attach_factcheck(record: dict[str, Any], factcheck: dict[str, Any]) -> dict[str, Any]:
    return transition(record, "fact_checked", factcheck=factcheck)


def review_article(record: dict[str, Any], content: str, note: str) -> dict[str, Any]:
    if not content.strip():
        raise ValueError("검토 기사 내용은 비어 있을 수 없습니다.")
    return transition(record, "reviewed", content=content.strip(), review_note=note.strip())


def approve_article(record: dict[str, Any], script: str) -> dict[str, Any]:
    if record.get("status") != "reviewed":
        raise ValueError("사람 검토가 끝난 기사만 승인할 수 있습니다.")
    return transition(record, "approved", script=script)
