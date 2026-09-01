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

### Giới hạn adapter SB3 v1
`stable-baselines3` chuẩn không áp dụng action mask cho PPO/DQN. `GymMatchingEnv` vì vậy thay action đề xuất đã hết quota bằng advisor hợp lệ có compatibility cao nhất và ghi `invalid_proposals` vào metrics. Đây là hard-constraint safety cho MVP, không phải action masking thực sự. Khi benchmark chính thức PPO, thay adapter bằng `sb3-contrib MaskablePPO` và báo cáo metric invalid proposals.

## Giai đoạn triển khai
1. Cleaning + quality report (đã tạo).
2. Compatibility builder và environment smoke test.
3. Baselines.
4. PPO training nhỏ để kiểm tra pipeline, sau đó tuning.
5. DQN, ablation reward, stress test và model registry.