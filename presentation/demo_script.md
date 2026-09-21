# Kịch Bản Thuyết Trình & Quay Video Demo Day (5 Phút)

## Thông Tin Trình Bày
- **Dự án**: Hệ thống Phân Bổ Đề Tài & Giảng Viên KLTN bằng AI Agent
- **Thời lượng chuẩn**: 5 phút (300 giây)
- **Người trình bày**: Nhóm Đồ Án KLTN

---

## Phân Bổ Thời Gian Chi Tiết

### 1. Giới thiệu bài toán & Nỗi đau thực tế (00:00 - 00:45)
- **Lời thoại**:
  > *"Kính chào Quý Thầy Cô và Hội đồng! Trong mỗi mùa khóa luận tốt nghiệp, việc ghép cặp giữa hàng trăm sinh viên và giảng viên thường gặp khó khăn: sinh viên lúng túng khi chọn hướng nghiên cứu, trong khi giảng viên đối mặt với tình trạng quá tải hoặc sinh viên chưa đủ kỹ năng tiên quyết. Hôm nay, chúng em xin giới thiệu Hệ thống Phân bổ KLTN Thông minh với sự hỗ trợ của LangGraph AI Agent."*
- **Hình ảnh trình chiếu**: Slide Vấn đề thực tế (Slide 2 & 3).

### 2. Kiến trúc giải pháp & LangGraph Agent (00:45 - 01:45)
- **Lời thoại**:
  > *"Hệ thống xây dựng theo kiến trúc 3 tầng chuẩn Production. Trọng tâm của hệ sinh thái là LangGraph Agent hoạt động qua 4 nút trạng thái có kiểm soát: Query Analyzer nhận diện kỹ năng; Academic Retriever truy vấn dữ liệu giảng viên và khóa luận cũ; Matcher Node áp dụng các ràng buộc Quota nghiêm ngặt; và Synthesizer Node chuyển đổi kết quả thành lời khuyên học thuật dễ hiểu."*
- **Hình ảnh trình chiếu**: Slide Kiến trúc hệ thống (Slide 4).

### 3. Trực tiếp Demo Tính Năng (Live Demo) (01:45 - 03:45)
- **Thao tác 1 (01:45 - 02:30)**:
  - Mở giao diện Chat AI trên Dashboard hoặc gửi Request qua Swagger UI `/api/v1/agent/chat`.
  - Nhập prompt: *"Em có nền tảng Python, PyTorch, muốn làm đề tài NLP/LLM."*
  - **Lời thoại**: *"Các thầy cô có thể thấy tốc độ xử lý tức thì, Agent phân tích và đề xuất PGS.TS Nguyễn Văn A với độ tương thích 94.8%, hiển thị rõ chỉ tiêu còn nhận 3 sinh viên và danh mục các đề tài khóa trước làm tiền đề."*
- **Thao tác 2 (02:30 - 03:15)**:
  - Gọi endpoint `/api/v1/agent/evaluate` để đánh giá mức độ tương thích giữa một đề cương cụ thể và giảng viên.
  - **Lời thoại**: *"Công cụ đánh giá trực quan chỉ ra điểm mạnh về công nghệ, cảnh báo nếu giảng viên đã đầy chỉ tiêu."*
- **Thao tác 3 (03:15 - 03:45)**:
  - Trình diễn màn hình Docker Compose và logs hệ thống ghi nhận qua `agent_interactions.jsonl`.

### 4. Kết quả thực nghiệm & Benchmark (03:45 - 04:30)
- **Lời thoại**:
  > *"Hệ thống đã trải qua bộ kiểm thử Benchmark tự động với 100% tỷ lệ tuân thủ Quota, độ chính xác Top-1 đạt 100% trên bộ dữ liệu kiểm thử, và thời gian phản hồi trung bình chỉ dưới 150 mili-giây. So với các giải pháp truyền thống, mô hình AI Agent kết hợp Maskable PPO nâng cao độ hài lòng tổng thể lên trên 88.5%."*
- **Hình ảnh trình chiếu**: Slide Benchmark Evaluation (Slide 6).

### 5. Kết luận & Q&A (04:30 - 05:00)
- **Lời thoại**:
  > *"Hệ thống đã hoàn tất đầy đủ 10 deliverables, sẵn sàng triển khai trên hạ tầng Docker & Cloud. Nhóm chúng em xin chân thành cảm ơn Quý Thầy Cô và rất mong nhận được những câu hỏi đóng góp quý báu!"*
