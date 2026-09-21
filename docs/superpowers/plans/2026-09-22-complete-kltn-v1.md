# Complete KLTN v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hoàn thiện, kiểm chứng, trực quan hóa và phát hành hệ thống KLTN trên branch `KLTN`.

**Architecture:** Giữ pipeline ML Python làm nguồn sự thật; kết quả được lưu bằng JSON/manifest và dùng chung cho báo cáo, biểu đồ, API, dashboard. FastAPI phục vụ cả API và frontend build để có một artifact triển khai đơn giản.

**Tech Stack:** Python, pandas, scikit-learn, Gymnasium, Stable-Baselines3/sb3-contrib, FastAPI, frontend hiện có, Docker, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-22-complete-kltn-v1-design.md`

## Global Constraints

- Không rò rỉ test vào lựa chọn model.
- Không ép model RL thắng baseline; promotion gate quyết định từ số đo.
- Không mất thay đổi hiện có khi xử lý Git.
- Không commit secret, cache, dependency directory hoặc file tạm.
- Tất cả tuyên bố hoàn thành phải có kiểm chứng mới.

---

### Task 1: Khôi phục trạng thái Git và khóa branch

**Files:** bốn file đang xung đột và toàn bộ working tree hiện hữu.

- [ ] Ghi nhận status, refs, stage 1/3 và nội dung hai phía.
- [ ] Giải quyết từng xung đột bằng phiên bản chức năng đầy đủ; không xóa thay đổi người dùng.
- [ ] Tạo/chuyển local branch `KLTN` từ trạng thái đã hợp nhất và đối chiếu `origin/KLTN`.
- [ ] Chạy `git diff --check` và lưu inventory trước khi sửa nghiệp vụ.

### Task 2: Baseline kiểm thử và audit chín phần

**Files:** `tests/`, `src/`, `backend/`, `frontend/`, workflow và config hiện có.

- [ ] Chạy test Python, frontend build/test/lint và ghi toàn bộ lỗi ban đầu.
- [ ] Truy nguyên nguyên nhân từng lỗi trước khi sửa.
- [ ] Lập ma trận checklist 1-9 với artifact, command và trạng thái bằng chứng.

### Task 3: Hoàn thiện data, feature, environment và promotion gate

**Files:** `src/data_pipeline/*`, `src/environment/*`, `src/rl/*`, `tests/*`.

- [ ] Viết test thất bại cho mọi gap thực tế phát hiện được.
- [ ] Sửa tối thiểu để quality, split, action mask và promotion fail-closed đạt hợp đồng.
- [ ] Chạy data validation và bộ test mục tiêu rồi chạy regression suite.

### Task 4: Benchmark đa seed và khóa model

**Files:** `scripts/train_overnight.py`, runner đánh giá, `outputs/` cục bộ.

- [ ] Kiểm chứng dry-run, dependency và tài nguyên máy.
- [ ] Chạy các seed/milestone còn thiếu; tái sử dụng artifact hợp lệ có checksum thay vì train lặp.
- [ ] Phân tích lỗi sau mỗi vòng; chỉ thêm thí nghiệm khi có giả thuyết đo được.
- [ ] Khóa lựa chọn trên validation, chạy test một lần và xuất promotion decision/manifest.

### Task 5: Phân tích dữ liệu và trực quan hóa

**Files:** `scripts/generate_figures.py`, module phân tích, tests, `outputs/figures/`.

- [ ] Viết test cho parser/tổng hợp metric và trường dữ liệu thiếu.
- [ ] Xuất thống kê dữ liệu, mean/std theo seed, optimality ratio, invalid/quota, fairness và convergence.
- [ ] Sinh biểu đồ so sánh model, constraint, learning curve và phân phối dữ liệu ở 300 DPI.
- [ ] Kiểm tra file ảnh, kích thước, nhãn, nguồn dữ liệu và tính nhất quán với JSON.

### Task 6: Hoàn thiện backend an toàn

**Files:** `backend/app/*`, schema/routes/tests, requirements.

- [ ] Viết API tests cho health, analytics, benchmark, matching, input lỗi và missing artifact.
- [ ] Sửa endpoint tối thiểu, validate input, CORS theo env, lỗi công khai an toàn.
- [ ] Chạy backend tests và smoke API.

### Task 7: Hoàn thiện frontend dashboard

**Files:** source frontend hiện có, tests và build config.

- [ ] Giữ visual identity hiện tại nhưng cải thiện hierarchy, responsive, accessibility và trạng thái loading/empty/error.
- [ ] Kết nối API thật cho KPI, model comparison, data visualization và matching; không dùng số liệu trang trí.
- [ ] Viết/hoàn thiện component tests; chạy lint, test và production build.
- [ ] Kiểm tra trực quan desktop/mobile và sửa lỗi quan sát được.

### Task 8: CI/CD và deployment miễn phí

**Files:** `Dockerfile`, `.dockerignore`, `.github/workflows/*`, deployment config.

- [ ] Thêm pipeline cài dependency khóa phiên bản, chạy Python tests, frontend checks và Docker build.
- [ ] Kiểm tra secret scan, ignored files và container health.
- [ ] Chọn nền tảng free hỗ trợ container, triển khai và smoke test URL công khai; nếu cần thao tác tài khoản, dừng đúng tại bước xác nhận.

### Task 9: Báo cáo, kiểm chứng và phát hành

**Files:** `docs/complete_kltn_v1.md` và các file dự án hợp lệ.

- [ ] Viết báo cáo đủ chín phần, số liệu lấy trực tiếp từ artifact đã kiểm chứng, kèm hạn chế trung thực.
- [ ] Chạy full tests, builds, data checks, figure checks, API smoke, Docker smoke và `git diff --check`.
- [ ] Review secret/large files; stage toàn bộ repo hợp lệ, loại cache/temp/secret/dependency.
- [ ] Commit trên `KLTN`, push `origin/KLTN`, xác minh remote SHA và URL triển khai.
