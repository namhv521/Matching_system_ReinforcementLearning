"""Integration tests for LangGraph matching agent graph execution."""

import pytest
from src.agents.graph import run_matching_agent
from src.agents.nodes.query_analyzer import analyze_query_node
from src.agents.nodes.retriever import retrieve_data_node
from src.agents.nodes.matcher import evaluate_matching_node
from src.agents.nodes.synthesizer import synthesize_response_node


def test_individual_nodes():
    """Test individual state transformation in each node."""
    init_state = {
        "messages": [{"role": "user", "content": "Em muốn làm đề tài về Computer Vision và YOLO"}],
        "student_profile": {"skills": ["python", "opencv"], "gpa": 3.4},
        "reasoning_steps": [],
        "tool_calls": [],
    }

    # 1. Analyze node
    state_analyzed = analyze_query_node(init_state)
    assert "extracted_intent" in state_analyzed
    assert "vision" in state_analyzed["extracted_intent"]["target_field"].lower() or "thị giác" in state_analyzed["extracted_intent"]["target_field"].lower()

    # 2. Retrieve node
    init_state.update(state_analyzed)
    state_retrieved = retrieve_data_node(init_state)
    assert len(state_retrieved["candidate_advisors"]) > 0

    # 3. Matcher node
    init_state.update(state_retrieved)
    state_evaluated = evaluate_matching_node(init_state)
    assert len(state_evaluated["match_evaluations"]) > 0

    # 4. Synthesizer node
    init_state.update(state_evaluated)
    state_final = synthesize_response_node(init_state)
    assert "final_answer" in state_final
    assert len(state_final["final_answer"]) > 50


def test_full_agent_workflow():
    """Test full agent invocation on student query."""
    res = run_matching_agent(
        query="Tôi muốn làm khóa luận về Xử lý ngôn ngữ tự nhiên và RAG",
        student_profile={"skills": ["Python", "Transformers"], "gpa": 3.6},
    )

    assert res["status"] in ("completed", "synthesized")
    assert len(res["reasoning_steps"]) >= 4
    assert len(res["candidate_advisors"]) > 0
    assert len(res["match_evaluations"]) > 0
    assert "KẾT QUẢ TƯ VẤN" in res["final_answer"]
