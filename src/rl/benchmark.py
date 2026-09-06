"""Train on earlier cohorts and benchmark models on the latest cohort."""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment

from src.environment.gym_matching_env import GymMatchingEnv
from src.environment.matching_core import build_compatibility

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "outputs" / "results"


def baseline(matrix, capacities, strategy, seed):
    rng = np.random.default_rng(seed)
    loads = np.zeros(matrix.shape[1], dtype=int)
    assignments = []
    for row in matrix:
        valid = np.flatnonzero(loads < capacities)
        if len(valid) == 0:
            break
        if strategy == "greedy":
            action = int(valid[np.argmax(row[valid])])
        else:
            action = int(rng.choice(valid))
        assignments.append(action); loads[action] += 1
    return np.asarray(assignments)


def optimal_assignment(matrix, capacities):
    """Solve the finite capacitated assignment exactly (evaluation upper bound)."""
    slots = np.repeat(np.arange(matrix.shape[1]), capacities.astype(int))
    rows, cols = linear_sum_assignment(-matrix[:, slots])
    actions = np.empty(matrix.shape[0], dtype=int)
    actions[rows] = slots[cols]
    return actions


def deferred_acceptance(matrix, capacities):
    """Student-proposing Gale-Shapley with advisor capacities (SPA form)."""
    n_students, n_advisors = matrix.shape
    preferences = np.argsort(-matrix, axis=1)
    rank = np.argsort(-matrix, axis=0)
    held = [[] for _ in range(n_advisors)]
    next_choice = np.zeros(n_students, dtype=int)
    free = list(range(n_students))
    while free:
        student = free.pop(0)
        if next_choice[student] >= n_advisors:
            continue
        advisor = int(preferences[student, next_choice[student]])
        next_choice[student] += 1
        held[advisor].append(student)
        held[advisor].sort(key=lambda s: int(rank[s, advisor]))
        if len(held[advisor]) > int(capacities[advisor]):
            rejected = held[advisor].pop()
            free.append(rejected)
    actions = np.full(n_students, -1, dtype=int)
    for advisor, students in enumerate(held):
        actions[students] = advisor
    return actions


def split_by_year(theses):
    years = pd.to_numeric(theses["completion_year"], errors="coerce")
    latest = int(years.max())
    train, test = theses[years.lt(latest)].copy(), theses[years.eq(latest)].copy()
    if not train.empty and not test.empty:
        return train, test, f"year_{latest}_holdout"
    ordered = theses.sort_values("student_id").reset_index(drop=True)
    cutoff = int(len(ordered) * 0.8)
    return ordered.iloc[:cutoff].copy(), ordered.iloc[cutoff:].copy(), "deterministic_80_20"


def metrics(actions, matrix, capacities, actual):
    loads = np.bincount(actions, minlength=len(capacities))
    scores = matrix[np.arange(len(actions)), actions]
    return {"assigned": len(actions), "mean_compatibility": round(float(scores.mean()), 6), "load_variance": round(float(np.var(loads)), 6), "quota_violations": int(np.maximum(loads - capacities, 0).sum()), "historical_top1_accuracy": round(float((actions == actual).mean()), 6)}


def rollout(model, env, masked):
    observation, _ = env.reset(); actions = []; done = False
    while not done:
        kwargs = {"action_masks": env.action_masks()} if masked else {}
        action, _ = model.predict(observation, deterministic=True, **kwargs)
        observation, _, done, _, _ = env.step(action)
        actions.append(env.core.assignments[-1])
    return np.asarray(actions), env.invalid_proposals


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--timesteps", type=int, default=2048)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    cleaned = ROOT / "data" / "cleaned"
    theses = pd.read_csv(cleaned / "theses.csv", encoding="utf-8-sig")
    advisors = pd.read_csv(cleaned / "advisors.csv", encoding="utf-8-sig")
    train, test, split = split_by_year(theses)
    train_matrix, vectorizer = build_compatibility(train, advisors)
    test_matrix, _ = build_compatibility(test, advisors, vectorizer=vectorizer, fit=False)
    train_capacity = np.full(len(advisors), int(np.ceil(len(train) / len(advisors))), dtype=int)
    test_capacity = np.full(len(advisors), int(np.ceil(len(test) / len(advisors))), dtype=int)
    train_env, test_env = GymMatchingEnv(train_matrix, train_capacity), GymMatchingEnv(test_matrix, test_capacity)
    name_to_id = {name: index for index, name in enumerate(advisors["advisor_name"])}
    actual = test["advisor_name"].map(name_to_id).to_numpy()
    rows = []
    for name in ("random", "greedy"):
        row = metrics(baseline(test_matrix, test_capacity, name, args.seed), test_matrix, test_capacity, actual)
        row.update({"algorithm": name, "invalid_proposals": 0}); rows.append(row)
    row = metrics(optimal_assignment(test_matrix, test_capacity), test_matrix, test_capacity, actual)
    row.update({"algorithm": "exact_optimal_upper_bound", "invalid_proposals": 0}); rows.append(row)
    for name in ("gale_shapley", "spa_deferred_acceptance"):
        row = metrics(deferred_acceptance(test_matrix, test_capacity), test_matrix, test_capacity, actual)
        row.update({"algorithm": name, "invalid_proposals": 0}); rows.append(row)
    from sb3_contrib import MaskablePPO
    from stable_baselines3 import DQN
    ppo = MaskablePPO("MlpPolicy", train_env, seed=args.seed, verbose=0, n_steps=256, batch_size=64)
    ppo.learn(total_timesteps=args.timesteps)
    actions, invalid = rollout(ppo, test_env, masked=True)
    ppo_metrics = metrics(actions, test_matrix, test_capacity, actual); ppo_metrics.update({"algorithm": "ppo_maskable", "invalid_proposals": invalid})
    dqn = DQN("MlpPolicy", train_env, seed=args.seed, verbose=0, learning_starts=100, buffer_size=5000, batch_size=64)
    dqn.learn(total_timesteps=args.timesteps)
    actions, invalid = rollout(dqn, test_env, masked=False)
    dqn_metrics = metrics(actions, test_matrix, test_capacity, actual); dqn_metrics.update({"algorithm": "dqn", "invalid_proposals": invalid})
    rows.extend([ppo_metrics, dqn_metrics])
    RESULTS.mkdir(parents=True, exist_ok=True)
    output = RESULTS / f"benchmark_{split}_seed{args.seed}_steps{args.timesteps}.json"
    payload = {"split": split, "train_students": len(train), "test_students": len(test), "advisors": len(advisors), "timesteps": args.timesteps, "seed": args.seed, "results": rows}
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
