# Product Technical Documentation

Thư mục này thuộc repo sản phẩm được push lên GitHub. Nó lưu kiến trúc, thiết kế thuật toán, hướng dẫn vận hành, báo cáo kiểm chứng và các kế hoạch kỹ thuật có giá trị tái lập.

## Tài liệu chính

| Tài liệu | Mô tả |
|---|---|
| [`gitflow.md`](./gitflow.md) | Git workflow độc lập của product repository. |
| [`architecture_diagram.md`](./architecture_diagram.md) | Kiến trúc dữ liệu, ML/RL, API và frontend. |
| [`rl_algorithm_design.md`](./rl_algorithm_design.md) | State, action, reward, masking và benchmark protocol. |
| [`complete_kltn_v1.md`](./complete_kltn_v1.md) | Báo cáo kỹ thuật và verification artifact của phiên bản v1. |
| [`overnight_training_analysis.md`](./overnight_training_analysis.md) | Phân tích các run huấn luyện dài. |
| [`guide/`](./guide/index.md) | Hướng dẫn xây dựng và vận hành các thành phần sản phẩm. |
| [`superpowers/`](./superpowers/) | Design/implementation plans lịch sử được giữ làm provenance. |

Product repo phải có thể hiểu và chạy khi clone độc lập; không dùng relative link tới `specs`, `planning` hoặc `tasks` của workspace local bên ngoài.
