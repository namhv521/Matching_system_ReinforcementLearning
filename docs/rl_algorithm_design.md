# Thiết kế thuật toán RL v1

## Bài toán
Với cohort gồm `N` sinh viên và `M` giảng viên, policy chọn một giảng viên cho từng sinh viên sao cho tổng compatibility cao, quota không bị vượt và tải được cân bằng.

## State, action, transition
- **State:** chỉ số student hiện tại, vector đặc trưng của student, compatibility với M advisors, remaining quota của M advisors và load hiện tại.
- **Action:** số nguyên `0..M-1`, tương ứng một advisor.
- **Transition:** tăng student index và load advisor được chọn.
- **Termination:** đã gán hết cohort.
- **Mask:** advisor hết quota bị loại; nếu tất cả hết quota thì episode kết thúc với penalty rõ ràng thay vì âm thầm gán sai.

## Compatibility
V1 dùng TF-IDF cosine trên text ghép từ thesis title, field, technologies và advisor skill/research fields. V2 có thể thay bằng sentence-transformers nhưng phải giữ nguyên ma trận khi benchmark các thuật toán.

## Reward
`r = 1.0 * compatibility + 0.15 * fairness_bonus - 2.0 * invalid_penalty`.
Fairness bonus là mức cải thiện so với load variance trước action. Sau khi có feedback thật, bổ sung preference/outcome với trọng số được ghi trong config.

## Huấn luyện và đánh giá
PPO là model chính vì phù hợp policy gradient và action masking/custom environment. DQN là đối chứng trên cùng state/action/reward. Split theo cohort/năm để tránh leakage; báo cáo mean/std qua nhiều seed. So sánh thêm Random và Greedy trước khi kết luận RL tốt hơn.

### Action masking và DQN
PPO dùng `sb3-contrib MaskablePPO` và `GymMatchingEnv.action_masks()`, nên advisor hết quota không thể được PPO chọn. DQN chuẩn không hỗ trợ action mask; environment thay action không hợp lệ bằng advisor hợp lệ có compatibility cao nhất và ghi `invalid_proposals`. Vì vậy metric này phải được báo cáo và DQN không được coi là bằng chứng về action masking.

## Protocol benchmark v2
- Train dùng thesis của các năm trước; test hold-out là năm mới nhất. Nếu không thể tách theo năm, fallback là split deterministic 80/20 theo `student_id`.
- TF-IDF vocabulary chỉ fit từ thesis train và advisor profiles; test chỉ transform để hạn chế text leakage.
- Mọi model và baseline đều dùng cùng advisor set, quota `ceil(cohort_size / advisor_count)` và compatibility matrix của cohort test.
- Metrics: mean compatibility, load variance, quota violations, historical top-1 accuracy và invalid proposals.
- Historical top-1 chỉ là mức độ tái tạo phân công lịch sử; nó không phải ground truth về matching tối ưu.

### Kết quả smoke benchmark (seed 42, 512 timesteps)
Split `year_2025_holdout` có 27 train và 163 test, nên chỉ dùng để xác nhận pipeline. Greedy đạt compatibility 0.219228; PPO Maskable mới train ngắn đạt 0.044382; DQN đạt 0.213330 nhưng có 157 invalid proposals. Chưa được dùng kết quả này để kết luận RL tốt hơn baseline. Cần có thêm cohort lịch sử hoặc dùng 80/20 cho tuning, sau đó chạy nhiều seed với 50k–200k timesteps.

## Giai đoạn triển khai
1. Cleaning + quality report (đã tạo).
2. Compatibility builder và environment smoke test.
3. Baselines.
4. PPO training nhỏ để kiểm tra pipeline, sau đó tuning.
5. DQN, ablation reward, stress test và model registry.