# =============================================================================
# Recipe Site Traffic – DataCamp DS Professional Practical Exam
# Business Goal: Predict high-traffic recipes with Precision >= 80%
# =============================================================================

import warnings
warnings.filterwarnings('ignore')

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')          # non-interactive backend – saves plots to files
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score,
    precision_score, recall_score, f1_score,
    roc_curve, ConfusionMatrixDisplay,
)

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.dpi"] = 100
RANDOM_STATE = 42

# Output folder for plots
PLOT_DIR = os.path.join(os.path.dirname(__file__), "plots")
os.makedirs(PLOT_DIR, exist_ok=True)

def save(name):
    path = os.path.join(PLOT_DIR, name)
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"  [saved] {path}")

# =============================================================================
# 1. DATA VALIDATION
# =============================================================================
print("=" * 60)
print("1. DATA VALIDATION")
print("=" * 60)

df_raw = pd.read_csv(os.path.join(os.path.dirname(__file__), "recipe_site_traffic_2212.csv"))
print(f"Shape: {df_raw.shape}")
print(df_raw.dtypes)
print("\nMissing values:\n", df_raw.isnull().sum())
print("\nservings unique :", sorted(df_raw["servings"].unique()))
print("high_traffic counts:\n", df_raw["high_traffic"].value_counts(dropna=False))

# ── Cleaning ─────────────────────────────────────────────────────────────────
df = df_raw.copy()

# 1. high_traffic → binary  (NaN = Not High = 0)
df["high_traffic"] = df["high_traffic"].apply(lambda x: 1 if x == "High" else 0)

# 2. servings → extract integer  ("4 as a snack" → 4)
df["servings"] = df["servings"].astype(str).str.extract(r"(\d+)").astype(int)

# 3. Numeric columns → median imputation
NUMERIC = ["calories", "carbohydrate", "sugar", "protein"]
for col in NUMERIC:
    med = df[col].median()
    n   = df[col].isnull().sum()
    df[col] = df[col].fillna(med)
    print(f"  {col}: filled {n} NaN with median = {med:.2f}")

# 4. category → label encode
le = LabelEncoder()
df["category_encoded"] = le.fit_transform(df["category"])

print(f"\nClass balance : {df['high_traffic'].mean():.1%} high traffic")
print(f"Remaining NaN:\n{df[NUMERIC + ['servings', 'high_traffic']].isnull().sum()}")

# =============================================================================
# 2. EXPLORATORY DATA ANALYSIS
# =============================================================================
print("\n" + "=" * 60)
print("2. EXPLORATORY DATA ANALYSIS")
print("=" * 60)

# ── Plot 1: Calorie distribution (single variable) ───────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

axes[0].hist(df["calories"], bins=40, color="steelblue", edgecolor="white", alpha=0.85)
axes[0].axvline(df["calories"].median(), color="red", linestyle="--", linewidth=1.8,
                label=f"Median = {df['calories'].median():.0f}")
axes[0].set_title("Distribution of Calories", fontweight="bold")
axes[0].set_xlabel("Calories"); axes[0].set_ylabel("Count"); axes[0].legend()

axes[1].boxplot(df["calories"], patch_artist=True,
                boxprops=dict(facecolor="lightblue", color="steelblue"),
                medianprops=dict(color="red", linewidth=2))
axes[1].set_title("Calories – Box Plot", fontweight="bold")
axes[1].set_ylabel("Calories"); axes[1].set_xticks([])

plt.suptitle("Calories: Univariate Analysis", fontsize=14, fontweight="bold", y=1.02)
plt.tight_layout()
save("plot1_calories.png")
# Finding: right-skewed; median ~289 kcal vs mean ~436 kcal; outliers >2500 kcal.

# ── Plot 2: Recipes per category (single variable) ───────────────────────────
cat_counts = df["category"].value_counts().sort_values()

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(cat_counts.index, cat_counts.values,
               color=sns.color_palette("Blues_d", len(cat_counts)))
