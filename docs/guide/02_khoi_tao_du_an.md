# Chương 2: Khởi Tạo Dự Án — Clone, Setup & Git Workflow
*Thời gian ước tính: 4 giờ*

---

## 2.1 Yêu Cầu Môi Trường (System Prerequisites)
Trước khi bắt đầu, đảm bảo máy trạm của bạn đã cài đặt các công cụ sau:
- **Python**: Phiên bản `>= 3.10` (Khuyến nghị Python 3.11 hoặc 3.12).
- **Node.js**: Phiên bản `>= 18.x LTS` (kèm theo `npm` hoặc `pnpm`).
- **Docker & Docker Compose**: Bản mới nhất hỗ trợ Compose v2.
- **Git**: Quản lý mã nguồn phân tán.

## 2.2 Quy Trình Thiết Lập Môi Trường Backend & Agent

```bash
# 1. Clone repository
git clone https://github.com/your-org/kltn-matching.git
cd kltn-matching

# 2. Tạo môi trường ảo Python độc lập
python -m venv .venv
# Kích hoạt trên Linux/macOS:
source .venv/bin/activate
# Hoặc trên Windows PowerShell:
.venv\Scripts\Activate.ps1

# 3. Cài đặt các thư viện phụ thuộc
pip install --upgrade pip
pip install -r requirements.txt
pip install fastapi uvicorn pydantic pydantic-settings pytest httpx

# 4. Chạy script kiểm tra môi trường tự động
python scripts/install_agent.py
```

## 2.3 Thiết Lập Biến Môi Trường (.env)
Tạo file `.env` tại thư mục gốc dự án theo mẫu sau:

```env
# Core Settings
APP_NAME="KLTN AI Advisor Matching Agent"
DEBUG=true
PORT=8000
HOST=0.0.0.0

# LLM Configuration (mock / openai / gemini)
LLM_PROVIDER=mock
OPENAI_API_KEY=""
GEMINI_API_KEY=""

# Database Configuration
MONGODB_ENABLED=false
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=kltn_matching
```

## 2.4 Chuẩn Git Workflow Của Nhóm
Để đảm bảo chất lượng code và tính toàn vẹn của nhánh chính:
1. **Trunk-based / Feature Branching**:
   - Mọi tính năng phát triển trên nhánh `feature/<feature-name>` hoặc `fix/<bug-name>`.
   - Các commit phải có thông điệp rõ ràng theo chuẩn Conventional Commits: `feat: ...`, `fix: ...`, `docs: ...`, `test: ...`.
2. **Pre-commit & Post-commit Hooks**:
   - Sử dụng hook `.github/hooks/post-commit` để tự động ghi log hoạt động commit và theo dõi tiến độ.
3. **Pull Request & Code Review**:
   - Mỗi PR phải vượt qua 100% các bài test trong GitHub Actions CI trước khi merge vào nhánh chính `main`.
