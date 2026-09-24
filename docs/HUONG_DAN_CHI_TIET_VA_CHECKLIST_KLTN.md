# HƯỚNG DẪN KỸ THUẬT & KẾ HOẠCH TÁC CHIẾN KHÓA LUẬN TỐT NGHIỆP
## ĐỀ TÀI: HỆ THỐNG REINFORCEMENT LEARNING TỐI ƯU PHÂN BỔ SINH VIÊN – GIẢNG VIÊN HƯỚNG DẪN DỰA TRÊN DỮ LIỆU LỊCH SỬ VÀ HỌC LIÊN TỤC

> **Sinh viên thực hiện:** Hoàng Văn Nam (MSV: 11236160)
> **Chuyên ngành:** Công nghệ thông tin – Viện Công nghệ thông tin & Kinh tế số (FIT – NEU)
> **Thời gian thực hiện:** 21/09/2026 – 15/11/2026 (8 tuần / 56 ngày tác chiến)
> **Hạn chót nộp khóa luận (Deadline):** **15/11/2026**
> **File Excel Checklist tương ứng:** `KE_HOACH_CHECKLIST_KLTN_RL_MATCHING.xlsx`

---

## MỤC LỤC

1. [Tổng quan Đề tài & Tuyên ngôn Bài toán](#1-tổng-quan-đề-tài--tuyên-ngôn-bài-toán)
2. [Thiết kế Hệ thống Machine Learning theo 7 Bước Chuẩn mực](#2-thiết-kế-hệ-thống-machine-learning-theo-7-bước-chuẩn-mực)
3. [Giải trình Chi tiết 6 Câu hỏi Nghiên cứu Cốt lõi (Trọng tâm Tuần 1)](#3-giải-trình-chi-tiết-6-câu-hỏi-nghiên-cứu-cốt-lõi-trọng-tâm-tuần-1)
   - 3.1. Giảng viên nhận features gì?
   - 3.2. Sinh viên nhận features gì?
   - 3.3. Hàm loss và hàm reward được thiết kế như thế nào?
   - 3.4. Đánh giá như thế nào, dựa trên cái gì?
   - 3.5. Các vòng đời V1, V2, V3... thiết kế thế nào? Tại sao 1 vòng dễ nhầm sang bài toán hồi quy?
   - 3.6. Accuracy dự định đạt từng vòng là bao nhiêu %, lấy gì để so sánh?
4. [Bảng Đối sánh Năng lực Các Thuật toán (RL vs Baselines)](#4-bảng-đối-sánh-năng-lực-các-thuật-toán-rl-vs-baselines)
5. [Lộ trình Tác chiến 8 Tuần & Bảng Checklist 56 Ngày](#5-lộ-trình-tác-chiến-8-tuần--bảng-checklist-56-ngày)
6. [Hướng dẫn Vận hành Hệ thống & Lệnh Thực thi CLI](#6-hướng-dẫn-vận-hành-hệ-thống--lệnh-thực-thi-cli)

---

## 1. TỔNG QUAN ĐỀ TÀI & TUYÊN NGÔN BÀI TOÁN

Trong các cơ sở giáo dục đại học nói chung và Khoa CNTT Trường ĐH Kinh tế Quốc dân (FIT NEU) nói riêng, công tác phân công giảng viên hướng dẫn (GVHD) khóa luận tốt nghiệp cho sinh viên là bài toán quản trị học thuật quan trọng và phức tạp:
- **Tính đa mục tiêu:** Cần tối đa hóa sự phù hợp giữa chủ đề khóa luận của sinh viên với năng lực/hướng nghiên cứu chuyên sâu của giảng viên, đồng thời bảo đảm phân bổ tải công bằng (fairness) giữa các giảng viên trong bộ môn.
- **Ràng buộc dung lượng cứng (Hard Capacity Constraints):** Mỗi giảng viên có hạn mức hướng dẫn tối đa $C_j = \lceil N / M \rceil$ không được phép vi phạm.
- **Tính chất tuần tự và biến động tài nguyên (Sequential Dynamic Process):** Khi phân công cho từng sinh viên, quỹ thời gian/chỉ tiêu còn lại của các giảng viên giảm dần, làm biến đổi không gian hành động hợp lệ cho các sinh viên tiếp theo.

Đề tài giải quyết bài toán bằng phương pháp **Reinforcement Learning (Học tăng cường)** kết hợp **Xử lý ngôn ngữ tự nhiên (NLP/Embeddings)**, mô hình hóa bài toán dưới dạng **Quá trình Ra quyết định Markov (MDP) tuần tự** có cơ chế **Mặt nạ hành động (Action Masking)**, đồng thời đối sánh toàn diện với các giải thuật tối ưu toán học kinh điển (**Exact Hungarian, Gale-Shapley SPA, Greedy Heuristic**).

## 2. THIẾT KẾ HỆ THỐNG MACHINE LEARNING THEO 7 BƯỚC CHUẨN MỰC

Để đáp ứng tiêu chuẩn khắt khe của một công trình kỹ thuật hệ thống học máy (Machine Learning System Design / MLE Workflow), đề tài được triển khai đầy đủ qua 7 bước:

```
+-----------------------------------------------------------------------------------+
|               QUY TRÌNH 7 BƯỚC THIẾT KẾ HỆ THỐNG MACHINE LEARNING                |
+-----------------------------------------------------------------------------------+
|  Bước 1: Problem Formulation & Business Objectives                                |
|  --> Xác định bài toán MDP có ràng buộc cứng; định hình mục tiêu tối ưu toàn cục   |
+-----------------------------------------------------------------------------------+
|  Bước 2: Data Ingestion, Cleaning & Provenance                                    |
|  --> Crawl hồ sơ GV; OCR/LLM trích xuất 198 khóa luận; audit quality report       |
+-----------------------------------------------------------------------------------+
|  Bước 3: Feature Engineering & Compatibility Representation                       |
|  --> TF-IDF cosine similarity & Sentence Transformers đa ngữ; zero leakage        |
+-----------------------------------------------------------------------------------+
|  Bước 4: Environment Modeling & RL State Dynamics                                 |
|  --> Gymnasium Env (GymMatchingEnv); Observation 3*M; Action Masking qua sb3      |
+-----------------------------------------------------------------------------------+
|  Bước 5: Reward Function & Loss Formulation                                       |
|  --> Reward đa mục tiêu (comp + delta_variance - penalty); Loss PPO vs DQN/QR-DQN  |
+-----------------------------------------------------------------------------------+
|  Bước 6: Multi-Algorithm Training & Comparative Benchmark                         |
|  --> Train PPO, DQN, A2C, QR-DQN theo milestones (500k, 1M, 2M); so sánh 5 baselines|
+-----------------------------------------------------------------------------------+
|  Bước 7: Model Governance, Deployment & Lifecycles V1-V4                          |
|  --> Promotion Gate; FastAPI + SPA Dashboard; Vòng đời V1 -> V2 -> V3 -> V4       |
+-----------------------------------------------------------------------------------+
```

### Chi tiết từng bước kỹ thuật:

1. **Bước 1: Problem Formulation & Framing**
   - Chuyển đổi bài toán phân công tĩnh sang MDP có ràng buộc dung lượng.
   - Không gian trạng thái $S$, không gian hành động $A$, hàm chuyển trạng thái $P(s' | s, a)$, hàm thưởng $R(s, a)$, hệ số chiết khấu $\gamma = 0.99$.
   - Xác định ranh giới nghiên cứu: RL hỗ trợ ra quyết định (Decision Support), con người giữ quyền duyệt cuối cùng (Human-in-the-loop).

2. **Bước 2: Data Ingestion, Cleaning & Provenance**
   - **Dữ liệu nguồn (Raw data):** 198 file PDF/DOCX luận văn các khóa trước và hồ sơ công khai của 39 giảng viên FIT NEU.
   - **Xử lý làm sạch (Deterministic Cleaning):** Chuẩn hóa tên giảng viên loại bỏ học hàm/học vị (`identity.py`), ánh xạ đồng nhất mã chuyên ngành, kiểm tra tính toàn vẹn.
   - **Provenance & Quality Gate:** Xuất báo cáo tự động `quality_report.json`: 0 unmatched rows, 0 duplicate students giữa các tập split, dữ liệu raw giữ nguyên không bị ghi đè.

3. **Bước 3: Feature Engineering & Compatibility Representation**
   - Biểu diễn văn bản phi cấu trúc (tên đề tài, công nghệ web, mobile, AI frameworks, phương pháp nghiên cứu).
   - Biểu diễn TF-IDF n-gram (1, 2) fit **duy nhất trên tập Train** để triệt tiêu nguy cơ rò rỉ dữ liệu (Data Leakage) sang Validation/Test.
   - Tùy chọn nâng cao: Dense vector embeddings 768 chiều từ `paraphrase-multilingual-mpnet-base-v2`.

4. **Bước 4: Environment Modeling & RL State Dynamics**
   - Kế thừa chuẩn `gymnasium.Env` (`GymMatchingEnv`).
   - Kích thước không gian quan sát: $\text{Dim}(S) = 3 \times M$ (với $M=39$ giảng viên $\rightarrow 117$ chiều).
   - Tích hợp **Action Masking** với `sb3-contrib`: tại bước $t$, nếu giảng viên $j$ đã đạt $L_j = C_j$, hành động $a=j$ bị gán xác suất $\pi(a=j | s) = 0$ trước tầng Softmax.

5. **Bước 5: Reward Function & Loss Formulation**
   - Thiết kế hàm thưởng đa mục tiêu kết hợp điểm tương thích chuyên môn và phần thưởng giảm phương sai tải:
     $$r_t = w_{\text{comp}} \cdot \text{comp}(i, a_t) + w_{\text{fair}} \cdot (\text{Var}_{\text{before}} - \text{Var}_{\text{after}}) - w_{\text{pen}} \cdot \mathbb{I}_{\text{invalid}}$$
   - Thiết kế hàm mất mát cho các họ giải thuật: Clipped Surrogate Objective Loss cho PPO; Temporal Difference Huber Loss cho DQN; Quantile Huber Loss cho QR-DQN.

6. **Bước 6: Multi-Algorithm Training & Comparative Benchmark**
   - Huấn luyện theo lộ trình tích lũy: 200k $\rightarrow$ 500k $\rightarrow$ 1,000,000 $\rightarrow$ 2,000,000 timesteps.
   - Huấn luyện 4 họ mô hình: Maskable PPO, DQN, QR-DQN, A2C với 3 random seeds.
   - Đối sánh với 4 baselines: Random, Greedy Similarity, Gale-Shapley (SPA), Exact Hungarian.

7. **Bước 7: Model Governance, Deployment & Lifecycles V1-V4**
   - Xây dựng **Promotion Gate** (`select_engine`): chỉ cho phép thăng hạng mô hình đạt 0 vi phạm quota và vượt baseline an toàn.
   - Đóng gói Model Manifest có SHA-256 checksum và dataset fingerprint.
   - Triển khai FastAPI backend & Interactive Web SPA Dashboard hiển thị đồ thị IEEE 300 DPI và cho phép điều chỉnh hạn mức thời gian thực.
---

## 3. GIẢI TRÌNH CHI TIẾT 6 CÂU HỎI NGHIÊN CỨU CỐT LÕI (TRỌNG TÂM TUẦN 1)

Tuần 1 là giai đoạn định hình nền tảng lý thuyết và kiến trúc hệ thống. Dưới đây là giải trình chi tiết cho 6 câu hỏi then chốt theo yêu cầu của nghiên cứu:

### 3.1. Giảng viên nhận features gì? (Advisor Feature Representation)

Trong hệ thống, mỗi giảng viên $j \in \{1, \dots, M\}$ được biểu diễn đồng thời bằng **2 nhóm đặc trưng**:

#### Nhóm 1: Đặc trưng Hồ sơ Tĩnh (Static Professional Profile)
- **Chuyên ngành chính (`primary_field`):** Phân loại hướng nghiên cứu chủ đạo (ví dụ: *Deep Learning, Web Development, Cybersecurity, Data Science, Mobile Development, IoT*).
- **Từ khóa kỹ năng (`skill_text` & `skill_count`):** Danh sách các kỹ năng, công nghệ và công cụ được trích xuất tự động từ các học phần giảng dạy và bài báo khoa học (ví dụ: *PyTorch, TensorFlow, React, FastAPI, Docker, Kubernetes*).
- **Bằng chứng năng lực khoa học (`publication_evidence_count`):** Số lượng bài báo khoa học đã công bố được liên kết làm minh chứng năng lực thực tế.
- **Học hàm / Học vị (`academic_title`):** TS, PGS, GS, ThS.
- **Biểu diễn văn bản tổng hợp:** Nối các trường văn bản phục vụ trích xuất vector đặc trưng $\mathbf{v}_j \in \mathbb{R}^D$ qua TF-IDF hoặc Sentence-Transformers.

#### Nhóm 2: Đặc trưng Ràng buộc & Tải Động (Dynamic Capacity & Workload State)
- **Hạn mức chỉ tiêu tối đa ($C_j$):** Số lượng sinh viên tối đa được phép hướng dẫn trong cohort, mặc định $C_j = \lceil N / M \rceil$ hoặc thiết lập riêng theo quy chế bộ môn.
- **Số lượng sinh viên đã gán tại bước $t$ ($L_{j, t}$):** Workload hiện tại, khởi tạo $L_{j, 0} = 0$, cập nhật $L_{j, t+1} = L_{j, t} + 1$ khi được Agent chọn.
- **Tỷ lệ dung lượng còn lại (`remaining_capacity_ratio`):**
  $$\text{rem}_{j, t} = \frac{C_j - L_{j, t}}{\max(C_j, 1)} \in [0.0, 1.0]$$
- **Tỷ lệ tải hiện thời (`current_load_ratio`):**
  $$\text{load}_{j, t} = \frac{L_{j, t}}{\max(C_j, 1)} \in [0.0, 1.0]$$

---

### 3.2. Sinh viên nhận features gì? (Student / Thesis Feature Representation)

Mỗi sinh viên $i \in \{1, \dots, N\}$ mang đề tài khóa luận được biểu diễn qua 2 cấp độ:

#### Cấp độ 1: Đặc trưng Đề tài & Năng lực Học thuật (Thesis Profile)
- **Tên đề tài khóa luận (`thesis_title`):** Chuỗi văn bản tiếng Việt mô tả nội dung đề tài nghiên cứu.
- **Lĩnh vực đề tài (`field_category`):** Phân loại đề tài (Phát triển Web, Trí tuệ nhân tạo, Di động, IoT, Hệ thống thông tin...).
- **Ngăn xếp công nghệ chi tiết (Tech Stack):**
  - Ngôn ngữ lập trình (`web_languages`, `app_languages`).
  - Frameworks (`frontend_frameworks`, `backend_frameworks`, `ai_frameworks`).
  - Cơ sở dữ liệu & Caching (`database_cache`, `app_db_backend`).
  - Bài toán & Công cụ AI (`ai_problems`, `data_tools`, `data_models`).
- **Phương pháp nghiên cứu (`research_methods`):** UML, Thực nghiệm đối chứng, Phân tích nghiệp vụ...
- **Phân loại vai trò kỹ thuật (`primary_role`, `secondary_roles`):** Backend, Frontend, Data/AI, Mobile, Security...
- **Biểu diễn văn bản tổng hợp:** Nối các trường văn bản để trích xuất vector đặc trưng $\mathbf{u}_i \in \mathbb{R}^D$.

#### Cấp độ 2: Vector Quan sát Động Đưa vào Mô hình RL (State Observation Vector)
Tại mỗi bước quyết định $t$ (khi đang cần phân công cho sinh viên $i = s_t$), môi trường cung cấp cho mạng nơ-ron của Agent vector trạng thái có kích thước **$3 \times M$ chiều**:
$$\mathbf{s}_t = \Big[ \mathbf{scores}_i, \; \mathbf{rem}_t, \; \mathbf{load}_t \Big] \in \mathbb{R}^{3M}$$
Trong đó:
1. $\mathbf{scores}_i = [\text{comp}(i, 1), \text{comp}(i, 2), \dots, \text{comp}(i, M)] \in [0, 1]^M$: Vector điểm tương thích chuyên môn giữa sinh viên $i$ và tất cả $M$ giảng viên.
2. $\mathbf{rem}_t = [\text{rem}_{1, t}, \dots, \text{rem}_{M, t}] \in [0, 1]^M$: Tỷ lệ dung lượng còn lại của $M$ giảng viên.
3. $\mathbf{load}_t = [\text{load}_{1, t}, \dots, \text{load}_{M, t}] \in [0, 1]^M$: Tỷ lệ tải hiện tại của $M$ giảng viên.

*(Với $M = 39$ giảng viên, vector quan sát có kích thước chính xác là $3 \times 39 = 117$ chiều số thực).*

---

### 3.3. Hàm loss và hàm reward được thiết kế như thế nào?

#### Thiết kế Hàm Thưởng Đa Mục Tiêu (Multi-Objective Reward Function)
Hàm phần thưởng tức thời $r_t$ tại bước $t$ khi Agent gán sinh viên $i$ cho giảng viên $a_t \in \{0, \dots, M-1\}$ được định nghĩa:
$$r_t = w_{\text{comp}} \cdot \text{comp}(i, a_t) + w_{\text{fair}} \cdot \Delta \text{Var}_t - w_{\text{pen}} \cdot \mathbb{I}_{\text{invalid}}$$

Trong đó:
1. **Thành phần tương thích chuyên môn:** $\text{comp}(i, a_t) = \cos(\mathbf{u}_i, \mathbf{v}_{a_t}) \in [0, 1]$. Trọng số $w_{\text{comp}} = 1.0$.
2. **Thành phần cân bằng tải (Fairness Bonus):**
   $$\Delta \text{Var}_t = \text{Var}(\mathbf{load}_t) - \text{Var}(\mathbf{load}_{t+1})$$
   với $\text{Var}(\mathbf{load}) = \frac{1}{M} \sum_{j=1}^M \left( \frac{L_j}{C_j} - \bar{L} \right)^2$.
   - **Ý nghĩa toán học:** Nếu hành động $a_t$ phân bổ vào giảng viên đang có ít sinh viên hơn, độ phân tán tải giảm xuống ($\text{Var}_{t+1} < \text{Var}_t \implies \Delta \text{Var}_t > 0$), Agent nhận được điểm thưởng cân bằng tải! Ngược lại, nếu dồn thêm sinh viên cho giảng viên đã nhận nhiều, $\Delta \text{Var}_t < 0$, Agent bị trừ điểm. Trọng số mặc định $w_{\text{fair}} = 0.15$.
3. **Hình phạt vi phạm (Invalid Penalty):**
   Nếu Agent đề xuất giảng viên $a_t$ đã hết dung lượng ($L_{a_t} \ge C_{a_t}$), $\mathbb{I}_{\text{invalid}} = 1$ và nhận hình phạt $w_{\text{pen}} = 2.0$.
   *(Với Maskable PPO, Action Masking triệt tiêu hành động này trước khi lấy mẫu nên $\mathbb{I}_{\text{invalid}} = 0$ tuyệt đối; hình phạt dùng để đo lường và răn đe các mô hình unmasked như DQN).*

#### Thiết kế Hàm Mất Mát (Loss Functions)

1. **Maskable PPO (Mô hình đề xuất chính):**
   $$L^{\text{PPO}}(\theta) = \hat{\mathbb{E}}_t \left[ L^{\text{CLIP}}(\theta) - c_1 L^{\text{VF}}(\theta) + c_2 S[\pi_\theta](s_t) \right]$$
   - **Policy Loss:** $L^{\text{CLIP}}(\theta) = \hat{\mathbb{E}}_t \left[ \min\left( \rho_t(\theta) \hat{A}_t, \; \text{clip}(\rho_t(\theta), 1-\epsilon, 1+\epsilon) \hat{A}_t \right) \right]$, với tỉ lệ xác suất $\rho_t(\theta) = \frac{\pi_\theta(a_t | s_t)}{\pi_{\theta_{\text{old}}}(a_t | s_t)}$ và $\epsilon = 0.2$.
   - **Value Function Loss:** $L^{\text{VF}}(\theta) = (V_\theta(s_t) - V_t^{\text{targ}})^2$ (Mean Squared Error).
   - **Entropy Bonus:** $S[\pi_\theta]$ khuyến khích khám phá không gian phân bổ.
   - **Cơ chế Action Masking:** Với tập hành động hợp lệ $\mathcal{A}_{\text{valid}}(s_t) = \{j \mid L_j < C_j\}$, phân phối xác suất hành động được chuẩn hóa lại:
     $$\pi_\theta(a | s_t) = \frac{\exp(z_a) \cdot \mathbb{I}_{a \in \mathcal{A}_{\text{valid}}}}{\sum_{k \in \mathcal{A}_{\text{valid}}} \exp(z_k)}$$

2. **DQN / Double DQN (Mô hình đối chứng Value-based):**
   $$L^{\text{DQN}}(\theta) = \mathbb{E}_{(s, a, r, s')} \left[ \left( r + \gamma \max_{a'} Q(s', a'; \theta^-) - Q(s, a; \theta) \right)^2 \right]$$
   Sử dụng mạng mục tiêu $Q(\cdot; \theta^-)$ và bộ nhớ đệm Replay Buffer để ổn định quá trình học.

3. **QR-DQN (Quantile Regression DQN - Đối chứng Distributional RL):**
   Ước lượng phân phối xác suất hoàn chỉnh của phần thưởng thay vì chỉ kỳ vọng, sử dụng **Quantile Huber Loss** trên $N_q = 32$ quantiles.

---

### 3.4. Đánh giá như thế nào, dựa trên cái gì? (Evaluation Methodology & Metrics)

Để bảo đảm tính khách quan và khoa học, hệ thống thiết lập bộ 6 chỉ số đánh giá đa chiều kết hợp với quy trình kiểm thử nghiêm ngặt:

#### Bộ 6 Thước đo Đánh giá (Metrics Suite)
1. **Độ tương thích chuyên môn trung bình (Mean Compatibility):**
   $$\text{Mean\_Comp} = \frac{1}{N} \sum_{i=1}^N \text{comp}(i, a_i) \in [0, 1]$$
   Thước đo trực tiếp chất lượng ghép đôi giữa nội dung đề tài và năng lực hướng dẫn của giảng viên.
2. **Số lượng vi phạm chỉ tiêu (Quota Violations - Hard Gate):**
   $$\text{Violations} = \sum_{j=1}^M \max(L_j - C_j, 0)$$
   **Tiêu chí sống còn:** Bắt buộc bằng **0** đối với mọi mô hình muốn được xem xét triển khai.
3. **Số đề xuất hành động sai luật (Invalid Action Proposals):**
   Số lần mô hình đề xuất giảng viên đã đầy tải. Đối với Maskable PPO, giá trị này bằng **0 tuyệt đối** nhờ Action Masking. Đối với unmasked DQN/A2C, chỉ số này phản ánh mức độ không an toàn của chính sách.
4. **Phương sai tải giảng viên (Load Variance / Fairness):**
   $$\text{Load\_Var} = \frac{1}{M} \sum_{j=1}^M (L_j - \bar{L})^2$$
   Phương sai càng thấp chứng minh sinh viên được chia đều giữa các giảng viên, tránh tình trạng "người quá tải, người không có sinh viên".
5. **Độ chính xác tái hiện lịch sử (Historical Top-1 Accuracy):**
   Tỷ lệ phần trăm sinh viên được mô hình gán trùng với giảng viên đã hướng dẫn trong hồ sơ quá khứ.
   *(Lưu ý học thuật quan trọng: Phân công lịch sử chịu ảnh hưởng bởi yếu tố cảm tính và thủ công, không phải chân lý tối ưu toàn cục; do đó chỉ số này dùng để tham khảo, không dùng làm thước đo duy nhất).*
6. **Tỷ lệ Tối ưu Lý thuyết (Theoretical Optimality Ratio):**
   $$\text{Optimality\_Ratio} = \frac{\text{Mean\_Comp}_{\text{Model}}}{\text{Mean\_Comp}_{\text{Hungarian}}} \times 100\%$$
   So sánh trực tiếp điểm số đạt được với cận trên tối ưu toàn cục của giải thuật Hungarian ($100\%$).

#### Giao thức Đánh giá (Evaluation Protocol)
- **Temporal Hold-Out Split:** Toàn bộ khóa luận trước năm 2025 + 75% khóa luận 2025 làm tập Train (158 bài); 12.5% làm Validation (20 bài); 12.5% làm Test (20 bài). Khóa cố định định danh sinh viên để không trùng lặp giữa các tập.
- **Zero Leakage:** TF-IDF vectorizer chỉ fit trên Train; Validation và Test chỉ transform.
- **Multi-Seed Aggregation:** Chạy độc lập trên **5 Random Seeds** (42, 123, 456, 789, 999), báo cáo dạng $\text{Mean} \pm \text{Std}$.
- **Kiểm định Thống kê:** Thực hiện paired t-test và Wilcoxon signed-rank test với ngưỡng ý nghĩa $p < 0.05$.

---

### 3.5. Các vòng đời V1, V2, V3... thiết kế thế nào? Tại sao nếu 1 vòng dễ nhầm sang bài toán hồi quy?

Đây là câu hỏi có ý nghĩa phương pháp luận then chốt để bảo vệ tính đúng đắn của việc áp dụng Học tăng cường trước Hội đồng:

#### Lý giải Cốt lõi: Vì sao 1 vòng (Single-Step) sẽ nhầm sang Hồi quy?
- **Bản chất của Bài toán Hồi quy / Phân loại Supervised (1 Bước độc lập):**
  Trong học có giám sát truyền thống, mỗi mẫu dữ liệu $(\mathbf{x}_i, y_i)$ được giả định là độc lập và cùng phân phối (i.i.d). Mô hình dự đoán $\hat{y}_i = f(\mathbf{x}_i)$.
  Nếu bài toán phân công chỉ xét 1 vòng duy nhất (chỉ đưa đặc trưng sinh viên vào và dự đoán giảng viên), quyết định gán sinh viên 1 cho giảng viên $A$ **hoàn toàn không làm ảnh hưởng** đến quyết định gán sinh viên 2 cho giảng viên $A$. Mô hình không có khái niệm "giảng viên $A$ đã hết chỗ"! Nếu nhiều sinh viên cùng làm về AI, mô hình hồi quy/phân loại sẽ dồn toàn bộ sinh viên vào 1-2 giảng viên nổi tiếng nhất về AI, dẫn đến vi phạm nghiêm trọng hạn mức chỉ tiêu và làm quá tải hệ thống.
- **Bản chất của Quá trình Ra quyết định Markov Tuần tự (Multi-Turn MDP):**
  Trong thực tế, khi giảng viên $A$ được gán cho sinh viên $s_1$, hạn mức còn lại của giảng viên $A$ **bị trừ đi 1** ($L_A$ tăng lên). Hành động $a_1$ đã **làm biến đổi trạng thái môi trường** $s_2 \sim P(s_2 \mid s_1, a_1)$!
  Đến bước $t=k$, khi giảng viên $A$ đã đủ chỉ tiêu ($L_A = C_A$), hành động chọn $A$ trở thành **hành động bất hợp lệ** và bị triệt tiêu bởi Action Masking. Sinh viên tiếp theo dù có làm đề tài AI trùng khớp với $A$ cũng buộc phải được điều phối sang giảng viên $B$ (người còn chỉ tiêu và có độ tương thích cao thứ hai).
  *Quyết định ở bước hiện tại làm thay đổi không gian hành động khả dĩ và tổng phần thưởng tích lũy trong tương lai!* Đây chính là định nghĩa toán học chuẩn tắc của **Quá trình ra quyết định Markov (MDP)** nhiều bước, hoàn toàn khác biệt với bài toán hồi quy tĩnh.

#### Thiết kế 4 Vòng đời Sản phẩm & Nghiên cứu (System Lifecycles V1 $\rightarrow$ V4)

1. **VÒNG ĐỜI V1 - Foundational Offline Multi-Step Matching (Giai đoạn Nền tảng):**
   - Môi trường MDP tuần tự xử lý từng sinh viên trong cohort tĩnh ($N$ bước).
   - Biểu diễn TF-IDF Cosine Similarity, Quota ràng buộc cứng, Action Masking.
   - Huấn luyện PPO, DQN, A2C và đối sánh với Exact Hungarian, Greedy, SPA.
2. **VÒNG ĐỜI V2 - Multi-Objective Semantic & Preference Matching (Nâng cao Trải nghiệm):**
   - Tích hợp **Nguyện vọng của sinh viên** (sinh viên nộp danh sách ưu tiên Top 1, Top 2, Top 3) vào hàm mục tiêu.
   - Nâng cấp bộ biểu diễn vector bằng **Multilingual Sentence Transformers** nắm bắt ngữ nghĩa sâu hơn.
   - Thêm phần thưởng khi sinh viên được ghép đúng nguyện vọng yêu thích.
3. **VÒNG ĐỜI V3 - Online Streaming & Asynchronous Arrival Simulation (Mô phỏng Luồng Thực):**
   - Thay vì toàn bộ sinh viên nộp cùng lúc, sinh viên đăng ký đề tài phân tán lệch thời gian (Rolling/Streaming window).
   - Quota và trạng thái tải của giảng viên biến động thời gian thực.
   - **Ưu thế tuyệt đối của RL:** Trong bài toán streaming không biết trước tương lai, giải thuật tối ưu tĩnh Hungarian **bất khả thi** hoặc phải chạy lại từ đầu với chi phí $O(N^3)$, trong khi Policy PPO đưa ra quyết định tức thời trong $O(M)$ với chất lượng vượt trội hoàn toàn so với Greedy!
4. **VÒNG ĐỜI V4 - Continual Learning & Human-in-the-Loop Decision Support (Ứng dụng Thực tế):**
   - Triển khai Dashboard cho Ban Giám hiệu / Trưởng Bộ môn: Xem đề xuất $\rightarrow$ Phê duyệt hoặc Điều chỉnh thủ công (Override).
   - Ghi nhận nhật ký phản hồi (Feedback Audit Log).
   - Fine-tune chính sách Policy định kỳ từ dữ liệu feedback mà không bị hiện tượng quên thảm khốc (Catastrophic Forgetting).

---

### 3.6. Accuracy dự định đạt từng vòng là bao nhiêu %, lấy gì để so sánh?

#### Hệ thống Đối chuẩn (Baselines - Lấy gì để so sánh?)
Để đánh giá mô hình Reinforcement Learning, luận văn xây dựng một quang phổ đối chứng toàn diện:
1. **Random Allocation (Cận dưới - Lower Bound):** Chọn ngẫu nhiên giảng viên còn slot. (Validation Compatibility: `0.018001`).
2. **Greedy Similarity Heuristic (Cận tham lam cục bộ):** Gán ngay giảng viên còn trống có độ tương thích cao nhất. (Validation Compatibility: `0.061767`).
3. **Gale-Shapley SPA (Thuật toán ghép đôi bền vững Nobel 2012):** Sinh viên đề xuất theo bảng ưu tiên, giảng viên giữ chỗ tạm thời và loại bỏ người kém ưu tiên hơn nếu quá tải. (Validation Compatibility: `0.061788`).
4. **Exact Hungarian Solver (CẬN TRÊN LÝ THUYẾT - 100% Global Optimum):** Quy hoạch nguyên tuyến tính cực tiểu hóa chi phí (Linear Sum Assignment) trên ma trận khoảng cách bù. (Validation Compatibility: `0.065601` $\rightarrow$ mốc 100% chuẩn).
5. **DQN / QR-DQN / A2C (Nhóm RL không dùng Mask):** Đối chứng hiệu quả của Action Masking.

#### Mục tiêu Định lượng (Accuracy & Target Metrics) cho Từng Vòng đời

| Vòng đời | Chỉ số Ràng buộc (Quota Violations) | Invalid Action Proposals | Tỷ lệ Tối ưu so với Hungarian (Optimality Ratio) | Historical Top-1 Accuracy | Độ thỏa mãn Nguyện vọng (Top-3 Preference) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Vòng 1** (Offline Static RL) | **0 vi phạm (100%)** | **0 (0%)** | Đạt **84.7%** (1M steps) $\rightarrow$ Mục tiêu tuning: **88% - 92%** | **25% - 35%** (lịch sử vốn mang tính cảm tính) | N/A (chưa xét nguyện vọng) |
| **Vòng 2** (Semantic & Preference) | **0 vi phạm (100%)** | **0 (0%)** | Đạt **90% - 95%** của Hungarian | **35% - 45%** | **$\ge$ 85%** sinh viên nhận GV trong Top 3 |
| **Vòng 3** (Online Streaming Arrival) | **0 vi phạm (100%)** | **0 (0%)** | **Vượt trội Hungarian tĩnh từ 8% - 14%**; **Vượt Greedy từ 12% - 18%** | N/A | **$\ge$ 88%** |
| **Vòng 4** (Human-in-the-Loop) | **0 vi phạm (100%)** | **0 (0%)** | Duy trì $\ge$ 95% sau các lượt override | Khớp **$\ge$ 75%** với quyết định của Hội đồng | **$\ge$ 92%** |

---

## 4. BẢNG ĐỐI SÁNH NĂNG LỰC CÁC THUẬT TOÁN (RL VS BASELINES)

Dưới đây là bảng tổng hợp kết quả thực nghiệm thực tế từ các lần chạy qua đêm (Overnight Experiment) trên tập Validation ($N=20$ đề tài, $M=39$ giảng viên):

| Họ giải thuật | Thuật toán | Cơ chế cốt lõi | Ràng buộc Quota | Điểm Compatibility TB | Vi phạm Quota | Đề xuất Sai luật (Invalid Proposals) | Trạng thái Nghiệp vụ |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Baseline** | Random | Lựa chọn ngẫu nhiên slot trống | Tuân thủ | 0.018001 | 0 | 0 | Cận dưới |
| **Baseline** | Greedy Similarity | Tham lam điểm tương thích cao nhất | Tuân thủ | 0.061767 | 0 | 0 | Heuristic cục bộ |
| **Baseline** | Gale-Shapley (SPA) | Đề xuất và chấp nhận hoãn lại | Tuân thủ | 0.061788 | 0 | 0 | Đối chuẩn ổn định 2 chiều |
| **Toán học** | **Exact Hungarian** | **Quy hoạch tuyến tính tối ưu toàn cục** | **Tuân thủ** | **0.065601** | **0** | **0** | **PROMOTED (Batch Engine)** |
| **RL Masked** | Maskable PPO (500k) | Policy Gradient + Action Masking | Tuân thủ | 0.040845 | 0 | 0 | Đang học |
| **RL Masked** | **Maskable PPO (1M)** | **Policy Gradient + Action Masking** | **Tuân thủ** | **0.055579** | **0** | **0** | **Mô hình RL tốt nhất (84.7%)** |
| **RL Masked** | Maskable PPO (2M) | Policy Gradient + Action Masking | Tuân thủ | 0.047653 | 0 | 0 | Chớm overfitting |
| **RL Unmasked**| Standard DQN (2M) | Deep Q-Learning, không mask | Can thiệp | 0.048941* | 0 (sau sửa) | **13 / 20 (65%)** | Bị từ chối (Không an toàn) |
| **RL Unmasked**| A2C (2M) | Advantage Actor-Critic, không mask | Can thiệp | 0.063387* | 0 (sau sửa) | **19 / 20 (95%)** | Bị từ chối (Không an toàn) |
| **RL Unmasked**| QR-DQN (2M) | Quantile Regression, không mask | Can thiệp | 0.064199* | 0 (sau sửa) | **17 / 20 (85%)** | Bị từ chối (Không an toàn) |

> **Nhận định quan trọng cho luận văn:**
> 1. **Tính tất yếu của Action Masking:** Nếu không có mặt nạ hành động, các mô hình RL (DQN, A2C, QR-DQN) liên tục đề xuất giảng viên đã kín chỗ (tỷ lệ lỗi từ 65% đến 95%). Duy nhất **Maskable PPO** đảm bảo 100% hành động đề xuất là hợp lệ (0 invalid proposals).
> 2. **Điểm dừng sớm (Early Stopping):** PPO đạt đỉnh tại 1,000,000 steps (`0.055579`). Ở mốc 2,000,000 steps, điểm số giảm nhẹ cho thấy hiện tượng quá khớp (overfitting) với phân phối của 150 đề tài tập train.
> 3. **Vị trí của RL vs Hungarian:** Đối với bài toán phân bổ toàn bộ (Full-batch static), Hungarian là tối ưu toàn cục. Vai trò thực tế của PPO là trong bài toán **phân bổ luồng trực tuyến (Online Streaming Allocation)** khi sinh viên đến bất đồng bộ và thông tin tương lai chưa được biết trước.

---

## 5. LỘ TRÌNH TÁC CHIẾN 8 TUẦN & BẢNG CHECKLIST 56 NGÀY

Toàn bộ 56 ngày từ 21/09/2026 đến 15/11/2026 được phân bổ chi tiết trong file Excel `KE_HOACH_CHECKLIST_KLTN_RL_MATCHING.xlsx` (Sheet `Checklist_HangNgay`). Dưới đây là tóm tắt các chặng chiến lược:

```
[Tuần 1: 21/09 - 27/09] -> Thiết lập Nền tảng, Trả lời 6 Câu hỏi Lớn & Chạy Baseline Hungarian
[Tuần 2: 28/09 - 04/10] -> Hoàn thiện Data Pipeline, Audit Provenance & Embeddings tiếng Việt
[Tuần 3: 05/10 - 11/10] -> Xây dựng Gymnasium Env v2, Action Masking & Multi-Objective Reward
[Tuần 4: 12/10 - 18/10] -> Huấn luyện Đa thuật toán (PPO, DQN, QR-DQN, A2C) theo Milestones
[Tuần 5: 19/10 - 25/10] -> Chạy Benchmark Đa Seed, Đánh giá Thống kê (t-test) & Test Set Final
[Tuần 6: 26/10 - 01/11] -> Hiện thực Lifecycle V2-V3, Khóa Promotion Gate & Triển khai Dashboard
[Tuần 7: 02/11 - 08/11] -> Soạn thảo Toàn diện 12 Chương Bản thảo Khóa luận Tốt nghiệp (120 trang)
[Tuần 8: 09/11 - 15/11] -> Tiếp thu Phản biện GVHD, Diễn tập Thuyết trình & NỘP KHÓA LUẬN (DL: 15/11)
```

### Phân rã Trọng tâm Từng Tuần:

- **Tuần 1 (21/09 - 27/09/2026) - Nền tảng Lý thuyết & Định nghĩa Toán học:**
  - *Mục tiêu:* Trả lời thấu đáo 6 câu hỏi lớn về Features GV/SV, Loss, Reward, Multi-turn MDP vs Hồi quy, Baselines và Accuracy targets.
  - *Sản phẩm:* Hoàn thành tài liệu thiết kế và chạy thành công Hungarian solver trên cả 3 split (Train/Val/Test).

- **Tuần 2 (28/09 - 04/10/2026) - Dữ liệu & Kỹ thuật Đặc trưng (ML Bước 2 & 3):**
  - *Mục tiêu:* Chuẩn hóa toàn diện 198 khóa luận (`theses.csv`) và 39 giảng viên (`advisors.csv`), hoàn thiện cơ chế tách từ tiếng Việt, tính ma trận Cosine Similarity bằng TF-IDF và Sentence Transformers.
  - *Sản phẩm:* `quality_report.json` đạt 0 lỗi, Data Contract tự động kiểm tra trước khi train.

- **Tuần 3 (05/10 - 11/10/2026) - Môi trường Gymnasium & Hàm Thưởng (ML Bước 4 & 5):**
  - *Mục tiêu:* Nâng cấp `GymMatchingEnv`, kiểm thử Action Masking triệt tiêu 100% việc chọn GV quá tải, tích hợp hàm thưởng đa mục tiêu với độ cân bằng tải `fairness_weight`.
  - *Sản phẩm:* Bộ kiểm thử `tests/test_gym_matching_env.py` pass 100%, CLI mô phỏng phân bổ theo từng bước `simulate_matching.py`.

- **Tuần 4 (12/10 - 18/10/2026) - Huấn luyện Đa thuật toán (ML Bước 6):**
  - *Mục tiêu:* Huấn luyện 4 thuật toán: Maskable PPO, DQN, QR-DQN, A2C qua các cột mốc tích lũy (500k, 1M, 2M steps) với 3 seeds.
  - *Sản phẩm:* 12 checkpoints `.zip`, log TensorBoard ghi nhận quá trình hội tụ và hiện tượng overfitting.

- **Tuần 5 (19/10 - 25/10/2026) - Đánh giá Thực nghiệm & Kiểm định Thống kê (ML Bước 7 Part 1):**
  - *Mục tiêu:* Chạy benchmark 8 giải thuật trên 5 seeds độc lập, tính Mean $\pm$ Std, chạy kiểm định paired t-test / Wilcoxon ($p < 0.05$), khóa đánh giá trên tập Test set.
  - *Sản phẩm:* `outputs/results/benchmark_validation_5seeds.json`, báo cáo kiểm định thống kê và ablation study.

- **Tuần 6 (26/10 - 01/11/2026) - Vòng đời V2-V3, Khóa Gate & Dashboard Web (ML Bước 7 Part 2):**
  - *Mục tiêu:* Mô phỏng Lifecycle V2 (nguyện vọng sinh viên) và Lifecycle V3 (online streaming arrival); Khóa Promotion Gate; Triển khai Dashboard Web SPA và xuất 5 biểu đồ IEEE 300 DPI.
  - *Sản phẩm:* Web Dashboard tương tác chạy tại `http://localhost:8000`, 5 sơ đồ chất lượng cao sẵn sàng đưa vào luận văn.

- **Tuần 7 (02/11 - 08/11/2026) - Soạn thảo Bản thảo Khóa luận Tốt nghiệp:**
  - *Mục tiêu:* Viết hoàn thiện từ Chương 1 đến Chương 12 bản thảo KLTN (dự kiến 100 - 120 trang), chèn toàn bộ hình ảnh, bảng biểu, công thức toán học và tài liệu tham khảo theo chuẩn NEU.
  - *Sản phẩm:* File bản thảo hoàn chỉnh `baocao/KLTN_HoangVanNam_Full_Draft.docx` gửi GVHD duyệt lần 1.

- **Tuần 8 (09/11 - 15/11/2026) - Hoàn thiện, Diễn tập & Nộp Khóa luận Chính thức:**
  - *Mục tiêu:* Sửa chữa theo góp ý của GVHD; Hoàn thành Slide PowerPoint bảo vệ (25 slides); Diễn tập thuyết trình 15 phút; In đóng quyển bìa cứng và nộp chính thức.
  - *Sản phẩm:* **HỒ SƠ KHÓA LUẬN HOÀN CHỈNH NỘP VĂN PHÒNG VIỆN CNTT&KTS TRƯỚC 15/11/2026.**

---

## 6. HƯỚNG DẪN VẬN HÀNH HỆ THỐNG & LỆNH THỰC THI CLI

Khi clone hoặc mở product repository, chạy các lệnh dưới đây trực tiếp từ Git root hiện hành (trên máy gốc là `C:\Su\KLTN\KLTN`):

### 1. Kiểm tra Môi trường & Chạy Bộ Kiểm thử Toàn diện (Unit Tests)
```powershell
# Kích hoạt môi trường ảo nếu có
# .venv\Scripts\Activate.ps1

# Chạy toàn bộ unit tests và integration tests
python -m pytest tests/ -v
```

### 2. Kiểm tra và Làm sạch Dữ liệu (Data Pipeline & Quality Report)
```powershell
# Làm sạch dữ liệu và xuất báo cáo chất lượng ra data/curated/quality_report.json
python -m src.data_pipeline.clean_processed_data

# Xác thực tính toàn vẹn và không rò rỉ dữ liệu
python scripts/validate_data.py
```

### 3. Chạy Thử nghiệm Đối chuẩn Baseline Nhanh (Smoke Benchmark)
```powershell
# Chạy benchmark trên tập validation với seed 42
python -m src.rl.benchmark --split validation --seed 42

# Chạy giải thuật đối chuẩn Hungarian (Cận trên lý thuyết)
python -m src.rl.benchmark --strategy exact --split validation

# Chạy giải thuật Gale-Shapley (SPA)
python -m src.rl.benchmark --strategy spa --split validation
```

### 4. Huấn luyện Mô hình Học tăng cường (RL Training)
```powershell
# Huấn luyện Maskable PPO (mô hình chính)
python -m src.rl.train --algorithm ppo --timesteps 1000000 --seed 42

# Huấn luyện DQN đối chứng
python -m src.rl.train --algorithm dqn --timesteps 1000000 --seed 42

# Huấn luyện qua đêm toàn bộ 4 thuật toán và các cột mốc
python scripts/train_overnight.py
```

### 5. Đánh giá Checkpoint & Chạy Cổng Thăng Hạng (Promotion Gate)
```powershell
# Đánh giá toàn bộ các checkpoint trên tập validation
python scripts/run_checkpoint_benchmarks.py --split validation

# Quyết định chọn engine sản phẩm dựa trên Promotion Gate
python -m src.rl.promotion
```

### 6. Xuất Bản Biểu Đồ Chuẩn Công Bố Khoa Học (IEEE/ACM 300 DPI)
```powershell
# Tạo 5 biểu đồ chất lượng cao trong outputs/figures/
python scripts/generate_figures.py
```

### 7. Khởi chạy Giao diện Tương tác Web SPA & Backend FastAPI
```powershell
# Khởi chạy máy chủ Dashboard thời gian thực
python run_dashboard.py
# Truy cập giao diện tại: http://localhost:8000
# Truy cập tài liệu API Swagger tại: http://localhost:8000/docs
```

### 8. Tạo Lại File Excel Kế Hoạch & Checklist
```powershell
# Tự động cập nhật hoặc tái tạo file Excel checklist
python -m scripts.kltn_excel_builder
```

---

## LỜI KẾT & CAM KẾT HÀNH ĐỘNG

Dự án Khóa luận tốt nghiệp đã được chuẩn bị đầy đủ về cả **hạ tầng dữ liệu**, **mã nguồn thuật toán**, **mô hình toán học MDP**, **hệ thống kiểm thử**, **giao diện ứng dụng** và **bản đồ tác chiến 56 ngày**.

Việc tuân thủ chặt chẽ checklist hàng ngày trong file `KE_HOACH_CHECKLIST_KLTN_RL_MATCHING.xlsx` và giải trình thấu đáo 6 câu hỏi học thuật cốt lõi trong tuần đầu tiên sẽ bảo đảm đề tài hoàn thành đúng hạn vào ngày **15/11/2026** và đạt kết quả xuất sắc cao nhất trước Hội đồng chấm khóa luận tốt nghiệp!
