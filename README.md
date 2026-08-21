# Climate AI Newsroom

프로젝트 1. 실시간 기상 특보 뉴스룸의 실행 애플리케이션입니다. 현재 날씨와 기상청 특보를 수집하고, RAG 근거 검색, AI 기사 초안, 규칙·LLM 팩트체크, 사람 검토·승인, 뉴스 대본과 Power BI CSV 출력을 하나의 흐름으로 제공합니다.

## 기준 환경

- Windows 11
- VS Code
- Python 3.13.15

## 빠른 실행 — API 키 없이 데모 모드

```powershell
py -3.13 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```

또는 `scripts\run_demo_windows.bat`를 실행합니다.

데모 모드는 `data/sample/`의 교육용 날씨·특보·기상 용어·재난 대응요령을 사용합니다. 실제 관측값으로 오해하면 안 됩니다.

## 실시간 모드

1. `.env.example`을 복사해 `.env`를 만듭니다.
2. 필요한 키를 입력합니다.
3. `APP_MODE=live`로 변경합니다.

```dotenv
APP_MODE=live
OPENWEATHER_API_KEY=발급받은_키
KMA_SERVICE_KEY=공공데이터포털_서비스키
KMA_API_HUB_KEY=기상청_인증키
OPENAI_API_KEY=선택_키
```

- OpenWeather: 현재 기상정보
- 기상청 공공데이터 API: 공식 기상특보
- OpenAI: 기사 초안·임베딩·문맥 검토
- OpenAI 키가 없어도 규칙 기반 검증과 데모 기사 생성은 동작합니다.
- 실시간 모드에서 개별 API가 실패해도 다른 수집 결과는 보존됩니다.

## 화면 흐름

1. 수집·시각화: 현재 날씨와 특보를 수집하고 최신순 이력을 확인합니다.
2. RAG 근거: 특보, 용어, 대응요령, 수집 데이터를 검색합니다.
3. 기사·팩트체크·승인: 초안 → 자동 검증 → 사람 검토 → 최종 승인 순서로 진행합니다.
4. 내보내기: Power BI CSV, 승인 기사, 뉴스 대본, 팩트체크 보고서를 내려받습니다.

## 저장 위치

```text
data/processed/   실행 중 수집한 데이터와 기사 상태
data/powerbi/     Power BI 연계 CSV
articles/         기사 산출물
reports/          팩트체크 보고서
vector_db/        실행 환경에서 생성한 FAISS 인덱스
```

실행 데이터, `.env`, FAISS 인덱스는 Git에 커밋하지 않습니다. `data/sample/`만 교육용 샘플로 관리합니다.

## 테스트

```powershell
pytest -q
```

테스트 항목에는 Asia/Seoul 시간, 최신순 정렬, 데모 수집, RAG 검색, 규칙 판정, 승인 상태 차단, Power BI 출력과 Streamlit 핵심 흐름이 포함됩니다.

버전 확인:

```powershell
python --version
# Python 3.13.15
```

## 주의사항

- 최종 기사 승인은 사람이 수행합니다.
- 규칙 판정과 LLM 판정이 다르면 자동 승인하지 않습니다.
- 기사와 영상에는 데이터 출처와 AI 활용 사실을 표시해야 합니다.
- 공공데이터 API의 응답 스키마나 서비스 URL이 변경되면 `.env`의 `KMA_ALERT_API_URL`과 파서를 함께 확인해야 합니다.
