# Chương 5: FastAPI Backend — Routes, Validation & Streaming
*Thời gian ước tính: 6 giờ*

---

## 5.1 Cấu Trúc Tuyến Đường (FastAPI Routes)
Toàn bộ các endpoint dành riêng cho AI Agent được định nghĩa trong `src/api/routes.py` với tiền tố `/api/v1/agent`:

| Phương thức | Đường dẫn | Chức năng chính | Request Body / Params |
| :---: | :--- | :--- | :--- |
| `POST` | `/chat` | Chat tư vấn và nhận đề xuất danh sách giảng viên kèm đề tài | `AgentChatRequest` |
| `POST` | `/stream` | Truyền phát token suy nghĩ & câu trả lời (Server-Sent Events) | `AgentChatRequest` |
| `POST` | `/evaluate` | Đánh giá trực tiếp mức độ phù hợp sinh viên vs 1 giảng viên | `MatchEvaluationRequest` |
| `GET` | `/health` | Kiểm tra trạng thái hoạt động của Agent, LLM và Tools | Không có |
| `GET` | `/tools` | Liệt kê metadata và mô tả chức năng của các công cụ | Không có |

## 5.2 Xử Lý Dữ Liệu Qua Pydantic v2
Tất cả các mô hình dữ liệu đầu vào và đầu ra đều được kiểm tra kiểu dữ liệu nghiêm ngặt qua Pydantic schemas trong `src/models/schemas.py`:
- `StudentProfileInput`: Chứa GPA (0.0 - 4.0), danh sách kỹ năng công nghệ, hướng nghiên cứu mong muốn.
- `AdvisorRecommendation`: Bao gồm thông tin giảng viên, điểm số tương đồng, tình trạng chỉ tiêu và lý do đề xuất.
- `AgentChatResponse`: Trả về lời giải đáp hoàn chỉnh kèm các bước suy luận Chain-of-Thought (CoT) phục vụ việc giải thích mô hình.

## 5.3 Kỹ Thuật Server-Sent Events (SSE) Streaming
Hệ thống hỗ trợ phản hồi thời gian thực qua giao thức SSE:
1. Phát sinh các chunk `{"type": "thought", "content": "..."}` để người dùng quan sát quá trình suy luận của Agent.
2. Truyền phát các token phản hồi `{"type": "token", "content": "..."}` giúp tối ưu hóa thời gian hiển thị đầu tiên (Time To First Token - TTFT).
3. Kết thúc bằng tín hiệu `{"type": "done", "status": "completed"}`.
