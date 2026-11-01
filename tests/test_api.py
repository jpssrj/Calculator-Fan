"""Testes de integração para a API FastAPI da Calculadora Fan."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "Calculadora Fan" in data["service"]


def test_calculate_endpoint_success():
    payload = {"expression": "12.5 * (4 + 6) / 2"}
    response = client.post("/api/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["result"] == "62.5"
    assert data["error"] is None


def test_calculate_endpoint_exact_decimals():
    payload = {"expression": "0.1 + 0.2"}
    response = client.post("/api/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["result"] == "0.3"


def test_calculate_endpoint_division_by_zero():
    payload = {"expression": "100 / 0"}
    response = client.post("/api/calculate", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "error"
    assert "DIVISÃO POR ZERO" in data["error"]
    assert data["result"] is None


def test_calculate_endpoint_security_block():
    payload = {"expression": "__import__('os').system('ls')"}
    response = client.post("/api/calculate", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "error"
    assert data["result"] is None
