"""Run independent RL benchmarks at fixed timestep budgets and assess convergence."""
import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "outputs" / "results"
CHECKPOINTS = (10_000, 20_000, 50_000, 100_000, 200_000)


def result_file(seed: int, timesteps: int) -> Path:
    matches = sorted(RESULTS.glob(f"benchmark_*_seed{seed}_steps{timesteps}.json"))
    if len(matches) != 1:
        raise FileNotFoundError(f"Expected exactly one benchmark result for seed={seed}, timesteps={timesteps}; found {matches}")
    return matches[0]


def by_algorithm(payload: dict, name: str) -> dict:
    for row in payload["results"]:
        if row["algorithm"] == name:
            return row
    raise KeyError(f"Algorithm '{name}' missing from benchmark result")


def assess(rows: list[dict], tolerance: float) -> dict:
    ppo_values = [row["ppo_mean_compatibility"] for row in rows]
    changes = [round(ppo_values[index] - ppo_values[index - 1], 6) for index in range(1, len(ppo_values))]
    latest = rows[-1]
    plateau = len(changes) >= 2 and all(abs(change) <= tolerance for change in changes[-2:])
    degraded = bool(changes and changes[-1] < -tolerance)
    beats_greedy = latest["ppo_mean_compatibility"] >= latest["greedy_mean_compatibility"]
    if plateau and not degraded:
        verdict = "PRELIMINARY_CONVERGED"
        reason = f"PPO compatibility changed by at most {tolerance} over the last two checkpoint intervals."
    elif degraded:
        verdict = "NOT_CONVERGED_OR_UNSTABLE"
        reason = "Latest PPO compatibility decreased beyond the configured tolerance."
    else:
        verdict = "NOT_YET_CONVERGED"
        reason = "PPO compatibility is still changing materially at recent checkpoints."
    return {"verdict": verdict, "reason": reason, "ppo_changes": changes, "ppo_beats_or_equals_greedy_at_latest": beats_greedy}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=42, help="Single fixed seed used at every timestep budget.")
    parser.add_argument("--tolerance", type=float, default=0.01, help="Absolute PPO compatibility change treated as a plateau.")
    parser.add_argument("--skip-existing", action="store_true", help="Reuse an existing result JSON instead of rerunning that budget.")
    parser.add_argument("--dry-run", action="store_true", help="Print the five planned benchmark commands without training.")
    args = parser.parse_args()
    RESULTS.mkdir(parents=True, exist_ok=True)
    if args.dry_run:
        print(f"Fixed seed: {args.seed}")
        print("Each run is independent and starts training from scratch.")
        for timesteps in CHECKPOINTS:
            print(" ".join([sys.executable, "-m", "src.rl.benchmark", "--timesteps", str(timesteps), "--seed", str(args.seed)]))
        return
    rows = []
    for timesteps in CHECKPOINTS:
        try:
            output = result_file(args.seed, timesteps)
            if not args.skip_existing:
                raise FileNotFoundError
            print(f"Reusing {output.name}")
        except FileNotFoundError:
            command = [sys.executable, "-m", "src.rl.benchmark", "--timesteps", str(timesteps), "--seed", str(args.seed)]
            print("Running:", " ".join(command))
            subprocess.run(command, cwd=ROOT, check=True)
            output = result_file(args.seed, timesteps)
        payload = json.loads(output.read_text(encoding="utf-8"))
        ppo, greedy, dqn = by_algorithm(payload, "ppo_maskable"), by_algorithm(payload, "greedy"), by_algorithm(payload, "dqn")
        rows.append({
            "timesteps": timesteps,
            "split": payload["split"],
            "ppo_mean_compatibility": ppo["mean_compatibility"],
            "greedy_mean_compatibility": greedy["mean_compatibility"],
            "dqn_mean_compatibility": dqn["mean_compatibility"],
            "ppo_load_variance": ppo["load_variance"],
            "ppo_invalid_proposals": ppo["invalid_proposals"],
            "dqn_invalid_proposals": dqn["invalid_proposals"],
        })
    assessment = assess(rows, args.tolerance)
    report = {"seed": args.seed, "checkpoints": list(CHECKPOINTS), "tolerance": args.tolerance, "independent_runs": True, "assessment": assessment, "results": rows}
    json_path = RESULTS / f"convergence_seed{args.seed}.json"
    text_path = RESULTS / f"convergence_seed{args.seed}.txt"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [f"Seed: {args.seed}", "Runs are independent; each timestep budget trains from scratch.", f"Verdict: {assessment['verdict']}", f"Reason: {assessment['reason']}", f"PPO changes: {assessment['ppo_changes']}", f"PPO >= Greedy at latest checkpoint: {assessment['ppo_beats_or_equals_greedy_at_latest']}", "", "timesteps | PPO compatibility | Greedy compatibility | DQN compatibility | PPO load variance | PPO invalid | DQN invalid"]
    for row in rows:
        lines.append(f"{row['timesteps']:>9} | {row['ppo_mean_compatibility']:.6f} | {row['greedy_mean_compatibility']:.6f} | {row['dqn_mean_compatibility']:.6f} | {row['ppo_load_variance']:.6f} | {row['ppo_invalid_proposals']} | {row['dqn_invalid_proposals']}")
    text_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"Saved: {json_path}\nSaved: {text_path}")


if __name__ == "__main__":
    main()