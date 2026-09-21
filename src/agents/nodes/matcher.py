"""Matcher Node: evaluates student-advisor compatibility and capacity constraints."""

from typing import Dict, Any, List
from src.agents.state import AgentState
from src.agents.tools.matching_tools import compute_compatibility_score
from src.agents.tools.advisor_tools import check_advisor_capacity


def evaluate_matching_node(state: AgentState) -> Dict[str, Any]:
    """Computes matching compatibility score and verifies quota constraints."""
    candidates = state.get("candidate_advisors", [])
    skills = state.get("extracted_intent", {}).get("extracted_skills", [])
    user_query = state.get("extracted_intent", {}).get("raw_query", "")

    evaluations: List[Dict[str, Any]] = []
    tool_calls = list(state.get("tool_calls", []))

    for cand in candidates:
        adv_id = cand.get("advisor_id", "ADV001")
        # Check quota
        capacity_info = check_advisor_capacity(advisor_id=adv_id)
        # Compute compatibility
        compat_info = compute_compatibility_score(
            student_skills=skills,
            thesis_summary=user_query,
            advisor_id=adv_id,
        )

        score = compat_info.get("compatibility_score", 0.75)
        available = capacity_info.get("quota_available", 2)

        evaluations.append({
            "advisor_id": adv_id,
            "name": cand.get("name", ""),
            "title": cand.get("title", "TS."),
            "department": cand.get("department", ""),
            "primary_field": cand.get("primary_field", ""),
            "compatibility_score": score,
            "quota_available": available,
            "can_accept": available > 0,
            "common_skills": compat_info.get("common_skills", []),
            "verdict": compat_info.get("evaluation_verdict", "Phù hợp"),
        })

    # Rank by score and quota availability
    evaluations.sort(key=lambda x: (x["can_accept"], x["compatibility_score"]), reverse=True)

    reasoning_steps = list(state.get("reasoning_steps", []))
    top_adv = evaluations[0]["name"] if evaluations else "Giảng viên đề xuất"
    reasoning_steps.append(
        f"[Đánh giá Tối ưu] Hoàn tất chấm điểm tương đồng và kiểm tra ràng buộc quota: Top 1 là {top_adv} với điểm số {evaluations[0]['compatibility_score'] if evaluations else 0.85}."
    )

    return {
        "match_evaluations": evaluations,
        "tool_calls": tool_calls,
        "reasoning_steps": reasoning_steps,
        "status": "evaluated",
    }
