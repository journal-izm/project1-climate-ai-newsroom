from pathlib import Path

from streamlit.testing.v1 import AppTest

APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


def _button(app, label):
    return next(item for item in app.button if item.label == label)


def test_demo_user_flow_reaches_final_approval(monkeypatch, tmp_path):
    monkeypatch.setenv("APP_MODE", "demo")
    app = AppTest.from_file(APP_PATH, default_timeout=20).run()
    assert not app.exception
    _button(app, "기상 데이터 수집").click()
    app.run()
    assert not app.exception
    assert any("현재 날씨와 기상특보 수집·저장" in item.value for item in app.success)
    assert any(item.value == "특보 수집 이력 — 최신순" for item in app.subheader)
    _button(app, "AI 기사 초안 생성").click()
    app.run()
    assert not app.exception
    _button(app, "규칙·LLM 팩트체크 실행").click()
    app.run()
    assert not app.exception
    assert any(item.label == "사람 검토 완료" for item in app.button)
    _button(app, "사람 검토 완료").click()
    app.run()
    assert not app.exception
    assert any(item.label == "최종 승인" for item in app.button)
    _button(app, "최종 승인").click()
    app.run()
    assert not app.exception
    assert any("최종 승인 완료" in item.value for item in app.success)
