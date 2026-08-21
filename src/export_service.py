from __future__ import annotations

from pathlib import Path
from typing import Any

from src.config import POWERBI_DIR, REPORT_DIR, ensure_runtime_dirs
from src.data_service import load_alert_history, load_weather_history


def export_powerbi_csv() -> dict[str, Path]:
    ensure_runtime_dirs()
    weather_path = POWERBI_DIR / "weather_history_powerbi.csv"
    alert_path = POWERBI_DIR / "weather_alerts_powerbi.csv"
    load_weather_history(descending=True).to_csv(weather_path, index=False, encoding="utf-8-sig")
    load_alert_history(descending=True).to_csv(alert_path, index=False, encoding="utf-8-sig")
    return {"weather": weather_path, "alerts": alert_path}


def build_factcheck_report(record: dict[str, Any]) -> str:
    factcheck = record.get("factcheck") or {}
    return f"# 기사 팩트체크 보고서\n\n- 기사 ID: {record.get('id')}\n- 상태: {record.get('status')}\n- 지역: {record.get('city')}\n- 생성 시각: {record.get('created_at')}\n- 승인 시각: {record.get('approved_at') or '-'}\n\n## 기사\n\n{record.get('content', '')}\n\n## 통합 판정\n\n{factcheck.get('status', '미실행')} — {factcheck.get('reason', '')}\n\n## 사람 검토 메모\n\n{record.get('review_note') or '-'}\n"


def save_factcheck_report(record: dict[str, Any]) -> Path:
    ensure_runtime_dirs()
    path = REPORT_DIR / f"fact_check_{record['id']}.md"
    path.write_text(build_factcheck_report(record), encoding="utf-8")
    return path
