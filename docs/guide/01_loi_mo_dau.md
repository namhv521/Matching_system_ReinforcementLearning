# Chương 1: Lời Mở Đầu — Mục Tiêu & Cách Sử Dụng
*Thời gian ước tính: 15 phút*

---

## 1.1 Bối Cảnh & Vấn Đề Thực Tiễn
Trong các trường đại học khối kỹ thuật và công nghệ thông tin, kỳ làm **Khóa luận tốt nghiệp (KLTN)** là giai đoạn mang tính quyết định. Tuy nhiên, quy trình truyền thống thường gặp các nút thắt lớn:
1. **Bất cân xứng thông tin**: Sinh viên không nắm rõ các hướng nghiên cứu hiện hành của giảng viên; giảng viên không có đủ thời gian phỏng vấn chi tiết năng lực từng sinh viên.
2. **Quá tải chỉ tiêu (Quota Bottlenecks)**: Các giảng viên danh tiếng thường bị quá tải nguyện vọng, trong khi các thầy cô trẻ hoặc hướng đề tài mới chưa tiếp cận được sinh viên phù hợp.
3. **Phân bổ thủ công thiếu minh bạch**: Việc xếp cặp bằng bảng tính Excel dễ dẫn đến sai sót, xung đột lợi ích và không tối ưu hóa được độ tương đồng chuyên môn.

## 1.2 Mục Tiêu Của Dự Án
Dự án được xây dựng với mục tiêu giải quyết trọn vẹn bài toán trên bằng cách kết hợp:
- **LangGraph AI Agent**: Hệ thống tư vấn tương tác thông minh, phân tích ngôn ngữ tự nhiên từ sinh viên để gợi ý hướng đề tài và giảng viên phù hợp nhất.
- **Thuật toán Tối ưu hóa Kết hợp**: Áp dụng Maskable Proximal Policy Optimization (PPO RL) và thuật toán Hungarian cổ điển để giải bài toán phân bổ toàn cục thỏa mãn 100% ràng buộc cứng về chỉ tiêu.
- **Nền tảng Full-Stack Chuẩn Doanh Nghiệp**: FastAPI Backend bất đồng bộ, Next.js 14 Dashboard trực quan, lưu trữ MongoDB linh hoạt và hệ thống kiểm thử tự động.

## 1.3 Cách Sử Dụng Bộ Sách Kỹ Thuật Này
Tài liệu này được biên soạn cho cả nhà phát triển (Developers), kỹ sư AI (MLE/Data Scientists) và hội đồng đánh giá:
- **Chương 2-3**: Dành cho việc khởi tạo môi trường và thấu hiểu kiến trúc.
- **Chương 4-5**: Hướng dẫn chuyên sâu về cài đặt LangGraph Agent và REST API.
- **Chương 6-7**: Hướng dẫn xây dựng giao diện và triển khai Docker, CI/CD.
- **Chương 8-10**: Quy chuẩn kiểm thử, đánh giá RAGAS và chuẩn bị cho Demo Day.
