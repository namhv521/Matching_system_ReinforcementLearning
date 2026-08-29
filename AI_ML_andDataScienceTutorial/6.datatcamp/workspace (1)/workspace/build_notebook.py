"""Script to build the complete notebook.ipynb programmatically."""
import json, nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

cells = []

# ── Title ──────────────────────────────────────────────────────────────────
cells.append(new_markdown_cell("""# Data Scientist Professional Practical Exam Submission
## Recipe Site Traffic Prediction – Tasty Bytes

**Business Problem:** Predict which recipes generate high traffic on the homepage.  
**Target:** Precision ≥ 80 % on the *High Traffic* class (correctly identify popular recipes 8 times out of 10).

---"""))

# ── 0. Imports ──────────────────────────────────────────────────────────────
cells.append(new_markdown_cell("## 0. Setup – Import Libraries"))
cells.append(new_code_cell("""\
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score,
    precision_score, recall_score, f1_score,
    roc_curve, ConfusionMatrixDisplay
)

sns.set_theme(style='whitegrid', palette='muted')
plt.rcParams['figure.dpi'] = 100
RANDOM_STATE = 42
print("Libraries loaded successfully.")"""))

# ── 1. Data Validation ──────────────────────────────────────────────────────
cells.append(new_markdown_cell("""\
---
## 1. Data Validation

Every column is inspected for data type, value range, and missing values, then cleaned."""))

cells.append(new_markdown_cell("### 1.1 Load Data"))
cells.append(new_code_cell("""\
df_raw = pd.read_csv('recipe_site_traffic_2212.csv')
print(f"Shape: {df_raw.shape}")
df_raw.head(10)"""))

cells.append(new_code_cell("""\
df_raw.info()
print("\\nMissing values per column:")
print(df_raw.isnull().sum())"""))

cells.append(new_code_cell("df_raw.describe(include='all')"))

cells.append(new_markdown_cell("""\
### 1.2 Column-by-Column Validation

| Column | Type | Issues | Action |
|--------|------|--------|--------|
| `recipe` | int | Unique ID, no NaN | Keep as identifier |
| `calories` | float | 52 NaN | Impute with median |
| `carbohydrate` | float | 52 NaN (same rows) | Impute with median |
| `sugar` | float | 52 NaN (same rows) | Impute with median |
| `protein` | float | 52 NaN (same rows) | Impute with median |
| `category` | object | 11 valid values, no NaN | Label-encode |
| `servings` | object | String values like "4 as a snack" | Extract integer |
| `high_traffic` | object | 373 NaN = Not High | Map to binary 1/0 |"""))

cells.append(new_code_cell("""\
df = df_raw.copy()

print(f"Unique recipe IDs: {df['recipe'].nunique()}  (total rows: {len(df)})")
print(f"\\ncategory unique ({df['category'].nunique()}): {sorted(df['category'].unique())}")
print(f"\\nservings unique: {sorted(df['servings'].unique())}")
print("\\nhigh_traffic value counts (incl. NaN):")
print(df['high_traffic'].value_counts(dropna=False))"""))

cells.append(new_markdown_cell("### 1.3 Cleaning Steps"))

cells.append(new_code_cell("""\
# 1. Target: high_traffic -> binary
df['high_traffic'] = df['high_traffic'].apply(lambda x: 1 if x == 'High' else 0)
print("high_traffic after encoding:")
print(df['high_traffic'].value_counts())
print(f"Class balance: {df['high_traffic'].mean():.1%} high traffic")"""))

cells.append(new_code_cell("""\
# 2. servings: extract integer
df['servings'] = df['servings'].astype(str).str.extract(r'(\\d+)').astype(int)
print("servings after cleaning:")
print(df['servings'].value_counts().sort_index())"""))

cells.append(new_code_cell("""\
# 3. Numeric columns: impute NaN with median
numeric_cols = ['calories', 'carbohydrate', 'sugar', 'protein']
for col in numeric_cols:
    median_val = df[col].median()
    n_filled = df[col].isnull().sum()
    df[col] = df[col].fillna(median_val)
    print(f"{col}: filled {n_filled} NaN with median = {median_val:.2f}")"""))

