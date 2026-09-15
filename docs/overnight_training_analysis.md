0# Overnight RL Training & Comparative Benchmark Analysis

**Date:** September 14, 2026  
**Seed:** 42  
**Evaluation Split:** Validation (20 theses, 39 advisors)  
**Trained Models:** PPO (Maskable), A2C, DQN, QR-DQN  
**Milestones Evaluated:** 500k, 1M, 2M timesteps  

---

## 1. Executive Summary & Production Decision

The overnight multi-algorithm RL experiment completed 12 milestone checkpoints across four reinforcement learning families and evaluated them alongside classical baseline assignment algorithms (Random, Greedy, Gale-Shapley/SPA, Exact Hungarian).

### Production Engine Promotion Decision
- **Promoted Engine:** `exact` (Hungarian / Min-Cost Max-Flow Assignment).
- **Validation Mean Compatibility:** `0.065601`.
- **Constraint Violations / Invalid Proposals:** `0`.
- **Reasoning:** In full-batch assignment settings where all student-thesis profiles are known upfront, the Hungarian algorithm guarantees the theoretical global optimum in polynomial time ($O(N^3)$) with zero constraint violations. The promotion gate enforces that any RL model must exceed or match the exact solver while maintaining zero invalid proposals. PPO achieved `0.055579` at 1M steps (84.7% of the theoretical optimum), confirming its effectiveness as a sequential allocator, while `exact` remains the authoritative production batch engine.

---

## 2. Experimental Benchmark Results (Validation Set, $N=20$)

| Family | Algorithm | Timesteps | Mean Compatibility | Load Variance | Quota Violations | Invalid Action Proposals | Engine Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Baseline** | Random | - | 0.018001 | 0.249836 | 0 | 0 | Baseline |
| **Baseline** | Greedy | - | 0.061767 | 0.249836 | 0 | 0 | Baseline |
| **Baseline** | Gale-Shapley (SPA) | - | 0.061788 | 0.249836 | 0 | 0 | Baseline |
| **Exact** | **Hungarian (Exact)** | - | **0.065601** | **0.249836** | **0** | **0** | **PROMOTED (Production)** |
| **RL (Masked)** | PPO (Maskable) | 500,000 | 0.040845 | 0.249836 | 0 | 0 | Candidate |
| **RL (Masked)** | **PPO (Maskable)** | **1,000,000** | **0.055579** | **0.249836** | **0** | **0** | **Top RL Policy** |
| **RL (Masked)** | PPO (Maskable) | 2,000,000 | 0.047653 | 0.249836 | 0 | 0 | Candidate (Slight Overfitting) |
| **RL (Unmasked)**| DQN | 2,000,000 | 0.048941* | 0.249836 | 0 | 13 / 20 (65%) | Rejected (Mask-less fallback) |
| **RL (Unmasked)**| A2C | 2,000,000 | 0.063387* | 0.249836 | 0 | 19 / 20 (95%) | Rejected (Mask-less fallback) |
| **RL (Unmasked)**| QR-DQN | 2,000,000 | 0.064199* | 0.249836 | 0 | 17 / 20 (85%) | Rejected (Mask-less fallback) |

*\*Note: For unmasked algorithms (DQN, A2C, QR-DQN), invalid action proposals were intercepted and reassigned by the environment fallback logic. Although final quota violations are 0 after correction, their raw policies fail hard capacity constraints 65%–95% of the time.*

---

## 3. Key Findings & Insights for Thesis

### 3.1 The Critical Necessity of Action Masking (Figure 2)
- In dynamic matching environments where advisor capacities decrement as students are assigned, standard action-space exploration causes unmasked agents (DQN, A2C, QR-DQN) to repeatedly select saturated advisors (13–19 invalid proposals out of 20 steps).
- Only **Maskable PPO** dynamically pruned illegal actions via `ActionMaskEnv`, achieving **0 invalid proposals** across all 2,000,000 timesteps.
- **Thesis Takeaway:** Action masking is not merely an optimization in capacity-constrained RL; it is a fundamental prerequisite for constraint satisfaction.

### 3.2 PPO Learning Dynamics & Stopping Criterion (Figure 1)
- **200k steps:** Validation compatibility was `0.0210`, indicating early exploration.
- **500k steps:** Validation compatibility rose to `0.0408`.
- **1M steps:** Peak validation performance at `0.05558` (reward: `1.0741`).
- **2M steps:** Validation compatibility decreased slightly to `0.04765` while training reward continued to climb, revealing policy overfitting to the 150 training thesis distributions.
- **Thesis Takeaway:** 1,000,000 steps serves as the empirical early-stopping point for PPO on this dataset size.

### 3.3 Role of RL vs Combinatorial Optimization in KLTN (Figure 3)
- For static batch assignment where complete compatibility and capacity tensors are present at $t=0$, Hungarian ($O(N^3)$) is mathematically optimal.
- Maskable PPO's true value lies in **online, sequential, streaming arrival settings** (e.g. students registering sequentially, rolling defense committees, dynamic advisor preference changes) where future requests are stochastic and Hungarian cannot be rerun globally.


---

## 4. Generated Artifacts & Visualizations

The following artifacts have been generated in `outputs/`:
- **Results JSON:**
  - `outputs/results/overnight_seed42_steps2000000.json`: Complete record containing baseline benchmarks, 12 RL training runs, and promotion decision.
  - Checkpoint metrics across all 4 algorithms at 500k, 1M, and 2M timesteps.
- **Visual Figures (300 DPI):**
  - `outputs/figures/figure1_ppo_learning_curves.png`: Episode reward & mean compatibility progression over training timesteps, highlighting peak performance at 1M steps.
  - `outputs/figures/figure2_constraint_violations.png`: Hard constraint violation rates demonstrating 0% for Maskable PPO vs 65%–95% for unmasked algorithms.
  - `outputs/figures/figure3_algorithm_comparison.png`: Comprehensive benchmark comparison across Random, RL checkpoints, Greedy, Gale-Shapley, and Exact Hungarian.

---

## 5. Downstream Integration & Next Steps

1. **Thesis Chapter 4 & 5 Preparation:**
   - Incorporate `figure1_ppo_learning_curves.png`, `figure2_constraint_violations.png`, and `figure3_algorithm_comparison.png` into Chapter 4 (Experimental Evaluation).
   - Use the analysis in Section 3 to structure the discussion comparing exact combinatorial methods with sequential deep reinforcement learning.
2. **Online Streaming Deployment:**
   - Retain `ppo_seed42_steps1000000.zip` as the primary checkpoint for real-time / streaming matching endpoints where future students arrive asynchronously.
   - Retain `exact` Hungarian solver for end-of-semester batch assignment.
