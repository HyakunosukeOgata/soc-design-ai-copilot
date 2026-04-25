"""Smoke tests for the FastAPI service.

Uses TestClient (no actual server). Triggers the lifespan event so the
index is built before requests fire.

Run:
    pytest tests/ -v
"""
from fastapi.testclient import TestClient
from soc_copilot.api.main import app


def test_health():
    with TestClient(app) as client:
        r = client.get("/health")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "ok"
        assert body["chunks_indexed"] > 0


def test_ask_in_scope():
    with TestClient(app) as client:
        r = client.post("/ask", json={
            "question": "How does the FIFO handle metastability?"
        })
        assert r.status_code == 200
        body = r.json()
        assert body["refused"] is False
        assert len(body["sources"]) > 0
        # Should mention synchronizer or Gray
        assert any(k in body["answer"].lower() for k in ["synchron", "gray"])


def test_ask_out_of_scope_refuses():
    with TestClient(app) as client:
        r = client.post("/ask", json={
            "question": "What is the price of NVIDIA H100?"
        })
        assert r.status_code == 200
        body = r.json()
        assert body["refused"] is True


def test_ask_validation_empty_question():
    with TestClient(app) as client:
        r = client.post("/ask", json={"question": ""})
        assert r.status_code == 422  # Pydantic validation