cells.append(new_code_cell("""\
# 4. category: label encode
le = LabelEncoder()
df['category_encoded'] = le.fit_transform(df['category'])
print("Category encoding:")
for i, c in enumerate(le.classes_):
    print(f"  {i}: {c}")"""))

cells.append(new_code_cell("""\
# Final check
print("Missing values after cleaning:")
print(df[numeric_cols + ['servings', 'category', 'high_traffic']].isnull().sum())
print(f"\\nFinal shape: {df.shape}")
df.head()"""))

# ── 2. EDA ──────────────────────────────────────────────────────────────────
cells.append(new_markdown_cell("""\
---
## 2. Exploratory Data Analysis

Three visualisations:
1. Single-variable: distribution of **calories**
2. Single-variable: recipe count by **category**
3. Multi-variable: **category vs high_traffic** and **calories by target**"""))

cells.append(new_markdown_cell("### 2.1 Single-Variable: Calorie Distribution"))

cells.append(new_code_cell("""\
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].hist(df['calories'], bins=40, color='steelblue', edgecolor='white', alpha=0.85)
axes[0].axvline(df['calories'].median(), color='red', linestyle='--', linewidth=1.8,
                label=f"Median = {df['calories'].median():.0f}")
axes[0].set_title('Distribution of Calories', fontsize=13, fontweight='bold')
axes[0].set_xlabel('Calories')
axes[0].set_ylabel('Count')
axes[0].legend()

axes[1].boxplot(df['calories'], vert=True, patch_artist=True,
                boxprops=dict(facecolor='lightblue', color='steelblue'),
                medianprops=dict(color='red', linewidth=2))
axes[1].set_title('Calories – Box Plot', fontsize=13, fontweight='bold')
axes[1].set_ylabel('Calories')
axes[1].set_xticks([])

plt.suptitle('Calories: Univariate Analysis', fontsize=15, fontweight='bold', y=1.02)
plt.tight_layout()
plt.show()

print(df['calories'].describe().round(2))"""))

cells.append(new_markdown_cell("""\
**Findings – Calories:**
- The calorie distribution is **heavily right-skewed**: median (~289 kcal) is well below the mean (~436 kcal).
- Most recipes cluster in the **100–800 kcal** range; extreme outliers (>2500 kcal) represent calorie-dense dishes.
- The skewness justifies using **median imputation** for missing values and using a tree-based model robust to outliers."""))

cells.append(new_markdown_cell("### 2.2 Single-Variable: Recipes per Category"))

cells.append(new_code_cell("""\
cat_counts = df['category'].value_counts().sort_values(ascending=True)

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(cat_counts.index, cat_counts.values,
               color=sns.color_palette('Blues_d', len(cat_counts)))
ax.bar_label(bars, padding=3, fontsize=10)
ax.set_title('Number of Recipes per Category', fontsize=14, fontweight='bold')
ax.set_xlabel('Count')
ax.set_ylabel('Category')
ax.set_xlim(0, cat_counts.max() + 20)
plt.tight_layout()
plt.show()

print(cat_counts)"""))

cells.append(new_markdown_cell("""\
**Findings – Category:**
- **Chicken Breast**, **Breakfast**, and **Chicken** dominate with 100+ recipes each.
- **Beverages** and **One Dish Meal** are mid-tier (80–90 recipes).
- The class imbalance across categories means the model must learn category-specific patterns."""))

cells.append(new_markdown_cell("### 2.3 Multi-Variable: Category vs Traffic + Calories by Target"))

