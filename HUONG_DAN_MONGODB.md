# 🍃 HƯỚNG DẪN TÍCH HỢP VÀ SỬ DỤNG MONGODB CHO HỆ THỐNG KLTN

Tài liệu này hướng dẫn chi tiết cách thiết lập, cấu hình và sử dụng **MongoDB** làm cơ sở dữ liệu Document Store (NoSQL) cho nền tảng Phân bổ Luận văn - Giảng viên KLTN.

> **💡 Thông báo quan trọng:**
> Toàn bộ mã nguồn, thư viện kết nối (PyMongo), script đồng bộ dữ liệu, bộ chỉ mục (Indexes) và các API endpoint liên quan đến MongoDB **đã được cài đặt và lập trình sẵn hoàn chỉnh trong dự án**. Bạn có thể thiết lập dịch vụ MongoDB bất cứ lúc nào bạn muốn ("setup sau") mà không cần phải viết lại code!

---

## 📋 MỤC LỤC
1. [Vai trò của MongoDB trong dự án](#1-vai-trò-của-mongodb-trong-dự-án)
2. [Các thành phần đã cài đặt sẵn trong mã nguồn](#2-các-thành-phần-đã-cài-đặt-sẵn-trong-mã-nguồn)
3. [Cấu trúc Collections và Indexes được thiết kế sẵn](#3-cấu-trúc-collections-và-indexes-được-thiết-kế-sẵn)
4. [Các cách thiết lập MongoDB (Chọn 1 trong 3 cách)](#4-các-cách-thiết-lập-mongodb-chọn-1-trong-3-cách)
   - [Cách A: Sử dụng Docker (Nhanh nhất & Khuyên dùng)](#cách-a-sử-dụng-docker-nhanh-nhất--khuyên-dùng)
   - [Cách B: Sử dụng MongoDB Atlas (Cloud miễn phí)](#cách-b-sử-dụng-mongodb-atlas-cloud-miễn-phí)
   - [Cách C: Cài đặt MongoDB Community Server trên máy](#cách-c-cài-đặt-mongodb-community-server-trên-máy)
5. [Cấu hình biến môi trường (.env)](#5-cấu-hình-biến-môi-trường-env)
6. [Hướng dẫn chạy script đẩy dữ liệu lên MongoDB](#6-hướng-dẫn-chạy-script-đẩy-dữ-liệu-lên-mongodb)
7. [Kiểm tra dữ liệu sau khi đẩy](#7-kiểm-tra-dữ-liệu-sau-khi-đẩy)
8. [Code mẫu truy vấn và sử dụng MongoDB](#8-code-mẫu-truy-vấn-và-sử-dụng-mongodb)
9. [Khắc phục sự cố thường gặp (Troubleshooting)](#9-khắc-phục-sự-cố-thường-gặp-troubleshooting)

---

## 1. Vai trò của MongoDB trong dự án

Trong khi SQLite/PostgreSQL xử lý các quan hệ dữ liệu có cấu trúc bảng chặt chẽ, **MongoDB** mang lại các ưu thế vượt trội cho nền tảng KLTN:
1. **Lưu trữ tài liệu dạng lồng ghép (Hierarchical Documents)**: Mỗi giảng viên đi kèm toàn bộ danh sách kỹ năng, điểm số và minh chứng trích xuất từ bài báo dạng JSON lồng ghép mà không cần JOIN nhiều bảng.
2. **Technical Stack linh hoạt**: Đề tài tốt nghiệp lưu trữ mảng công nghệ (`tech_stack: ["React", "FastAPI", "MongoDB", "PyTorch"]`) cho phép truy vấn tìm kiếm phần tử mảng cực nhanh bằng toán tử `$in` hoặc `$all`.
3. **Full-Text Search đa trường**: Tìm kiếm nhanh đề tài và giảng viên bằng chỉ mục Text Index đa ngữ (Tiếng Việt + Tiếng Anh).
4. **Lưu vết mô phỏng phân bổ (Cohort Simulation Runs)**: Lưu lại toàn bộ kết quả phân bổ sinh viên theo từng lượt chạy thuật toán để phân tích lịch sử ra quyết định.

---

## 2. Các thành phần đã cài đặt sẵn trong mã nguồn

| Đường dẫn file | Chức năng cài đặt sẵn |
| :--- | :--- |
| `backend/app/db/mongodb.py` | Connection pool (PyMongo), kiểm tra kết nối (`ping_mongodb`), khởi tạo indexes (`setup_mongodb_indexes`), và hàm đồng bộ dữ liệu (`push_relational_to_mongodb`). |
| `backend/app/core/config.py` | Các cài đặt: `MONGODB_ENABLED`, `MONGODB_URI`, `MONGODB_DB_NAME`. |
| `scripts/push_to_mongodb.py` | Công cụ dòng lệnh (CLI) tự động tạo index và đẩy toàn bộ dữ liệu sang MongoDB với giao diện báo cáo tiến độ trực quan. |
| `backend/app/api/v1/system.py` | Endpoint `GET /api/v1/system/mongodb-status` trả về trạng thái kết nối máy chủ MongoDB. |
| `tests/test_mongodb.py` | Bộ test tự động kiểm tra kết nối và index MongoDB. |
| `docker-compose.mongo.yml` | File cấu hình chạy sẵn MongoDB và Mongo Express Web UI bằng Docker. |
| `requirements.txt` | Đã khai báo sẵn thư viện `pymongo>=4.6.0`. |

---

## 3. Cấu trúc Collections và Indexes được thiết kế sẵn

Hệ thống đã cấu hình sẵn 6 Collections chính trong cơ sở dữ liệu `kltn_matching`:

1. **`advisors` (Giảng viên & Kỹ năng)**:
   - Cấu trúc document: `advisor_id`, `canonical_name`, `academic_title`, `department`, `email`, `primary_field`, `skill_text`, `skills` (danh sách bằng chứng kỹ năng kèm trích dẫn bài báo khoa học).
   - Indexes:
     - `idx_advisor_id_unique`: Unique Index trên `advisor_id`.
     - `idx_canonical_name`: Index tìm kiếm theo tên.
     - `idx_advisor_text_search`: Text Index kết hợp trên `canonical_name`, `primary_field`, và `skill_text`.

2. **`theses` (Danh mục Luận văn tốt nghiệp)**:
   - Cấu trúc document: `record_id`, `student_id`, `student_name`, `advisor_id`, `thesis_title`, `major`, `field_category`, `completion_year`, `tech_stack` (mảng từ khóa), `student_profile` (lồng hồ sơ sinh viên).
   - Indexes:
     - `idx_record_id_unique`: Unique Index trên `record_id`.
     - `idx_student_id`, `idx_advisor_id`, `idx_major`, `idx_completion_year`.
     - `idx_thesis_text_search`: Text Index tìm kiếm nhanh theo tiêu đề và công nghệ.

3. **`courses` (Chương trình đào tạo)**:
   - Cấu trúc document: `course_code`, `course_name`, `credits`, `major_name`, `major_url`.
   - Indexes: Compound Unique Index trên cặp (`course_code`, `major_name`).

4. **`cohort_runs` (Lịch sử mô phỏng phân bổ)**:
   - Cấu trúc document: `run_id`, `created_at`, `algorithm`, `metrics`, `student_allocations`.
   - Indexes: `run_id` (Unique), `created_at` (Sắp xếp thời gian), `algorithm`.

5. **`benchmarks` (Chỉ số so sánh thuật toán)**:
   - Cấu trúc document: `algorithm`, `mean_compatibility`, `quota_violations`, `gini_index`, `execution_time_ms`.
   - Indexes: Unique Index trên `algorithm`.

6. **`training_curves` (Đường cong huấn luyện RL)**:
   - Cấu trúc document: `algorithm`, `milestone`, `train_reward`, `val_reward`, `train_compatibility`.

---

## 4. Các cách thiết lập MongoDB (Chọn 1 trong 3 cách)

Khi bạn đã sẵn sàng thiết lập MongoDB ("setup sau"), bạn chỉ cần chọn **1 trong 3 cách** dưới đây:

### Cách A: Sử dụng Docker (Nhanh nhất & Khuyên dùng)
Nếu máy bạn đã cài Docker Desktop:

**Lựa chọn 1: Chạy trực tiếp 1 dòng lệnh:**
```bash
docker run -d --name kltn-mongo -p 27017:27017 -v kltn_mongo_data:/data/db mongo:latest
```

**Lựa chọn 2: Sử dụng Docker Compose (Có sẵn Web UI trực quan):**
Chạy file `docker-compose.mongo.yml` có sẵn trong dự án:
```bash
docker compose -f docker-compose.mongo.yml up -d
```
- MongoDB Database: `localhost:27017`
- Giao diện quản lý Web (Mongo Express): Mở trình duyệt tại **`http://localhost:8081`** (tài khoản: `admin`, mật khẩu: `pass123`).

---

### Cách B: Sử dụng MongoDB Atlas (Cloud miễn phí 512MB)
Nếu bạn không muốn cài đặt phần mềm trên máy tính, bạn có thể dùng dịch vụ Cloud hoàn toàn miễn phí của MongoDB:

1. Đăng ký tài khoản miễn phí tại: [https://www.mongodb.com/cloud/atlas/register](https://www.mongodb.com/cloud/atlas/register)
2. Chọn gói **M0 Free (Shared Cluster)** -> Chọn khu vực gần Việt Nam (ví dụ: `Singapore - AWS`).
3. Tạo Database User: Đặt `Username` và `Password` (ví dụ: user: `kltn_admin`, password: `Password123!`).
4. Cấu hình IP Access List (Network Access): Chọn **"Allow Access from Anywhere"** (`0.0.0.0/0`) để có thể kết nối từ máy tính của bạn.
5. Lấy Connection String: Bấm nút **"Connect"** -> Chọn **"Drivers" (Python)** -> Copy chuỗi kết nối dạng:
   ```text
   mongodb+srv://kltn_admin:<password>@cluster0.abcde.mongodb.net/?retryWrites=true&w=majority
   ```
6. Thay `<password>` bằng mật khẩu bạn đã tạo ở bước 3.

---

### Cách C: Cài đặt MongoDB Community Server trên máy tính
1. Tải bản cài đặt miễn phí cho hệ điều hành của bạn:
   - [Tải MongoDB Community Server](https://www.mongodb.com/try/download/community)
2. Cài đặt MongoDB và chọn cài thêm công cụ **MongoDB Compass** (Giao diện xem dữ liệu đồ họa).
3. Mặc định sau khi cài, MongoDB service sẽ tự khởi động trên cổng `localhost:27017`.

---

## 5. Cấu hình biến môi trường (.env)

Sau khi có chuỗi kết nối MongoDB, bạn chỉ cần mở file `.env` tại thư mục gốc dự án và cập nhật 3 dòng cấu hình:

### Nếu dùng Docker hoặc Local MongoDB trên máy:
```ini
MONGODB_ENABLED=true
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=kltn_matching
```

### Nếu dùng MongoDB Atlas Cloud:
```ini
MONGODB_ENABLED=true
MONGODB_URI=mongodb+srv://kltn_admin:Password123!@cluster0.abcde.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=kltn_matching
```

---

## 6. Hướng dẫn chạy script đẩy dữ liệu lên MongoDB

Script `scripts/push_to_mongodb.py` được lập trình sẵn để tự động:
- Kiểm tra ping máy chủ MongoDB.
- Tạo toàn bộ các Unique Indexes, Text Indexes đa ngữ, và Performance Indexes.
- Đọc dữ liệu từ SQLite/SQLAlchemy ORM.
- Đẩy toàn bộ dữ liệu vào các collections tương ứng (39 giảng viên, 198 luận văn, 163 môn học, 8 benchmarks, 12 training curves).

### Lệnh chạy đẩy dữ liệu thông thường:
```bash
python scripts/push_to_mongodb.py
```

### Lệnh chạy với URI tùy ý (không cần chỉnh .env):
```bash
python scripts/push_to_mongodb.py --uri "mongodb+srv://kltn_admin:Password123!@cluster0.abcde.mongodb.net/?retryWrites=true&w=majority" --db "kltn_matching"
```

### Lệnh kiểm tra kết nối & index trước (Dry Run, không ghi đè dữ liệu):
```bash
python scripts/push_to_mongodb.py --dry-run
```

**Màn hình xuất kết quả mẫu:**
```text
======================================================================
[*] KLTN MATCHING PLATFORM - MONGODB DATA SYNC UTILITY
======================================================================
Target MongoDB URI: mongodb://localhost:27017
Target Database:    kltn_matching
======================================================================

[1/3] Kiem tra ket noi MongoDB...
[OK] Ket noi thanh cong! Phien ban MongoDB: 8.3.4

[2/3] Khoi tao bo chi muc (Indexes)...
  * advisors          : 3 indexes created
  * theses            : 6 indexes created
  * courses           : 1 indexes created
  * cohort_runs       : 3 indexes created
  * benchmarks        : 1 indexes created

[3/3] Dong bo du lieu tu SQLite/SQLAlchemy sang MongoDB...
[OK] Hoan tat dong bo du lieu thanh cong!

Bao cao so luong ban ghi da dong bo sang MongoDB:
  * advisors          :   39 documents
  * theses            :  198 documents
  * courses           :  163 documents
  * benchmarks        :    8 documents
  * training_curves   :   12 documents

======================================================================
[SUCCESS] Hoan thanh! MongoDB da san sang de truy van va van hanh.
======================================================================
```

---

## 7. Kiểm tra dữ liệu sau khi đẩy

### Cách 1: Sử dụng MongoDB Compass (Giao diện trực quan)
1. Mở phần mềm **MongoDB Compass**.
2. Dán chuỗi kết nối URI (`mongodb://localhost:27017` hoặc `mongodb+srv://...`) rồi bấm **Connect**.
3. Chọn database `kltn_matching` -> Bạn sẽ thấy danh sách 6 collections với đầy đủ documents và indexes.

### Cách 2: Gọi API Backend để kiểm tra trạng thái
Khi backend đang chạy, bạn có thể kiểm tra qua trình duyệt hoặc cURL:
```bash
curl http://localhost:8000/api/v1/system/mongodb-status
```
Kết quả trả về JSON:
```json
{
  "enabled": true,
  "database_name": "kltn_matching",
  "connection": {
    "status": "connected",
    "server_version": "8.3.4",
    "target_uri": "mongodb://localhost:27017"
  }
}
```

### Cách 3: Chạy Unit Test tự động
```bash
pytest tests/test_mongodb.py
```


---

## 8. Code mẫu truy vấn và sử dụng MongoDB

Hệ thống cung cấp sẵn module `backend.app.db.mongodb` với các hàm tiện ích. Bạn có thể sử dụng trực tiếp trong mã nguồn Python như sau:

### 8.1. Lấy kết nối Database
```python
from backend.app.db.mongodb import get_mongo_db

# Tự động lấy database theo cấu hình trong .env
db = get_mongo_db()
```

### 8.2. Tìm kiếm giảng viên theo từ khóa (Full-Text Search)
```python
from backend.app.db.mongodb import get_mongo_db

db = get_mongo_db()
# Tìm kiếm các giảng viên có nghiên cứu về "Trí tuệ nhân tạo" hoặc "Deep Learning"
results = db["advisors"].find(
    {"$text": {"$search": "Trí tuệ nhân tạo"}},
    {"score": {"$meta": "textScore"}}
).sort([("score", {"$meta": "textScore"})])

for adv in results:
    print(adv["canonical_name"], adv["primary_field"])
```

### 8.3. Tìm luận văn theo công nghệ kỹ thuật (Array matching)
```python
from backend.app.db.mongodb import get_mongo_db

db = get_mongo_db()
# Tìm tất cả đề tài sử dụng cả React và FastAPI trong tech_stack
theses = db["theses"].find({
    "tech_stack": {"$all": ["React", "FastAPI"]}
})
for th in theses:
    print(th["record_id"], th["thesis_title"])
```

### 8.4. Ghi nhận lịch sử chạy mô phỏng phân bổ sinh viên
```python
from datetime import datetime, timezone
import uuid
from backend.app.db.mongodb import get_mongo_db

db = get_mongo_db()
db["cohort_runs"].insert_one({
    "run_id": str(uuid.uuid4()),
    "created_at": datetime.now(timezone.utc),
    "algorithm": "PPO_RL_Agent",
    "split": "test",
    "total_students": 50,
    "mean_compatibility": 0.885,
    "quota_violations": 0,
    "allocations": [
        {"student_id": "2021001", "assigned_advisor_id": "GV01", "compatibility": 0.92},
        {"student_id": "2021002", "assigned_advisor_id": "GV04", "compatibility": 0.87},
    ]
})
```

---

## 9. Khắc phục sự cố thường gặp (Troubleshooting)

### 1. `ServerSelectionTimeoutError: No replica set members found`
- **Nguyên nhân**: Dịch vụ MongoDB chưa được khởi động hoặc sai địa chỉ cổng.
- **Khắc phục**:
  - Nếu dùng Docker: Kiểm tra container xem có đang chạy không bằng lệnh `docker ps`.
  - Nếu chưa chạy: `docker start kltn-mongo`.
  - Nếu dùng MongoDB Atlas: Kiểm tra lại xem máy tính đã được thêm vào mục **Network Access (IP Whitelist)** chưa (khuyến nghị chọn `0.0.0.0/0` để cho phép truy cập).

### 2. `Authentication failed` (Lỗi xác thực người dùng)
- **Nguyên nhân**: Sai username hoặc password trong chuỗi `MONGODB_URI`.
- **Khắc phục**:
  - Kiểm tra lại username/password trên MongoDB Atlas hoặc trong Docker.
  - Lưu ý: Nếu mật khẩu có chứa các ký tự đặc biệt như `@`, `#`, `:`, `%`, cần mã hóa URL (URL encode).

### 3. Cài đặt lại thư viện PyMongo
Nếu bạn gặp lỗi `ModuleNotFoundError: No module named 'pymongo'`:
```bash
pip install pymongo>=4.6.0
```

