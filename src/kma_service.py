from __future__ import annotations

import re

import requests

from src.config import SUPPORTED_CITIES, Settings
from src.models import AlertRecord
from src.time_utils import iso_seoul


WRN_NAMES = {
    "W": "강풍",
    "R": "호우",
    "C": "한파",
    "D": "건조",
    "O": "폭풍해일",
    "N": "지진해일",
    "V": "풍랑",
    "T": "태풍",
    "S": "대설",
    "Y": "황사",
    "H": "폭염",
    "F": "안개",
    "K": "열대야",
}
LEVEL_NAMES = {"1": "예비특보", "2": "주의보", "3": "경보"}
COMMAND_NAMES = {
    "1": "발표",
    "2": "대치",
    "3": "해제",
    "4": "대치해제",
    "5": "연장",
    "6": "변경",
    "7": "변경해제",
}
RELEASE_COMMANDS = {"3", "4", "7"}

_ROW_PATTERN = re.compile(
    r"^\s*(?P<reg_up>\S+)\s+"
    r"(?P<reg_up_ko>.+?)\s+"
    r"(?P<reg_id>\S+)\s+"
    r"(?P<reg_ko>.+?)\s+"
    r"(?P<tm_fc>\d{12})\s+"
    r"(?P<tm_ef>\d{12})\s+"
    r"(?P<wrn>\S+)\s+"
    r"(?P<lvl>\S+)\s+"
    r"(?P<cmd>\S+)\s*$"
)


def _decode_response(response: requests.Response) -> str:
    content = getattr(response, "content", None)
    if isinstance(content, bytes):
        for encoding in ("utf-8", "cp949", "euc-kr"):
            try:
                return content.decode(encoding)
            except UnicodeDecodeError:
                continue
        return content.decode("utf-8", errors="replace")
    return str(getattr(response, "text", ""))


def _parse_row(line: str) -> dict[str, str] | None:
    if "\t" in line:
        values = [value.strip() for value in line.split("\t") if value.strip()]
        if len(values) == 9:
            keys = (
                "reg_up",
                "reg_up_ko",
                "reg_id",
                "reg_ko",
                "tm_fc",
                "tm_ef",
                "wrn",
                "lvl",
                "cmd",
            )
            return dict(zip(keys, values))
    match = _ROW_PATTERN.match(line)
    return match.groupdict() if match else None


def parse_kma_alert_response(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for raw_line in text.replace("\ufeff", "").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        row = _parse_row(line)
        if row:
            rows.append(row)

    lowered = text.lower()
    error_markers = ("error", "invalid", "인증키 오류", "권한이 없습니다")
    if not rows and any(marker in lowered for marker in error_markers):
        raise RuntimeError("기상청 API 허브가 오류 응답을 반환했습니다. 인증키와 활용승인을 확인하세요.")
    return rows


def _matches_city(row: dict[str, str], city: str) -> bool:
    city_ko = SUPPORTED_CITIES[city]
    upper_region = row.get("reg_up_ko", "")
    detail_region = row.get("reg_ko", "")
    if upper_region:
        return city_ko in upper_region
    return city_ko in detail_region


def collect_kma_alerts(city: str, settings: Settings | None = None) -> list[AlertRecord]:
    settings = settings or Settings()
    if not settings.kma_api_hub_key:
        raise ValueError("KMA_API_HUB_KEY가 설정되지 않았습니다.")
    if city not in SUPPORTED_CITIES:
        raise ValueError(f"지원하지 않는 지역입니다: {city}")

    params = {
        "fe": "f",
        "tm": "",
        "disp": "0",
        "help": "0",
        "authKey": settings.kma_api_hub_key,
    }
    response = requests.get(settings.kma_alert_api_url, params=params, timeout=15)
    response.raise_for_status()
    rows = parse_kma_alert_response(_decode_response(response))
    results: list[AlertRecord] = []
    for row in rows:
        if not _matches_city(row, city) or row["cmd"] in RELEASE_COMMANDS:
            continue
        region = row["reg_ko"]
        weather_name = WRN_NAMES.get(row["wrn"], "기상특보")
        level = LEVEL_NAMES.get(row["lvl"], "정보")
        command = COMMAND_NAMES.get(row["cmd"], "현황")
        alert_type = f"{weather_name}{level}" if level != "정보" else weather_name
        issued_at = iso_seoul(row["tm_fc"])
        effective_at = iso_seoul(row["tm_ef"])
        content = (
            f"{region} {alert_type} {command}. "
            f"발표 {issued_at}, 발효 {effective_at}."
        )
        results.append(
            AlertRecord(
                collected_at=iso_seoul(),
                region=region,
                alert_type=alert_type,
                level=level,
                issued_at=issued_at,
                effective_at=effective_at,
                content=content,
                mode="live",
                source_url=settings.kma_alert_api_url,
            )
        )
    return sorted(results, key=lambda item: item.issued_at, reverse=True)