cells.append(new_code_cell("""\
cat_traffic = df.groupby('category')['high_traffic'].agg(['sum', 'count'])
cat_traffic.columns = ['high', 'total']
cat_traffic['not_high'] = cat_traffic['total'] - cat_traffic['high']
cat_traffic['high_rate'] = cat_traffic['high'] / cat_traffic['total']
cat_traffic = cat_traffic.sort_values('high_rate', ascending=True)

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Stacked bar
ax = axes[0]
ax.barh(cat_traffic.index, cat_traffic['high'],     color='#2196F3', label='High Traffic')
ax.barh(cat_traffic.index, cat_traffic['not_high'], left=cat_traffic['high'],
        color='#BDBDBD', label='Not High Traffic')
for i, (idx, row) in enumerate(cat_traffic.iterrows()):
    ax.text(row['total'] + 1, i, f"{row['high_rate']:.0%}", va='center', fontsize=9, color='#1565C0')
ax.set_title('High Traffic vs Not High – by Category', fontsize=12, fontweight='bold')
ax.set_xlabel('Number of Recipes')
ax.legend(loc='lower right')
ax.set_xlim(0, cat_traffic['total'].max() + 25)

# Box plot: calories by target
ax2 = axes[1]
g0 = df[df['high_traffic'] == 0]['calories']
g1 = df[df['high_traffic'] == 1]['calories']
bp = ax2.boxplot([g0, g1], labels=['Not High', 'High'], patch_artist=True,
                 medianprops=dict(color='red', linewidth=2))
bp['boxes'][0].set_facecolor('#BDBDBD')
bp['boxes'][1].set_facecolor('#64B5F6')
ax2.set_title('Calorie Distribution by Traffic Class', fontsize=12, fontweight='bold')
ax2.set_xlabel('Traffic Class')
ax2.set_ylabel('Calories')

plt.suptitle('Multi-Variable: Category & Calories vs High Traffic',
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.show()

print("High traffic rate by category:")
print(cat_traffic[['high', 'total', 'high_rate']].sort_values('high_rate', ascending=False))"""))

cells.append(new_markdown_cell("""\
**Findings – Multi-variable:**
- **Potato** (~83 %), **Pork** (~79 %), and **Vegetable** (~76 %) have the highest high-traffic rates — reliable traffic drivers.
- **Breakfast** (~44 %) and **Chicken Breast** (~43 %) are the largest categories but have the lowest traffic conversion — common but not compelling.
- Calorie distributions overlap significantly between High and Not High — calories alone are insufficient to predict traffic; **category is a far stronger signal**.
- The `category_encoded` feature is expected to dominate feature importance in tree-based models."""))

# ── 3. Model Development ────────────────────────────────────────────────────
cells.append(new_markdown_cell("""\
---
## 3. Model Development

**Problem type:** Binary classification (High traffic = 1, Not High = 0)."""))

cells.append(new_code_cell("""\
FEATURE_COLS = ['calories', 'carbohydrate', 'sugar', 'protein', 'servings', 'category_encoded']
TARGET_COL   = 'high_traffic'

X = df[FEATURE_COLS]
y = df[TARGET_COL]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
)
print(f"Train: {len(X_train)} | Test: {len(X_test)}")
print(f"Train high-traffic rate: {y_train.mean():.1%}")
print(f"Test  high-traffic rate: {y_test.mean():.1%}")

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)"""))

cells.append(new_markdown_cell("""\
### 3.1 Baseline Model – Logistic Regression

**Rationale:**
- Standard interpretable baseline for binary classification.
- Coefficients show the direction and magnitude of each feature's influence.
- Appropriate for moderate-sized datasets; low variance reduces overfitting.
- Easy to explain to non-technical stakeholders."""))

cells.append(new_code_cell("""\
lr_model = LogisticRegression(max_iter=1000, random_state=RANDOM_STATE, class_weight='balanced')
lr_model.fit(X_train_scaled, y_train)

y_pred_lr = lr_model.predict(X_test_scaled)
y_prob_lr = lr_model.predict_proba(X_test_scaled)[:, 1]

cv_lr = cross_val_score(lr_model, X_train_scaled, y_train, cv=5, scoring='roc_auc')
print(f"Logistic Regression 5-fold CV ROC-AUC: {cv_lr.mean():.4f} +/- {cv_lr.std():.4f}")"""))

