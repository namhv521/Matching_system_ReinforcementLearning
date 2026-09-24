# Product Repository Agent Guide

## Repository boundary

File này áp dụng khi làm việc trực tiếp trong Git repository sản phẩm. Git root là thư mục chứa file này; không giả định tồn tại planning workspace bên ngoài khi repo được clone từ GitHub.

## Mục tiêu

Phát triển hệ thống phân bổ sinh viên–giảng viên gồm data pipeline, Gymnasium environment, các RL/baseline engines, FastAPI backend, React dashboard, database adapters, tests và deployment configuration.

## Quy tắc làm việc

- Luôn kiểm tra `git status --short` trước và sau khi sửa.
- Giữ nguyên thay đổi có sẵn ngoài phạm vi yêu cầu.
- Không ghi đè `data/raw` hoặc `data/processed`.
- Dữ liệu train tái lập ghi vào `data/curated`; dữ liệu có thể công bố ghi vào `data/public` sau khi ẩn danh.
- Không commit `.env`, API key, PII, logs hoặc checkpoint lớn.
- Dùng UTF-8 cho CSV/JSON và hỗ trợ tiếng Việt.
- Thay đổi hành vi phải đi kèm test và cập nhật tài liệu kỹ thuật phù hợp.

## Ràng buộc ML/RL

- Temporal split phải group theo `student_id`; TF-IDF chỉ fit trên Train.
- Quota violations bắt buộc bằng 0.
- Maskable PPO phải dùng action mask tại train và inference.
- DQN không mask phải ghi nhận `invalid_proposals` và dùng fallback an toàn.
- Exact Hungarian là batch production fallback nếu candidate RL không đạt promotion gate.
- Không tuyên bố kết quả nghiên cứu nếu chưa có artifact benchmark đa seed.

## Lệnh thường dùng

```powershell
python -m pytest tests
python -m src.data_pipeline.clean_processed_data
python -m src.rl.train --algorithm ppo --timesteps 10000
python -m src.rl.benchmark --timesteps 2048 --seed 42
npm --prefix frontend run test:run
npm --prefix frontend run build
python run_dashboard.py
```

## Git workflow

- Branch: `feature/KLTN-XXX-short-name`.
- Commit: `KLTN-XXX: concise description`.
- Chỉ merge khi test/build liên quan pass và diff đúng phạm vi.
