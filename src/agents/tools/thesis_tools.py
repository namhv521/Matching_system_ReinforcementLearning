"""Thesis search and topic suggestion tools for AI Agent."""

import json
from pathlib import Path
from typing import List, Dict, Any
from src.agents.tools.base import tool

CURATED_DIR = Path(__file__).resolve().parents[3] / "data" / "curated"


def _load_theses_fallback() -> List[Dict[str, Any]]:
    """Load past theses records."""
    json_path = CURATED_DIR / "theses.json"
    if json_path.exists():
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return [
        {
            "record_id": "TH001",
            "thesis_title": "Xây dựng hệ thống khuyến nghị khóa học trực tuyến sử dụng Graph Neural Networks",
            "field_category": "Trí tuệ Nhân tạo & Khai phá Dữ liệu",
            "completion_year": 2024,
            "tech_stack": ["Python", "PyTorch Geometric", "FastAPI", "Neo4j"],
            "score": 9.2,
        },
        {
            "record_id": "TH002",
            "thesis_title": "Ứng dụng mô hình ngôn ngữ lớn (LLM) và RAG trong hỗ trợ giải đáp quy chế học vụ",
            "field_category": "Xử lý Ngôn ngữ Tự nhiên (NLP)",
            "completion_year": 2024,
            "tech_stack": ["LangChain", "OpenAI API", "ChromaDB", "React"],
            "score": 9.5,
        },
        {
            "record_id": "TH003",
            "thesis_title": "Tối ưu hóa kiến trúc Microservices chịu tải cao dựa trên Kubernetes và gRPC",
            "field_category": "Kỹ thuật Phần mềm & Cloud Computing",
            "completion_year": 2023,
            "tech_stack": ["Go", "Docker", "Kubernetes", "gRPC", "Prometheus"],
            "score": 8.8,
        },
        {
            "record_id": "TH004",
            "thesis_title": "Nhận diện tổn thương võng mạc đái tháo đường từ ảnh đáy mắt bằng Deep Learning",
            "field_category": "Thị giác Máy tính (Computer Vision)",
            "completion_year": 2023,
            "tech_stack": ["Python", "TensorFlow", "OpenCV", "Flask"],
            "score": 9.0,
        },
    ]


@tool
def search_past_theses(keyword: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Tìm kiếm các đề tài khóa luận các năm trước theo từ khóa công nghệ hoặc lĩnh vực nghiên cứu."""
    theses = _load_theses_fallback()
    kw_lower = keyword.lower()
    matches = []

    for item in theses:
        title = item.get("thesis_title", "")
        field = item.get("field_category", "")
        stack = item.get("tech_stack", [])

        match_score = 0.0
        if kw_lower in title.lower():
            match_score += 0.6
        if kw_lower in field.lower():
            match_score += 0.4
        for tech in stack:
            if kw_lower in tech.lower():
                match_score += 0.3

        if match_score > 0.0 or not keyword:
            matches.append({
                "record_id": item.get("record_id", "TH000"),
                "title": title,
                "field": field,
                "year": item.get("completion_year", 2024),
                "tech_stack": stack,
                "similarity": min(1.0, match_score if keyword else 0.75),
            })

    matches.sort(key=lambda x: x["similarity"], reverse=True)
    normalized_fallback = [
        {
            "record_id": item.get("record_id", "TH000"),
            "title": item.get("thesis_title") or item.get("title", ""),
            "field": item.get("field_category") or item.get("field", ""),
            "year": item.get("completion_year") or item.get("year", 2024),
            "tech_stack": item.get("tech_stack", []),
            "similarity": item.get("score", 8.5) / 10.0,
        }
        for item in theses[:max_results]
    ]
    return matches[:max_results] if matches else normalized_fallback


@tool
def suggest_thesis_topics(field: str, keywords: List[str]) -> List[str]:
    """Gợi ý các hướng phát triển đề tài khóa luận mới mẻ dựa trên chuyên ngành và từ khóa mong muốn."""
    kw_str = ", ".join(keywords) if keywords else "AI & Software"
    return [
        f"Nghiên cứu ứng dụng {kw_str} trong bài toán tự động hóa phân bổ tài nguyên học thuật",
        f"Phát triển nền tảng Multi-Agent hỗ trợ ra quyết định phân tích dữ liệu lớn trong lĩnh vực {field}",
        f"Đánh giá và tối ưu hóa mô hình học sâu kết hợp Explainable AI (XAI) cho bài toán dự báo thông minh",
    ]
