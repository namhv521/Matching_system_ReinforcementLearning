"""Gymnasium adapter for the sequential student-advisor matching core."""
import gymnasium as gym
import numpy as np
from gymnasium import spaces

from src.environment.matching_core import MatchingEnv


class GymMatchingEnv(gym.Env):
    metadata = {"render_modes": []}

    def __init__(self, compatibility: np.ndarray, capacities: np.ndarray):
        super().__init__()
        self.core = MatchingEnv(compatibility=compatibility, capacities=capacities)
        size = compatibility.shape[1] * 3
        self.action_space = spaces.Discrete(compatibility.shape[1])
        self.observation_space = spaces.Box(low=-1.0, high=1.0, shape=(size,), dtype=np.float32)
        self.invalid_proposals = 0

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self.invalid_proposals = 0
        return self.core.reset(), {"action_mask": self.core.valid_actions()}

    def action_masks(self):
        """Mask API required by sb3-contrib MaskablePPO."""
        mask = self.core.valid_actions()
        # A zero mask is invalid for categorical policies; keep one safe action.
        if not mask.any():
            mask = np.ones(self.action_space.n, dtype=bool)
        return mask

    def step(self, action):
        action = int(action)
        valid = self.core.valid_actions()
        corrected = action
        if not valid[action]:
            self.invalid_proposals += 1
            candidates = np.flatnonzero(valid)
            if len(candidates) == 0:
                return self.core.observation(), -2.0, True, False, {"invalid": True, "invalid_proposals": self.invalid_proposals}
            corrected = int(candidates[np.argmax(self.core.compatibility[self.core.student_index, candidates])])
        observation, reward, terminated, info = self.core.step(corrected)
        info.update({"proposed_action": action, "executed_action": corrected, "invalid_proposals": self.invalid_proposals, "action_mask": self.core.valid_actions()})
        return observation, reward, terminated, False, info