# Báo cáo hoàn thiện KLTN v1

## 1. Phạm vi và bài toán

Đề tài xây dựng hệ thống hỗ trợ phân bổ sinh viên làm khóa luận cho giảng viên hướng dẫn. Một phương án phân bổ phải đồng thời tối đa hóa độ tương thích chuyên môn, không vượt hạn mức hướng dẫn và hạn chế mất cân bằng tải. Hệ thống không thay thế hội đồng chuyên môn; kết quả là đề xuất có thể kiểm tra và điều chỉnh.

Bài toán batch, khi toàn bộ cohort đã biết trước, được giải bằng Exact Hungarian để có cận trên tối ưu toàn cục. Bài toán tuần tự được mô hình hóa thành MDP và đánh giá Maskable PPO cùng A2C, DQN và QR-DQN. Promotion gate không mặc định chọn RL: engine chỉ được chọn từ số đo validation và phải fail-closed khi thiếu metric hoặc vi phạm ràng buộc.

## 2. Dữ liệu, làm sạch và provenance

Pipeline curated được chạy bằng:

```powershell
python -m src.data_pipeline.prepare_curated_data
```

Kết quả kiểm chứng ngày 22/09/2026:

| Chỉ số | Giá trị |
| --- | ---: |
| Dòng khóa luận đầu vào | 198 |
| Dòng khóa luận curated | 198 |
| Giảng viên trong roster | 39 |
| Học phần hợp lệ | 163 |
| Dòng bằng chứng kỹ năng | 215 |
| Advisor không ánh xạ | 0 |
| Advisor có tên nhưng không ánh xạ | 0 |
| Ánh xạ fuzzy cần audit | 3 |

Dữ liệu nguồn không bị ghi đè. Những bản ghi gần giống nhau vẫn được giữ như các quan sát nguồn; việc chia tập dựa trên nhóm sinh viên để cùng một người không xuất hiện ở nhiều split. Tập public dùng cho triển khai thay `student_id` và `student_name` bằng mã giả; phép kiểm tra giao nhau với định danh curated cho kết quả bằng 0.

## 3. Feature engineering và chống leakage

Đề tài sử dụng TF-IDF n-gram và cosine similarity trên tiêu đề, lĩnh vực, công nghệ và hồ sơ kỹ năng giảng viên. Vocabulary chỉ được fit trên train; validation và test chỉ được transform. Split hiện hành gồm 156 dòng train, 20 validation và 22 test. Validation dùng để chọn milestone/model; test chỉ dùng sau khi khóa lựa chọn.

Các nhóm vai trò chính trong 198 đề tài gồm Data/AI 69, Backend 43, Frontend 31, Game/Graphics 23, Mobile 20 và các nhóm nhỏ khác. Phân bố này cho thấy dữ liệu nghiêng mạnh về Data/AI và phát triển phần mềm, cần được nêu như một giới hạn khi khái quát hóa.

## 4. Môi trường RL và ràng buộc

`GymMatchingEnv` xử lý từng sinh viên theo thứ tự. Observation ghép ba vector theo giảng viên: compatibility, tỷ lệ capacity còn lại và tỷ lệ tải hiện tại. Action là chọn một giảng viên. Maskable PPO loại bỏ giảng viên đã đầy quota trước khi lấy mẫu; các model không mask vẫn ghi nhận `invalid_proposals` ngay cả khi hệ thống fallback để tạo phân bổ hợp lệ.

Các test kiểm tra reset/step, split theo nhóm, thuật toán được hỗ trợ và promotion gate. Quota violation và invalid proposal được báo riêng để không che giấu hành vi policy không an toàn.

## 5. Reward, loss và tiêu chí đánh giá

Reward kết hợp compatibility và mức giảm phương sai tải; hành động không hợp lệ nhận penalty. PPO dùng clipped surrogate objective, A2C dùng advantage actor-critic, DQN dùng TD loss và QR-DQN dùng quantile regression loss.

Metric chính:

- Mean compatibility trên validation/test.
- Optimality ratio so với Exact Hungarian.
- Load variance/fairness.
- Quota violations.
- Invalid proposals trước fallback.
- Historical top-1 accuracy chỉ dùng tham khảo, không xem assignment lịch sử là ground truth tối ưu.

Promotion gate yêu cầu đủ metric, `quota_violations = 0` và `invalid_proposals = 0`. Nếu RL không vượt điều kiện đã định nghĩa, Exact tiếp tục là engine batch an toàn.

## 6. Huấn luyện và benchmark

Protocol huấn luyện gồm PPO, A2C, DQN và QR-DQN ở các mốc tích lũy 500k, 1M và 2M timesteps; Random, Greedy, Gale-Shapley và Exact được đánh giá trên cùng validation cohort. Artifact được đặt tại `outputs/results/` và checkpoint tại `outputs/models/`.

Kết quả seed 42 đã kiểm chứng:

| Thuật toán | Compatibility validation | Invalid proposals | Trạng thái |
| --- | ---: | ---: | --- |
| Random | 0.018001 | 0 | Baseline dưới |
| Greedy | 0.061767 | 0 | An toàn |
| Gale-Shapley | 0.061788 | 0 | An toàn |
| Exact Hungarian | 0.065601 | 0 | Engine batch được chọn |
| Maskable PPO, 2M | 0.047653 | 0 | An toàn nhưng dưới Exact |
| A2C, 2M | 0.063387 | 19 | Không qua gate |
| DQN, 2M | 0.048941 | 13 | Không qua gate |
| QR-DQN, 2M | 0.064199 | 17 | Không qua gate |

