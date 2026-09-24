# Thiết kế triển khai cloud tách lớp KLTN v2.3

## Mục tiêu

Tách hệ thống hiện tại thành ba lớp có thể nâng cấp độc lập:

- React + Vite trên Vercel để giao diện và static assets phản hồi nhanh.
- FastAPI trên Render để giữ toàn bộ nghiệp vụ matching, model inference và API contract.
- Supabase PostgreSQL làm nguồn dữ liệu ứng dụng chính; bật `pgvector` cho nâng cấp semantic search sau này.

Kết quả phải giữ nguyên benchmark, promotion gate và dữ liệu public đã ẩn danh. Báo cáo mới được ghi vào `docs/complete_kltn_v2_3.md`; không thay đổi `docs/complete_kltn_v1.md`.

## Kiến trúc

```text
Browser
  -> Vercel React/Vite static site
       -> HTTPS FastAPI API on Render
            -> Supabase Shared Pooler Session Mode over SSL
            -> read-only model/result/figure artifacts in container
```

Frontend không kết nối trực tiếp PostgreSQL và không giữ database password hoặc Supabase service key. FastAPI là ranh giới duy nhất cho validation, authorization tương lai và database access.

## Frontend trên Vercel

Giữ React 18 + Vite thay vì chuyển sang Next.js. Build dùng `npm ci && npm run build`, output là `frontend/dist`. `VITE_API_URL` trỏ đến Render API. Vercel rewrite chỉ phục vụ SPA routes; không proxy toàn bộ API để tránh thêm một lớp latency.

Tối ưu trong phạm vi migration:

- Lazy-load Recharts và các trang analytics nặng.
- Giữ loading/error/empty state; thông báo rõ khi backend Render Free đang cold start.
- Cấu hình cache dài hạn cho asset có hash, cache ngắn hoặc không cache cho `index.html`.
- Security headers thích hợp cho static frontend; CSP `connect-src` chỉ cho Render API.

Không redesign giao diện và không thêm chức năng ngoài phạm vi deployment.

## Backend trên Render

Docker image chỉ chứa FastAPI, source ML, model đã chọn, figures và public seed snapshot. Frontend build bị loại khỏi Docker image để giảm kích thước, build time và cold-start surface.

Runtime configuration:

- `DATABASE_URL`: Supabase Shared Pooler Session Mode, `sslmode=require`.
- `CORS_ORIGINS`: URL Vercel production, preview pattern được xử lý có kiểm soát, localhost cho development.
- `FRONTEND_URL`: URL production để redirect hoặc ghi metadata khi cần.
- Không commit secrets vào Git; `.env.example` chỉ chứa placeholder.

`/health` phân biệt trạng thái ứng dụng và database. Database unavailable trả `degraded` có chủ đích; không trả stack trace hoặc connection string. Model và vectorizer chỉ được load ở route cần matching, không cản static metadata/health.

## Supabase PostgreSQL và pgvector

Supabase là nguồn dữ liệu chính cho catalog public và dữ liệu vận hành:

- `advisors`, `lecturers`, `advisor_skill_evidences`, `advisor_identity_maps`
- `theses`, `student_profiles`, `courses`
- `benchmark_metrics`, `training_curve_points`
- `cohort_runs`, `assignment_records`, `advisor_workload_records`

Alembic quản lý schema. Migration đầu tiên tạo schema hiện hành và bật extension `vector`. Không thêm embedding column cho đến khi có lựa chọn model/dimension và benchmark riêng; extension được bật để tránh thay đổi hạ tầng khi nâng cấp.

Seed script là idempotent: upsert theo natural/primary key, chạy lại không nhân bản dữ liệu. Backend ưu tiên DB; CSV/JSON trong repo chỉ là snapshot tái lập và fallback read-only có cảnh báo.

## Quy tắc dữ liệu và riêng tư

Chỉ import dữ liệu public đã ẩn danh. Audit trước migration phải kiểm tra mọi cột, không chỉ `student_id` và `student_name`.

Hiện `data/public/theses.csv` vẫn có `source_file` chứa ID và tên gốc trong filename. Migration phải sửa public export để thay `source_file` bằng định danh trung tính hoặc hash ổn định, tái chạy kiểm tra không giao nhau với identifier/name gốc, rồi mới seed Supabase.

Không import raw PDFs, OCR text riêng tư, file nguồn hoặc curated identifiers lên Supabase/Vercel/Render. Database credential chỉ đặt trong Render environment. Frontend không có Supabase secret.

## Data flow

1. Script tạo public snapshot đã khử định danh toàn bộ trường nhạy cảm.
2. Alembic tạo/cập nhật schema Supabase.
3. Seed script upsert snapshot và benchmark artifacts vào PostgreSQL.
4. FastAPI repositories đọc/ghi Supabase bằng SQLAlchemy.
5. Matching service lấy cohort/advisors từ repository, chạy Exact/PPO và ghi run/assignment/workload trở lại DB.
6. Vercel frontend gọi Render API qua HTTPS và render kết quả.

## Failure handling

- Supabase tạm dừng hoặc lỗi kết nối: health trả `degraded`; endpoint phụ thuộc DB trả lỗi 503 có message chung.
- Render cold start: frontend hiển thị trạng thái đang đánh thức backend và cho phép retry.
- Vercel thiếu `VITE_API_URL`: production build fail sớm.
- Seed/import lỗi giữa chừng: transaction rollback; chạy lại an toàn.
- CORS sai: integration test fail trước deploy.

## CI/CD

GitHub Actions chạy:

1. Python unit/integration tests với SQLite.
2. Migration smoke test trên PostgreSQL service container.
3. Public-data privacy audit và idempotent seed test.
4. Frontend Vitest, TypeScript và Vite production build.
5. Backend-only Docker build.

Render auto-deploy backend từ nhánh `KLTN`. Vercel auto-deploy `frontend/` từ cùng nhánh. Supabase schema thay đổi chỉ qua migration; không tự chạy destructive migration từ frontend.

## Kiểm chứng hoàn tất

- Toàn bộ Python tests pass.
- Frontend tests/build pass và bundle analytics được tách chunk.
- PostgreSQL migration chạy từ database trống và upgrade idempotent.
- Seed counts khớp snapshot: 198 thesis, 39 advisors và các bảng liên quan.
- Privacy audit không tìm thấy student ID/name hoặc filename nguồn gốc trong public cloud payload.
- Render `/health` báo application/database healthy.
- Vercel root trả HTTP 200 và tải dashboard.
- Browser network xác nhận frontend chỉ gọi Render URL; CORS hợp lệ.
- Luồng overview, advisor directory, recommendation và cohort matching chạy trên production URLs.

## Báo cáo v2.3

Tạo `docs/complete_kltn_v2_3.md` sau khi triển khai. Báo cáo gồm kiến trúc mới, schema/migration, audit riêng tư, CI, biến môi trường không chứa secret, URL Vercel/Render, Supabase evidence, smoke tests, giới hạn Free tier và hướng nâng cấp pgvector. Chỉ ghi trạng thái hoàn tất khi có bằng chứng trực tiếp.

## Ngoài phạm vi

- Chuyển frontend sang Next.js.
- Thay TF-IDF bằng embedding hoặc thay promotion gate.
- Thêm đăng nhập Supabase Auth.
- Dùng Pinecone, ChromaDB, Qdrant hoặc MongoDB song song.
- Đưa raw/curated private data lên cloud.
