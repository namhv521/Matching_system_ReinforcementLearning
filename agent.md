# Agent guide — Student–Advisor Reinforcement Learning

## Mục tiêu
Xây dựng hệ thống phân bổ sinh viên–giảng viên hướng dẫn khóa luận bằng PPO (mô hình chính), DQN (đối chứng), và các baseline truyền thống.

## Quy tắc làm việc
- Làm việc từ thư mục `C:\Su\KLTN`.
- Không ghi đè dữ liệu raw hoặc kết quả processed đã có nếu chưa được yêu cầu.
- Bước cleaning tái lập được phải ghi kết quả vào `data/cleaned/`.
- Không commit `.env`, API key, model checkpoint, log hoặc dữ liệu nhạy cảm.
- Luôn kiểm tra `git status` trước và sau khi sửa. Thay đổi có sẵn của người dùng phải được giữ nguyên.
- Dùng UTF-8 cho CSV/JSON và hỗ trợ tiếng Việt.

## Dữ liệu
- Input lịch sử: `data/processed/thesis_extracted.csv`.
- Input profile: `data/processed/advisor_profiles.csv` và `advisor_skills.csv`.
- Output cleaning: `data/cleaned/theses.csv`, `advisors.csv`, `quality_report.json`.
- Bản ghi hợp lệ cần có `student_id`, `student_name`, `thesis_title`, `advisor_name`; chỉ nhận `extraction_status=success`.

## Lộ trình RL
1. Clean và audit dữ liệu, không dùng dữ liệu lỗi làm ground truth.
2. Tạo text representation cho thesis/advisor và compatibility matrix cosine/TF-IDF.
3. Matching environment: mỗi bước xử lý một student; action là advisor; quota là hard constraint.
4. Observation gồm student embedding/feature, advisor compatibility, remaining capacity và current loads.
5. Reward: compatibility + preference − load imbalance − invalid assignment penalty.
6. Train PPO; train DQN trên cùng environment/protocol để đối chứng.
7. So sánh Random, Greedy, Gale–Shapley/SPA, PPO, DQN bằng compatibility, quota violations, load variance và historical Recall@K.
8. Lưu seed, config, metrics và checkpoint; chỉ deploy model qua evaluation gate.

## Lệnh thường dùng
```powershell
python -m src.data_pipeline.clean_processed_data
python -m src.rl.train --algorithm ppo --timesteps 10000
python -m src.rl.train --algorithm dqn --timesteps 10000
python -m src.rl.benchmark --timesteps 2048 --seed 42
python -m src.data_pipeline.run_pipeline --no-crawl --limit 5
git status --short
```

## Trạng thái hiện tại
Phase 1 đã có pipeline PDF/DOCX và profile giảng viên. Phase 2–3 (embedding, environment, PPO/DQN) đang được triển khai từng bước.