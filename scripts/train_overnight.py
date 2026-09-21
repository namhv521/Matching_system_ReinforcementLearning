"""Run the full matching experiment overnight; PPO and DQN train sequentially."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.rl.benchmark import baseline, deferred_acceptance, metrics, optimal_assignment
from src.rl.promotion import aggregate_runs, select_engine
from src.rl.train import RESULTS, load_environments, train_milestones


def baseline_results(seed: int) -> list[dict]:
    envs, frames, advisors, _ = load_environments(seed)
    frame = frames["validation"]
    matrix = envs["validation"].core.compatibility
    capacities = envs["validation"].core.capacities
    advisor_ids = {name: index for index, name in enumerate(advisors["advisor_name"])}
    actual = frame["advisor_name"].map(advisor_ids).to_numpy()
    algorithms = {
        "random": baseline(matrix, capacities, "random", seed),
        "exact": optimal_assignment(matrix, capacities),
        "greedy": baseline(matrix, capacities, "greedy", seed),
        "gale_shapley": deferred_acceptance(matrix, capacities),
    }
    rows = []
    for name, actions in algorithms.items():
        row = metrics(actions, matrix, capacities, actual)
        row.update({"algorithm": name, "invalid_proposals": 0})
        rows.append(row)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--milestones", type=int, nargs="+", default=[500_000, 1_000_000, 2_000_000])
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--verbose", type=int, choices=[0, 1, 2], default=1)
    parser.add_argument("--reuse-existing", action="store_true", help="Load existing milestone results if available.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if any(step <= 0 for step in args.milestones) or args.milestones != sorted(set(args.milestones)):
        parser.error("--milestones must be unique positive integers in ascending order")
    plan = {
        "milestones": args.milestones,
        "seed": args.seed,
        "train": ["ppo", "a2c", "dqn", "qrdqn"],
        "baselines": ["random", "exact", "greedy", "gale_shapley"],
        "select_after_all_results": True,
    }
    if args.dry_run:
        print(json.dumps(plan))
        return

    print(json.dumps(plan, ensure_ascii=False), flush=True)
    rows = baseline_results(args.seed)
    training_runs = {}
    for algorithm in plan["train"]:
        if args.reuse_existing:
            milestone_files = [RESULTS / f"{algorithm}_seed{args.seed}_steps{m}.json" for m in args.milestones]
            if all(f.exists() for f in milestone_files):
                runs = [json.loads(f.read_text(encoding="utf-8")) for f in milestone_files]
            else:
                runs = train_milestones(algorithm, args.milestones, args.seed, args.verbose)
        else:
            runs = train_milestones(algorithm, args.milestones, args.seed, args.verbose)
        training_runs[algorithm] = runs
        row = dict(runs[-1]["validation_metrics"])
        row.update({"algorithm": f"{algorithm}_maskable" if algorithm == "ppo" else algorithm})
        row.setdefault("quota_violations", 0)
        rows.append(row)
    RESULTS.mkdir(parents=True, exist_ok=True)
    decision = select_engine(aggregate_runs([{"results": rows}]))
    output = RESULTS / f"overnight_seed{args.seed}_steps{args.milestones[-1]}.json"
    output.write_text(json.dumps({"plan": plan, "evaluation_split": "validation", "training_runs": training_runs, "results": rows, "decision": decision}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(output), "results": rows, "decision": decision}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
