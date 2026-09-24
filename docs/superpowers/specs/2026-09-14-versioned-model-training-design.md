# Thiết kế huấn luyện và phát hành model theo phiên bản

## Mục tiêu

Tạo quy trình tái lập được để huấn luyện, đánh giá và phát hành từng phiên bản của hệ thống phân công sinh viên–giảng viên. PPO là một ứng viên nghiên cứu, không được mặc định là model tốt nhất. Engine được chọn bằng kết quả benchmark và ràng buộc vận hành.

## Phạm vi

- Tái sử dụng pipeline dữ liệu, environment, PPO, DQN, Random và Greedy hiện có.
- Bổ sung exact constrained optimizer làm chuẩn production và các baseline matching cần thiết cho luận văn.
- Train theo milestone tích lũy, đánh giá nhiều seed trên cùng data split.
- Lưu provenance, metrics và manifest cho mỗi phiên bản.
- Push code/config/manifest lên Git; đưa checkpoint nhị phân lên GitHub Release.
- Không xây web/API trong giai đoạn này.

## Quy tắc chọn engine

1. Mọi engine phải đạt hard constraints: không vượt quota, không gán advisor unavailable, giữ assignment đã lock và báo infeasible khi thiếu capacity.
2. Exact optimizer là lựa chọn production mặc định khi toàn cohort và constraints đã biết trước.
3. PPO chỉ được promotion nếu đạt hard constraints và cải thiện có ý nghĩa so với exact/Greedy trên validation qua nhiều seed.
4. Nếu PPO không hiệu quả, báo cáo kết quả âm và chọn model phù hợp hơn: exact optimizer cho phân công batch; Greedy hoặc matching truyền thống làm fallback; supervised ranker/embedding chỉ được xét khi có nhãn chuyên gia đủ tin cậy.
5. Test set chỉ dùng cho phiên bản đã được chọn từ validation.

## Data contract và chống leakage

- Một dataset snapshot có fingerprint từ các file curated, schema và split metadata.
- Chia theo thời gian khi có năm; các bản ghi cùng sinh viên không xuất hiện ở nhiều split.
- TF-IDF/vectorizer chỉ fit trên train.
- Dữ liệu lịch sử là weak label, không phải ground truth tối ưu.
- Không commit raw data, PII, `.env`, logs hoặc checkpoint vào Git.

## Luồng huấn luyện

1. Validate dependency, schema, capacity và dữ liệu đầu vào.
2. Chạy compile/test và smoke benchmark.
3. Chạy baseline exact, Greedy và matching truyền thống.
4. Train PPO/DQN theo milestone `200000`, `500000`, `1000000`; tiếp tục từ checkpoint trước trong cùng run.
5. Chạy nhiều seed ở milestone được validation chọn.
6. Tổng hợp mean/std, constraint violations, compatibility, fairness, runtime và invalid proposals.
7. Tạo manifest bất biến cho version đạt gate.

Các phiên train dài chạy trong cửa sổ PowerShell/CMD riêng. Codex dừng tương tác trong lúc tiến trình chạy và tiếp tục sau khi tiến trình kết thúc. Trước khi chạy phải ước lượng tài nguyên, kiểm tra dung lượng và ghi log local.

## Version và GitHub

- `model-v0.1.0`: pipeline và smoke/evaluation contract hoạt động.
- `model-v0.2.0`: milestone trung gian đạt hard constraints.
- `model-v1.0.0`: model/engine được chọn sau đánh giá nhiều seed và test cuối.
- Mỗi version có Git tag, release notes, manifest, config, dataset fingerprint, commit SHA và metrics tóm tắt.
- Source/config/tests/manifest được commit và push lên `origin`.
- Checkpoint `.zip` chỉ đính kèm GitHub Release; version không đạt gate chỉ giữ local.
- Có thể rollback bằng cách chọn lại release/tag đã đạt gate; không cần retrain.

## Promotion gate

- Tất cả test và smoke benchmark pass.
- Constraint violations bằng 0.
- Kết quả deterministic với exact engine khi input/config/version không đổi.
- RL báo cáo mean/std qua nhiều seed và không dùng test để tuning.
- Manifest tham chiếu đầy đủ dataset fingerprint, config, algorithm, seed, timesteps và commit.
- Checkpoint có thể load và chạy inference smoke test.

## Kiểm thử

- Unit test cho split, fingerprint, manifest và gate.
- Regression test cho capacity, unavailable advisor, locked assignment và infeasible cohort.
- Smoke train/load/inference cho từng loại model.
- Benchmark so sánh trên cùng cohort, split và seeds.
- Kiểm tra `git diff --check`, secret/PII và nội dung release trước khi push.

## Giới hạn

- Không tự học online từ feedback chưa kiểm duyệt.
- Không tự công bố assignment cho người dùng cuối.
- Không thêm MLOps service, model registry server hoặc Git LFS khi GitHub Releases đã đủ dùng.
- Việc phát hành lên GitHub chỉ diễn ra sau khi từng version vượt gate tương ứng.