PPO seed 42 đạt validation tốt nhất `0.055579` ở checkpoint 1M, tương đương khoảng 84,7% Exact. Điểm giảm ở 2M là bằng chứng cần early stopping theo validation, không phải lý do để tiếp tục train vô hạn. Một lần chạy độc lập với seed 123 được dừng tại checkpoint PPO 1M sau khi đã lưu artifact: compatibility validation `0.022589`, `0` invalid proposal và `0` quota violation. Kết quả này xác nhận tính an toàn của action masking nhưng cũng cho thấy độ nhạy theo split/seed; vì vậy không có cơ sở nâng PPO thay Exact. Test không được dùng để điều chỉnh model.

## 7. Model governance và vòng đời

Kết quả seed 42 chọn `exact` với lý do đây là mặc định batch an toàn. Checkpoint PPO 1M được giữ cho mô phỏng streaming vì policy có action masking và inference tuần tự. Dashboard hiển thị engine được promote, model RL tốt nhất, seed và metric từ JSON artifact thay vì số hard-code.

Vòng đời đề xuất:

1. V1: batch matching với TF-IDF, quota cứng và benchmark đầy đủ.
2. V2: preference Top-3 và embedding đa ngữ khi có dữ liệu hợp lệ.
3. V3: streaming arrival, đánh giá policy trong bối cảnh không biết tương lai.
4. V4: human-in-the-loop, audit override và continual learning có kiểm soát.

## 8. Phân tích dữ liệu và trực quan hóa

`src/analysis/experiment_analysis.py` đọc mọi file thí nghiệm hoàn chỉnh `overnight_seed*_steps*.json`, kiểm tra metric bắt buộc và tổng hợp mean, sample standard deviation, safe-run rate, invalid proposal và quota violation theo model. `scripts/generate_figures.py` dùng trực tiếp kết quả này, không còn hard-code các cột so sánh. Artifact PPO seed 123 được giữ riêng vì run được dừng có chủ đích tại checkpoint 1M, không trộn một run dở dang vào bảng so sánh đầy đủ 2M.

Các hình được sinh ở 300 DPI:

- `figure1_ppo_learning_curves.png`: reward và compatibility theo milestone.
- `figure2_constraint_violations.png`: invalid proposals trung bình theo model RL.
- `figure3_algorithm_comparison.png`: mean ± SD compatibility; màu thể hiện độ an toàn ràng buộc.
- `figure4_system_architecture.png`: kiến trúc hệ thống.
- `figure5_rl_mdp_flow.png`: luồng MDP/action mask.
- `figure6_data_distribution.png`: phân bố vai trò đề tài và bằng chứng kỹ năng giảng viên.

Lệnh tái lập:

```powershell
python scripts/generate_figures.py
```

## 9. Frontend, backend, CI/CD và triển khai

Frontend React/TypeScript cung cấp tổng quan, mô phỏng cohort, gợi ý giảng viên, danh bạ, benchmark, learning curves và thư viện hình. Dữ liệu được lấy từ FastAPI; giao diện có loading, empty/error state, responsive navigation và copy được sửa để phản ánh đúng 198 bản ghi cùng protocol split hiện hành.

FastAPI cung cấp health, analytics, figures, benchmark, directory, recommendation và cohort matching. Input được kiểm tra bằng schema; security headers được kiểm thử; lỗi public không trả stack trace. Bản deploy dùng dataset đã loại định danh sinh viên.

CI trên GitHub chạy toàn bộ pytest, Vitest, TypeScript/Vite build và Docker build cho `main` và `KLTN`. Container build frontend rồi phục vụ static bundle cùng FastAPI, giảm còn một web service. `render.yaml` cấu hình Render free web service với `/health`; free instance có thể sleep khi không hoạt động và cold-start khi truy cập lại.

## Kiểm chứng

Các kiểm chứng đã chạy trong phiên hoàn thiện:

| Hạng mục | Kết quả hiện tại |
| --- | --- |
| Toàn bộ Python | 26 tests pass |
| Frontend Vitest | 5 tests pass |
| Frontend production build | Thành công |
| FastAPI `/health` và `/` | HTTP 200 |
| Public dataset | 198 dòng; 0 ID/name giao với curated |
| Figure generation | 6 PNG được tạo; figure 2, 3, 6 đọc artifact/dataset thật |

Remote branch đã được xác minh tại `namhv521/sutudy`, nhánh `KLTN`. Docker smoke test, CI cuối và deployment URL chỉ được ghi là hoàn tất sau khi có bằng chứng tương ứng.

## Hạn chế và hướng tiếp theo

- Cohort validation/test nhỏ nên phương sai đa-seed và confidence interval quan trọng hơn một điểm đơn lẻ.
- TF-IDF không nắm bắt đầy đủ đồng nghĩa tiếng Việt; embedding chỉ nên thêm sau ablation có kiểm soát.
- Historical advisor không phải ground truth tối ưu.
- Exact là lựa chọn đúng cho batch đầy đủ; lợi ích RL phải được chứng minh ở streaming, không tuyên bố từ batch benchmark.
- Deployment free có cold start và giới hạn tài nguyên; model/training không chạy trực tiếp trên web service.
