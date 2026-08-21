from __future__ import annotations

import json
from typing import Any

from src.config import Settings


def llm_review_article(article: str, evidence: list[dict[str, Any]], settings: Settings | None = None) -> dict[str, Any]:
    settings = settings or Settings()
    if not settings.openai_api_key:
        return {"status": "검토 생략", "reason": "OPENAI_API_KEY가 없어 LLM 문맥 검토를 생략했습니다.", "issues": [], "mode": "demo"}
    from openai import OpenAI
    client = OpenAI(api_key=settings.openai_api_key)
    prompt = f"""기사와 근거를 비교해 문맥, 과장, 근거 없는 전망, 누락, 편향을 검토하라.
수치·날짜·지역·특보 여부는 별도 규칙 엔진이 판정한다. JSON 형식으로 status(적합|수정 필요|근거 부족), reason, issues 배열을 반환하라.
[기사]\n{article}\n[근거]\n{evidence}"""
    response = client.chat.completions.create(model=settings.chat_model, messages=[{"role": "system", "content": "너는 저널리즘 품질 검토자다."}, {"role": "user", "content": prompt}], response_format={"type": "json_object"}, temperature=0)
    result = json.loads(response.choices[0].message.content or "{}")
    result["mode"] = "openai"
    return result


def combine_checks(rule_result: dict[str, Any], llm_result: dict[str, Any]) -> dict[str, Any]:
    ok = rule_result.get("status") == "사실" and llm_result.get("status") in {"적합", "검토 생략"}
    return {"status": "사람 검토 대기" if ok else "사람 검토 필요", "reason": "자동 검증을 통과했습니다. 사람의 최종 검토와 승인이 필요합니다." if ok else "규칙 또는 LLM 검토에서 문제를 발견해 자동 승인하지 않습니다.", "rule": rule_result, "llm": llm_result}
