"""Retriever Node: fetches relevant faculty advisors and historical theses using agent tools."""

from typing import Dict, Any
from src.agents.state import AgentState
from src.agents.tools.advisor_tools import search_advisors
from src.agents.tools.thesis_tools import search_past_theses


def retrieve_data_node(state: AgentState) -> Dict[str, Any]:
    """Retrieves candidate advisors and similar completed theses from data store."""
    intent_data = state.get("extracted_intent", {})
    target_field = intent_data.get("target_field", "")
    skills = intent_data.get("extracted_skills", [])
    search_keyword = " ".join(skills[:3]) if skills else target_field

    # Tool executions
    candidates = search_advisors(query=search_keyword)
    past_theses = search_past_theses(keyword=search_keyword)

    tool_calls = list(state.get("tool_calls", []))
    tool_calls.append({
        "tool_name": "search_advisors",
        "input_args": {"query": search_keyword},
        "output_summary": f"Tìm thấy {len(candidates)} giảng viên tiềm năng phù hợp",
    })
    tool_calls.append({
        "tool_name": "search_past_theses",
        "input_args": {"keyword": search_keyword},
        "output_summary": f"Tìm thấy {len(past_theses)} khóa luận tương đồng",
    })

    reasoning_steps = list(state.get("reasoning_steps", []))
    reasoning_steps.append(
        f"[Truy xuất Dữ liệu] Đã tra cứu qua Vector & Keyword Search: thu được {len(candidates)} giảng viên và {len(past_theses)} đề tài khóa luận tham khảo."
    )

    return {
        "candidate_advisors": candidates,
        "relevant_theses": past_theses,
        "tool_calls": tool_calls,
        "reasoning_steps": reasoning_steps,
        "status": "retrieved",
    }
