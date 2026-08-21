"""이전 CLI와의 호환용 수집 스크립트. 애플리케이션은 weather_service를 사용합니다."""

from src.data_service import save_weather
from src.weather_service import collect_weather


def main() -> None:
    record = collect_weather("Seoul")
    save_weather(record)
    print(record.to_dict())


if __name__ == "__main__":
    main()
