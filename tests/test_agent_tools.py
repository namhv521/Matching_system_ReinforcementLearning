"""Unit tests for AI Agent Tools."""

import pytest
from src.agents.tools.advisor_tools import search_advisors, check_advisor_capacity
from src.agents.tools.thesis_tools import search_past_theses, suggest_thesis_topics
from src.agents.tools.matching_tools import (
    compute_compatibility_score,
    get_matching_system_benchmarks,
)


def test_search_advisors():
    """Test searching advisors by keyword."""
    results = search_advisors(query="NLP")
    assert isinstance(results, list)
    assert len(results) > 0
    assert "advisor_id" in results[0]
    assert "relevance_score" in results[0]


def test_check_advisor_capacity():
    """Test checking advisor capacity constraints."""
    cap = check_advisor_capacity("ADV001")
    assert "quota_available" in cap
    assert "can_accept_student" in cap
    assert cap["quota_max"] >= cap["quota_current"]


def test_search_past_theses():
    """Test searching past theses."""
    results = search_past_theses(keyword="Microservices")
    assert isinstance(results, list)
    assert len(results) > 0
    assert "title" in results[0]
    assert "similarity" in results[0]


def test_suggest_thesis_topics():
    """Test topic expansion suggestions."""
    suggestions = suggest_thesis_topics("AI", ["Graph", "Healthcare"])
    assert isinstance(suggestions, list)
    assert len(suggestions) >= 3


def test_compute_compatibility_score():
    """Test semantic compatibility scoring tool."""
    res = compute_compatibility_score(
        student_skills=["python", "nlp", "transformers"],
        thesis_summary="Nghiên cứu mô hình ngôn ngữ lớn",
        advisor_id="ADV001",
    )
    assert 0.0 <= res["compatibility_score"] <= 1.0
    assert "evaluation_verdict" in res
    assert len(res["common_skills"]) > 0


def test_get_matching_benchmarks():
    """Test retrieving system algorithm benchmarks."""
    benchmarks = get_matching_system_benchmarks()
    assert "benchmarks" in benchmarks
    assert len(benchmarks["benchmarks"]) >= 3
