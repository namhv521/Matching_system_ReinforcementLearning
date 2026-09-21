"""Generate publication-quality figures for KLTN from overnight training results."""
from pathlib import Path
import json
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.analysis.experiment_analysis import load_payloads, summarize_results, write_summary

RESULTS = ROOT / "outputs" / "results"
FIGURES = ROOT / "outputs" / "figures"
CURATED = ROOT / "data" / "curated"
FIGURES.mkdir(parents=True, exist_ok=True)

plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.titlesize": 14,
})


def plot_ppo_learning_curves():
    """Figure 1: PPO training progression across milestones (200k, 500k, 1M, 2M)."""
    milestones = [200_000, 500_000, 1_000_000, 2_000_000]
    steps_labels = ["200k", "500k", "1M", "2M"]
    train_rewards, val_rewards = [], []
    train_comps, val_comps = [], []

    for m in milestones:
        file = RESULTS / f"ppo_seed42_steps{m}.json"
        if not file.exists():
            continue
        data = json.loads(file.read_text(encoding="utf-8"))
        train_rewards.append(data["train_metrics"]["total_reward"])
        val_rewards.append(data["validation_metrics"]["total_reward"])
        train_comps.append(data["train_metrics"]["mean_compatibility"])
        val_comps.append(data["validation_metrics"]["mean_compatibility"])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8), dpi=300)

    ax1.plot(steps_labels, train_rewards, marker="o", linewidth=2, color="#1f77b4", label="Train Reward")
    ax1.plot(steps_labels, val_rewards, marker="s", linewidth=2, color="#ff7f0e", label="Validation Reward")
    ax1.set_title("PPO Episode Reward Progression")
    ax1.set_xlabel("Training Timesteps")
    ax1.set_ylabel("Total Episode Reward")
    ax1.grid(True, linestyle="--", alpha=0.6)
    ax1.legend()

    ax2.plot(steps_labels, train_comps, marker="o", linewidth=2, color="#2ca02c", label="Train Compatibility")
    ax2.plot(steps_labels, val_comps, marker="s", linewidth=2, color="#d62728", label="Validation Compatibility")
    ax2.axhline(0.065601, color="black", linestyle=":", label="Exact Baseline (Upper Bound)")
    ax2.axhline(0.061767, color="gray", linestyle="--", label="Greedy Baseline")
    ax2.set_title("PPO Mean Compatibility Progression")
    ax2.set_xlabel("Training Timesteps")
    ax2.set_ylabel("Mean Compatibility")
    ax2.grid(True, linestyle="--", alpha=0.6)
    ax2.legend()

    plt.tight_layout()
    out_path = FIGURES / "figure1_ppo_learning_curves.png"
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")
def _summary():
    return summarize_results(load_payloads(RESULTS))


def plot_constraint_violations(summary):
    """Figure 2: Invalid Action Proposals on Validation Cohort (Constraint Adherence)."""
    preferred = ["ppo_maskable", "dqn", "qrdqn", "a2c"]
    algos = [name for name in preferred if name in summary["algorithms"]]
    invalid_counts = [summary["algorithms"][name]["mean_invalid_proposals"] for name in algos]
    colors = ["#2ca02c" if count == 0 else "#d62728" for count in invalid_counts]

    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=300)
    bars = ax.bar(algos, invalid_counts, color=colors, width=0.55, edgecolor="black", linewidth=0.8)

    for bar, count in zip(bars, invalid_counts):
        yval = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            yval + 0.5,
            f"{count:.1f}",
            ha="center",
            va="bottom",
            fontweight="bold",
        )

    ax.set_ylim(0, max(invalid_counts + [1]) * 1.25)
    ax.set_title(f"Invalid Proposals on Validation ({len(summary['seeds'])} seed(s))")
    ax.set_xlabel("Algorithm")
    ax.set_ylabel("Invalid Action Proposals (Full Quota Chosen)")
    ax.grid(axis="y", linestyle="--", alpha=0.6)

    plt.tight_layout()
    out_path = FIGURES / "figure2_constraint_violations.png"
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")


def plot_algorithm_comparison(summary):
    """Figure 3: Mean Compatibility Benchmark across Baselines and RL at 2M steps."""
    ordered = ["random", "ppo_maskable", "dqn", "qrdqn", "a2c", "greedy", "gale_shapley", "exact"]
    labels = [name for name in ordered if name in summary["algorithms"]]
    compatibilities = [summary["algorithms"][name]["mean_compatibility"] for name in labels]
    errors = [summary["algorithms"][name]["std_compatibility"] for name in labels]
    colors = ["#2ca02c" if summary["algorithms"][name]["safe_run_rate"] == 1 else "#d62728" for name in labels]

    fig, ax = plt.subplots(figsize=(11, 5.2), dpi=300)
    bars = ax.bar(labels, compatibilities, yerr=errors, capsize=3, color=colors, width=0.6, edgecolor="black", linewidth=0.8)

    for bar, val in zip(bars, compatibilities):
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            val + 0.0015,
            f"{val:.4f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    ax.set_ylim(0, 0.078)
    ax.set_title(f"Matching Engine Benchmark: Mean ± SD ({len(summary['seeds'])} seed(s))")
    ax.set_xlabel("Green: all runs satisfy hard constraints; red: unsafe proposals observed")
    ax.set_ylabel("Mean Compatibility Score")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=25, ha="right")
    ax.grid(axis="y", linestyle="--", alpha=0.6)

    plt.tight_layout()
    out_path = FIGURES / "figure3_algorithm_comparison.png"
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")


def plot_data_distribution():
    theses = pd.read_csv(CURATED / "theses.csv", encoding="utf-8-sig")
    advisors = pd.read_csv(CURATED / "advisors.csv", encoding="utf-8-sig")
    roles = theses["primary_role"].fillna("unknown").value_counts().sort_values()
    evidence = advisors["skill_count"].fillna(0)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=300)
    roles.plot.barh(ax=ax1, color="#2563eb")
    ax1.set_title("Phân bố vai trò kỹ thuật của đề tài")
    ax1.set_xlabel("Số khóa luận")
    ax1.set_ylabel("Vai trò chính")
    ax2.hist(evidence, bins=min(10, max(3, evidence.nunique())), color="#0f766e", edgecolor="white")
    ax2.set_title("Phân bố số nhóm kỹ năng của giảng viên")
    ax2.set_xlabel("Số nhóm kỹ năng")
    ax2.set_ylabel("Số giảng viên")
    plt.tight_layout()
    out_path = FIGURES / "figure6_data_distribution.png"
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")


def main():
    summary = _summary()
    write_summary(RESULTS, RESULTS / "analysis_summary.json")
    plot_ppo_learning_curves()
    plot_constraint_violations(summary)
    plot_algorithm_comparison(summary)
    plot_data_distribution()
    print("All figures successfully generated in outputs/figures/.")


if __name__ == "__main__":
    main()
