# Chương 3: Thiết Kế Kiến Trúc — 3-Tier, Diagram & ADR
*Thời gian ước tính: 6 giờ*

---

## 3.1 Mô Hình 3 Tầng Tổng Thể (3-Tier Architecture)

Hệ thống được thiết kế theo nguyên lý phân tách trách nhiệm (Separation of Concerns):

1. **Presentation Tier (Tầng Trình Diễn)**:
   - `Next.js 14 Dashboard`: Giao diện web tương tác thời gian thực dành cho sinh viên, giảng viên và ban quản lý khoa. Sử dụng TailwindCSS và React Query.
   - `Streamlit Lab UI`: Môi trường kiểm thử và trực quan hóa thuật toán phân bổ dành cho các nhà nghiên cứu dữ liệu.
2. **Business & Agent Logic Tier (Tầng Xử Lý Nghiệp Vụ)**:
   - `FastAPI Gateway`: Cung cấp RESTful endpoints chuẩn OpenAPI, xử lý xác thực, kiểm tra dữ liệu qua Pydantic v2 và stream SSE.
   - `LangGraph AI Agent`: Quản lý đồ thị trạng thái tư vấn học thuật, điều phối các công cụ (Agent Tools) và LLM Client.
   - `Optimization Core`: Module thuật toán Hungarian và Maskable PPO thực thi phân bổ sinh viên - giảng viên.
3. **Data Tier (Tầng Dữ Liệu)**:
   - `MongoDB`: Lưu trữ hồ sơ sinh viên, thông tin giảng viên, ma trận nguyện vọng và lịch sử phân bổ.
   - `SQLite & Curated JSON`: Lưu trữ dữ liệu danh mục chuẩn hóa phục vụ tra cứu tốc độ cao cục bộ.

## 3.2 Architecture Decision Records (ADR)

### ADR-01: Lựa chọn LangGraph làm Agent Orchestrator
- **Bối cảnh**: Hệ thống cần một luồng điều khiển quyết định nhiều bước (Multi-step Reasoning) có tính kiểm soát cao, khả năng quay lui và quản lý trạng thái rõ ràng.
- **Quyết định**: Sử dụng `LangGraph` thay vì các framework agent tự do (như BabyAGI hay CrewAI) vì LangGraph cung cấp đồ thị trạng thái tuần tự và có nhánh rẽ (StateGraph with conditional edges), đảm bảo quá trình tư vấn không bị lạc đề (hallucination drift).
- **Hệ quả**: Code dễ kiểm thử đơn vị trên từng Node, có thể chạy offline với Mock LLM hoặc cắm nối với OpenAI/Gemini khi triển khai thực tế.

### ADR-02: Phối hợp Thuật toán Hungarian và Reinforcement Learning (PPO)
- **Bối cảnh**: Bài toán phân bổ sinh viên - giảng viên là bài toán gán có trọng số với ràng buộc chỉ tiêu cứng (Quota Constraints).
- **Quyết định**: Sử dụng thuật toán Hungarian để tạo lời giải đường cơ sở (Baseline) tối ưu tổng độ tương đồng. Áp dụng Reinforcement Learning với kỹ thuật Maskable PPO để học chính sách phân bổ linh hoạt trong các điều kiện ràng buộc động.
- **Hệ quả**: Đáp ứng 100% không vi phạm chỉ tiêu giảng viên trong mọi tình huống.
