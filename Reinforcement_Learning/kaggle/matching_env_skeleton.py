"""
matching_env.py
================
Skeleton cho Matching Environment (mục 9 của đề cương KLTN).

Được chuyển thể TRỰC TIẾP từ cấu trúc `ConnectFourGym` ở bài học
"04_Deep_Reinforcement_Learning_PPO_ConnectX_VN.ipynb" -- so sánh 2 file
để thấy rõ mọi khái niệm (reset/step/observation_space/action_space/
reward shaping/action masking) đều giữ nguyên "hình dạng", chỉ đổi
nội dung cụ thể.

Vị trí trong cấu trúc mã nguồn đề xuất (mục 19):
    student-advisor-rl/environment/matching_env.py

Thiết kế action space theo kiểu "xử lý từng sinh viên 1" để né vấn đề
action space bùng nổ đã nêu ở mục 11.2 (500 sv x 50 gv = 25.000 cặp
nếu action = assign(student, advisor) trực tiếp).
"""

import numpy as np
import gymnasium as gym
from gymnasium import spaces


class MatchingEnv(gym.Env):
    """
    Mỗi episode = 1 cohort (1 đợt phân công sinh viên - giảng viên).
    Mỗi step = xử lý 1 sinh viên trong hàng đợi, agent chọn 1 advisor cho
    sinh viên đó. Episode kết thúc khi toàn bộ sinh viên trong cohort đã
    được assign (hoặc hết advisor khả dụng).

    Đây là điểm khác biệt LỚN NHẤT so với ConnectFourGym: ConnectX là
    2-player đối kháng (agent vs agent_doi_thu), còn đây là single-agent
    xử lý tuần tự (agent vs chính bài toán tối ưu hoá cohort).
    """

    def __init__(self, simulator, embedding_dim=384, max_advisors=50,
                 reward_weights=None):
        super().__init__()

        # simulator: đối tượng Matching Simulator (mục 10) - sinh cohort,
        # advisor profile, quota, preference proxy... GIỐNG VAI TRÒ của
        # `make("connectx")` ở bài 4, nhưng đây là simulator TỰ VIẾT
        # thay vì dùng thư viện có sẵn.
        self.simulator = simulator
        self.embedding_dim = embedding_dim
        self.max_advisors = max_advisors

        # Trọng số reward đa mục tiêu (mục 9.3) - tương đương việc bạn
        # từng tinh chỉnh trọng số heuristic ở bài 2
        # (1e6, 1e2, 1, -1e2, -1e6), nhưng ở đây có ý nghĩa "học được"
        # (dùng cho reward, không phải chọn nước đi trực tiếp).
        self.reward_weights = reward_weights or {
            "compatibility": 1.0,
            "student_pref": 0.5,
            "advisor_pref": 0.3,
            "fairness": 0.4,
            "outcome": 0.2,
        }
        self.penalty_quota_violation = -10.0  # hard constraint -> phạt nặng

        # ================= ACTION SPACE =================
        # Chọn 1 trong tối đa `max_advisors` giảng viên cho SINH VIÊN
        # HIỆN TẠI (không phải chọn cặp student-advisor trực tiếp).
        # -> Tương đương spaces.Discrete(self.columns) ở ConnectFourGym,
        #    nhưng "columns" bây giờ là "advisors".
        self.action_space = spaces.Discrete(self.max_advisors)

        # ================= OBSERVATION SPACE =================
        # Ở ConnectFourGym, observation là ảnh 1 kênh (rows x columns).
        # Ở đây, state (mục 9.1) là tổ hợp nhiều nhóm thông tin khác
        # kiểu dữ liệu -> dùng spaces.Dict thay vì Box đơn giản.
        self.observation_space = spaces.Dict({
            # Thesis embedding của sinh viên hiện tại đang cần assign
            "student_embedding": spaces.Box(
                low=-1.0, high=1.0, shape=(embedding_dim,), dtype=np.float32
            ),
            # Research embedding của TẤT CẢ advisor (padding nếu ít hơn max_advisors)
            "advisor_embeddings": spaces.Box(
                low=-1.0, high=1.0, shape=(max_advisors, embedding_dim), dtype=np.float32
            ),
            # Quota còn lại của từng advisor -> dùng để tính action mask
            "advisor_remaining_quota": spaces.Box(
                low=0, high=50, shape=(max_advisors,), dtype=np.int32
            ),
            # Preference của sinh viên hiện tại (rank các advisor, -1 nếu không xếp hạng)
            "student_preference_rank": spaces.Box(
                low=-1, high=max_advisors, shape=(max_advisors,), dtype=np.int32
            ),
            # Action mask: 1 = advisor còn hợp lệ để chọn, 0 = vi phạm hard constraint
            # (giống hệt ý tưởng obs_board_top_free() ở ConnectFourGym bài 4,
            #  nhưng ở đây trả thẳng ra ngoài observation để policy network
            #  "nhìn thấy" được, thay vì chỉ agent tự kiểm tra sau khi step)
            "action_mask": spaces.Box(
                low=0, high=1, shape=(max_advisors,), dtype=np.int8
            ),
        })

        self._current_cohort = None
        self._current_student_idx = None

    # ------------------------------------------------------------------
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        # Tương đương self.trainer.reset() ở ConnectFourGym, nhưng thay vì
        # reset 1 ván cờ, ta sinh 1 COHORT MỚI từ Matching Simulator (mục 10)
        self._current_cohort = self.simulator.sample_cohort()
        self._current_student_idx = 0
        obs = self._build_observation()
        return obs, {}

    # ------------------------------------------------------------------
    def step(self, action):
        student = self._current_cohort.students[self._current_student_idx]
        action_mask = self._compute_action_mask()

        # ==== ACTION MASKING (giống bài 4, nhưng là HARD CONSTRAINT bắt buộc) ====
        if action_mask[action] == 0:
            # Vi phạm hard constraint (advisor hết quota / không đúng department...)
            # -> phạt nặng, KHÔNG kết thúc episode ngay (khác ConnectFourGym,
            #    vì ở đây ta muốn agent học tiếp trong cùng cohort, không phải
            #    "thua ván" như ConnectX)
            reward = self.penalty_quota_violation
        else:
            advisor = self._current_cohort.advisors[action]
            reward = self._compute_reward(student, advisor)
            self._current_cohort.assign(student, advisor)

        self._current_student_idx += 1
        terminated = self._current_student_idx >= len(self._current_cohort.students)
        truncated = False

        obs = self._build_observation() if not terminated else self._build_observation(final=True)
        info = {"cohort_id": self._current_cohort.id}
        return obs, reward, terminated, truncated, info

    # ------------------------------------------------------------------
    def _compute_reward(self, student, advisor):
        """
        Reward đa mục tiêu (mục 9.3):
        R = w1*compatibility + w2*student_pref + w3*advisor_pref
            + w4*fairness + w5*outcome - penalties

        TƯƠNG ĐƯƠNG shape_reward() ở ConnectFourGym bài 4, nhưng ở đó chỉ
        có 2-3 số hạng (thắng/thua + tín hiệu nhỏ mỗi bước). Ở đây có
        5 số hạng độc lập -> nên tách hàm riêng cho từng thành phần để
        dễ làm REWARD ABLATION (mục 13.3: bỏ từng thành phần, so sánh).
        """
        w = self.reward_weights

        compatibility = self._cosine_similarity(student.embedding, advisor.embedding)
        student_pref = self._student_preference_score(student, advisor)
        advisor_pref = self._advisor_preference_score(student, advisor)
        fairness = self._fairness_score(advisor)
        outcome = self._outcome_proxy_score(student, advisor)  # chỉ dùng nếu đủ dữ liệu (mục 6.1)

        reward = (
            w["compatibility"] * compatibility
            + w["student_pref"] * student_pref
            + w["advisor_pref"] * advisor_pref
            + w["fairness"] * fairness
            + w["outcome"] * outcome
        )
        return reward

    # ------------------------------------------------------------------
    def _compute_action_mask(self):
        """
        Trả về vector 0/1 độ dài max_advisors.
        1 = advisor còn quota VÀ thuộc phạm vi được phép hướng dẫn sinh viên hiện tại.
        Đây là nơi triển khai TOÀN BỘ hard constraints ở mục 9.2 và mục 17
        ("Hard constraints phải được kiểm tra trước khi assignment được chấp nhận").
        """
        student = self._current_cohort.students[self._current_student_idx]
        mask = np.zeros(self.max_advisors, dtype=np.int8)
        for i, advisor in enumerate(self._current_cohort.advisors):
            if advisor.remaining_quota > 0 and advisor.can_supervise(student):
                mask[i] = 1
        return mask

    # ------------------------------------------------------------------
    def _build_observation(self, final=False):
        """Đóng gói state hiện tại (mục 9.1) thành dict đúng observation_space."""
        # TODO: implement dựa trên self._current_cohort, self._current_student_idx
        raise NotImplementedError("Bạn tự hoàn thiện dựa trên schema dữ liệu thực tế")

    # ------------------------------------------------------------------
    @staticmethod
    def _cosine_similarity(vec_a, vec_b):
        denom = (np.linalg.norm(vec_a) * np.linalg.norm(vec_b)) + 1e-8
        return float(np.dot(vec_a, vec_b) / denom)

    def _student_preference_score(self, student, advisor):
        # TODO: dựa trên student.preference_rank (mục 6.2)
        raise NotImplementedError

    def _advisor_preference_score(self, student, advisor):
        # TODO: dựa trên advisor.preference/ranking nếu có (mục 6.3)
        raise NotImplementedError

    def _fairness_score(self, advisor):
        # TODO: ví dụ -abs(advisor.current_load - target_load) để cân bằng workload
        raise NotImplementedError

    def _outcome_proxy_score(self, student, advisor):
        # TODO: dùng grade/feedback lịch sử NẾU ĐỦ DỮ LIỆU (mục 6.1, mục 17:
        # không tự tạo nhãn giả nếu dữ liệu không có)
        raise NotImplementedError


# ======================================================================
# Cách dùng - TƯƠNG ĐƯƠNG check_env() + PPO(...) ở bài 4:
#
#   from stable_baselines3 import PPO
#   from stable_baselines3.common.env_checker import check_env
#
#   simulator = MatchingSimulator(historical_data=...)   # mục 10
#   env = MatchingEnv(simulator)
#   check_env(env, warn=True)   # LUÔN chạy trước khi train, y hệt bài 4
#
#   model = PPO("MultiInputPolicy", env, verbose=1)  # MultiInputPolicy vì
#                                                     # observation_space là Dict
#   model.learn(total_timesteps=200_000)
#
# Với DQN (nhánh B, mục 11.2) cấu trúc environment y hệt, chỉ đổi:
#   from stable_baselines3 import DQN
#   model_dqn = DQN("MultiInputPolicy", env, verbose=1)
#
# -> Đây chính là điểm mấu chốt của "So sánh công bằng" (mục 13.2): PPO và
#    DQN dùng CHUNG 1 class MatchingEnv, chỉ khác thuật toán train.
# ======================================================================
