"""Synthesizer Node: produces full Vietnamese academic consultation and recommendation response."""

from typing import Dict, Any
from src.agents.state import AgentState
from src.services.llm import get_llm_client


def synthesize_response_node(state: AgentState) -> Dict[str, Any]:
    """Generates the final structured advice for the student."""
    intent = state.get("extracted_intent", {})
    evaluations = state.get("match_evaluations", [])
    theses = state.get("relevant_theses", [])
    raw_query = intent.get("raw_query", "")

    top_eval = evaluations[:3]
    top_theses = theses[:3]

    lines = []
    lines.append("### 🎓 KẾT QUẢ TƯ VẤN VÀ ĐỀ XUẤT GIẢNG VIÊN HƯỚNG DẪN KLTN\n")
    lines.append(f"Chào bạn, hệ thống AI Matching đã phân tích yêu cầu: *\"{raw_query}\"*\n")

    lines.append("#### 1. Danh sách Giảng viên Hướng dẫn phù hợp nhất:")
    for idx, adv in enumerate(top_eval, 1):
        status_badge = "✅ Còn chỉ tiêu" if adv["can_accept"] else "⚠️ Hết chỉ tiêu"
        lines.append(
            f"**{idx}. {adv['title']} {adv['name']}** - {adv['department']}\n"
            f"   - **Hướng nghiên cứu chính**: {adv['primary_field']}\n"
            f"   - **Độ tương đồng học thuật**: `{adv['compatibility_score'] * 100:.1f}%` ({adv['verdict']})\n"
            f"   - **Tình trạng chỉ tiêu**: {status_badge} (còn nhận: {adv['quota_available']} sinh viên)\n"
            f"   - **Kỹ năng giao thoa**: {', '.join(adv['common_skills']) if adv['common_skills'] else 'Nền tảng CNTT'}\n"
        )

    if top_theses:
        lines.append("#### 2. Các đề tài Khóa luận tiêu biểu các năm trước để tham khảo:")
        for t in top_theses:
            title = t.get("title") or t.get("thesis_title", "Đề tài tham khảo")
            lines.append(
                f"- **{title}** ({t.get('year', 2024)})\n"
                f"  *Lĩnh vực*: {t.get('field', 'CNTT')} | *Công nghệ*: `{', '.join(t.get('tech_stack', []))}`"
            )
        lines.append("")

    lines.append("#### 3. Khuyến nghị hành động tiếp theo:")
    lines.append(
        "1. Chuẩn bị đề cương sơ bộ (1-2 trang) nêu rõ bài toán, công nghệ dự kiến và mục tiêu nghiên cứu.\n"
        "2. Liên hệ trao đổi trực tiếp với Giảng viên ưu tiên số 1 để xin ý kiến định hướng đề tài.\n"
        "3. Đăng ký nguyện vọng chính thức trên cổng thông tin phân bổ KLTN trước hạn quy định."
    )

    final_text = "\n".join(lines)

    reasoning_steps = list(state.get("reasoning_steps", []))
    reasoning_steps.append(
        f"[Tổng hợp Phản hồi] Đã sinh tư vấn chi tiết kết hợp {len(top_eval)} giảng viên và {len(top_theses)} đề tài tham chiếu."
    )

    return {
        "final_answer": final_text,
        "reasoning_steps": reasoning_steps,
        "status": "completed",
    }
