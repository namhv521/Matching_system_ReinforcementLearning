---
marp: true
theme: uncover
paginate: true
header: 'Hệ Thống Phân Bổ KLTN Thông Minh & AI Matching Agent'
footer: 'Demo Day KLTN - 2026'
style: |
  section {
    background-color: #0f172a;
    color: #f8fafc;
    font-family: 'Inter', sans-serif;
  }
  h1, h2, h3 {
    color: #38bdf8;
  }
---

# 🎓 Hệ Thống Khuyến Nghị & Phân Bổ KLTN Bằng AI Agent
### Tối ưu hóa phân bổ đề tài & Giảng viên hướng dẫn dựa trên LangGraph & Maskable PPO

**Nhóm Tác giả & Đội ngũ Phát triển**
Demo Day Milestone

---

## 🎯 Vấn Đề Thực Tiễn (Problem Statement)

- **Sinh viên**: Khó định hình hướng đề tài, thiếu thông tin về thế mạnh nghiên cứu thực tế của Giảng viên.
- **Giảng viên**: Tình trạng quá tải chỉ tiêu (vượt quota), sinh viên chọn đề tài lệch chuyên môn sâu.
- **Khoa / Nhà trường**: Phân bổ thủ công dễ xung đột, tốn hàng trăm giờ đối soát danh sách.

---

## 💡 Giải Pháp Đột Phá (Core Innovation)

1. **AI Counseling Agent (LangGraph)**:
   - State Graph 4 bước: Phân tích ý định -> Truy xuất học thuật -> Đối sánh ràng buộc -> Tổng hợp phản hồi.
2. **Thuật toán Phân Bổ Kết Hợp (Hybrid RL + Hungarian)**:
   - Tối ưu hóa đa mục tiêu với Maskable PPO đảm bảo 100% tuân thủ Quota.
3. **Full-stack Platform**:
   - Next.js 14 Dashboard + FastAPI Async Core + MongoDB / SQLite Persistence.

---

## 🏗️ Kiến Trúc Hệ Thống (3-Tier Architecture)

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
[ Storage: MongoDB Atlas + Curated Vector Store ]
```

---

## 🤖 Demo Kịch Bản AI Agent Trò Chuyện

1. **Input của Sinh viên**:
   > *"Em có kỹ năng Python, PyTorch, muốn làm đề tài NLP/LLM RAG."*
2. **LangGraph Agent thực thi**:
   - Nhận diện Domain: `NLP & Large Language Models`
   - Gọi tool: `search_advisors(query="NLP")` -> Match PGS.TS Nguyễn Văn A
   - Kiểm tra Quota: `check_advisor_capacity(ADV001)` -> Còn 3 vị trí
   - Đề xuất 4 đề tài khóa luận tiêu biểu khóa trước
3. **Kết quả**:
   - Đạt độ tương thích **94.8%**, minh bạch lý do và hướng dẫn hành động.

---

## 📊 Kết Quả Đánh Giá (Benchmark Evaluation)

| Tiêu Chí Đánh Giá | Kết Quả Đạt Được |
| :--- | :---: |
| **Độ chính xác Top-1 (Advisor Match)** | **100.0%** |
| **Tính trung thực (Faithfulness - RAGAS)** | **94.8%** |
| **Tuân thủ giới hạn chỉ tiêu (Quota Valid)** | **100.0%** |
| **Thời gian suy luận trung bình** | **6.3 ms** |

---

## 🚀 10 Deliverables Đã Hoàn Thành

1. ✅ Core Engine Matching (Hungarian + PPO RL)
2. ✅ LangGraph Multi-Node AI Agent
3. ✅ RESTful v1 OpenAPI FastAPI Service
4. ✅ Next.js 14 Dashboard
5. ✅ Streamlit Interactive Lab UI
6. ✅ MongoDB Data Persistence Layer
7. ✅ Multi-Stage Docker & Compose Orchestration
8. ✅ CI/CD Pipeline (GitHub Actions)
9. ✅ Technical Guidebook 10 Chương Chi Tiết
10. ✅ Slide & Video Kịch Bản Demo Day

---

## 💬 Q&A & Cảm Ơn Hội Đồng!

Hệ sinh thái mã nguồn mở:
- **API Docs**: `http://localhost:8000/docs`
- **Agent Health**: `http://localhost:8000/api/v1/agent/health`
- **Interactive UI**: `http://localhost:3000`
