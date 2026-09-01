"""Train a PPO or DQN student-advisor matching policy from cleaned data."""
import argparse
import json
import math
import random
from pathlib import Path

import numpy as np
import pandas as pd
from stable_baselines3 import DQN
from sb3_contrib import MaskablePPO

from src.environment.gym_matching_env import GymMatchingEnv
from src.environment.matching_core import build_compatibility

ROOT = Path(__file__).resolve().parents[2]
CLEANED = ROOT / "data" / "cleaned"
RESULTS = ROOT / "outputs" / "results"
MODELS = ROOT / "outputs" / "models"


def load_environment(seed: int) -> tuple[GymMatchingEnv, pd.DataFrame, pd.DataFrame]:
    theses = pd.read_csv(CLEANED / "theses.csv", encoding="utf-8-sig")
    advisors = pd.read_csv(CLEANED / "advisors.csv", encoding="utf-8-sig")
    compatibility, _ = build_compatibility(theses, advisors)
    capacity = math.ceil(len(theses) / len(advisors))
    env = GymMatchingEnv(compatibility, np.full(len(advisors), capacity, dtype=np.int32))
    env.reset(seed=seed)
    return env, theses, advisors


def evaluate(model, env: GymMatchingEnv) -> dict:
    observation, _ = env.reset()
    done = False
    reward = 0.0
    compatibility = []
    while not done:
        action, _ = model.predict(observation, deterministic=True)
        observation, step_reward, done, _, info = env.step(action)
        reward += step_reward
        compatibility.append(info["compatibility"])
    return {"total_reward": round(float(reward), 6), "mean_compatibility": round(float(np.mean(compatibility)), 6), "load_variance": round(float(np.var(env.core.loads)), 6), "invalid_proposals": env.invalid_proposals}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--algorithm", choices=["ppo", "dqn"], default="ppo")
    parser.add_argument("--timesteps", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    random.seed(args.seed); np.random.seed(args.seed)
    env, theses, advisors = load_environment(args.seed)
    if args.algorithm == "ppo":
        model = MaskablePPO("MlpPolicy", env, seed=args.seed, verbose=0, n_steps=256, batch_size=64)
    else:
        model = DQN("MlpPolicy", env, seed=args.seed, verbose=0, learning_starts=500, buffer_size=20_000, batch_size=64)
    model.learn(total_timesteps=args.timesteps)
    metrics = evaluate(model, env)
    metrics.update({"algorithm": args.algorithm, "timesteps": args.timesteps, "seed": args.seed, "theses": len(theses), "advisors": len(advisors)})
    RESULTS.mkdir(parents=True, exist_ok=True); MODELS.mkdir(parents=True, exist_ok=True)
    stem = f"{args.algorithm}_seed{args.seed}_steps{args.timesteps}"
    model.save(MODELS / stem)
    (RESULTS / f"{stem}.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()