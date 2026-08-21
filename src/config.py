from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
SAMPLE_DIR = DATA_DIR / "sample"
PROCESSED_DIR = DATA_DIR / "processed"
POWERBI_DIR = DATA_DIR / "powerbi"
ARTICLE_DIR = ROOT_DIR / "articles"
REPORT_DIR = ROOT_DIR / "reports"
VECTOR_DB_DIR = ROOT_DIR / "vector_db" / "weather"

SUPPORTED_CITIES = {
    "Seoul": "서울",
    "Busan": "부산",
    "Daegu": "대구",
    "Incheon": "인천",
    "Gwangju": "광주",
    "Daejeon": "대전",
    "Ulsan": "울산",
}


@dataclass(frozen=True)
class Settings:
    app_mode: str = os.getenv("APP_MODE", "demo").strip().lower()
    openweather_api_key: str = os.getenv("OPENWEATHER_API_KEY", "").strip()
    kma_service_key: str = os.getenv("KMA_SERVICE_KEY", "").strip()
    kma_alert_api_url: str = os.getenv(
        "KMA_ALERT_API_URL",
        "https://apihub.kma.go.kr/api/typ01/url/wrn_met_data.php",
    ).strip()
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "").strip()
    chat_model: str = os.getenv("OPENAI_CHAT_MODEL", "gpt-4.1-mini").strip()
    embedding_model: str = os.getenv(
        "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
    ).strip()

    @property
    def demo_mode(self) -> bool:
        return self.app_mode != "live"


def ensure_runtime_dirs() -> None:
    for path in (PROCESSED_DIR, POWERBI_DIR, ARTICLE_DIR, REPORT_DIR):
        path.mkdir(parents=True, exist_ok=True)
