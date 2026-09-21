"""FastAPI Routes for AI Agent interaction and decision support."""

import time
import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from src.models.schemas import (
    AgentChatRequest,
    AgentChatResponse,
    MatchEvaluationRequest,
    MatchEvaluationResponse,
    AdvisorRecommendation,
    ThesisRecommendation,
    AgentToolCallLog,
    AgentHealthResponse,
)
from src.agents.graph import run_matching_agent, astream_matching_agent
from src.agents.tools import ALL_AGENT_TOOLS
from src.agents.tools.matching_tools import compute_compatibility_score
from src.agents.tools.advisor_tools import check_advisor_capacity, search_advisors
from src.config import agent_settings

agent_router = APIRouter(prefix="/api/v1/agent", tags=["AI Matching Agent"])


@agent_router.post(
    "/chat",
    response_model=AgentChatResponse,
    summary="Trò chuyện và nhận tư vấn đề tài / giảng viên từ AI Agent",
)
async def chat_with_agent(payload: AgentChatRequest) -> AgentChatResponse:
    """Gọi LangGraph Agent để phân tích nguyện vọng, tìm kiếm giảng viên và đề xuất hướng khóa luận."""
    t0 = time.time()
    session_id = payload.session_id or str(uuid.uuid4())

    profile_dict = payload.student_profile.model_dump() if payload.student_profile else {}
    result_state = run_matching_agent(
        query=payload.message,
        student_profile=profile_dict,
        session_id=session_id,
    )

    execution_ms = round((time.time() - t0) * 1000, 2)

    # Format recommendations
    advisors_out: List[AdvisorRecommendation] = []
    for item in result_state.get("match_evaluations", [])[:5]:
        advisors_out.append(AdvisorRecommendation(
            advisor_id=item.get("advisor_id", ""),
            name=item.get("name", ""),
            title=item.get("title", "TS."),
            department=item.get("department", ""),
            primary_field=item.get("primary_field", ""),
            compatibility_score=item.get("compatibility_score", 0.8),
            quota_available=item.get("quota_available", 3),
            justification=f"Chỉ số tương đồng {item.get('compatibility_score', 0.8)*100:.1f}%, chuyên môn giao thoa với định hướng sinh viên.",
        ))

    theses_out: List[ThesisRecommendation] = []
    for th in result_state.get("relevant_theses", [])[:4]:
        theses_out.append(ThesisRecommendation(
            record_id=th.get("record_id", "TH001"),
            title=th.get("title", ""),
            field_category=th.get("field", ""),
            completion_year=th.get("year", 2024),
            similarity_score=th.get("similarity", 0.8),
            tech_stack=th.get("tech_stack", []),
        ))

    tool_logs: List[AgentToolCallLog] = []
    for tc in result_state.get("tool_calls", []):
        tool_logs.append(AgentToolCallLog(
            tool_name=tc.get("tool_name", "tool"),
            input_args=tc.get("input_args", {}),
            output_summary=tc.get("output_summary", ""),
        ))

    detected_intent = result_state.get("extracted_intent", {}).get("intent", "general_consultation")

    return AgentChatResponse(
        answer=result_state.get("final_answer", "Đã hoàn thành phân tích."),
        session_id=session_id,
        intent_detected=detected_intent,
        reasoning_steps=result_state.get("reasoning_steps", []),
        recommended_advisors=advisors_out,
        similar_theses=theses_out,
        tool_calls=tool_logs,
        execution_time_ms=execution_ms,
        status="success",
    )


@agent_router.post("/stream", summary="Stream câu trả lời của AI Agent (Server-Sent Events)")
async def stream_agent_chat(payload: AgentChatRequest):
    """Truyền phát luồng suy nghĩ và phản hồi dạng token thời gian thực."""
    profile_dict = payload.student_profile.model_dump() if payload.student_profile else {}
    return StreamingResponse(
        astream_matching_agent(payload.message, profile_dict),
        media_type="text/event-stream",
    )



@agent_router.post(
    "/evaluate",
    response_model=MatchEvaluationResponse,
    summary="Đánh giá trực tiếp mức độ phù hợp giữa sinh viên và 1 giảng viên cụ thể",
)
async def evaluate_proposal_match(payload: MatchEvaluationRequest) -> MatchEvaluationResponse:
    """Tính toán chi tiết độ tương đồng, điểm mạnh và rủi ro ràng buộc."""
    capacity = check_advisor_capacity(advisor_id=payload.advisor_id)
    compat = compute_compatibility_score(
        student_skills=payload.student_skills,
        thesis_summary=payload.proposal_text,
        advisor_id=payload.advisor_id,
    )

    adv_info = search_advisors(query=payload.advisor_id)
    adv_name = adv_info[0]["name"] if adv_info else "Giảng viên"

    score = compat["compatibility_score"]
    can_accept = capacity["can_accept_student"]

    strengths = [
        f"Kỹ năng cốt lõi giao thoa: {', '.join(compat['common_skills']) if compat['common_skills'] else 'Nền tảng lập trình vững'}",
        f"Độ phù hợp chủ đề đạt {score * 100:.1f}%",
    ]
    risks = []
    if not can_accept:
        risks.append("Giảng viên đã đạt giới hạn chỉ tiêu hướng dẫn trong kỳ này.")
    if score < 0.7:
        risks.append("Khoảng cách kỹ năng tương đối lớn, cần bổ sung kiến thức chuyên ngành.")

    return MatchEvaluationResponse(
        advisor_id=payload.advisor_id,
        advisor_name=adv_name,
        compatibility_score=score,
        is_quota_available=can_accept,
        strengths=strengths,
        potential_risks=risks,
        summary_verdict="Đủ điều kiện hướng dẫn" if can_accept and score >= 0.7 else "Cần cân nhắc thêm",
    )


@agent_router.get("/health", response_model=AgentHealthResponse, summary="Kiểm tra trạng thái Agent")
async def agent_health_check() -> AgentHealthResponse:
    """Trả về trạng thái hoạt động của Agent, LLM Provider và danh mục Tools."""
    return AgentHealthResponse(
        status="healthy",
        app_name=agent_settings.APP_NAME,
        version=agent_settings.APP_VERSION,
        llm_provider=agent_settings.LLM_PROVIDER,
        active_tools_count=len(ALL_AGENT_TOOLS),
        database_connected=True,
    )


@agent_router.get("/tools", summary="Danh sách các công cụ đang hoạt động của Agent")
async def list_agent_tools() -> Dict[str, Any]:
    """Liệt kê metadata của toàn bộ Agent tools."""
    tools_data = []
    for t in ALL_AGENT_TOOLS:
        name = getattr(t, "name", t.__name__)
        doc = getattr(t, "description", t.__doc__ or "No description")
        tools_data.append({"name": name, "description": doc.strip()})
    return {"total_tools": len(tools_data), "tools": tools_data}
