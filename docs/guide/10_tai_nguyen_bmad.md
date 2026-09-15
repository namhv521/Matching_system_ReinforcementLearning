# Chương 10: Tài Nguyên & Phương Pháp Luận BMAD
*Tài liệu tham khảo mở rộng*

---

## 10.1 Phương Pháp Luận BMAD (Business - Model - Architecture - Data)
Hệ thống được phát triển tuân thủ triệt để phương pháp tiếp cận 4 trụ cột BMAD:

1. **B — Business (Giá trị Nghiệp vụ)**:
   - Thấu hiểu sâu sắc bài toán phân bổ đề tài và áp lực hướng dẫn của giảng viên.
   - Định lượng hóa lợi ích: giảm 90% thời gian phân bổ thủ công, nâng độ hài lòng của sinh viên lên trên 88%.
2. **M — Model (Mô hình & Giải thuật)**:
   - Kết hợp mô hình ngôn ngữ lớn (LLM) để hiểu ngữ nghĩa với mô hình Học tăng cường (Maskable PPO) để giải quyết bài toán tối ưu hóa có điều kiện ràng buộc.
3. **A — Architecture (Kiến trúc Hệ thống)**:
   - Mô hình 3 tầng phân tán, module hóa bằng LangGraph StateGraph, đảm bảo tính mở rộng và khả năng bảo trì lâu dài.
4. **D — Data (Dữ liệu & Khai phá)**:
   - Dữ liệu giảng viên, đề tài khóa luận được chuẩn hóa, vector hóa và lưu trữ đồng bộ giữa MongoDB và hệ thống file curated.

## 10.2 Các Khóa Học & Tài Liệu Tham Khảo Khuyến Nghị
- **LangChain & LangGraph**:
  - *LangGraph Official Documentation*: Hướng dẫn thiết kế Human-in-the-loop và StateGraph.
  - *DeepLearning.AI*: Khóa học "AI Agents in LangGraph" của Harrison Chase.
- **FastAPI & Async Python**:
  - *FastAPI Documentation*: Tiêu chuẩn thiết kế Dependency Injection và Pydantic v2.
- **Reinforcement Learning**:
  - *Stable-Baselines3 Docs*: Tài liệu về Maskable PPO và Action Masking.
- **RAG & Agent Evaluation**:
  - *RAGAS Framework*: Bộ công cụ tự động hóa đánh giá độ trung thực và liên quan của Agent.