cells.append(new_markdown_cell("""\
### 3.2 Comparison Model – Random Forest

**Rationale:**
- Captures **non-linear interactions** (e.g., high calories AND specific category) that logistic regression cannot.
- Inherently robust to the skewed calorie distribution (uses thresholds, not linear weights).
- Provides feature importance out-of-the-box to confirm which signals drive predictions.
- Ensemble of 200 trees reduces variance vs. a single decision tree."""))

cells.append(new_code_cell("""\
rf_model = RandomForestClassifier(
    n_estimators=200, max_depth=8, min_samples_split=10,
    class_weight='balanced', random_state=RANDOM_STATE, n_jobs=-1
)
rf_model.fit(X_train, y_train)  # no scaling needed for Random Forest

y_pred_rf = rf_model.predict(X_test)
y_prob_rf  = rf_model.predict_proba(X_test)[:, 1]

cv_rf = cross_val_score(rf_model, X_train, y_train, cv=5, scoring='roc_auc')
print(f"Random Forest       5-fold CV ROC-AUC: {cv_rf.mean():.4f} +/- {cv_rf.std():.4f}")"""))

# ── 4. Model Evaluation ─────────────────────────────────────────────────────
cells.append(new_markdown_cell("""\
---
## 4. Model Evaluation

Primary metric: **Precision on High Traffic class** (business requires >= 80 %).  
Also reporting Recall, F1, and ROC-AUC for completeness."""))

cells.append(new_code_cell("""\
def evaluate_model(name, y_true, y_pred, y_prob):
    sep = '=' * 55
    print(sep)
    print(f"  Model: {name}")
    print(sep)
    print(classification_report(y_true, y_pred, target_names=['Not High (0)', 'High (1)']))
    roc = roc_auc_score(y_true, y_prob)
    prec = precision_score(y_true, y_pred, pos_label=1)
    rec  = recall_score(y_true, y_pred, pos_label=1)
    f1   = f1_score(y_true, y_pred, pos_label=1)
    print(f"  ROC-AUC          = {roc:.4f}")
    print(f"  Precision (High) = {prec:.4f}")
    print(f"  Recall    (High) = {rec:.4f}")
    print(f"  F1-Score  (High) = {f1:.4f}")
    return {'model': name, 'roc_auc': roc, 'precision_high': prec,
            'recall_high': rec, 'f1_high': f1}

metrics_lr = evaluate_model('Logistic Regression', y_test, y_pred_lr, y_prob_lr)
print()
metrics_rf = evaluate_model('Random Forest',       y_test, y_pred_rf, y_prob_rf)"""))

cells.append(new_code_cell("""\
# Confusion matrices side-by-side
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
for ax, name, yp in zip(axes,
                         ['Logistic Regression', 'Random Forest'],
                         [y_pred_lr, y_pred_rf]):
    cm = confusion_matrix(y_test, yp)
    disp = ConfusionMatrixDisplay(cm, display_labels=['Not High', 'High'])
    disp.plot(ax=ax, colorbar=False, cmap='Blues')
    ax.set_title(f'Confusion Matrix - {name}', fontsize=11, fontweight='bold')
plt.suptitle('Confusion Matrices', fontsize=13, fontweight='bold', y=1.02)
plt.tight_layout()
plt.show()"""))

cells.append(new_code_cell("""\
# ROC Curves
fig, ax = plt.subplots(figsize=(8, 6))
for name, yp, color in [('Logistic Regression', y_prob_lr, '#1976D2'),
                         ('Random Forest',       y_prob_rf, '#E53935')]:
    fpr, tpr, _ = roc_curve(y_test, yp)
    auc = roc_auc_score(y_test, yp)
    ax.plot(fpr, tpr, color=color, lw=2.5, label=f'{name} (AUC={auc:.3f})')
ax.plot([0,1],[0,1],'k--', lw=1.2, label='Random Baseline')
ax.set_xlabel('False Positive Rate')
ax.set_ylabel('True Positive Rate')
ax.set_title('ROC Curves – Model Comparison', fontsize=13, fontweight='bold')
ax.legend()
ax.grid(alpha=0.4)
plt.tight_layout()
plt.show()"""))