ax.bar_label(bars, padding=3, fontsize=10)
ax.set_title("Recipes per Category", fontsize=13, fontweight="bold")
ax.set_xlabel("Count"); ax.set_xlim(0, cat_counts.max() + 20)
plt.tight_layout()
save("plot2_category_counts.png")
# Finding: Chicken Breast, Breakfast, Chicken dominate (100+ each).

# ── Plot 3: Category vs traffic + calories by target (multi-variable) ────────
cat_t = df.groupby("category")["high_traffic"].agg(["sum", "count"]).rename(
    columns={"sum": "high", "count": "total"})
cat_t["not_high"] = cat_t["total"] - cat_t["high"]
cat_t["rate"] = cat_t["high"] / cat_t["total"]
cat_t = cat_t.sort_values("rate")

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

ax = axes[0]
ax.barh(cat_t.index, cat_t["high"],     color="#2196F3", label="High Traffic")
ax.barh(cat_t.index, cat_t["not_high"], left=cat_t["high"], color="#BDBDBD", label="Not High")
for i, (_, row) in enumerate(cat_t.iterrows()):
    ax.text(row["total"] + 1, i, f"{row['rate']:.0%}", va="center", fontsize=9, color="#1565C0")
ax.set_title("High Traffic Rate by Category", fontweight="bold")
ax.legend(loc="lower right"); ax.set_xlim(0, cat_t["total"].max() + 25)
ax.set_xlabel("Recipes")

ax2 = axes[1]
bp = ax2.boxplot([df[df["high_traffic"] == 0]["calories"],
                  df[df["high_traffic"] == 1]["calories"]],
                 labels=["Not High", "High"], patch_artist=True,
                 medianprops=dict(color="red", linewidth=2))
bp["boxes"][0].set_facecolor("#BDBDBD"); bp["boxes"][1].set_facecolor("#64B5F6")
ax2.set_title("Calories by Traffic Class", fontweight="bold"); ax2.set_ylabel("Calories")

plt.suptitle("Category & Calories vs High Traffic", fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
save("plot3_multivariate.png")

print("\nHigh-traffic rate by category:")
print(cat_t[["high", "total", "rate"]].sort_values("rate", ascending=False).round(3))
# Finding: Potato(83%), Pork(79%), Vegetable(76%) best; Breakfast(44%), Chicken Breast(43%) worst.

# =============================================================================
# 3. MODEL DEVELOPMENT   (Binary classification: 1=High, 0=Not High)
# =============================================================================
print("\n" + "=" * 60)
print("3. MODEL DEVELOPMENT")
print("=" * 60)

FEATURES = ["calories", "carbohydrate", "sugar", "protein", "servings", "category_encoded"]
X = df[FEATURES]
y = df["high_traffic"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y)
print(f"Train: {len(X_train)}  |  Test: {len(X_test)}")

scaler  = StandardScaler()
X_tr_sc = scaler.fit_transform(X_train)
X_te_sc = scaler.transform(X_test)

# ── Baseline: Logistic Regression ────────────────────────────────────────────
# Why: interpretable linear baseline; coefficients show feature direction;
#      low variance; easy to explain to non-technical stakeholders.
lr = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=RANDOM_STATE)
lr.fit(X_tr_sc, y_train)
y_pred_lr = lr.predict(X_te_sc)
y_prob_lr = lr.predict_proba(X_te_sc)[:, 1]
cv_lr = cross_val_score(lr, X_tr_sc, y_train, cv=5, scoring="roc_auc")
print(f"Logistic Regression  5-fold CV AUC: {cv_lr.mean():.4f} ± {cv_lr.std():.4f}")

