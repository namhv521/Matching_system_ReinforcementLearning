"""Framework-independent sequential assignment environment and RL data builder."""
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


THESIS_TEXT_COLUMNS = ["thesis_title", "field_category", "web_languages", "frontend_frameworks", "backend_frameworks", "ai_frameworks", "ai_problems", "data_tools", "research_methods"]
ADVISOR_TEXT_COLUMNS = ["primary_field", "top_ai_frameworks", "top_web_stack", "top_backend", "top_db", "top_data_tools"]


def _row_text(frame: pd.DataFrame, columns: list[str]) -> list[str]:
    return frame.reindex(columns=columns, fill_value="").fillna("").astype(str).agg(" ".join, axis=1).tolist()


def build_compatibility(theses: pd.DataFrame, advisors: pd.DataFrame, vectorizer=None, fit: bool = True):
    """Return compatibility and vectorizer; fit vocabulary only on training data."""
    thesis_text = _row_text(theses, THESIS_TEXT_COLUMNS)
    advisor_text = _row_text(advisors, ADVISOR_TEXT_COLUMNS)
    if vectorizer is None:
        vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), min_df=1)
    if fit:
        vectors = vectorizer.fit_transform(thesis_text + advisor_text)
        return cosine_similarity(vectors[: len(theses)], vectors[len(theses) :]).astype(np.float32), vectorizer
    return cosine_similarity(vectorizer.transform(thesis_text), vectorizer.transform(advisor_text)).astype(np.float32), vectorizer


@dataclass
class MatchingEnv:
    compatibility: np.ndarray
    capacities: np.ndarray
    fairness_weight: float = 0.15
    invalid_penalty: float = 2.0

    def reset(self):
        self.student_index = 0
        self.loads = np.zeros(len(self.capacities), dtype=np.int32)
        self.assignments = []
        return self.observation()

    def valid_actions(self) -> np.ndarray:
        return self.loads < self.capacities

    def observation(self) -> np.ndarray:
        if self.student_index >= len(self.compatibility):
            scores = np.zeros(self.compatibility.shape[1], dtype=np.float32)
        else:
            scores = self.compatibility[self.student_index]
        remaining = (self.capacities - self.loads) / np.maximum(self.capacities, 1)
        return np.concatenate([scores, remaining.astype(np.float32), self.loads / np.maximum(self.capacities, 1)]).astype(np.float32)

    def step(self, action: int):
        valid = self.valid_actions()
        if self.student_index >= len(self.compatibility) or action < 0 or action >= len(self.capacities) or not valid[action]:
            return self.observation(), -self.invalid_penalty, True, {"invalid": True}
        before = np.var(self.loads / np.maximum(self.capacities, 1))
        score = float(self.compatibility[self.student_index, action])
        self.loads[action] += 1
        after = np.var(self.loads / np.maximum(self.capacities, 1))
        reward = score + self.fairness_weight * float(before - after)
        self.assignments.append(action)
        self.student_index += 1
        terminated = self.student_index == len(self.compatibility)
        return self.observation(), reward, terminated, {"compatibility": score, "invalid": False}