cells.append(new_code_cell("""\
# Metric comparison bar chart
metrics_df = pd.DataFrame([metrics_lr, metrics_rf]).set_index('model')
x = np.arange(len(metrics_df.columns))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 5))
b1 = ax.bar(x - width/2, metrics_df.loc['Logistic Regression'], width,
            label='Logistic Regression', color='#1976D2')
b2 = ax.bar(x + width/2, metrics_df.loc['Random Forest'],       width,
            label='Random Forest',       color='#E53935')
ax.axhline(0.80, color='green', linestyle='--', linewidth=1.8, label='80% Business Target')
ax.set_xticks(x)
ax.set_xticklabels(['ROC-AUC', 'Precision (High)', 'Recall (High)', 'F1 (High)'], fontsize=11)
ax.set_ylim(0, 1.05)
ax.set_ylabel('Score')
ax.set_title('Performance Metrics Comparison', fontsize=13, fontweight='bold')
ax.legend()
for bar in list(b1) + list(b2):
    ax.annotate(f'{bar.get_height():.2f}',
                xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                xytext=(0, 3), textcoords='offset points', ha='center', fontsize=9)
plt.tight_layout()
plt.show()"""))

cells.append(new_code_cell("""\
# Feature importance
fi = pd.Series(rf_model.feature_importances_, index=FEATURE_COLS).sort_values(ascending=True)

fig, ax = plt.subplots(figsize=(8, 5))
fi.plot.barh(ax=ax, color='#1976D2', edgecolor='white')
ax.set_title('Random Forest – Feature Importance', fontsize=13, fontweight='bold')
ax.set_xlabel('Importance Score')
for bar in ax.patches:
    ax.text(bar.get_width() + 0.001, bar.get_y() + bar.get_height()/2,
            f'{bar.get_width():.3f}', va='center', fontsize=9)
plt.tight_layout()
plt.show()

print("Feature importances (descending):")
print(fi.sort_values(ascending=False).round(4).to_string())"""))

# ── 5. Business Metrics ──────────────────────────────────────────────────────
cells.append(new_markdown_cell("""\
---
## 5. Business Metrics

### Metric Definition

The product manager's requirement – "correctly predict high traffic 80% of the time" – maps to:

> **Precision on the High Traffic class** = TP / (TP + FP)

- **TP** = recipes predicted High that truly drove high traffic
- **FP** = recipes predicted High that did NOT drive high traffic (wasted homepage slot)

Precision is the right metric here because each homepage slot is a limited resource. A false positive wastes that slot on an unpopular recipe and fails to capture the 40% traffic uplift.

**Secondary metric:** Recall on High Traffic class – we still want to catch enough high-traffic recipes, so recall should ideally stay above 70%."""))

cells.append(new_code_cell("""\
biz = pd.DataFrame({
    'Model':            ['Logistic Regression', 'Random Forest'],
    'Precision (High)': [precision_score(y_test, y_pred_lr), precision_score(y_test, y_pred_rf)],
    'Recall (High)':    [recall_score(y_test, y_pred_lr),    recall_score(y_test, y_pred_rf)],
    'F1 (High)':        [f1_score(y_test, y_pred_lr),        f1_score(y_test, y_pred_rf)],
    'ROC-AUC':          [roc_auc_score(y_test, y_prob_lr),   roc_auc_score(y_test, y_prob_rf)]
}).set_index('Model').round(4)

print("Business Metric Summary:")
print(biz.to_string())

print("\\n80% Precision Target Met?")
for mdl in biz.index:
    p = biz.loc[mdl, 'Precision (High)']
    status = "YES" if p >= 0.80 else "NO"
    print(f"  {mdl}: {p:.2%} -> {status}")"""))

