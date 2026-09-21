"""Generate architectural and MDP formulation diagrams for KLTN thesis."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "outputs" / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)


def draw_system_architecture():
    fig, ax = plt.subplots(figsize=(14, 8), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis("off")
    fig.patch.set_facecolor("#f8fafc")

    ax.text(7, 7.6, "KIẾN TRÚC HỆ THỐNG PHÂN BỔ KHÓA LUẬN VỚI REINFORCEMENT LEARNING",
            ha="center", va="center", fontsize=14, fontweight="bold", color="#0f172a")
    ax.text(7, 7.25, "End-to-End Architecture: Data Ingestion, Semantic Compatibility, MDP Environment & Matching Engines",
            ha="center", va="center", fontsize=10.5, fontstyle="italic", color="#475569")

    layers = [
        {"title": "1. Curated Data Layer", "color": "#e0f2fe", "border": "#0284c7", "x": 0.5, "w": 2.8},
        {"title": "2. NLP & Compatibility", "color": "#fef3c7", "border": "#d97706", "x": 3.7, "w": 2.8},
        {"title": "3. Gymnasium MDP Core", "color": "#dcfce7", "border": "#16a34a", "x": 6.9, "w": 3.0},
        {"title": "4. Allocation Engines", "color": "#f3e8ff", "border": "#9333ea", "x": 10.3, "w": 3.2},
    ]

    for layer in layers:
        rect = patches.FancyBboxPatch((layer["x"], 0.6), layer["w"], 6.2,
                                     boxstyle="round,pad=0.1,rounding_size=0.2",
                                     linewidth=1.5, edgecolor=layer["border"], facecolor=layer["color"], alpha=0.35)
        ax.add_patch(rect)
        ax.text(layer["x"] + layer["w"]/2, 6.5, layer["title"], ha="center", va="center",
                fontsize=11.5, fontweight="bold", color=layer["border"])

    items1 = [
        "FIT NEU Crawler\n(39 Lecturers Roster)",
        "Theses Extractor\n(198 Curated Records)",
        "Skill Evidence Graph\n(Publications & Roles)",
        "Temporal Splitter\n(Train / Val / Test)",
    ]
    for i, item in enumerate(items1):
        y = 5.4 - i * 1.3
        box = patches.FancyBboxPatch((0.7, y - 0.4), 2.4, 0.9, boxstyle="round,pad=0.08,rounding_size=0.15",
                                    facecolor="#ffffff", edgecolor="#0284c7", linewidth=1.2)
        ax.add_patch(box)
        ax.text(1.9, y + 0.05, item, ha="center", va="center", fontsize=9.5, color="#1e293b")

    items2 = [
        "Text Normalizer &\nDomain Keywords",
        "Leak-Free Vocabulary\n(Fit on Train Only)",
        "TF-IDF Vectorizer &\nCosine Similarity",
        "Compatibility Matrix\nC in [0, 1] (N x M)",
    ]
    for i, item in enumerate(items2):
        y = 5.4 - i * 1.3
        box = patches.FancyBboxPatch((3.9, y - 0.4), 2.4, 0.9, boxstyle="round,pad=0.08,rounding_size=0.15",
                                    facecolor="#ffffff", edgecolor="#d97706", linewidth=1.2)
        ax.add_patch(box)
        ax.text(5.1, y + 0.05, item, ha="center", va="center", fontsize=9.5, color="#1e293b")

    items3 = [
        "Sequential State S_t\n[c_i, remaining, load]",
        "Action Masking Layer\nFilter Full Quotas",
        "Reward Formulation\nCompat - lambda*Var(load)",
        "Fairness & Quota Tracker\n(Zero Violation Guard)",
    ]
    for i, item in enumerate(items3):
        y = 5.4 - i * 1.3
        box = patches.FancyBboxPatch((7.1, y - 0.4), 2.6, 0.9, boxstyle="round,pad=0.08,rounding_size=0.15",
                                    facecolor="#ffffff", edgecolor="#16a34a", linewidth=1.2)
        ax.add_patch(box)
        ax.text(8.4, y + 0.05, item, ha="center", va="center", fontsize=9.5, color="#1e293b")

    items4 = [
        "Exact Hungarian [PROMOTED]\nGlobal Optimal Batch (0.0656)",
        "Maskable PPO [ONLINE RL]\nAction Masked Policy (0.0556)",
        "Gale-Shapley (SPA)\nDeferred Acceptance (0.0618)",
        "FastAPI & Interactive SPA\nReal-time Decision Support",
    ]
    for i, item in enumerate(items4):
        y = 5.4 - i * 1.3
        box = patches.FancyBboxPatch((10.5, y - 0.4), 2.8, 0.9, boxstyle="round,pad=0.08,rounding_size=0.15",
                                    facecolor="#ffffff", edgecolor="#9333ea", linewidth=1.2)
        ax.add_patch(box)
        ax.text(11.9, y + 0.05, item, ha="center", va="center", fontsize=9.5, color="#1e293b")

    arrow_props = dict(facecolor="#64748b", edgecolor="#475569", width=1.5, headwidth=6, headlength=7, shrink=0.1)
    for y in [5.4, 4.1, 2.8, 1.5]:
        ax.annotate("", xy=(3.9, y + 0.05), xytext=(3.1, y + 0.05), arrowprops=arrow_props)
        ax.annotate("", xy=(7.1, y + 0.05), xytext=(6.3, y + 0.05), arrowprops=arrow_props)
        ax.annotate("", xy=(10.5, y + 0.05), xytext=(9.7, y + 0.05), arrowprops=arrow_props)

    plt.tight_layout()
    out_path = FIGURES / "figure4_system_architecture.png"
    plt.savefig(out_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"Saved: {out_path}")



def draw_mdp_formulation():
    fig, ax = plt.subplots(figsize=(13, 7.5), dpi=300)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 7.5)
    ax.axis("off")
    fig.patch.set_facecolor("#ffffff")

    ax.text(6.5, 7.1, "QUY TRÌNH RA QUYẾT ĐỊNH MARKOV (MDP) CÓ ACTION MASKING",
            ha="center", va="center", fontsize=14, fontweight="bold", color="#0f172a")
    ax.text(6.5, 6.75, "Sequential Matching Step: State Observation, Illegal Action Filtering, Policy Inference & Quota Update",
            ha="center", va="center", fontsize=10.5, fontstyle="italic", color="#475569")

    box_state = patches.FancyBboxPatch((0.6, 3.5), 3.0, 2.5, boxstyle="round,pad=0.1", facecolor="#eff6ff", edgecolor="#2563eb", linewidth=1.5)
    ax.add_patch(box_state)
    ax.text(2.1, 5.6, "State Vector s_t in R^(3M)", ha="center", va="center", fontsize=11, fontweight="bold", color="#1e40af")
    state_desc = "- c_i: Compatibility vector\n  sinh vien i voi M giang vien\n- rem_j: Capacity con lai\n  cua tung giang vien j\n- w_j: Workload hien tai\n  dang gan cho giang vien j"
    ax.text(2.1, 4.4, state_desc, ha="center", va="center", fontsize=9.5, color="#1e293b")

    box_mask = patches.FancyBboxPatch((4.5, 3.5), 2.8, 2.5, boxstyle="round,pad=0.1", facecolor="#fef2f2", edgecolor="#dc2626", linewidth=1.5)
    ax.add_patch(box_mask)
    ax.text(5.9, 5.6, "Action Masking M_t", ha="center", va="center", fontsize=11, fontweight="bold", color="#b91c1c")
    mask_desc = "M_t(j) = 1  neu  w_j < C_j\nM_t(j) = 0  neu  w_j >= C_j\n\nTriet tieu hoan toan\nxac suat chon GV het quota:\nP(a | s, M_t) = 0 khi M_t(a)=0"
    ax.text(5.9, 4.4, mask_desc, ha="center", va="center", fontsize=9.5, color="#1e293b")

    box_policy = patches.FancyBboxPatch((8.2, 3.5), 4.2, 2.5, boxstyle="round,pad=0.1", facecolor="#f0fdf4", edgecolor="#16a34a", linewidth=1.5)
    ax.add_patch(box_policy)
    ax.text(10.3, 5.6, "Maskable PPO Policy", ha="center", va="center", fontsize=11, fontweight="bold", color="#15803d")
    policy_desc = "Logits z = f_theta(s_t)\nMasked Softmax: exp(z_j)*M_t(j) / sum(...)\nAction a_t ~ pi(a | s_t, M_t)\n-> 0 Vi pham Quota (0 Invalid Actions)"
    ax.text(10.3, 4.4, policy_desc, ha="center", va="center", fontsize=9.5, color="#1e293b")

    box_env = patches.FancyBboxPatch((2.0, 0.7), 9.0, 2.0, boxstyle="round,pad=0.1", facecolor="#faf5ff", edgecolor="#7e22ce", linewidth=1.5)
    ax.add_patch(box_env)
    ax.text(6.5, 2.3, "Environment Transition & Reward Engine (Gymnasium)", ha="center", va="center", fontsize=11.5, fontweight="bold", color="#6b21a8")
    env_desc = "1. Cap nhat: load(a_t) = load(a_t) + 1 | Student index: i = i + 1\n2. Phan thuong: R_t = Compatibility(i, a_t) - lambda * Var(Workloads) - P_invalid\n3. Episode ket thuc khi toan bo sinh vien trong cohort duoc phan bo"
    ax.text(6.5, 1.35, env_desc, ha="center", va="center", fontsize=10, color="#1e293b")

    arrow = dict(facecolor="#475569", edgecolor="#334155", width=1.5, headwidth=6, headlength=7, shrink=0.08)
    ax.annotate("", xy=(4.5, 4.75), xytext=(3.6, 4.75), arrowprops=arrow)
    ax.annotate("", xy=(8.2, 4.75), xytext=(7.3, 4.75), arrowprops=arrow)

    ax.annotate("Action a_t (Hop le)", xy=(10.3, 2.7), xytext=(10.3, 3.5),
                ha="center", va="center", fontsize=9, fontweight="bold", color="#15803d",
                arrowprops=dict(facecolor="#16a34a", edgecolor="#15803d", width=1.5, headwidth=6, headlength=7, shrink=0.05))

    ax.annotate("Next State s_(t+1) & Reward R_t", xy=(2.1, 3.5), xytext=(2.1, 2.7),
                ha="center", va="center", fontsize=9, fontweight="bold", color="#2563eb",
                arrowprops=dict(facecolor="#2563eb", edgecolor="#1d4ed8", width=1.5, headwidth=6, headlength=7, shrink=0.05))

    plt.tight_layout()
    out_path = FIGURES / "figure5_rl_mdp_flow.png"
    plt.savefig(out_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"Saved: {out_path}")


def main():
    draw_system_architecture()
    draw_mdp_formulation()
    print("All architecture and MDP diagrams generated successfully.")


if __name__ == "__main__":
    main()
