from fastapi.testclient import TestClient
from app.main import app
import io


client = TestClient(app)


def mock_predict(_input, from_bytes=False, top_k=5):
    return {"predictions": [{"label": "ayam", "probability": 0.95}, {"label": "telur", "probability": 0.03}]}


def test_scan_endpoint_monkeypatch(monkeypatch):
    # monkeypatch the predict_ingredients function to avoid TF dependency
    import app.services.ai_service as aisvc
    monkeypatch.setattr(aisvc, "predict_ingredients", mock_predict)

    # create a fake image bytes (small png header is enough since we mock predict)
    fake_image = io.BytesIO(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR")
    files = {"file": ("test.png", fake_image, "image/png")}

    r = client.post("/scan/", files=files)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    assert "predictions" in data
    assert "detected_ingredients" in data
    assert "nutrition" in data
