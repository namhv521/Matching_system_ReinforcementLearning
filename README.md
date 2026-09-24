# Hệ thống RL Phân bổ Sinh viên – Giảng viên Hướng dẫn

> **Production repository — Reinforcement Learning-Based Student–Advisor Matching System**  
> **Sinh viên:** Hoàng Văn Nam — 11236160  

Repository này là sản phẩm hoàn chỉnh được version-control và push lên GitHub. Planning/spec/task orchestration được quản lý ở workspace local bên ngoài repo; repository này chỉ chứa mã nguồn, kiểm thử, tài liệu kỹ thuật, artifact có thể công bố và hạ tầng vận hành.

## Kiến trúc repository

```txt
src/              # Data pipeline, matching environment, RL agents, benchmark
backend/          # FastAPI, SQLAlchemy, API/service/repository layers
frontend/         # React + TypeScript + Vite + TailwindCSS
configs/          # Centralized ML/data configuration
data/              # raw, processed, curated, public, storage
outputs/           # result JSON, models/checkpoints, publication figures
tests/             # Python unit and integration tests
eval/              # Evaluation runner and reports
docs/              # Technical docs, architecture and runbooks
baocao/            # Thesis deliverables
presentation/      # Defense/demo deliverables
scripts/           # Reproducible maintenance and experiment scripts
.github/workflows/ # CI pipeline
Dockerfile         # Multi-stage frontend/backend production image
docker-compose.yml # Local container orchestration
.env.example       # Environment contract without secrets
```

## Công nghệ

| Layer | Technology |
|---|---|
| ML/RL | Python, Gymnasium, Stable-Baselines3, SB3-Contrib, scikit-learn |
| API | FastAPI, Uvicorn, Pydantic Settings |
| Database | SQLAlchemy; SQLite local mặc định; PostgreSQL qua `DATABASE_URL`; MongoDB tùy chọn |
| Frontend | React 18, TypeScript, Vite, TailwindCSS, Recharts, React Query |
| Test | Pytest, Vitest, Testing Library |
| Delivery | Docker, Docker Compose, GitHub Actions, Render |

## Khởi chạy local

### Backend + built frontend

```powershell
Copy-Item .env.example .env
python -m pip install -r requirements.txt
npm --prefix frontend ci
npm --prefix frontend run build
python run_dashboard.py
```

- Dashboard: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`

### Chế độ phát triển tách frontend/backend

```powershell
# Terminal 1
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2
npm --prefix frontend run dev
```

### Docker

```powershell
docker compose up --build
```

## Kiểm thử

```powershell
python -m pytest tests
npm --prefix frontend run test:run
npm --prefix frontend run build
docker build -t kltn-matching:local .
```

## Git remote

Git root là chính thư mục này. Luôn chạy Git tại repo hiện hành:

```powershell
git status --short
git remote -v
```

Không commit `.env`, raw/private data, PII, log hoặc checkpoint lớn.

## Bài toán và tiêu chí an toàn

Mỗi episode xử lý tuần tự một cohort sinh viên. State kết hợp compatibility, remaining capacity và current load; action chọn một advisor; Action Masking loại bỏ advisor đã đầy quota. Candidate RL chỉ được promote khi quota violations và invalid proposals bằng 0 và đạt promotion gate trên hold-out đa seed.

## Dữ liệu và đạo đức

Raw/private data phải giữ local. Chỉ public snapshot đã ẩn danh và artifact tái lập được mới được commit. Kết quả matching là hỗ trợ quyết định và phải được hội đồng chuyên môn duyệt trước khi áp dụng.
