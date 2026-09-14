# 🚀 HƯỚNG DẪN CÀI ĐẶT VÀ CHẠY HỆ THỐNG KLTN MATCHING PLATFORM

Tài liệu này hướng dẫn chi tiết từng bước từ cài đặt môi trường, cấu hình cơ sở dữ liệu đến khởi chạy toàn bộ hệ thống nền tảng Hỗ trợ Ra quyết định Phân bổ Luận văn - Giảng viên hướng dẫn (KLTN Thesis-Advisor Allocation Decision Support Platform).

---

## 📋 MỤC LỤC
1. [Yêu cầu hệ thống](#1-yêu-cầu-hệ-thống)
2. [Cấu trúc thư mục dự án](#2-cấu-trúc-thư-mục-dự-án)
3. [Cài đặt môi trường Backend (Python)](#3-cài-đặt-môi-trường-backend-python)
4. [Cài đặt môi trường Frontend (Node.js)](#4-cài-đặt-môi-trường-frontend-nodejs)
5. [Cấu hình biến môi trường (.env)](#5-cấu-hHình-biến-môi-trường-env)
6. [Khởi tạo Database và nạp dữ liệu ban đầu](#6-khởi-tạo-database-và-nạp-dữ-liệu-ban-đầu)
7. [Khởi chạy ứng dụng](#7-khởi-chạy-ứng-dụng)
   - [Cách 1: Khởi chạy thống nhất Full-stack (Khuyên dùng)](#cách-1-khởi-chạy-thống-nhất-full-stack-khuyên-dùng)
   - [Cách 2: Chạy riêng Backend và Frontend Dev](#cách-2-chạy-riêng-backend-và-frontend-dev)
8. [Hướng dẫn sử dụng các tính năng giao diện](#8-hướng-dẫn-sử-dụng-các-tính-năng-giao-diện)
9. [Kiểm thử tự động (Unit & Integration Tests)](#9-kiểm-thử-tự-động-unit--integration-tests)
10. [Tài liệu API (Swagger UI / ReDoc)](#10-tài-liệu-api-swagger-ui--redoc)
11. [Khắc phục sự cố thường gặp (Troubleshooting)](#11-khắc-phục-sự-cố-thường-gặp-troubleshooting)

---

## 1. Yêu cầu hệ thống

Trước khi bắt đầu, hãy đảm bảo máy tính của bạn đã cài đặt các công cụ sau:
- **Hệ điều hành**: Windows 10/11, macOS, hoặc Linux (Ubuntu 20.04+).
- **Python**: Phiên bản `3.10` trở lên (Khuyến nghị Python `3.11` hoặc `3.12`).
- **Node.js**: Phiên bản `18.x` hoặc `20.x` LTS trở lên.
- **npm**: Đi kèm với Node.js (hoặc pnpm/yarn).
- **Git**: Dùng để quản lý mã nguồn.
- *(Tùy chọn)* **MongoDB**: Phiên bản 6.0+ nếu muốn kích hoạt lưu trữ NoSQL (xem chi tiết tại file `HUONG_DAN_MONGODB.md`).

Kiểm tra phiên bản trên máy bằng Terminal / PowerShell:
```bash
python --version
node --version
npm --version
```

---

## 2. Cấu trúc thư mục dự án

```text
KLTN/
├── backend/                  # Mã nguồn Backend FastAPI
│   └── app/
│       ├── api/              # API Routers (v1 RESTful & legacy routes)
│       ├── core/             # Configuration, logging, security
│       ├── data/             # Transformers & normalizers
│       ├── db/               # SQLAlchemy SQLite/Postgres & MongoDB manager
│       ├── models/           # SQLAlchemy ORM models
│       ├── schemas/          # Pydantic validation schemas
│       └── services/         # Domain business logic (Matching, Advisor, Thesis, v.v.)
├── frontend/                 # Mã nguồn Frontend (React + Vite + Tailwind CSS)
│   ├── src/                  # React components, pages, hooks, state
│   ├── dist/                 # Production build bundle (sau khi npm run build)
│   └── package.json
├── data/
│   ├── curated/              # Dữ liệu sạch (CSV/JSON) đã qua xử lý
│   └── storage/              # File SQLite database (kltn_matching.db)
├── scripts/                  # Scripts hỗ trợ (seed_database, push_to_mongodb, v.v.)
├── tests/                    # Backend test suite (pytest)
├── run_dashboard.py          # Unified entrypoint chạy cả API và giao diện UI
├── requirements.txt          # Danh sách thư viện Python
├── .env.example              # Mẫu biến môi trường
├── HUONG_DAN_CHAY.md         # Tài liệu này

---

## 3. Cài đặt môi trường Backend (Python)

### Bước 3.1: Tạo môi trường ảo (Virtual Environment)
Khuyến nghị tạo môi trường ảo độc lập để tránh xung đột thư viện:

**Cách A: Dùng `venv` tiêu chuẩn:**
```bash
# Trên Windows (PowerShell):
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Trên Linux / macOS:
python3 -m venv .venv
source .venv/bin/activate
```

**Cách B: Dùng Conda / Miniconda:**
```bash
conda create -n kltn python=3.12 -y
conda activate kltn
```

### Bước 3.2: Cài đặt các thư viện Python
Chạy lệnh sau tại thư mục gốc của dự án:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> **Lưu ý**: File `requirements.txt` đã bao gồm đầy đủ các gói: FastAPI, Uvicorn, SQLAlchemy, Alembic, Pydantic v2, PyMongo, Pandas, Scikit-learn, v.v.

---

## 4. Cài đặt môi trường Frontend (Node.js)

Dự án có giao diện Web SPA hiện đại được xây dựng bằng React, Vite và Tailwind CSS.

Di chuyển vào thư mục `frontend` và cài đặt các dependencies:
```bash
cd frontend
npm install
```

Tiến hành build gói giao diện phục vụ cho chế độ Full-stack:
```bash
npm run build
cd ..
```
*Lệnh trên sẽ tạo ra thư mục `frontend/dist` chứa toàn bộ tài nguyên web tĩnh đã được tối ưu.*

---

## 5. Cấu hình biến môi trường (.env)

Tạo file `.env` từ file mẫu `.env.example`:

**Trên Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**Trên Linux / macOS:**
```bash
cp .env.example .env
```

Nội dung cơ bản trong file `.env`:
```ini
# Database SQLite mặc định
DATABASE_URL=sqlite:///./data/storage/kltn_matching.db

# Thông tin ứng dụng
APP_NAME="KLTN Thesis-Advisor Allocation Decision Support API"
APP_ENV=development
LOG_LEVEL=INFO
DEBUG=false
CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173","http://localhost:8000","http://127.0.0.1:8000"]
MATCHING_SEED=42

# MongoDB (Đã cấu hình sẵn, có thể bật khi khởi động MongoDB)
MONGODB_ENABLED=true
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=kltn_matching
```

---

## 6. Khởi tạo Database và nạp dữ liệu ban đầu

Hệ thống đã có sẵn script nạp toàn bộ 198 đề tài tốt nghiệp, 39 giảng viên, danh bạ kỹ năng, 163 môn học và các chỉ số benchmark vào database SQLite:

Chạy lệnh:
```bash
python scripts/seed_database.py
```

Kết quả hiển thị mẫu khi thành công:
```text
======================================================================
KLTN Matching Platform - Database Seed & Import Pipeline
======================================================================
[1/6] Initializing database tables via SQLAlchemy Base metadata...
[2/6] Seeding Faculty & Lecturers from curated CSVs...
  -> Loaded 39 advisors.
[3/6] Seeding Advisor Skill Evidences...
  -> Loaded 625 skill evidence records.
[4/6] Seeding Theses and Student Profiles...
  -> Loaded 198 curated theses and student profiles.
[5/6] Seeding Curriculum Courses...
  -> Loaded 163 curriculum courses.
[6/6] Seeding Algorithm Benchmark Metrics and Training Curves...
  -> Seeded 8 benchmark algorithms and 12 training curve points.
======================================================================
[SUCCESS] Database initialized & seeded successfully!
```
File cơ sở dữ liệu sẽ nằm tại `data/storage/kltn_matching.db`.

---

## 7. Khởi chạy ứng dụng

### Cách 1: Khởi chạy thống nhất Full-stack (Khuyên dùng)
Hệ thống cung cấp một script thống nhất `run_dashboard.py` khởi động máy chủ FastAPI, tự động phục vụ đồng thời cả backend API và frontend SPA production:

```bash
python run_dashboard.py
```

Khi chạy thành công, console sẽ hiển thị:
```text
======================================================================
KLTN Thesis-Advisor Decision Support Dashboard
======================================================================
* Server URL:     http://localhost:8000
* REST API Docs:  http://localhost:8000/docs
* Redoc:          http://localhost:8000/redoc
* Health Check:   http://localhost:8000/health
* Mode:           Full-stack Unified SPA + REST API
======================================================================
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

👉 Mở trình duyệt web và truy cập: **`http://localhost:8000`**

---

### Cách 2: Chạy riêng Backend và Frontend Dev (Dành cho Lập trình viên)
Nếu bạn muốn chỉnh sửa code frontend với tính năng Hot Module Reload (HMR):

**Terminal 1 (Backend FastAPI):**
```bash
uvicorn backend.app.main:app --reload --port 8000
```
API sẽ hoạt động tại: `http://localhost:8000`

**Terminal 2 (Frontend React Vite dev server):**
```bash
cd frontend
npm run dev
```
Giao diện dev sẽ hoạt động tại: `http://localhost:5173` (đã cấu hình proxy ngầm về backend `http://localhost:8000`).

---

## 8. Hướng dẫn sử dụng các tính năng giao diện

Trên thanh điều hướng (Sidebar / Header) của Dashboard tại `http://localhost:8000`:

1. **📊 Overview (Tổng quan)**:
   - Hiển thị thống kê tổng hợp số lượng đề tài, giảng viên, môn học, phân bố chuyên ngành (CNTT, KTPM, HTTT, KHMT, ATTT, v.v.).
   - Biểu đồ phân bổ tỷ lệ đề tài theo năm và xu hướng công nghệ.

2. **🎯 Match Simulation (Mô phỏng Phân bổ)**:
   - Chọn thuật toán phân bổ (TF-IDF Similarity, Constraint Optimization, PPO Reinforcement Learning, v.v.).
   - Thiết lập chỉ tiêu hướng dẫn tối đa của mỗi giảng viên (Quota: ví dụ 5 - 10 SV/GV).
   - Bấm **"Chạy mô phỏng"** để xem ma trận tương thích, danh sách sinh viên được ghép cặp và các cảnh báo vi phạm quota.

3. **🏆 Benchmark (So sánh Thuật toán)**:
   - Bảng so sánh 8 thuật toán matching (DQN, PPO, Hungarian, Greedy, Genetic, v.v.).
   - Các tiêu chí: Điểm tương thích trung bình (`mean_compatibility`), Số vi phạm (`quota_violations`), Hệ số công bằng Gini (`gini_index`), Thời gian thực thi (`execution_time_ms`).

4. **📈 Training Curves (Đường cong Huấn luyện RL)**:
   - Trực quan hóa tiến trình huấn luyện tác tử RL qua các mốc thời gian (milestones).
   - Theo dõi Reward huấn luyện, Reward kiểm định, và Tỷ lệ đề xuất không hợp lệ giảm dần theo thời gian.

5. **👨‍🏫 Advisor Directory (Danh bạ Giảng viên)**:
   - Danh sách 39 giảng viên khoa CNTT.
   - Tìm kiếm theo tên hoặc lĩnh vực nghiên cứu (AI, Web, IoT, An ninh mạng).
   - Xem chi tiết danh mục kỹ năng, minh chứng trích xuất từ bài báo khoa học.

6. **📚 Thesis Catalog (Danh mục Đề tài)**:
   - Danh sách 198 luận văn tốt nghiệp.
   - Lọc theo năm tốt nghiệp, chuyên ngành, tên giảng viên hướng dẫn hoặc từ khóa công nghệ (React, PyTorch, Spring Boot, v.v.).

---

## 9. Kiểm thử tự động (Unit & Integration Tests)

Hệ thống đã có đầy đủ bộ kiểm thử tự động cho cả Backend và Frontend:

### Kiểm thử Backend (pytest):
```bash
# Chạy toàn bộ các bài test
pytest

# Hoặc chạy kiểm tra theo từng module:
pytest tests/test_v1_endpoints.py    # Kiểm tra 14 RESTful API v1 endpoints
pytest tests/test_data_validation.py  # Kiểm tra ràng buộc và schema validation
pytest tests/test_services.py         # Kiểm tra Matching service & Analytics
pytest tests/test_mongodb.py          # Kiểm tra kết nối và chỉ mục MongoDB
```

### Kiểm thử Frontend (vitest):
```bash
cd frontend
npm run test:run
cd ..
```

---

## 10. Tài liệu API (Swagger UI / ReDoc)

FastAPI tự động sinh tài liệu tương tác chuẩn OpenAPI:
- **Swagger UI (Có thể gọi thử trực tiếp API)**: `http://localhost:8000/docs`
- **ReDoc (Giao diện đọc tài liệu chi tiết)**: `http://localhost:8000/redoc`
- **OpenAPI Schema (JSON)**: `http://localhost:8000/openapi.json`

Các nhóm endpoint chính:
- `/api/v1/system/*`: Trạng thái máy chủ, báo cáo chất lượng dữ liệu, MongoDB health status.
- `/api/v1/advisors/*`: Danh bạ giảng viên, phân trang, tìm kiếm, chi tiết kỹ năng.
- `/api/v1/theses/*`: Danh mục luận văn, bộ lọc chuyên ngành, công nghệ.
- `/api/v1/matching/*`: Mô phỏng phân bổ sinh viên - giảng viên, chạy thuật toán tối ưu.
- `/api/v1/curriculum/*`: Tra cứu chương trình đào tạo và môn học.

---

## 11. Khắc phục sự cố thường gặp (Troubleshooting)

### 1. Lỗi cổng `8000` bị chiếm dụng (`Address already in use`):
- **Windows**:
  ```powershell
  # Tìm PID đang chiếm port 8000:
  netstat -ano | findstr :8000
  # Tắt process (thay <PID> bằng mã số tìm được):
  taskkill /PID <PID> /F
  ```
- Hoặc đổi sang port khác khi chạy:
  ```bash
  uvicorn run_dashboard:app --port 8080
  ```

### 2. Lỗi giao diện trắng trang khi mở `http://localhost:8000`:
- Nguyên nhân: Chưa build frontend bundle trước khi chạy.
- Khắc phục:
  ```bash
  cd frontend && npm install && npm run build && cd ..
  python run_dashboard.py
  ```

### 3. Lỗi `ModuleNotFoundError: No module named '...'`:
- Nguyên nhân: Chưa kích hoạt môi trường ảo hoặc thiếu thư viện.
- Khắc phục:
  ```bash
  pip install -r requirements.txt
  ```

### 4. Muốn nạp lại dữ liệu sạch từ đầu:
- Chỉ cần chạy lại:
  ```bash
  python scripts/seed_database.py
  ```

