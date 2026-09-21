# Script thuyết trình với GVHD

## Chủ đề

**Hệ thống phân bổ sinh viên – giảng viên hướng dẫn bằng Reinforcement Learning**

## 1. Mở đầu: vấn đề cần giải quyết

Em xin trình bày những phần đã thực hiện trong đề tài phân bổ sinh viên cho giảng viên hướng dẫn bằng Reinforcement Learning.

Bài toán là: với một nhóm sinh viên và danh sách giảng viên, làm thế nào để phân bổ mỗi sinh viên cho một giảng viên phù hợp nhất. Nếu chỉ chọn giảng viên có độ tương đồng cao nhất cho từng sinh viên độc lập thì có thể xảy ra tình trạng nhiều sinh viên cùng chọn một giảng viên, vượt quota, workload mất cân bằng, hoặc các lựa chọn đầu làm cho sinh viên phía sau không còn phương án phù hợp.

Vì vậy, em không xem đây chỉ là bài toán tìm kiếm độc lập. Em mô hình hóa nó thành bài toán ra quyết định tuần tự trên toàn bộ cohort.

**Visual trình chiếu:** [Hình 1 – Workflow RL](figures/01_workflow_rl.png)

## 2. Chuyển bài toán thành MDP

Ý tưởng chính là dùng Reinforcement Learning để agent lần lượt phân bổ từng sinh viên. Một episode tương ứng với một cohort. Ở mỗi bước, agent quan sát trạng thái hiện tại và chọn một giảng viên.

- **State** gồm compatibility của sinh viên hiện tại với tất cả giảng viên, quota còn lại và workload hiện tại.
- **Action** là chọn một giảng viên cho sinh viên đang xét.
- **Transition** là tăng workload của giảng viên được chọn và chuyển sang sinh viên tiếp theo.
- **Reward** phản ánh độ phù hợp và mức cân bằng workload.

Mục tiêu là tối đa hóa tổng reward trên toàn cohort nhưng vẫn không vượt quota. Đây là điểm khác so với việc chọn advisor tốt nhất cho từng sinh viên riêng lẻ: action hiện tại ảnh hưởng đến các bước tiếp theo.

**Visual trình chiếu:** [Hình 2 – MDP state/action/reward](figures/02_mdp_state_action_reward.png)

## 3. Dữ liệu và compatibility

Em đã chuẩn bị dữ liệu cho hai phía: thông tin đề tài sinh viên và thông tin chuyên môn của giảng viên.

Với sinh viên, các trường gồm tiêu đề đề tài, lĩnh vực, ngôn ngữ, framework, công cụ dữ liệu và phương pháp nghiên cứu. Với giảng viên, các trường gồm lĩnh vực chính, kỹ năng, framework, công nghệ và công cụ dữ liệu.

Ở phiên bản hiện tại, em ghép các trường văn bản và dùng **TF-IDF kết hợp cosine similarity** để tạo compatibility matrix giữa từng sinh viên và từng giảng viên.

Em chọn TF-IDF vì dễ tái lập, phù hợp với dữ liệu hiện tại, dễ kiểm tra và có thể dùng chung cho PPO, DQN và các baseline. Hệ thống cũng có thể thử sentence-transformer, nhưng khi so sánh phải giữ nguyên cách chia dữ liệu và phiên bản encoder.

## 4. Matching Environment

Em đã xây dựng environment cho matching tuần tự. Nếu có `M` giảng viên, observation có dạng:

```text
[compatibility của student hiện tại,
 quota còn lại đã chuẩn hóa,
 workload hiện tại đã chuẩn hóa]
```

Do đó, kích thước state là `3M`.

Mỗi action là một số nguyên từ `0` đến `M-1`, tương ứng với một giảng viên. Sau action hợp lệ:

```text
load[advisor] tăng lên 1
student_index tăng lên 1
```

Episode kết thúc khi toàn bộ sinh viên trong cohort được phân bổ.

**Visual trình chiếu:** [Hình 3 – Mô phỏng episode](figures/03_episode_simulation.png)

## 5. Action masking và quota

Một phần quan trọng em đã thực hiện là **action masking cho PPO**.

Nếu một giảng viên đã đủ quota thì giảng viên đó bị loại khỏi tập action hợp lệ. PPO vì vậy không chọn trực tiếp advisor đã đầy. Đây là cách xử lý phù hợp vì quota là hard constraint, không chỉ là một yếu tố để cộng hoặc trừ nhẹ trong reward.

