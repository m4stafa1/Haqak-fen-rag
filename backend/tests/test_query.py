from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_query_invalid_input():
    response = client.post("/query", json={"question": "ab"})  # أقل من min_length=3
    assert response.status_code == 422

def test_query_happy_path():
    response = client.post("/query", json={"question": "ما هي مدة الاسترجاع للسلعة المعيبة؟"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert isinstance(data["sources"], list)