# ── Comparison: Random Forest ─────────────────────────────────────────────────
# Why: captures non-linear interactions (e.g. calorie level AND category);
#      robust to skewed data; built-in feature importance; ensemble reduces overfitting.
rf = RandomForestClassifier(n_estimators=200, max_depth=8, min_samples_split=10,
                             class_weight="balanced", random_state=RANDOM_STATE, n_jobs=-1)
rf.fit(X_train, y_train)
y_pred_rf = rf.predict(X_test)
y_prob_rf  = rf.predict_proba(X_test)[:, 1]
cv_rf = cross_val_score(rf, X_train, y_train, cv=5, scoring="roc_auc")
print(f"Random Forest        5-fold CV AUC: {cv_rf.mean():.4f} ± {cv_rf.std():.4f}")

# =============================================================================
# 4. MODEL EVALUATION
# =============================================================================
print("\n" + "=" * 60)
print("4. MODEL EVALUATION")
print("=" * 60)

def eval_model(name, y_true, y_pred, y_prob):
    print(f"\n{'='*50}\n  {name}\n{'='*50}")
    print(classification_report(y_true, y_pred, target_names=["Not High", "High"]))
    return {
        "model":          name,
        "roc_auc":        roc_auc_score(y_true, y_prob),
        "precision_high": precision_score(y_true, y_pred),
        "recall_high":    recall_score(y_true, y_pred),
        "f1_high":        f1_score(y_true, y_pred),
    }

m_lr = eval_model("Logistic Regression", y_test, y_pred_lr, y_prob_lr)
m_rf = eval_model("Random Forest",       y_test, y_pred_rf, y_prob_rf)

# ── Confusion matrices ────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
for ax, name, yp in zip(axes,
                         ["Logistic Regression", "Random Forest"],
                         [y_pred_lr, y_pred_rf]):
    ConfusionMatrixDisplay(confusion_matrix(y_test, yp),
                           display_labels=["Not High", "High"]).plot(
        ax=ax, colorbar=False, cmap="Blues")
    ax.set_title(f"Confusion Matrix – {name}", fontweight="bold")