Đối với DQN, thuật toán chuẩn không hỗ trợ action mask giống Maskable PPO. Em vẫn sử dụng DQN làm đối chứng, nhưng ghi nhận riêng số lần DQN đề xuất action không hợp lệ. Vì vậy khi đánh giá DQN, không chỉ nhìn vào compatibility mà phải nhìn thêm `invalid_proposals`.

**Visual trình chiếu:** [Hình 5 – Action masking và quota](figures/05_action_masking_quota.png)

## 6. Reward hiện tại

Reward có hai thành phần chính: compatibility và fairness.

Fairness được tính bằng variance của workload trước và sau action. Nếu action làm workload cân bằng hơn thì agent nhận thêm reward:

```text
reward = compatibility
       + 0.15 * (variance_before - variance_after)
```

Action không hợp lệ bị phạt `-2.0` trong environment lõi.

Hiện tại em chưa đưa preference, mức độ hài lòng, điểm khóa luận hay outcome vào reward vì chưa có dữ liệu đủ đầy và đáng tin cậy. Nếu đưa nhãn không tốt vào reward thì agent có thể tối ưu một mục tiêu sai.

## 7. Các thuật toán RL

Thuật toán chính là **Maskable PPO**. PPO phù hợp vì đây là bài toán policy learning, action space là discrete và có thể kết hợp action masking để xử lý quota.

Ngoài PPO, em đã chuẩn bị:

- **DQN**: thuật toán value-based trên discrete action space, dùng làm RL đối chứng;
- **A2C**: một policy-gradient method bổ sung;
- **QRDQN**: biến thể distributional của DQN.

Trong phạm vi trình bày, PPO là mô hình đề xuất còn DQN là mô hình đối chứng chính.

## 8. Baseline để kiểm chứng RL

Em không đánh giá RL một cách độc lập. Các baseline sử dụng cùng compatibility matrix, cùng cohort và cùng quota:

1. **Random**: chọn ngẫu nhiên advisor còn quota, làm mức nền thấp.
2. **Greedy Similarity**: mỗi sinh viên chọn advisor còn quota có compatibility cao nhất tại thời điểm đó.
3. **Exact capacitated assignment**: tìm assignment tối ưu toàn cục theo compatibility và capacity, dùng làm upper bound hoặc fallback an toàn.
4. **Gale–Shapley**: matching dựa trên ranking và tính ổn định.
5. **Student–Project Allocation**: matching có capacity/quota.

Các baseline giúp trả lời câu hỏi: PPO có thật sự tạo ra giá trị so với quy tắc đơn giản hoặc phương pháp matching truyền thống hay không.

## 9. Protocol thực nghiệm và chống leakage

Em sử dụng temporal split để mô phỏng việc dùng dữ liệu lịch sử cho cohort mới:

- dữ liệu trước năm 2025 và một phần năm 2025 dùng cho train;
- phần còn lại của năm 2025 chia thành validation và test;
- các record cùng một student ở cùng một split;
- TF-IDF chỉ fit trên train;
- validation và test chỉ transform bằng vectorizer đã fit từ train.

Nếu không thể chia theo năm thì dùng fallback deterministic 80/20 theo `student_id`. Mục đích là tránh để model nhìn thấy thông tin của test và đánh giá quá lạc quan.

## 10. Metrics

Em sử dụng nhiều metrics:

- **Mean compatibility**: độ phù hợp trung bình của các cặp được phân bổ;
- **Total reward**: tổng reward của episode;
- **Load variance**: mức chênh lệch workload;
- **Quota violations**: số lượng phân bổ vượt quota;
- **Invalid proposals**: số action không hợp lệ model đề xuất;
- **Assigned count**: số sinh viên được phân bổ;
- **Historical top-1 accuracy**: mức độ trùng với assignment lịch sử.

Quota violations và invalid proposals là các metric bắt buộc. Model có compatibility cao nhưng vi phạm quota thì không thể xem là model tốt. Historical top-1 chỉ tham khảo vì assignment lịch sử không chắc là phương án tối ưu.

## 11. Kết quả hiện tại

Repo hiện có smoke benchmark với seed 42, gồm 156 mẫu train, 20 mẫu validation, 22 mẫu test, 39 giảng viên và 512 timesteps.

Một số kết quả được ghi nhận:

