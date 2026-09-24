# Chương 4: LangGraph Agent — State, Node, Edge, Tool & RAG
*Thời gian ước tính: 8 giờ*

---

## 4.1 Thiết Kế Trạng Thái (Agent State Schema)
Trạng thái trung tâm của Agent được định nghĩa bằng `TypedDict` trong file `src/agents/state.py`:

```python
class AgentState(TypedDict, total=False):
    messages: List[Dict[str, str]]
    student_profile: Dict[str, Any]
    extracted_intent: Dict[str, Any]
    candidate_advisors: List[Dict[str, Any]]
    relevant_theses: List[Dict[str, Any]]
    match_evaluations: List[Dict[str, Any]]
    reasoning_steps: List[str]
    tool_calls: List[Dict[str, Any]]
    final_answer: str
    iteration_count: int
    status: str
    session_id: str
    error: Optional[str]
```

## 4.2 Các Node Chức Năng Trong Đồ Thị
Agent vận hành thông qua 4 nút xử lý độc lập:

1. **Query Analyzer Node (`src/agents/nodes/query_analyzer.py`)**:
   - Nhận diện câu hỏi của sinh viên.
   - Bóc tách từ khóa công nghệ (`python`, `pytorch`, `fastapi`, `nlp`,...).
   - Phân loại ý định: Tìm giảng viên, gợi ý đề tài, kiểm tra độ tương thích hoặc hỏi chỉ tiêu.
2. **Academic Retriever Node (`src/agents/nodes/retriever.py`)**:
   - Gọi các Agent Tools để tìm kiếm danh sách giảng viên trong cùng chuyên ngành và tra cứu các đề tài khóa luận tương tự của những năm trước.
3. **Matcher Node (`src/agents/nodes/matcher.py`)**:
   - Tính toán chỉ số tương thích (Compatibility Score) dựa trên mức độ giao thoa kỹ năng.
   - Kiểm tra ràng buộc chỉ tiêu hiện hành của giảng viên (`quota_current < quota_max`).
   - Sắp xếp và chọn lọc Top giảng viên tiềm năng nhất.
4. **Synthesizer Node (`src/agents/nodes/synthesizer.py`)**:
   - Tổng hợp toàn bộ dữ kiện thành báo cáo tư vấn học thuật hoàn chỉnh bằng tiếng Việt.
   - Đưa ra khuyến nghị cụ thể về 3 bước hành động tiếp theo cho sinh viên.

## 4.3 Hệ Thống Công Cụ Của Agent (Agent Tools)
Các công cụ được đặt trong `src/agents/tools/`:
- `search_advisors(query, department)`: Tra cứu giảng viên theo từ khóa chuyên môn.
- `check_advisor_capacity(advisor_id)`: Kiểm tra dung lượng còn trống và chỉ tiêu hướng dẫn.
- `search_past_theses(keyword)`: Tìm kiếm đề tài khóa luận tiêu biểu làm tư liệu tham khảo.
- `compute_compatibility_score(student_skills, thesis_summary, advisor_id)`: Tính toán điểm tương thích học thuật.
