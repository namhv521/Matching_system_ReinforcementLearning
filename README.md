# Hệ thống RL Phân bổ Sinh viên – Giảng viên Hướng dẫn

> Reinforcement Learning-Based Student–Advisor Matching System

## Giới thiệu

Dự án nghiên cứu hệ thống hỗ trợ phân bổ sinh viên thực hiện khóa luận tốt nghiệp cho giảng viên hướng dẫn. Hệ thống kết hợp biểu diễn ngôn ngữ tự nhiên của đề tài và hồ sơ chuyên môn giảng viên với Reinforcement Learning để tối ưu phân bổ trên toàn cohort.

Mục tiêu không chỉ là chọn giảng viên có độ tương thích cao cho từng sinh viên độc lập, mà còn cân bằng workload, tuân thủ quota và tạo nền tảng để cải thiện policy khi có thêm dữ liệu feedback ở các cohort tiếp theo.

## Mục tiêu nghiên cứu

- Xây dựng dữ liệu khóa luận và hồ sơ giảng viên có thể tái lập, có kiểm tra chất lượng.
- Tính compatibility giữa thesis và advisor từ nội dung đề tài, lĩnh vực và kỹ năng chuyên môn.
- Mô hình hóa bài toán phân bổ tuần tự với quota là hard constraint.
- Sử dụng PPO có action masking là mô hình chính; DQN là mô hình đối chứng.
- So sánh khách quan với Random, Greedy Similarity, Gale–Shapley và Student–Project Allocation khi các baseline tương ứng hoàn thiện.
- Đánh giá bằng compatibility, fairness, quota violations, historical matching accuracy và outcome/feedback khi dữ liệu này sẵn sàng.

## Thành phần hệ thống

### Dữ liệu và preprocessing

Dự án thu thập thông tin từ các khóa luận PDF/DOCX, khảo sát và hồ sơ công khai của giảng viên. Pipeline tạo dữ liệu trích xuất, profile kỹ năng theo giảng viên và dataset đã làm sạch dành riêng cho thí nghiệm RL.

Nguồn dữ liệu raw được tách biệt khỏi dữ liệu processed. Bước cleaning là deterministic, chỉ ghi kết quả mới vào thư mục dữ liệu sạch và không ghi đè dữ liệu nguồn.

### Compatibility

Phiên bản hiện tại sử dụng TF-IDF với cosine similarity trên title, field, công nghệ của thesis và các trường chuyên môn của advisor. Vocabulary được fit trên tập train, còn tập hold-out chỉ được transform để hạn chế data leakage.

### Matching environment

Mỗi episode xử lý lần lượt các sinh viên trong một cohort. Mỗi action là chọn một advisor. State bao gồm compatibility của sinh viên hiện tại, capacity còn lại và workload hiện tại của tất cả advisor.

Quota được coi là ràng buộc cứng. PPO dùng action masking để không chọn advisor đã đầy quota. DQN được giữ làm đối chứng; số action không hợp lệ mà DQN đề xuất được đo và báo cáo riêng.

### Reward

Reward v1 kết hợp compatibility và phần thưởng cân bằng tải. Assignment không hợp lệ bị phạt. Khi có dữ liệu preference, grade hoặc feedback đủ tin cậy, reward sẽ được mở rộng bằng các thành phần này với trọng số được version hóa.

## Trạng thái triển khai

Đã hoàn thành các phần sau:

- Pipeline trích xuất và tổng hợp dữ liệu khóa luận.
- Crawler và profile kỹ năng giảng viên.
- Cleaning dataset tái lập được cho thí nghiệm RL.
- TF-IDF cosine compatibility matrix.
- Sequential matching environment với quota và fairness reward.
- PPO có action masking, DQN đối chứng, Random và Greedy Similarity.
- Benchmark hold-out theo năm, có fallback deterministic khi không thể tách cohort theo năm.

Các phần tiếp theo gồm Gale–Shapley, Student–Project Allocation, preference modeling, outcome feedback, model registry và lớp ứng dụng phục vụ inference.

## Đánh giá thực nghiệm

Protocol hiện tại train trên các cohort trước và đánh giá trên cohort của năm mới nhất. Khi không đủ dữ liệu theo thời gian, hệ thống dùng split deterministic theo định danh sinh viên để phục vụ kiểm thử kỹ thuật.

Các metric gồm mean compatibility, load variance, quota violations, historical top-1 accuracy và invalid proposals. Historical top-1 accuracy chỉ phản ánh mức độ tái tạo assignment lịch sử; không được coi là ground truth của phân bổ tối ưu.

Kết quả smoke test chỉ chứng minh pipeline hoạt động. Kết luận học thuật yêu cầu nhiều seed, số timesteps đủ lớn, baseline đầy đủ và dữ liệu train có quy mô phù hợp.

## Tài liệu liên quan

- `agent.md`: quy tắc làm việc, vị trí dữ liệu và hướng dẫn vận hành cho các lần phát triển tiếp theo.
- `docs/rl_algorithm_design.md`: state, action, reward, masking, protocol benchmark và các giới hạn hiện tại.
- `requirements.txt`: dependency của pipeline, NLP và RL.
- `configs/settings.py`: cấu hình đường dẫn, schema và biến môi trường.

## Lưu ý dữ liệu và đạo đức

Dữ liệu sinh viên và giảng viên cần được sử dụng theo đúng phạm vi được cho phép. Hệ thống là công cụ hỗ trợ ra quyết định; kết quả matching cần được admin hoặc hội đồng chuyên môn kiểm tra trước khi áp dụng chính thức.
