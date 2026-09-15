# Chương 9: Demo Day — 10 Deliverables & Checklist Bàn Giao
*Thời gian ước tính: 2 giờ*

---

## 9.1 Danh Mục 10 Sản Phẩm Bàn Giao (10 Deliverables)

Hệ thống đã hoàn tất đầy đủ 10 hạng mục sản phẩm bàn giao theo tiêu chuẩn bảo vệ đồ án:

| STT | Deliverable | Vị trí mã nguồn / Tài liệu | Trạng thái |
| :---: | :--- | :--- | :---: |
| **1** | **Core Matching Algorithms** | `src/rl/`, `src/baselines/` | ✅ Hoàn tất |
| **2** | **LangGraph Multi-Node AI Agent** | `src/agents/` (`graph.py`, `nodes/`, `tools/`, `state.py`) | ✅ Hoàn tất |
| **3** | **RESTful v1 OpenAPI Backend** | `src/api/routes.py`, `src/main.py` | ✅ Hoàn tất |
| **4** | **Next.js 14 Web Dashboard** | `frontend/` (App router, TypeScript, TailwindCSS) | ✅ Hoàn tất |
| **5** | **Interactive Streamlit Lab** | `app.py`, `src/simulator/` | ✅ Hoàn tất |
| **6** | **MongoDB Persistence Layer** | `backend/app/db/mongodb.py`, `docker-compose.mongo.yml` | ✅ Hoàn tất |
| **7** | **Multi-stage Docker Container** | `Dockerfile`, `docker-compose.yml` | ✅ Hoàn tất |
| **8** | **Automated CI/CD Pipeline** | `.github/workflows/ci.yml` | ✅ Hoàn tất |
| **9** | **Technical Guidebook (10 Chương)** | `docs/guide/` (Chương 1 đến Chương 10) | ✅ Hoàn tất |
| **10**| **Demo Day Presentation & Scripts** | `presentation/slide_deck.md`, `demo_script.md` | ✅ Hoàn tất |

## 9.2 Checklist Chuẩn Bị Cho Ngày Báo Cáo (Demo Day Checklist)
- [x] Đảm bảo toàn bộ 12 test case của Agent chạy pass: `pytest tests/test_agent_*.py`.
- [x] Đảm bảo 3 test case của Frontend chạy pass: `npm run test:run`.
- [x] Chạy script benchmark tự động: `python eval/run_eval.py`.
- [x] Khởi động Docker Compose kiểm tra cổng `8000` (API) và `8081` (Mongo Express).
- [x] Xem lại kịch bản thuyết trình 5 phút trong `presentation/demo_script.md`.
- [x] Mở sẵn tài liệu Swagger UI tại `http://localhost:8000/docs`.
