"""Query Analyzer Node: parses student intent, tech skills, and target research field."""

import re
from typing import Dict, Any
from src.agents.state import AgentState


def analyze_query_node(state: AgentState) -> Dict[str, Any]:
    """Node that extracts intent and key parameters from user messages and student profile."""
    messages = state.get("messages", [])
    user_query = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            user_query = msg.get("content", "")
            break

    profile = state.get("student_profile", {}) or {}
    skills = list(profile.get("skills", []))
    interests = list(profile.get("interests", []))

    # Keyword extraction heuristics
    tech_keywords = ["python", "pytorch", "tensorflow", "nlp", "llm", "rag", "react", "fastapi", "docker", "vision", "graph", "microservices"]
    query_lower = user_query.lower()
    for kw in tech_keywords:
        if kw in query_lower and kw not in skills:
            skills.append(kw)

    # Intent classification
    intent = "find_advisor"
    if any(w in query_lower for w in ["đề tài", "chủ đề", "hướng nghiên cứu", "gợi ý"]):
        intent = "topic_exploration"
    elif any(w in query_lower for w in ["phù hợp", "điểm số", "tương đồng", "đánh giá"]):
        intent = "compatibility_check"
    elif any(w in query_lower for w in ["chỉ tiêu", "quota", "còn nhận"]):
        intent = "quota_inquiry"

    detected_field = "Trí tuệ Nhân tạo & Khoa học Dữ liệu"
    if any(w in query_lower for w in ["web", "microservice", "devops", "phần mềm"]):
        detected_field = "Kỹ thuật Phần mềm & Hệ thống Phân tán"
    elif any(w in query_lower for w in ["nlp", "ngôn ngữ", "text", "llm"]):
        detected_field = "Xử lý Ngôn ngữ Tự nhiên (NLP)"
    elif any(w in query_lower for w in ["ảnh", "vision", "yolo", "thị giác"]):
        detected_field = "Thị giác Máy tính (Computer Vision)"

    extracted_intent = {
        "intent": intent,
        "target_field": detected_field,
        "extracted_skills": skills,
        "interests": interests or [detected_field],
        "raw_query": user_query,
    }

    reasoning_steps = list(state.get("reasoning_steps", []))
    reasoning_steps.append(
        f"[Phân tích Ngữ nghĩa] Đã nhận diện ý định: '{intent}', lĩnh vực quan tâm: '{detected_field}' với {len(skills)} kỹ năng cốt lõi."
    )

    return {
        "extracted_intent": extracted_intent,
        "reasoning_steps": reasoning_steps,
        "status": "analyzed",
    }
