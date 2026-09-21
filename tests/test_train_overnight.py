import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def test_dry_run_lists_trainable_and_baseline_algorithms():
    result = subprocess.run(
        [sys.executable, "scripts/train_overnight.py", "--dry-run"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )

    plan = json.loads(result.stdout)
    assert plan["milestones"] == [500_000, 1_000_000, 2_000_000]
    assert plan["train"] == ["ppo", "a2c", "dqn", "qrdqn"]
    assert plan["baselines"] == ["random", "exact", "greedy", "gale_shapley"]
    assert plan["select_after_all_results"] is True
