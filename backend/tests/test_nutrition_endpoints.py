import json
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_known_ingredients():
    r = client.get("/nutrition/known")
    assert r.status_code == 200
    data = r.json()
    assert "known" in data
    assert isinstance(data["known"], list)


def test_nutrition_detail_exists():
    # pick an ingredient we added in nutrition_service
    r = client.get("/nutrition/ayam")
    assert r.status_code == 200
    data = r.json()
    assert data["ingredient"] == "ayam"
    assert "nutrition_per_100g" in data


def test_nutrition_detail_not_found():
    r = client.get("/nutrition/__not_found__")
    assert r.status_code == 404
