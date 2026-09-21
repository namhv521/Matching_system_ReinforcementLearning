# Thiết kế hoàn thiện KLTN v1

## Mục tiêu

Hoàn thiện hệ thống phân bổ sinh viên - giảng viên theo quy trình ML chín phần: bảy bước trong checklist gốc, phân tích/trực quan hóa kết quả, và sản phẩm web có kiểm thử, CI/CD, triển khai miễn phí. Hệ thống là công cụ hỗ trợ quyết định; người dùng duyệt kết quả cuối cùng.

## Nguyên tắc bắt buộc

- Giữ nguyên dữ liệu nguồn; làm sạch theo cách tái lập và không gộp mất các quan sát trùng có giá trị.
- Tách tập theo nhóm sinh viên và thời gian; fit đặc trưng trên train; chọn trên validation; chỉ mở test sau khi khóa model.
- Không mặc định PPO là model tốt nhất. Exact Hungarian là chuẩn batch; model học chỉ được thăng hạng khi qua promotion gate.
- Model được chấp nhận phải có `quota_violations = 0`, `invalid_proposals = 0`, đủ metric bắt buộc và artifact tái lập được.
- Không commit secret, `.env`, cache, `node_modules`, file Excel tạm hoặc dữ liệu cá nhân/raw bị ignore.
- Branch phát hành là `KLTN` của repository `namhv521/sutudy`.

## Chín phần thực hiện

1. Khóa bài toán, prediction contract, tiêu chí promotion và phạm vi human-in-the-loop.
2. Kiểm định data ingestion, cleaning, provenance và quality report.
3. Kiểm định TF-IDF/compatibility, chống leakage và tính tái lập.
4. Kiểm định Gym environment, state/action, quota và action masking.
5. Kiểm định reward/loss, lỗi hành động và metric fairness.
6. Benchmark Random, Greedy, Gale-Shapley, Exact, PPO, A2C, DQN và QR-DQN trên nhiều seed/milestone. Dừng khi gate đạt hoặc khi bằng chứng cho thấy Exact vẫn là lựa chọn đúng; không train vô hạn để ép kết quả.
7. Đóng gói promotion decision, manifest, API phục vụ inference và vòng đời model.
8. Phân tích dữ liệu và kết quả sau train; xuất bảng thống kê, biểu đồ so sánh model, constraint, convergence và phân phối dữ liệu bằng script tái lập.
9. Hoàn thiện dashboard responsive, FastAPI, Docker, GitHub Actions, kiểm thử backend/frontend và triển khai miễn phí từ một container nếu nền tảng cho phép.

## Kiến trúc sản phẩm

Pipeline Python tạo dữ liệu curated, ma trận compatibility, checkpoint và JSON kết quả. Lớp đánh giá đọc JSON, áp promotion gate và tạo biểu đồ. FastAPI cung cấp health, dữ liệu phân tích, benchmark và matching; frontend hiện có được build thành static assets và FastAPI phục vụ cùng container để giảm chi phí và độ phức tạp triển khai.

Dashboard ở chế độ vận hành: tổng quan KPI, so sánh thuật toán, chất lượng/ràng buộc, dữ liệu, danh sách ghép và trạng thái hệ thống. Mọi biểu đồ phải có nhãn, đơn vị, chú giải, bảng thay thế hoặc nội dung văn bản hỗ trợ accessibility; có loading, empty và error states.

## Kiểm thử và bằng chứng

- Unit/integration tests cho data split, environment, promotion, API và logic phân tích.
- Frontend lint/test/build và smoke test API/static app.
- Kiểm tra secret, dependency, CORS, input schema và thông báo lỗi không lộ chi tiết nội bộ.
- Báo cáo `docs/complete_kltn_v1.md` ghi rõ command, dữ liệu, seed, metric, artifact, hạn chế và URL triển khai; không tuyên bố kết quả nếu chưa có log/exit code/artifact hiện hành.

## Git và triển khai

Trạng thái merge hiện tại phải được xử lý theo hướng giữ phiên bản chức năng đầy đủ, không làm mất thay đổi người dùng. Sau khi kiểm chứng, stage toàn bộ file dự án hợp lệ, commit trên `KLTN`, push `origin/KLTN`. Deployment dùng lựa chọn miễn phí phù hợp với ứng dụng container tại thời điểm triển khai; nếu nhà cung cấp yêu cầu đăng nhập hoặc xác nhận tài khoản, chuẩn bị cấu hình hoàn chỉnh và ghi đúng blocker thay vì giả nhận đã deploy.
