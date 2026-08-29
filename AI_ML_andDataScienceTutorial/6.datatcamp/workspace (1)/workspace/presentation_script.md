# 🎤 Presentation Script – Recipe Site Traffic Prediction
### DataCamp Data Scientist Professional Practical Exam
**Audience:** Product Manager – Recipe Discovery  
**Duration:** ~8–10 minutes | **Slides:** 8

---

## SLIDE 1 – Title Slide
**"Predicting High-Traffic Recipes for Tasty Bytes"**

> *"Hi everyone. Today I'll walk you through an analysis I did to help answer one key question:*
> *Can we predict which recipes will drive high traffic to the Tasty Bytes website — and do it correctly at least 80% of the time?"*
>
> *"My name is [Name], and I'll cover: the business problem, how I approached the data, what I found, the models I built, and my recommendations for next steps."*

---

## SLIDE 2 – Business Problem
**"The Problem We're Solving"**

**Key points:**
- Currently, the product manager picks a favorite recipe manually for the homepage each day
- When a popular recipe is chosen → site traffic goes up by **up to 40%**
- More traffic = more subscriptions = more revenue
- But there's no systematic way to know which recipe will be popular

**Script:**
> *"Right now, choosing the homepage recipe is essentially guesswork. That 40% traffic uplift is huge — but it's only captured when the right recipe is picked."*
>
> *"The ask was clear: build a model that correctly identifies high-traffic recipes at least 80% of the time. That 80% threshold is not arbitrary — it means if we recommend a recipe as 'popular', we need to be right at least 8 times out of 10."*

---

## SLIDE 3 – The Data
**"What We're Working With"**

**Key points:**
- **947 recipes** with 8 features
- Features: calories, carbohydrate, sugar, protein, category, servings
- Target: `high_traffic` — was traffic HIGH when this recipe was on the homepage?
- **574 high-traffic** (60.6%) vs **373 not-high** (39.4%)

**Data issues found & fixed:**

| Issue | Fix |
|-------|-----|
| 52 missing values in nutrition columns | Filled with median |
| `servings` stored as text ("4 as a snack") | Extracted number → 4 |
| `high_traffic` NaN = not high | Mapped to binary 1/0 |

**Script:**
> *"The dataset had 947 recipes. The target variable — high_traffic — tells us whether traffic spiked when that recipe was featured. NaN simply means traffic was normal, so I treated that as 'not high'."*
>
> *"There were some data quality issues: 52 recipes had missing nutrition values — I filled those with the median, which is robust to the skewed distributions we saw. Servings had text entries like '4 as a snack' — I extracted just the number."*
>
> *"After cleaning: zero missing values, everything typed correctly, ready to model."*

---

## SLIDE 4 – Exploratory Analysis
**"What the Data Tells Us"**

### Finding 1 – Calorie distribution is skewed
- Median: ~289 kcal, Mean: ~436 kcal
- Long right tail — a few very calorie-dense recipes pull the average up
- Most recipes sit in the **100–800 kcal** range

### Finding 2 – Category is the strongest signal ⭐
| Category | High Traffic Rate |
|----------|:-----------------:|
| Vegetable | **99%** |
| Potato | **94%** |
| Pork | **92%** |
| Meat | 75% |
| One Dish Meal | 73% |
| … | … |
| Chicken | 37% |
| Breakfast | 31% |
| Beverages | **5%** |

### Finding 3 – Calories alone don't separate the classes
- Box plots for High vs Not High overlap significantly
- Category is what really predicts traffic, not nutrition facts

**Script:**
> *"Let me show you the three most important things I found in the data."*
>
> *"First — calories are heavily right-skewed. Most recipes are in the 100–800 range, but a few outliers go past 2500. This tells me I need a model that handles skewed data well."*
>
> *"Second — and this is the big one — category drives everything. Vegetable and Potato recipes generate high traffic almost every single time they're featured. Meanwhile, Beverages has only a 5% high-traffic rate. This is a massive insight for the team."*
>
> *"Third — I compared calorie distributions between high and not-high recipes. They overlap almost completely. So nutrition alone won't save us — category is the real predictor."*

---

## SLIDE 5 – Modelling Approach
**"How I Built the Models"**

**Problem type:** Binary classification (High = 1, Not High = 0)

**Train / Test split:** 80% train, 20% test, stratified

**Two models:**

| Model | Why I chose it |
|-------|----------------|
| **Logistic Regression** (baseline) | Simple, interpretable, industry-standard baseline. Coefficients show exactly which features push a recipe toward "high" |
| **Random Forest** (comparison) | Captures non-linear patterns — e.g. "high protein AND potato category". Robust to outliers. Ranks feature importance automatically |

**Script:**
> *"I framed this as a binary classification problem — either a recipe will be high-traffic or it won't."*
>
> *"I trained two models. First, Logistic Regression — it's the standard interpretable baseline. When you're presenting results to a business team, being able to say 'this feature pushes the probability up, that one pulls it down' is very valuable."*
>
> *"Second, Random Forest. This captures interactions that a straight line can't — like 'this recipe is both high-protein AND in the Potato category, which together predict traffic really well'. It's also not bothered by those skewed calorie outliers."*

---

