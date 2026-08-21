import src.export_service as export_service
from src.data_service import save_alerts, save_weather
from src.demo_service import load_demo_alerts, load_demo_weather


def test_powerbi_export(tmp_path, monkeypatch):
    monkeypatch.setattr(export_service, "POWERBI_DIR", tmp_path)
    save_weather(load_demo_weather("Seoul"))
    save_alerts(load_demo_alerts("Seoul"))
    paths = export_service.export_powerbi_csv()
    assert paths["weather"].exists()
    assert paths["alerts"].exists()
    assert paths["weather"].read_bytes().startswith(b"\xef\xbb\xbf")
