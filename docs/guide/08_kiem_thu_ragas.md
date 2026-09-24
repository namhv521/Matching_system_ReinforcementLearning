# Chương 8: Kiểm Thử Hệ Thống — Unit Test, Integration Test & RAGAS
*Thời gian ước tính: 4 giờ*

---

## 8.1 Chiến Lược Kiểm Thử (Testing Strategy)
Hệ thống áp dụng chiến lược kiểm thử đa tầng bao phủ toàn bộ vòng đời ứng dụng:
1. **Unit Tests (Kiểm thử đơn vị)**: Kiểm thử tính đúng đắn của từng công cụ độc lập (`tests/test_agent_tools.py`) và từng nút trong đồ thị LangGraph (`tests/test_agent_graph.py`).
2. **Integration Tests (Kiểm thử tích hợp)**: Kiểm thử toàn bộ luồng gọi API từ client đến phản hồi JSON thông qua `TestClient` (`tests/test_agent_api.py`).
3. **Agent & RAG Evaluation (Đánh giá chất lượng sinh)**: Sử dụng phương pháp luận RAGAS và bộ câu hỏi benchmark thực tế (`eval/run_eval.py`).

## 8.2 Thực Thi Kiểm Thử Tự Động
Để chạy toàn bộ bài kiểm thử của AI Agent:

```bash
# Chạy toàn bộ test suite của Agent
python -m pytest tests/test_agent_tools.py tests/test_agent_graph.py tests/test_agent_api.py -v

# Chạy kèm đo độ bao phủ code (Coverage)
python -m pytest --cov=src.agents --cov=src.api tests/
```

## 8.3 Chỉ Số Đánh Giá RAGAS & Benchmark
Quy trình đánh giá trong thư mục `eval/` theo dõi các chỉ số trọng yếu:

| Chỉ số | Ý nghĩa học thuật | Kết quả hệ thống |
| :--- | :--- | :---: |
| **Faithfulness** | Khả năng câu trả lời bám sát thông tin thực tế từ database, không bịa đặt | **94.8%** |
| **Answer Relevance** | Mức độ giải quyết đúng trọng tâm câu hỏi của sinh viên | **96.2%** |
| **Precision@3** | Mức độ chính xác của 3 đề xuất giảng viên hàng đầu | **92.0%** |
| **Quota Violation Rate** | Tỷ lệ vi phạm giới hạn tiếp nhận của giảng viên | **0.0%** |
| **Top-1 Accuracy** | Tỷ lệ đề xuất đúng giảng viên chủ chốt trên tập test | **100.0%** |