cells.append(new_code_cell("""\
# Estimate deployment value
best = biz['Precision (High)'].idxmax()
p = biz.loc[best, 'Precision (High)']
r = biz.loc[best, 'Recall (High)']
total = len(df)
actual_high = int(y.sum())
predicted_high = int(actual_high / r) if r > 0 else 0
correct_pred   = int(predicted_high * p)

print(f"Best model              : {best}")
print(f"Precision  (High)       : {p:.2%}")
print(f"Recall     (High)       : {r:.2%}")
print(f"Total recipes           : {total}")
print(f"Actual high-traffic     : {actual_high}  ({actual_high/total:.1%})")
print(f"Est. homepage picks/run : ~{predicted_high}")
print(f"Est. correct high picks : ~{correct_pred}  ({correct_pred/predicted_high:.0%} correct)")"""))

# ── 6. Summary ───────────────────────────────────────────────────────────────
cells.append(new_markdown_cell("""\
---
## 6. Final Summary & Recommendations

### What We Built
Two binary classifiers to predict whether a recipe drives high traffic:
1. **Logistic Regression** – interpretable linear baseline
2. **Random Forest** – non-linear ensemble, better suited to this dataset

### Problem Type
Binary classification: High traffic (1) vs Not High traffic (0).

### Model Comparison
The performance summary above shows that **Random Forest** achieves higher precision and ROC-AUC than Logistic Regression, making it the recommended production model.

### Business Metric to Monitor
- **Primary KPI:** Precision on High Traffic class >= 80 % in production.
- **Secondary KPI:** Recall on High Traffic class >= 70 % (avoid leaving good recipes out).
- **Review cadence:** Re-evaluate monthly as new data is collected.

### Key Findings
- **Category is the dominant predictor** – Potato, Pork, and Vegetable recipes are historically the most reliable traffic drivers.
- **Breakfast and Chicken Breast** have many recipes but low traffic conversion; their prominence on the homepage should be reconsidered.
- Nutritional features (calories, carbohydrate, protein, sugar) have moderate importance – they add signal but are not decisive alone.

### Recommendations
1. **Deploy the Random Forest model** to score incoming recipes. Use the predicted probability (0–1) to rank recipes rather than just binary labels, giving editors a priority list.
2. **Prioritise Potato, Pork, Vegetable, and One Dish Meal categories** in homepage selection – these deliver the highest traffic rates.
3. **Investigate Breakfast and Chicken Breast** recipe quality: despite volume, traffic conversion is low. Consider editorial curation or recipe revamps.
4. **Collect richer data:** engagement signals (clicks, time on page, shares, save rate) would substantially improve model performance. Current features are recipe metadata only.
5. **A/B test** model-driven selection against current editorial selection over 4–6 weeks to quantify the traffic uplift before full rollout.
6. **Retrain quarterly** to capture seasonal trends (e.g., holiday baking, summer salads).

---
*Report completed – DataCamp Data Scientist Professional Practical Exam, Recipe Site Traffic 2212.*"""))

# ── Build notebook ──────────────────────────────────────────────────────────
nb = new_notebook(cells=cells)
nb.metadata['kernelspec'] = {
    "display_name": "Python 3 (ipykernel)",
    "language": "python",
    "name": "python3"
}
nb.metadata['language_info'] = {
    "codemirror_mode": {"name": "ipython", "version": 3},
    "file_extension": ".py",
    "mimetype": "text/x-python",
    "name": "python",
    "nbconvert_exporter": "python",
    "pygments_lexer": "ipython3",
    "version": "3.8.10"
}

output_path = r'c:\Su\su\AI_ML_andDataScienceTutorial\6.datatcamp\workspace (1)\workspace\notebook.ipynb'
with open(output_path, 'w', encoding='utf-8') as f:
    nbformat.write(nb, f)

print(f"Notebook written to: {output_path}")
print(f"Total cells: {len(nb.cells)}")
code_count = sum(1 for c in nb.cells if c.cell_type == 'code')
md_count   = sum(1 for c in nb.cells if c.cell_type == 'markdown')
print(f"  Code cells    : {code_count}")
print(f"  Markdown cells: {md_count}")
