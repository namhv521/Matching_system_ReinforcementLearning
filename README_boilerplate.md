# 🎓 [Tên Dự Án] — Nền Tảng Phân Bổ KLTN & AI Matching Agent

[![CI Pipeline](https://github.com/your-org/kltn-matching/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/kltn-matching/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agent-ff69b4.svg)](https://langchain-ai.github.io/langgraph/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)

> **Khung README mẫu dành cho dự án của đội phát triển**: Hệ thống giải quyết bài toán tư vấn chọn đề tài khóa luận và tối ưu ghép cặp Giảng viên - Sinh viên dựa trên kiến trúc Multi-Agent LangGraph và Reinforcement Learning.

---

## 📌 1. Mục Tiêu Dự Án (Project Goal)
- **Tư vấn tự động**: Sinh viên được định hướng đề tài theo năng lực, sở thích và kỹ năng công nghệ.
- **Tối ưu hóa phân bổ**: Đảm bảo 100% không vi phạm giới hạn chỉ tiêu (Quota Constraints) của từng Giảng viên.
- **Minh bạch và giải thích được (Explainable AI)**: Đưa ra lý do đối sánh chuyên môn và các đề tài tham chiếu khóa trước.

---

## 🏛️ 2. Kiến Trúc Tổng Thể (System Architecture)

```
[ Frontend: Next.js 14 / Streamlit ]
                │
                ▼ REST API & SSE Streaming
[ Backend: FastAPI v1 + LangGraph Agent ]
   ├── Query Analyzer Node
   ├── Academic Retriever (Vector/BM25)
   ├── Matcher Node (Quota Constraints)
   └── Synthesizer Node (Explainable Advice)
                │
                ▼ Persistence & Caching
[ Storage: MongoDB Atlas + SQLite + Curated Datasets ]
```

---

## 🚀 3. Hướng Dẫn Cài Đặt Nhanh (Quickstart)

### Cách 1: Khởi Chạy Bằng Docker (Khuyến nghị)
```bash
# 1. Clone repository
git clone https://github.com/your-org/kltn-matching.git
cd kltn-matching

# 2. Khởi động toàn bộ dịch vụ (MongoDB + Backend AI Agent + Mongo Express)
docker compose up -d

# 3. Kiểm tra API Docs tại
http://localhost:8000/docs
```

### Cách 2: Chạy Thủ Công (Local Environment)
```bash
# 1. Cài đặt môi trường ảo
python -m venv .venv
source .venv/bin/activate  # Trên Windows: .venv\Scripts\activate

# 2. Cài đặt dependencies
pip install -r requirements.txt
pip install fastapi uvicorn pydantic pydantic-settings pytest

# 3. Khởi chạy FastAPI AI Agent Server
python -m uvicorn src.main:app --reload --port 8000
```

---

## 🤖 4. Điểm Nhấn Công Nghệ (Tech Stack)

| Hạng mục | Công nghệ sử dụng |
| :--- | :--- |
| **Agent Orchestrator** | LangGraph (StateGraph, 4 Nodes, Conditional Routing) |
| **LLM & Client** | OpenAI GPT-4o-mini / Google Gemini / Local Mock Fallback |
| **Backend API** | FastAPI, Pydantic v2, Pydantic Settings, Uvicorn |
| **Thuật toán Phân bổ** | Maskable PPO (RL), Hungarian Algorithm, Gale-Shapley |
| **Cơ sở dữ liệu** | MongoDB 7.0 (Motor Async Driver), SQLite Curated DB |
| **Kiểm thử & CI** | Pytest, TestClient, GitHub Actions CI/CD |

---

## 📡 5. Danh Sách Endpoint Chính (API Reference)

- `POST /api/v1/agent/chat`: Trò chuyện và tư vấn đề tài / giảng viên từ AI Agent.
- `POST /api/v1/agent/stream`: Truyền phát token dạng Server-Sent Events (SSE).
- `POST /api/v1/agent/evaluate`: Đánh giá tương thích giữa sinh viên và giảng viên cụ thể.
- `GET /api/v1/agent/health`: Kiểm tra sức khỏe hệ thống và trạng thái Agent Tools.
- `GET /api/v1/agent/tools`: Liệt kê metadata các công cụ của Agent.

---

## 👥 6. Thành Viên Nhóm Phát Triển (Team Members)

- **Thành viên 1**: [Họ tên] — AI Agent Architecture & RL Optimization
- **Thành viên 2**: [Họ tên] — Backend API & Database Engineering
- **Thành viên 3**: [Họ tên] — Frontend Dashboard & UX Design
- **Thành viên 4**: [Họ tên] — Evaluation Benchmark & DevOps CI/CD
