# Chương 6: Giao Diện Người Dùng — Next.js 14 & Streamlit
*Thời gian ước tính: 6 giờ*

---

## 6.1 Tổng Quan Kiến Trúc Giao Diện Kép (Dual-UI Architecture)
Dự án cung cấp hai giao diện tương tác phục vụ hai đối tượng người dùng khác nhau:
1. **Next.js 14 Web Application (`frontend/`)**: Giao diện người dùng chính thức (Production Portal) dành cho sinh viên, giảng viên và ban chủ nhiệm khoa.
2. **Streamlit Interactive Lab**: Giao diện phòng thí nghiệm nghiên cứu dành cho Data Scientists và ban đánh giá kỹ thuật để thử nghiệm tham số thuật toán phân bổ.

## 6.2 Next.js 14 Dashboard
- **Công nghệ**: Next.js 14 App Router, TypeScript, TailwindCSS, Lucide Icons, Vitest.
- **Các thành phần cốt lõi**:
  - `ChatAssistant`: Hộp thoại AI tư vấn thông minh tích hợp trực tiếp với endpoint `/api/v1/agent/chat` và `/api/v1/agent/stream`.
  - `ProposalEvaluationCard`: Thẻ đánh giá tương thích đề tài với phân tích điểm mạnh (Strengths) và cảnh báo rủi ro (Risks).
  - `AdvisorDirectory`: Bảng tra cứu danh sách giảng viên kèm chỉ báo trực quan về tình trạng chỉ tiêu (Quota Available Badge).
  - `AssignmentMatrixView`: Bảng ma trận kết quả phân bổ sinh viên theo từng thuật toán.

## 6.3 Chạy & Kiểm Thử Giao Diện Next.js
```bash
cd frontend
# Cài đặt dependencies
npm install

# Khởi chạy môi trường phát triển
npm run dev

# Chạy kiểm thử tự động với Vitest
npm run test:run
```

## 6.4 Streamlit Exploration Lab
Môi trường Streamlit cho phép trực quan hóa nhanh ma trận phân bổ, so sánh đường cong hội tụ giữa mô hình học tăng cường Maskable PPO và thuật toán Hungarian.
```bash
# Khởi chạy ứng dụng Streamlit
streamlit run app.py
```
