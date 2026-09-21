# Dàn ý cơ bản khóa luận

## Tên đề tài

**Xây dựng hệ thống hỗ trợ phân bổ sinh viên – giảng viên hướng dẫn bằng Reinforcement Learning và các phương pháp matching có ràng buộc**

## Chương 1. Giới thiệu

1. Bối cảnh phân bổ sinh viên–giảng viên.
2. Vấn đề của matching thủ công: compatibility, quota, workload và quy mô cohort.
3. Mục tiêu: compatibility matrix, MDP tuần tự, PPO/DQN, baseline, evaluation và web hỗ trợ quyết định.
4. Phạm vi: offline benchmark, quota-aware matching, human review; không tự động quyết định cuối cùng.
5. Câu hỏi nghiên cứu về MDP, PPO, action masking, baseline và tổng quát hóa cohort mới.
6. Đóng góp dự kiến và cấu trúc khóa luận.

## Chương 2. Cơ sở lý thuyết và công trình liên quan

1. Student–Advisor Matching.
2. TF-IDF, embedding và cosine similarity.
3. Capacitated assignment, Hungarian, Greedy.
4. Gale–Shapley và Student–Project Allocation.
5. MDP và Reinforcement Learning.
6. PPO, DQN, A2C, QRDQN và action masking.
7. Data leakage, temporal evaluation và model governance.

## Chương 3. Phân tích yêu cầu và dữ liệu

1. Actor: sinh viên, giảng viên, admin/hội đồng.
2. Workflow phân bổ hiện tại và pain-point evidence cần thu thập.
3. Nguồn thesis lịch sử, advisor profile, skill evidence.
4. Quyền sử dụng, anonymization và bảo mật.
5. Làm sạch, chuẩn hóa tên, deduplicate student và quality report.
6. Schema cho preference, feedback, override và outcome trong tương lai.

## Chương 4. Compatibility và temporal split

1. Các trường text của thesis/advisor.
2. Compatibility bằng TF-IDF/cosine.
3. Backend sentence-transformer tùy chọn.
4. Temporal split: pre-2025 + 75% 2025 train, phần còn lại validation/test.
5. Giữ cùng student trong một split.
6. Fit vocabulary chỉ trên train để chống leakage.

## Chương 5. Thiết kế Matching Environment và MDP

1. Episode là một cohort.
2. State: compatibility, remaining capacity, current load.
3. Action: chọn advisor.
4. Transition: cập nhật load và student index.
5. Termination và invalid action.
6. Action masking cho PPO.
7. Reward v1: compatibility, fairness improvement, invalid penalty.
8. Simulator minh họa state/action/reward.
9. Reward mở rộng: preference, acceptance và outcome.

## Chương 6. Huấn luyện thuật toán RL

1. Maskable PPO: model chính, train/inference masking.
2. DQN: model đối chứng và invalid proposals.
3. A2C và QRDQN: thuật toán bổ sung.
4. Seed, hyperparameter và cumulative milestones.
5. Lưu checkpoint, result JSON và provenance.

## Chương 7. Baseline và thiết kế thực nghiệm

1. Random: lower bound.
2. Greedy Similarity: local upper heuristic.
3. Exact/Hungarian: global objective và fallback.
4. Gale–Shapley: stability.
5. SPA: capacity/quota.
6. Protocol công bằng: cùng matrix, cohort, capacity, split, metrics và seed.
7. Preference trực tiếp so với preference proxy.

## Chương 8. Metrics và kết quả

1. Mean compatibility.
2. Total reward.
3. Load variance/fairness.
4. Quota violations.
5. Invalid proposals.
6. Assigned count, historical top-1 và runtime.
7. Mean/std qua nhiều seed.
8. Preference satisfaction, acceptance và outcome trong giai đoạn tiếp theo.
9. Bảng kết quả benchmark và learning curves.
10. Phân tích có nên dùng PPO hay exact/fallback.

## Chương 9. Ablation, stress test và promotion gate

1. Bỏ fairness reward.
2. Thay đổi fairness weight.
3. Bật/tắt action masking.
4. Thay đổi quota và kích thước cohort.
5. TF-IDF so với sentence-transformer.
6. Nhiều seed/cohort.
7. Model registry, dataset fingerprint và checkpoint hash.
8. Promotion: không violation, không invalid, vượt exact theo margin, ổn định và human review.

## Chương 10. Thiết kế phần mềm và web

1. Data, compatibility, matching, benchmark và API services.
2. Portal sinh viên: nhập skill, tìm advisor, xem đề tài lịch sử, preference và feedback.
3. Portal giảng viên: profile, quota, availability, danh sách sinh viên, accept/decline và lý do.
4. Portal admin/hội đồng: allocation, benchmark, override, audit, approve và rollback.
5. Feedback contract: actor, object, event, reason, HCD stage, model/dataset version.
6. Phân quyền, audit log và bảo vệ dữ liệu.

## Chương 11. HCD và vòng lặp feedback

1. Phỏng vấn admin/hội đồng về workflow phân công.
2. Phỏng vấn giảng viên về skill, quota, workload và lý do từ chối.
3. Phỏng vấn sinh viên về preference, trust và usefulness.
4. Pain-point evidence log: actor, bước workflow, tần suất, tác động, workaround và bằng chứng.
5. Định tuyến feedback vào Define/Ideate/Prototype/Test/Deploy/Evaluate.
6. Phân biệt feedback về constraint, preference, model error, explanation và outcome.
7. Human-in-the-loop: proposal → review → feedback → retrain/evaluate → promotion.

## Chương 12. Kết luận và hướng phát triển

1. Tổng kết đóng góp MDP, environment, RL, baseline và evaluation.
2. Giới hạn dữ liệu và giới hạn historical accuracy.
3. Exact là default/fallback hiện tại; PPO là candidate cần gate.
4. Preference/outcome/feedback learning.
5. Web role-based và continuous learning có rollback.

## Phụ lục

1. Schema dữ liệu.
2. Pseudocode environment.
3. Mermaid MDP.
4. Bảng hyperparameter.
5. Bảng checkpoint và metrics.
6. Benchmark JSON.
7. Interview guide và pain-point evidence log.
8. Hướng dẫn chạy code và tái lập thí nghiệm.