- Greedy có compatibility khoảng `0.219228`;
- PPO train ngắn có compatibility khoảng `0.044382`;
- DQN có compatibility khoảng `0.213330`;
- DQN có `157 invalid proposals`.

Em không dùng các con số này để kết luận cuối cùng vì đây mới là smoke result với một seed và số timestep ngắn. Có thể kết luận rằng pipeline đã chạy được, PPO xử lý quota tốt nhờ masking, còn DQN cần được đánh giá kèm invalid proposals.

**Visual trình chiếu:** [Hình 4 – Smoke benchmark](figures/04_benchmark_smoke.png)

## 12. Checkpoint và tái lập

Em đã tổ chức train theo các milestone như 500 nghìn, 1 triệu và 2 triệu timesteps. Mỗi lần train lưu checkpoint model và file kết quả tương ứng, gồm thuật toán, timestep, seed, split và metrics.

Ngoài ra, registry lưu hash checkpoint, fingerprint dataset, cấu hình, metrics và commit code. Mục tiêu là biết model được tạo từ dữ liệu, cấu hình và phiên bản code nào.

## 13. Đánh giá có nên tiếp tục PPO không

Em đề xuất tiếp tục giữ PPO làm hướng chính, nhưng chưa tuyên bố PPO là phương án cuối cùng.

Lý do là PPO phù hợp với MDP tuần tự, hỗ trợ action masking và có thể tối ưu trade-off giữa compatibility với fairness. Tuy nhiên, exact assignment vẫn nên là phương án an toàn mặc định vì nó tối ưu global objective hiện tại.

Chỉ chọn PPO khi:

1. không có quota violation;
2. không có invalid proposal;
3. compatibility trên hold-out vượt exact theo margin định trước;
4. load variance nằm trong mức chấp nhận;
5. kết quả ổn định qua nhiều seed và cohort;
6. có đánh giá của chuyên gia.

Nếu không đạt, exact vẫn là fallback.

**Visual trình chiếu:** [Hình 6 – Promotion gate](figures/06_promotion_gate.png)

## 14. Những gì đã làm được

Tóm lại, em đã:

1. Chuẩn hóa dữ liệu thesis và advisor cho thí nghiệm.
2. Xây dựng compatibility matrix bằng TF-IDF và cosine similarity.
3. Xây dựng environment matching tuần tự.
4. Định nghĩa state, action, transition và reward.
5. Xử lý quota bằng action masking cho PPO.
6. Huấn luyện PPO và DQN trên cùng environment.
7. Chuẩn bị A2C và QRDQN để mở rộng so sánh.
8. Xây dựng Random, Greedy, Exact, Gale–Shapley và SPA baseline.
9. Thiết lập temporal split chống leakage.
10. Thiết lập benchmark với compatibility, fairness, quota và invalid proposal.
11. Lưu checkpoint theo milestone và metadata tái lập.
12. Thiết kế promotion gate để không thay thế phương án an toàn khi PPO chưa chứng minh hiệu quả.

## 15. Giới hạn và kế hoạch tiếp theo

Giới hạn hiện tại là dữ liệu còn nhỏ, kết quả chưa đủ nhiều seed, smoke benchmark chưa phải kết quả cuối, chưa có preference/outcome đầy đủ và chưa có đủ bằng chứng từ người dùng thực tế.

Các bước tiếp theo là chạy nhiều seed hơn, tăng timestep, hoàn thiện Gale–Shapley/SPA, thực hiện reward ablation, stress test với quota khác nhau, so sánh TF-IDF với sentence-transformer và thu thập preference/feedback/outcome có cấu trúc.

## 16. Câu kết

Đóng góp chính của em là chuyển bài toán phân bổ sinh viên–giảng viên thành một MDP tuần tự có compatibility, quota và workload; sau đó xây dựng environment để huấn luyện và đánh giá các thuật toán RL, trong đó PPO là phương pháp chính và DQN là đối chứng.

Điểm quan trọng là em không chỉ train một model, mà còn có baseline, metrics và promotion gate để kiểm tra model có thực sự tốt hơn hay không.

Ở thời điểm hiện tại, PPO là hướng nghiên cứu phù hợp và đáng tiếp tục, nhưng exact assignment vẫn là fallback an toàn. Kết luận cuối cùng về PPO sẽ chỉ được đưa ra sau khi có thêm nhiều seed, nhiều cohort, ablation và đánh giá đầy đủ hơn.
