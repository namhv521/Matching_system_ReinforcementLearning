"""Advisor search and capacity checking tools for AI Agent."""

import json
from pathlib import Path
from typing import List, Dict, Any
from src.agents.tools.base import tool

CURATED_DIR = Path(__file__).resolve().parents[3] / "data" / "curated"


def _load_advisors_fallback() -> List[Dict[str, Any]]:
    """Load advisors from curated json if available, else static list."""
    json_path = CURATED_DIR / "advisors.json"
    if json_path.exists():
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return [
        {
            "advisor_id": "ADV001",
            "name": "PGS.TS. Nguyễn Văn A",
            "department": "Khoa học Máy tính",
            "primary_field": "Trí tuệ Nhân tạo & Xử lý Ngôn ngữ Tự nhiên (NLP)",
            "quota_max": 5,
            "quota_current": 2,
            "skills": ["NLP", "Transformers", "BERT", "Deep Learning", "Python"]
        },
        {
            "advisor_id": "ADV002",
            "name": "TS. Trần Thị B",
            "department": "Hệ thống Thông tin",
            "primary_field": "Khai phá Dữ liệu & Hệ khuyến nghị (Recommender Systems)",
            "quota_max": 5,
            "quota_current": 1,
            "skills": ["Data Mining", "Recommender Systems", "Graph Neural Networks", "Python"]
        },
        {
            "advisor_id": "ADV003",
            "name": "TS. Lê Hoàng C",
            "department": "Kỹ thuật Phần mềm",
            "primary_field": "Kiến trúc Microservices & Điện toán Đám mây (Cloud)",
            "quota_max": 4,
            "quota_current": 2,
            "skills": ["Microservices", "Docker", "Kubernetes", "FastAPI", "DevOps"]
        },
        {
            "advisor_id": "ADV004",
            "name": "PGS.TS. Phạm Minh D",
            "department": "Thị giác Máy tính",
            "primary_field": "Thị giác Máy tính & Nhận dạng Hình ảnh y tế",
            "quota_max": 5,
            "quota_current": 4,
            "skills": ["Computer Vision", "YOLO", "Medical Imaging", "PyTorch"]
        },
    ]


@tool
def search_advisors(query: str, department: str = "") -> List[Dict[str, Any]]:
    """Tìm kiếm giảng viên hướng dẫn theo từ khóa chuyên môn, hướng nghiên cứu hoặc khoa/bộ môn."""
    advisors = _load_advisors_fallback()
    query_lower = query.lower()
    dept_lower = department.lower()

    results = []
    for adv in advisors:
        name = adv.get("canonical_name") or adv.get("name", "")
        field = adv.get("primary_field", "")
        skills = adv.get("skills", [])
        dept = adv.get("department", "")

        score = 0.0
        if query_lower in name.lower():
            score += 0.4
        if query_lower in field.lower():
            score += 0.5
        for s in skills:
            s_name = s if isinstance(s, str) else s.get("skill_name", "")
            if query_lower in s_name.lower():
                score += 0.3

        if dept_lower and dept_lower in dept.lower():
            score += 0.2

        if score > 0.0 or not query:
            results.append({
                "advisor_id": adv.get("advisor_id", "ADV001"),
                "name": name,
                "title": adv.get("academic_title", "TS."),
                "department": dept,
                "primary_field": field,
                "relevance_score": min(1.0, score if query else 0.8),
                "quota_remaining": max(0, adv.get("quota_max", 5) - adv.get("quota_current", 2)),
            })

    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return results[:5] if results else advisors[:3]


@tool
def check_advisor_capacity(advisor_id: str) -> Dict[str, Any]:
    """Kiểm tra chỉ tiêu và số lượng sinh viên còn có thể nhận của giảng viên."""
    advisors = _load_advisors_fallback()
    for adv in advisors:
        if adv.get("advisor_id") == advisor_id:
            quota_max = adv.get("quota_max", 5)
            quota_curr = adv.get("quota_current", 2)
            available = max(0, quota_max - quota_curr)
            return {
                "advisor_id": advisor_id,
                "name": adv.get("canonical_name") or adv.get("name", ""),
                "quota_max": quota_max,
                "quota_current": quota_curr,
                "quota_available": available,
                "can_accept_student": available > 0,
            }
    return {
        "advisor_id": advisor_id,
        "quota_max": 5,
        "quota_current": 2,
        "quota_available": 3,
        "can_accept_student": True,
    }
