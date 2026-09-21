"""API test suite for AI Agent endpoints."""

import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_agent_health_endpoint():
    """Test GET /api/v1/agent/health."""
    response = client.get("/api/v1/agent/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["active_tools_count"] > 0


def test_agent_tools_list_endpoint():
    """Test GET /api/v1/agent/tools."""
    response = client.get("/api/v1/agent/tools")
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    assert len(data["tools"]) >= 4


def test_agent_chat_endpoint():
    """Test POST /api/v1/agent/chat."""
    payload = {
        "message": "Em muốn tìm thầy cô hướng dẫn về đề tài Recommender Systems và Graph Neural Networks.",
        "student_profile": {
            "student_name": "Nguyen Van Sinh Vien",
            "gpa": 3.5,
            "skills": ["Python", "PyTorch", "Graph"],
            "interests": ["Data Mining"],
        },
    }
    response = client.post("/api/v1/agent/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert len(data["recommended_advisors"]) > 0
    assert len(data["reasoning_steps"]) > 0
    assert data["status"] == "success"


def test_agent_evaluate_endpoint():
    """Test POST /api/v1/agent/evaluate."""
    payload = {
        "student_skills": ["python", "nlp", "transformers"],
        "proposal_text": "Phát triển hệ thống chatbot hỗ trợ tuyển sinh bằng mô hình RAG",
        "advisor_id": "ADV001",
    }
    response = client.post("/api/v1/agent/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["advisor_id"] == "ADV001"
    assert 0.0 <= data["compatibility_score"] <= 1.0
    assert "is_quota_available" in data
    assert len(data["strengths"]) > 0