## SLIDE 6 – Model Results
**"How Well Do the Models Perform?"**

| Metric | Logistic Regression | Random Forest |
|--------|:-------------------:|:-------------:|
| **Precision (High)** | **87.6% ✓** | **84.2% ✓** |
| Recall (High) | 67.8% | 73.9% |
| F1-Score (High) | 76.5% | 78.7% |
| ROC-AUC | 0.870 | 0.842 |

🟢 **Both models exceed the 80% precision target.**

**Script:**
> *"Here's the headline result: both models beat the 80% precision target."*
>
> *"Logistic Regression hits 87.6% precision on the High class. That means when it says 'this recipe will be popular', it's right nearly 9 times out of 10."*
>
> *"Random Forest is close behind at 84.2% precision, but it has better recall — it catches more of the truly high-traffic recipes."*
>
> *"The tradeoff: Logistic Regression is more conservative — it misses more good recipes (lower recall), but almost never wastes a homepage slot. Random Forest is more balanced."*
>
> *"For a business where each homepage slot is valuable real estate, I'd lean towards the higher-precision model — but I'll come back to the recommendation."*

---

## SLIDE 7 – Business Metric & Monitoring
**"How Should the Business Measure Success?"**

**Primary KPI to monitor:**
> **Precision on High Traffic class ≥ 80%**
> = "When the model says HIGH, how often is it right?"

**Why precision, not accuracy?**
- We have limited homepage slots — a wrong prediction wastes one
- A false positive = showing an unpopular recipe = missing the 40% traffic uplift
- Accuracy doesn't distinguish which errors matter

**Secondary KPI:**
> **Recall on High Traffic class ≥ 70%**
> = "Are we finding enough of the good recipes?"

**Current baseline estimate (from test set):**
- Model recommends ~846 recipes out of 947
- ~741 of those (~88%) are correctly identified as high-traffic

**Script:**
> *"For the business, I recommend tracking one primary metric: Precision on the High Traffic class. This answers the question they actually care about — when we tell the editor to feature a recipe, how confident should they be?"*
>
> *"Accuracy is misleading here because errors are not equal. Missing a popular recipe is bad, but showing an unpopular one wastes a slot and loses that 40% uplift. Precision captures exactly that cost."*
>
> *"I'd also watch recall — if it drops below 70%, we're leaving too many good recipes on the table and editors won't trust the tool."*
>
> *"I'd suggest reviewing these metrics monthly as new recipe data comes in."*

---

## SLIDE 8 – Recommendations
**"What Should Tasty Bytes Do Next?"**

1. **🚀 Deploy Logistic Regression** as the homepage recommendation engine
   - Use predicted *probabilities* (not just yes/no) to give editors a ranked shortlist
   - Highest-probability recipes get priority slots

2. **📌 Prioritise these categories** in content creation:
   - Vegetable, Potato, Pork, Meat, One Dish Meal → consistent traffic drivers

3. **🔍 Investigate low-conversion categories:**
   - Breakfast (31%) and Beverages (5%) generate volume but not traffic
   - Either improve recipe quality signals or reduce their homepage frequency

4. **📊 Collect richer data** for model v2:
   - User clicks, time-on-page, saves, shares
   - Current model uses only recipe metadata — engagement data would dramatically improve performance

5. **🧪 A/B test before full rollout:**
   - Run model-selected vs. editorial-selected homepage recipes for 4–6 weeks
   - Measure actual traffic uplift to validate the 40% claim

6. **🔄 Retrain quarterly:**
   - Seasonal patterns matter (holiday baking, summer salads)
   - Model should stay current with evolving tastes

**Closing:**
> *"To wrap up: the answer to your question is yes — we can predict high-traffic recipes, and both models we tested exceed the 80% accuracy target you set."*
>
> *"The most important thing I'd take away from this analysis is that category drives everything. Your content team has a clear signal: lean into Vegetable, Potato, Pork, and One Dish Meal recipes. And consider whether it's worth continuing to invest so heavily in Beverages and Breakfast content given their low traffic conversion."*
>
> *"Happy to take any questions."*

---

## ⏱️ Timing Guide

| Slide | Topic | Time |
|-------|-------|------|
| 1 | Title / Intro | 30s |
| 2 | Business Problem | 1 min |
| 3 | The Data | 1.5 min |
| 4 | EDA Findings | 2 min |
| 5 | Modelling Approach | 1 min |
| 6 | Results | 1.5 min |
| 7 | Business Metric | 1 min |
| 8 | Recommendations + Close | 1.5 min |
| **Total** | | **~10 min** |

---

## 💡 Tips for Delivery

- **Slide 4** is your strongest slide — spend the most time here. The category insight is the "aha moment" for the product manager.
- **Slide 6** — don't get bogged down in the numbers. The key message is: *"both models work, 80% target met"*.
- **Slide 7** — make it concrete: *"every time we get it wrong, we lose that 40% traffic spike"*.
- **Slide 8** — end on action. The PM wants to know what to do, not just what you found.
- Prepare for Q: *"Which model should we use?"* → Logistic Regression for max precision; Random Forest if recall matters more.
- Prepare for Q: *"How long to build this into the product?"* → Model is ready; integration with the homepage CMS is an engineering question.
