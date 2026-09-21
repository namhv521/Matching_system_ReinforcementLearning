# Bộ demo và visual cho thuyết trình

## Mục đích

Thư mục `figures/` chứa các ảnh mô phỏng dùng trực tiếp khi trình bày với GVHD. Các số liệu benchmark lấy từ smoke result seed 42 hiện có; episode 3 sinh viên–2 giảng viên là ví dụ minh họa trong script, không phải kết quả production.

## Thứ tự trình chiếu đề xuất

| Thứ tự | File | Nội dung | Dùng ở phần script |
|---:|---|---|---|
| 1 | [`01_workflow_rl.png`](figures/01_workflow_rl.png) | Luồng dữ liệu → compatibility → environment → RL → gate | Mở đầu/workflow |
| 2 | [`02_mdp_state_action_reward.png`](figures/02_mdp_state_action_reward.png) | State, action, transition, reward | Phần MDP |
| 3 | [`03_episode_simulation.png`](figures/03_episode_simulation.png) | Mô phỏng từng bước của episode | Phần environment/reward |
| 4 | [`05_action_masking_quota.png`](figures/05_action_masking_quota.png) | Advisor đầy quota bị loại khỏi action set | Phần PPO/action masking |
| 5 | [`04_benchmark_smoke.png`](figures/04_benchmark_smoke.png) | Greedy, DQN, PPO theo smoke metrics | Phần kết quả |
| 6 | [`06_promotion_gate.png`](figures/06_promotion_gate.png) | Điều kiện để PPO được chọn hoặc giữ exact fallback | Phần kết luận |

## Cách nói ngắn khi chiếu từng ảnh

### Hình 1 — Workflow

“Đây là workflow kỹ thuật của đề tài. Dữ liệu thesis và advisor được chuyển thành compatibility matrix. Matrix này đi vào Matching Environment. Sau đó em huấn luyện các thuật toán RL và chạy các baseline trên cùng điều kiện. Kết quả được đánh giá qua metrics trước khi quyết định có nên tiếp tục dùng PPO hay giữ exact làm fallback.”

### Hình 2 — MDP

“Mỗi timestep xử lý một sinh viên. Agent nhìn thấy compatibility, quota còn lại và workload hiện tại. Agent chọn một advisor, sau đó workload được cập nhật, reward được tính và episode chuyển sang sinh viên tiếp theo.”

### Hình 3 — Episode

“Ví dụ này có ba sinh viên và hai advisor, mỗi advisor có quota hai. Sau mỗi action, load thay đổi. Vì vậy action của sinh viên trước ảnh hưởng đến tập lựa chọn của sinh viên sau. Đây là lý do bài toán có tính sequential.”

### Hình 4 — Benchmark

“Đây là smoke benchmark với seed 42 và 512 timesteps. Greedy đang có compatibility cao hơn PPO train ngắn. DQN gần Greedy nhưng có 157 invalid proposals. Vì vậy em không đánh giá model chỉ bằng compatibility; PPO có lợi thế là invalid bằng 0 nhờ action masking, nhưng vẫn cần train và đánh giá thêm.”

### Hình 5 — Action masking

“Khi advisor C đã đầy quota, PPO không còn được chọn advisor C. Đây là hard constraint được xử lý ngay ở action space. Với DQN, vì không có mask chuẩn, em ghi nhận invalid proposal riêng.”

### Hình 6 — Promotion gate

“PPO không được chọn chỉ vì có reward cao. Model phải không vi phạm quota, không có invalid proposal, ổn định qua nhiều seed, không kém exact và được đánh giá bởi chuyên gia. Nếu không đạt, exact vẫn là fallback an toàn.”

## Lưu ý khi trình bày số liệu

- Hình benchmark là **smoke result**, không phải kết luận cuối cùng.
- Không nói PPO đã tốt hơn baseline.
- Nhấn mạnh PPO là hướng nghiên cứu chính vì action masking phù hợp với quota.
- Nhấn mạnh exact là fallback hiện tại.
- Episode minh họa giúp giải thích cơ chế, không đại diện cho toàn bộ dataset.
