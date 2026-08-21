from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass
class WeatherRecord:
    collected_at: str
    city: str
    city_ko: str
    temperature: float
    feels_like: float
    humidity: int
    pressure: int
    wind_speed: float
    weather: str
    source: str
    source_url: str
    mode: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AlertRecord:
    collected_at: str
    region: str
    alert_type: str
    level: str
    issued_at: str
    effective_at: str
    content: str
    source: str = "기상청"
    source_url: str = "https://www.weather.go.kr/w/wnuri-fct2021/main/digital-forecast.do"
    mode: str = "live"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RuleCheckResult:
    status: str
    reason: str
    checks: List[Dict[str, Any]] = field(default_factory=list)
    evidence: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
