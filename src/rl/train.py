"""Train a PPO or DQN student-advisor matching policy from curated data."""
import argparse
import json
import os
import math
import os
import random
from pathlib import Path

import numpy as np
import pandas as pd
from stable_baselines3 import A2C, DQN
from sb3_contrib import MaskablePPO, QRDQN

from src.environment.gym_matching_env import GymMatchingEnv
from src.environment.matching_core import build_compatibility
from src.data_pipeline.split_dataset import temporal_train_validation_test_split

ROOT = Path(__file__).resolve().parents[2]
CURATED = Path(os.environ.get("DATA_DIR", ROOT / "data" / "curated"))
RESULTS = ROOT / "outputs" / "results"
MODELS = ROOT / "outputs" / "models"
SUPPORTED_ALGORITHMS = ("ppo", "a2c", "dqn", "qrdqn")


def load_environments(seed: int) -> tuple[dict[str, GymMatchingEnv], dict[str, pd.DataFrame], pd.DataFrame, dict]:
    theses = pd.read_csv(CURATED / "theses.csv", encoding="utf-8-sig")
    advisors = pd.read_csv(CURATED / "advisors.csv", encoding="utf-8-sig")
    train, validation, test, split_metadata = temporal_train_validation_test_split(theses, seed=seed)
    backend = os.getenv("MATCHING_TEXT_BACKEND", "tfidf")
    train_matrix, vectorizer = build_compatibility(train, advisors, backend=backend)
    validation_matrix, _ = build_compatibility(validation, advisors, vectorizer=vectorizer, fit=False, backend=backend)
    test_matrix, _ = build_compatibility(test, advisors, vectorizer=vectorizer, fit=False, backend=backend)
    frames = {"train": train, "validation": validation, "test": test}
    matrices = {"train": train_matrix, "validation": validation_matrix, "test": test_matrix}
    envs = {}
    for name, matrix in matrices.items():
        capacity = math.ceil(len(frames[name]) / len(advisors))
        envs[name] = GymMatchingEnv(matrix, np.full(len(advisors), capacity, dtype=np.int32))
        envs[name].reset(seed=seed)
    return envs, frames, advisors, split_metadata


def evaluate(model, env: GymMatchingEnv) -> dict:
    observation, _ = env.reset()
    done = False
    reward = 0.0
    compatibility = []
    while not done:
        # MaskablePPO must receive the current mask at inference too; otherwise
        # a trained policy can propose a full advisor and be silently corrected.
        kwargs = {"action_masks": env.action_masks()} if isinstance(model, MaskablePPO) else {}
        action, _ = model.predict(observation, deterministic=True, **kwargs)
        observation, step_reward, done, _, info = env.step(action)
        reward += step_reward
        compatibility.append(info["compatibility"])
    return {
        "total_reward": round(float(reward), 6),
        "mean_compatibility": round(float(np.mean(compatibility)), 6),
        "load_variance": round(float(np.var(env.core.loads)), 6),
        "quota_violations": int(np.maximum(env.core.loads - env.core.capacities, 0).sum()),
        "invalid_proposals": env.invalid_proposals,
    }


def load_checkpoint(algorithm: str, path: Path | str, env: GymMatchingEnv | None = None):
    path = Path(path)
    if algorithm == "ppo":
        return MaskablePPO.load(path, env=env)
    elif algorithm == "a2c":
        return A2C.load(path, env=env)
    elif algorithm == "dqn":
        return DQN.load(path, env=env)
    elif algorithm == "qrdqn":
        return QRDQN.load(path, env=env)
    raise ValueError(f"Unsupported algorithm: {algorithm}")


def train_milestones(algorithm: str, milestones: list[int], seed: int, verbose: int = 1) -> list[dict]:
    """Train once and save cumulative checkpoints at increasing milestones.

    A 200k -> 500k -> 1M schedule performs one million total environment
    steps, not three independent runs totalling 1.7 million steps.
    """
    if not milestones or any(step <= 0 for step in milestones):
        raise ValueError("Milestones must contain positive integers.")
    if milestones != sorted(set(milestones)):
        raise ValueError("Milestones must be unique and strictly increasing.")

    random.seed(seed)
    np.random.seed(seed)
    envs, frames, advisors, split_metadata = load_environments(seed)
    env = envs["train"]
    if algorithm == "ppo":
        model = MaskablePPO(
            "MlpPolicy", env, seed=seed, verbose=verbose,
            n_steps=256, batch_size=64,
        )
    elif algorithm == "a2c":
        model = A2C("MlpPolicy", env, seed=seed, verbose=verbose, n_steps=256)
    elif algorithm == "dqn":
        model = DQN(
            "MlpPolicy", env, seed=seed, verbose=verbose,
            learning_starts=500, buffer_size=20_000, batch_size=64,
        )
    elif algorithm == "qrdqn":
        model = QRDQN(
            "MlpPolicy", env, seed=seed, verbose=verbose,
            learning_starts=500, buffer_size=20_000, batch_size=64,
        )
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    RESULTS.mkdir(parents=True, exist_ok=True)
    MODELS.mkdir(parents=True, exist_ok=True)
    completed = 0
    all_metrics = []
    for milestone in milestones:
        additional_steps = milestone - completed
        print(f"\n=== {algorithm.upper()} training: {completed:,} -> {milestone:,} steps ===", flush=True)
        model.learn(
            total_timesteps=additional_steps,
            reset_num_timesteps=(completed == 0),
        )
        metrics = {
            "algorithm": algorithm,
            "timesteps": milestone,
            "additional_timesteps": additional_steps,
            "seed": seed,
            "theses": sum(len(frame) for frame in frames.values()),
            "advisors": len(advisors),
            "training_mode": "cumulative_milestones",
            "split": split_metadata,
            "train_metrics": evaluate(model, envs["train"]),
            "validation_metrics": evaluate(model, envs["validation"]),
        }
        # Preserve the test set for one final, unbiased evaluation.
        if milestone == milestones[-1]:
            metrics["test_metrics"] = evaluate(model, envs["test"])
        stem = f"{algorithm}_seed{seed}_steps{milestone}"
        model.save(MODELS / stem)
        (RESULTS / f"{stem}.json").write_text(
            json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        all_metrics.append(metrics)
        completed = milestone
        print(json.dumps(metrics, ensure_ascii=False, indent=2), flush=True)
    return all_metrics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--algorithm", choices=SUPPORTED_ALGORITHMS, default="ppo")
    parser.add_argument("--timesteps", type=int, default=None,
                        help="Single training milestone (default: 10000).")
    parser.add_argument("--milestones", type=int, nargs="+", default=None,
                        help="Increasing cumulative checkpoints, e.g. 200000 500000 1000000.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--verbose", type=int, choices=[0, 1, 2], default=1)
    args = parser.parse_args()
    if args.milestones and args.timesteps is not None:
        parser.error("Use either --timesteps or --milestones, not both.")
    milestones = args.milestones or [args.timesteps or 10_000]
    train_milestones(args.algorithm, milestones, args.seed, args.verbose)


if __name__ == "__main__":
    main()