plt.suptitle("Confusion Matrices", fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
save("plot4_confusion_matrices.png")

# ── ROC curves ────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 5))
for name, yp, col in [("Logistic Regression", y_prob_lr, "#1976D2"),
                       ("Random Forest",       y_prob_rf, "#E53935")]:
    fpr, tpr, _ = roc_curve(y_test, yp)
    ax.plot(fpr, tpr, color=col, lw=2.5,
            label=f"{name} (AUC={roc_auc_score(y_test, yp):.3f})")
ax.plot([0, 1], [0, 1], "k--", lw=1.2, label="Random Baseline")
ax.set_xlabel("FPR"); ax.set_ylabel("TPR")
ax.set_title("ROC Curves", fontweight="bold"); ax.legend(); ax.grid(alpha=0.4)
plt.tight_layout()
save("plot5_roc_curves.png")

# ── Metrics bar chart ─────────────────────────────────────────────────────────
metrics_df = pd.DataFrame([m_lr, m_rf]).set_index("model")
x, w = np.arange(len(metrics_df.columns)), 0.35
fig, ax = plt.subplots(figsize=(10, 5))
b1 = ax.bar(x - w/2, metrics_df.loc["Logistic Regression"], w,
            label="Logistic Regression", color="#1976D2")
b2 = ax.bar(x + w/2, metrics_df.loc["Random Forest"],       w,
            label="Random Forest",       color="#E53935")
ax.axhline(0.80, color="green", linestyle="--", lw=1.8, label="80% Business Target")
ax.set_xticks(x)
ax.set_xticklabels(["ROC-AUC", "Precision (High)", "Recall (High)", "F1 (High)"], fontsize=11)
ax.set_ylim(0, 1.05); ax.set_ylabel("Score"); ax.legend()
ax.set_title("Performance Metrics Comparison", fontweight="bold")
for bar in list(b1) + list(b2):
    ax.annotate(f"{bar.get_height():.2f}",
                xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                xytext=(0, 3), textcoords="offset points", ha="center", fontsize=9)
plt.tight_layout()
save("plot6_metrics_comparison.png")

# ── Feature importance ────────────────────────────────────────────────────────
fi = pd.Series(rf.feature_importances_, index=FEATURES).sort_values()
fig, ax = plt.subplots(figsize=(8, 4))
fi.plot.barh(ax=ax, color="#1976D2", edgecolor="white")
ax.set_title("Random Forest – Feature Importance", fontweight="bold")
ax.set_xlabel("Importance Score")
for bar in ax.patches:
    ax.text(bar.get_width() + 0.001, bar.get_y() + bar.get_height() / 2,
            f"{bar.get_width():.3f}", va="center", fontsize=9)
plt.tight_layout()
save("plot7_feature_importance.png")

print("\nFeature importances (desc):")
print(fi.sort_values(ascending=False).round(4).to_string())

# =============================================================================
# 5. BUSINESS METRICS
# =============================================================================
print("\n" + "=" * 60)
print("5. BUSINESS METRICS")
print("=" * 60)
# Primary KPI : Precision on High Traffic class = TP / (TP + FP)
#   → how often are we right when we say "this recipe will be popular"?
# Secondary KPI: Recall on High Traffic class >= 70%
#   → don't leave too many good recipes out of the rotation.

biz = pd.DataFrame([m_lr, m_rf]).set_index("model").round(4)
print(biz.to_string())

print("\n80% Precision Target Met?")
for mdl in biz.index:
    p      = biz.loc[mdl, "precision_high"]
    status = "YES ✓" if p >= 0.80 else "NO ✗"
    print(f"  {mdl}: {p:.2%}  →  {status}")

best           = biz["precision_high"].idxmax()
p, r           = biz.loc[best, "precision_high"], biz.loc[best, "recall_high"]
actual_high    = int(y.sum())
predicted_high = int(actual_high / r) if r > 0 else 0
correct_pred   = int(predicted_high * p)
print(f"\nRecommended model   : {best}")
print(f"  Actual high-traffic recipes : {actual_high} / {len(df)} ({actual_high/len(df):.1%})")
print(f"  Est. homepage picks / batch : ~{predicted_high}")
print(f"  Est. correctly identified   : ~{correct_pred} ({correct_pred/predicted_high:.0%} correct)")

# =============================================================================
# 6. FINAL SUMMARY & RECOMMENDATIONS
# =============================================================================
print("\n" + "=" * 60)
print("6. FINAL SUMMARY & RECOMMENDATIONS")
print("=" * 60)
print(f"""
Problem type      : Binary classification (High = 1 / Not High = 0)
Recommended model : {best}

  - Achieves highest Precision on the High Traffic class
  - Handles skewed calorie data and non-linear category interactions
  - Feature importance confirms 'category' is the dominant predictor

Key findings:
  - Potato (83%), Pork (79%), Vegetable (76%)  →  most reliable traffic drivers
  - Breakfast (44%), Chicken Breast (43%)       →  high volume, low conversion
  - Nutritional features (calories, protein…)   →  moderate signal; category dominates

Business KPIs to monitor:
  PRIMARY  : Precision (High Traffic class) >= 80%
  SECONDARY: Recall    (High Traffic class) >= 70%  [review monthly]

Recommendations:
  1. Deploy {best}; use predicted probabilities to rank recipes for editors.
  2. Prioritise Potato, Pork, Vegetable, One Dish Meal in homepage slots.
  3. Revisit Breakfast & Chicken Breast strategy – high volume, low conversion.
  4. Collect richer data: clicks, time-on-page, saves → better future models.
  5. A/B test model vs. editorial picks over 4–6 weeks before full rollout.
  6. Retrain quarterly to capture seasonal trends (holiday baking, summer salads).

Plots saved to: {PLOT_DIR}
""")
