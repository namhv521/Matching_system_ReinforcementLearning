# Kiến Trúc Hệ Thống KLTN AI Matching Agent (Architecture Diagram)

Tài liệu mô tả chi tiết kiến trúc hệ sinh thái phân bổ đề tài và giảng viên hướng dẫn khóa luận tốt nghiệp (KLTN) bằng AI Agent và thuật toán tối ưu hóa đa mục tiêu.

---

## 1. Sơ Đồ Kiến Trúc 3 Tầng (3-Tier Architecture)

```mermaid
graph TD
    subgraph Client Layer [1. Lớp Trình Diễn - Presentation]
        FE[Next.js 14 Web Dashboard]
        ST[Streamlit Interactive Lab]
        API_DOCS[OpenAPI / Swagger UI]
    end

    subgraph Service Layer [2. Lớp Dịch Vụ & Xử Lý Nghiệp Vụ - Business Core]
        API[FastAPI Gateway / RESTful v1]
        
        subgraph Agent Engine [LangGraph StateGraph Workflow]
            N1[Node 1: Query Analyzer]
            N2[Node 2: Academic Retriever]
            N3[Node 3: Matcher & Constraint Evaluator]
            N4[Node 4: Explainable Synthesizer]
        end
        
        subgraph Optimization Engine [Phân Bổ Tối Ưu]
            HUNG[Hungarian Algorithm O_N3]
            RL[Maskable PPO Agent]
            GS[Gale-Shapley Stable Marriage]
        end
    end

    subgraph Data Layer [3. Lớp Dữ Liệu & Lưu Trữ - Persistence]
        MONGO[(MongoDB 7.0 / Motor Async)]
        SQLITE[(SQLite Curated Store)]
        AUDIT[(Audit JSONL Logs)]
    end

    FE -->|HTTP / SSE| API
    ST -->|HTTP| API
    API_DOCS -->|Docs Query| API

    API --> Agent Engine
    API --> Optimization Engine

    N1 --> N2
    N2 --> N3
    N3 --> N4

    N2 -->|Search Tools| MONGO
    N2 -->|Keyword Search| SQLITE
    N4 -->|Log Interaction| AUDIT
    Optimization Engine -->|Sync Matrix| MONGO
```

---

## 2. Luồng Trạng Thái LangGraph Agent (StateGraph Flow)

```mermaid
stateDiagram-v2
    [*] --> START
    START --> analyze_query: Nhận Query & Hồ sơ sinh viên
    
    state analyze_query {
        [*] --> Phân tích từ khóa công nghệ
        Phân tích từ khóa công nghệ --> Xác định ý định (Intent Classification)
        Xác định ý định --> Đóng gói Extracted Intent
    }
    
    analyze_query --> retrieve_data: Intent hợp lệ
    
    state retrieve_data {
        [*] --> search_advisors(query)
        search_advisors(query) --> search_past_theses(keyword)
        search_past_theses(keyword) --> Thu thập danh sách ứng viên
    }
    
    retrieve_data --> evaluate_matching: Candidates Ready
    
    state evaluate_matching {
        [*] --> check_advisor_capacity(adv_id)
        check_advisor_capacity(adv_id) --> compute_compatibility_score()
        compute_compatibility_score() --> Sắp xếp xếp hạng theo Điểm & Quota
    }
    
    evaluate_matching --> synthesize_response: Bảng điểm & Ràng buộc xong
    
    state synthesize_response {
        [*] --> Soạn thảo phản hồi học thuật
        Soạn thảo phản hồi học thuật --> Gợi ý hướng đề cương tiếp theo
    }
    
    synthesize_response --> END
    END --> [*]
```

---

## 3. Sơ Đồ Trình Tự Cuộc Gọi API (Sequence Diagram)

```mermaid
sequenceDiagram
    autonumber
    actor SV as Sinh Viên (Client)
    participant API as FastAPI Router (/chat)
    participant Graph as LangGraph Workflow
    participant Tools as Agent Tools
    participant DB as Curated Database

    SV->>API: POST /api/v1/agent/chat (Query + Skills)
    API->>Graph: run_matching_agent(initial_state)
    
    Graph->>Graph: analyze_query_node()
    Graph->>Tools: search_advisors(query)
    Tools->>DB: Query faculty records
    DB-->>Tools: Top faculty matches
    
    Graph->>Tools: check_advisor_capacity(adv_id)
    Tools-->>Graph: Quota availability status
    
    Graph->>Tools: search_past_theses(keyword)
    Tools->>DB: Query past theses records
    DB-->>Tools: Past theses list
    
    Graph->>Graph: evaluate_matching_node()
    Graph->>Graph: synthesize_response_node()
    
    Graph-->>API: Result State (Answer + Recommendations)
    API-->>SV: JSON Response (HTTP 200)
```
