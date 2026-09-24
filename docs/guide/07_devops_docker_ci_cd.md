# Chương 7: DevOps — Docker, CI/CD, Deploy & Logging
*Thời gian ước tính: 6 giờ*

---

## 7.1 Đóng Gói Multi-Stage Docker
File `Dockerfile` gốc sử dụng kỹ thuật Multi-stage build để tối ưu hóa dung lượng image và bảo mật:
- **Stage 1 (`builder`)**: Cài đặt các công cụ biên dịch (`build-essential`, `curl`), build và cài đặt các thư viện Python vào `/root/.local`.
- **Stage 2 (`runner`)**: Sử dụng base image `python:3.11-slim`, chỉ copy các gói đã build từ stage 1, loại bỏ trình biên dịch thừa giúp image nhẹ và giảm thiểu bề mặt tấn công.
- **Healthcheck**: Tích hợp lệnh kiểm tra `HEALTHCHECK` tự động gửi request đến `/api/v1/agent/health`.

## 7.2 Quản Lý Đa Dịch Vụ Với Docker Compose
File `docker-compose.yml` điều phối toàn bộ các dịch vụ:
1. `mongodb`: Cơ sở dữ liệu NoSQL Mongo 7.0 lưu trữ bền vững kèm volume `mongo_data`.
2. `mongo-express`: Bảng điều khiển quản trị web trực quan tại cổng `8081`.
3. `backend`: Dịch vụ AI Agent FastAPI phục vụ tại cổng `8000`.

```bash
# Khởi động cụm dịch vụ
docker compose up -d

# Kiểm tra trạng thái các container
docker compose ps

# Xem log thời gian thực của backend agent
docker compose logs -f backend
```

## 7.3 Tự Động Hóa CI/CD Với GitHub Actions
Quy trình CI được cấu hình trong `.github/workflows/ci.yml`:
- Tự động kích hoạt khi có commit đẩy lên các nhánh `main`, `develop` hoặc các nhánh `suso/**`.
- Thực hiện cài đặt môi trường, chạy bộ kiểm thử `pytest` cho AI Agent và API.
- Chạy tự động script đánh giá Benchmark `eval/run_eval.py`.
- Kiểm thử giao diện frontend thông qua Vitest.

## 7.4 Hệ Thống Ghi Log AI (Audit Logging)
Mọi lượt tương tác của Agent đều được ghi nhận qua hook `scripts/log_ai_interaction.py` vào file `logs/agent/agent_interactions.jsonl` bao gồm:
- Mã định danh phiên (`session_id`) và dấu thời gian UTC.
- Câu hỏi của sinh viên và câu trả lời của hệ thống.
- Danh sách công cụ đã gọi cùng thời gian phản hồi (latency ms).
