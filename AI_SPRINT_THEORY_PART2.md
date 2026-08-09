# 📚 Tổng Hợp Lý Thuyết - AI Sprint (Phần 2)
## Tiếp Theo Phần 3: AI/ML & Phần 4: Product/Ethics

---

# PHẦN 3: AI/ML (30 câu) - Tiếp theo

## 3.1 ML Foundations (Tiếp)

### Supervised vs Unsupervised vs Reinforcement
```
SUPERVISED LEARNING (có label):
- Regression: Dự đoán giá nhà, nhiệt độ
- Classification: Phân loại email spam, bệnh
- Cần: Dữ liệu có nhãn (X, y)
- Ví dụ: (ảnh, "mèo"), (text, "spam")

UNSUPERVISED LEARNING (không label):
- Clustering: Phân nhóm khách hàng
- Dimensionality Reduction: PCA
- Cần: Chỉ dữ liệu X (không có y)
- Tự tìm pattern

REINFORCEMENT LEARNING:
- Agent học qua reward/punishment
- Ứng dụng: Game AI, robotics
- Không thuộc phạm vi thi chính
```

### Train/Validation/Test Split
```
Dataset chia thành 3 phần:

TRAIN (60-80%):
- Fit/train model
- Update parameters

VALIDATION (10-20%):
- Tune hyperparameters
- Model selection
- Early stopping
- KHÔNG dùng để update model parameters

TEST (10-20%):
- Đánh giá cuối cùng
- Báo cáo performance
- Chỉ dùng 1 LẦN ở cuối
- KHÔNG bao giờ dùng để tune

⚠️ QUAN TRỌNG:
- Fit scaler CHỈ trên train
- Validation để chọn model
- Test giữ độc lập tuyệt đối
```

### Overfitting vs Underfitting
```
OVERFITTING (học quá, generalize kém):
Dấu hiệu:
- Train accuracy rất cao (>95%)
- Validation accuracy thấp hơn nhiều
- Khoảng cách train-val lớn

Nguyên nhân:
- Model quá phức tạp
- Training quá lâu
- Dữ liệu ít

Giải pháp:
- Regularization (L1, L2, dropout)
- Early stopping
- More data
- Giảm model complexity

UNDERFITTING (học kém):
Dấu hiệu:
- Train accuracy thấp
- Validation accuracy cũng thấp
- Cả hai gần nhau nhưng đều thấp

Nguyên nhân:
- Model quá đơn giản
- Features không đủ tốt
- Training chưa đủ

Giải pháp:
- Tăng model complexity
- Thêm features
- Train lâu hơn
```

### Bias-Variance Tradeoff
```
HIGH BIAS (underfitting):
- Model quá đơn giản
- Không capture pattern
- Train error cao

HIGH VARIANCE (overfitting):
- Model quá phức tạp
- Learn noise
- Generalization kém

SWEET SPOT:
- Balance bias và variance
- Good generalization
```

### Data Leakage
```
Xảy ra khi: thông tin từ test "rò" vào training

Ví dụ SAI:
# ❌ Fit scaler trên toàn bộ data
scaler.fit(all_data)  # LEAK!
X_train, X_test = split(all_data)
X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)

Ví dụ ĐÚNG:
# ✓ Fit scaler CHỈ trên train
X_train, X_test = split(all_data)
scaler.fit(X_train)  # OK
X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)

Các dạng leakage khác:
- Dùng feature biết sau thời điểm prediction
- Dùng target để tạo feature
- Include test trong any preprocessing
```

### Cross-Validation
```
K-Fold CV (k=5):
┌────────────────────────────┐
│ Train Train Train Train Val │ Fold 1
│ Train Train Train Val Train │ Fold 2
│ Train Train Val Train Train │ Fold 3
│ Train Val Train Train Train │ Fold 4
│ Val Train Train Train Train │ Fold 5
└────────────────────────────┘

Mỗi fold làm validation 1 lần
Score cuối = mean của 5 scores

Ứng dụng:
- Hyperparameter tuning
- Model selection
- Ước lượng performance ổn định hơn

⚠️ CV trên train/dev, KHÔNG bao gồm test set
```

---

## 3.2 Evaluation Metrics (QUAN TRỌNG NHẤT!)

### Confusion Matrix
```
             Predicted
             Pos    Neg
Actual Pos   TP     FN    ← Actual Positive
Actual Neg   FP     TN    ← Actual Negative
             ↑      ↑
        Pred Pos  Pred Neg

TP (True Positive): Dự đoán dương, thực tế dương ✓
TN (True Negative): Dự đoán âm, thực tế âm ✓
FP (False Positive): Dự đoán dương, thực tế âm ✗ (Type I error)
FN (False Negative): Dự đoán âm, thực tế dương ✗ (Type II error)

Ví dụ:
y_true = [1, 0, 1, 1, 0, 0, 1, 0]
y_pred = [1, 0, 1, 0, 0, 1, 1, 0]

TP = 3 (vị trí 0, 2, 6)
TN = 3 (vị trí 1, 4, 7)
FP = 1 (vị trí 5: dự đoán 1, thật 0)
FN = 1 (vị trí 3: dự đoán 0, thật 1)
```

### Accuracy
```
Accuracy = (TP + TN) / (TP + TN + FP + FN)
         = Correct / Total

Ví dụ:
TP=3, TN=3, FP=1, FN=1
Accuracy = (3+3)/(3+3+1+1) = 6/8 = 0.75

⚠️ HẠN CHẾ:
Với imbalanced data, accuracy lừa dối!

Ví dụ: 99% không bệnh, 1% bệnh
Model dự đoán: "Tất cả không bệnh"
Accuracy = 99%  ← Trông tốt!
Nhưng: Recall bệnh = 0% ← Thực tế tệ!
```

### Precision
```
Precision = TP / (TP + FP)
          = TP / (Predicted Positive)

Ý nghĩa: Trong các dự đoán DƯƠNG, bao nhiêu % ĐÚNG?

Ví dụ:
TP=3, FP=1
Precision = 3/(3+1) = 0.75 (75%)
→ 75% dự đoán dương là đúng

Khi nào quan trọng:
- False positive tốn kém
- Ví dụ: Spam filter (email quan trọng bị đánh spam)
- Medical test (cần tránh diagnose sai bệnh)
```

### Recall (Sensitivity)
```
Recall = TP / (TP + FN)
       = TP / (Actual Positive)

Ý nghĩa: Trong các ca thật DƯƠNG, phát hiện được bao nhiêu %?

Ví dụ:
TP=3, FN=1
Recall = 3/(3+1) = 0.75 (75%)
→ Phát hiện 75% ca dương thực tế

Khi nào quan trọng:
- False negative tốn kém
- Ví dụ: Cancer detection (bỏ sót ca ung thư nguy hiểm!)
- Fraud detection (bỏ sót gian lận)
```

### Specificity
```
Specificity = TN / (TN + FP)
            = TN / (Actual Negative)

Ý nghĩa: Trong các ca thật ÂM, phát hiện đúng bao nhiêu %?

Ví dụ:
TN=3, FP=1
Specificity = 3/(3+1) = 0.75 (75%)
→ Nhận diện đúng 75% ca âm thực tế
```

### F1-Score
```
F1 = 2 × (Precision × Recall) / (Precision + Recall)
   = 2TP / (2TP + FP + FN)

Harmonic mean của Precision và Recall

Ví dụ:
Precision = 0.8, Recall = 0.6
F1 = 2 × (0.8 × 0.6) / (0.8 + 0.6)
   = 0.96 / 1.4 = 0.686

Khi nào dùng:
- Cần cân bằng Precision và Recall
- Imbalanced data
- Single metric thay vì 2 metrics
```

### F-beta Score
```
F_β = (1 + β²) × (Precision × Recall) / (β² × Precision + Recall)

β < 1: Favor precision (giảm FP quan trọng)
β = 1: F1-score (cân bằng)
β > 1: Favor recall (giảm FN quan trọng)

F2-score: β=2, favor recall
F0.5-score: β=0.5, favor precision
```

### Macro vs Micro Averaging (Multiclass)
```
MACRO:
- Tính metric cho từng class
- Average (mỗi class trọng số bằng nhau)
- Good với balanced classes

MICRO:
- Gộp tất cả TP/TN/FP/FN
- Tính metric trên gộp
- Bị chi phối bởi majority class

Ví dụ:
Class A: 100 samples, F1=0.9
Class B: 10 samples, F1=0.5

Macro-F1 = (0.9 + 0.5) / 2 = 0.7
Micro-F1 ≈ 0.87 (bị A chi phối)
```

### ROC & AUC
```
ROC (Receiver Operating Characteristic):
- Plot: True Positive Rate vs False Positive Rate
- Thay đổi threshold từ 0 → 1

AUC (Area Under Curve):
- Diện tích dưới ROC curve
- Range: 0 đến 1
- AUC = 0.5: Random classifier
- AUC = 1.0: Perfect classifier
- AUC > 0.8: Good model

Ưu điểm:
- Threshold-independent
- Good với imbalanced data
```

### Threshold Tuning
```
Default threshold = 0.5:
If P(positive) > 0.5 → predict positive

Giảm threshold (0.5 → 0.3):
- More predictions → positive
- Recall ↑ (catch more positives)
- Precision ↓ (more false positives)
- FN ↓, FP ↑

Tăng threshold (0.5 → 0.7):
- Fewer predictions → positive
- Precision ↑ (fewer false positives)
- Recall ↓ (miss some positives)
- FP ↓, FN ↑

Chọn threshold dựa trên business requirement
```

### Code: Tính Metrics Bằng NumPy
```python
import numpy as np

y_true = np.array([1, 0, 1, 1, 0, 0, 1, 0])
y_pred = np.array([1, 0, 1, 0, 0, 1, 1, 0])

# Confusion matrix
tp = np.sum((y_true == 1) & (y_pred == 1))
tn = np.sum((y_true == 0) & (y_pred == 0))
fp = np.sum((y_true == 0) & (y_pred == 1))
fn = np.sum((y_true == 1) & (y_pred == 0))

# Metrics
accuracy = (tp + tn) / len(y_true)
precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0

print(f"TP={tp}, TN={tn}, FP={fp}, FN={fn}")
print(f"Accuracy: {accuracy:.3f}")
print(f"Precision: {precision:.3f}")
print(f"Recall: {recall:.3f}")
print(f"F1: {f1:.3f}")
print(f"Specificity: {specificity:.3f}")
```

---

## 3.3 ML Algorithms

### Linear Regression
```
y = β₀ + β₁x₁ + β₂x₂ + ... + βₙxₙ

Minimize: MSE = (1/n) Σ(y - ŷ)²

Assumptions:
- Linear relationship
- Normally distributed errors
- Homoscedasticity (constant variance)
- Independent observations

Evaluation:
- R² (coefficient of determination)
- MSE, RMSE, MAE
```

### Logistic Regression
```
P(y=1) = σ(z) = 1 / (1 + e^(-z))
z = β₀ + β₁x₁ + ... + βₙxₙ

Sigmoid function σ maps (-∞, +∞) → (0, 1)

Output: Probability [0, 1]
Decision: P > 0.5 → class 1

Loss: Binary cross-entropy
```

### Decision Trees
```
Splitting criteria:
- Gini impurity
- Entropy/Information gain

Pros:
- Interpretable
- Handle non-linear
- No feature scaling needed

Cons:
- Overfit easily (nếu sâu)
- Unstable (small data change → different tree)

Regularization:
- max_depth
- min_samples_split
- min_samples_leaf
```

### K-Nearest Neighbors (KNN)
```
Phân loại based on k nearest neighbors

Steps:
1. Tính khoảng cách từ test point đến all training points
2. Lấy k neighbors gần nhất
3. Vote: Majority class (classification) hoặc mean (regression)

Hyperparameters:
- k: số neighbors (thường lẻ để tránh tie)
- Distance metric: Euclidean, Manhattan, Minkowski

Pros:
- Simple, no training
- Non-linear boundaries

Cons:
- Slow với large dataset
- Curse of dimensionality
- Cần feature scaling
```

### K-Means Clustering
```
Unsupervised learning

Algorithm:
1. Chọn k centroids ngẫu nhiên
2. Assign each point → nearest centroid
3. Update centroids = mean of assigned points
4. Repeat 2-3 until convergence

Hyperparameters:
- k: số clusters
- Initialization method

Objective: Minimize within-cluster sum of squares

Evaluation:
- Elbow method (plot k vs inertia)
- Silhouette score
```

### PCA (Principal Component Analysis)
```
Dimensionality reduction

Steps:
1. Standardize data (mean=0, std=1)
2. Compute covariance matrix
3. Compute eigenvectors và eigenvalues
4. Sort eigenvectors by eigenvalue (giảm dần)
5. Select top k components
6. Project data onto k components

Ứng dụng:
- Visualization (reduce to 2D/3D)
- Feature extraction
- Noise reduction
- Speed up training

⚠️ Components không dễ interpret như features gốc
```

---

## 3.4 Deep Learning & Neural Networks

### Neural Network Basics
```
Architecture:
Input layer → Hidden layers → Output layer

Forward pass:
z = Wx + b      (linear)
a = σ(z)        (activation)

Backpropagation:
Compute gradients via chain rule
Update weights: W = W - η∇L
```

### Activation Functions
```
SIGMOID: σ(x) = 1/(1+e^(-x))
- Range: (0, 1)
- Problem: Vanishing gradient

RELU: f(x) = max(0, x)
- Most popular for hidden layers
- Fast, simple
- Problem: Dying ReLU (neurons always 0)

LEAKY RELU: f(x) = max(0.01x, x)
- Fix dying ReLU

TANH: tanh(x) = (e^x - e^(-x))/(e^x + e^(-x))
- Range: (-1, 1)
- Better than sigmoid (centered at 0)

SOFTMAX: For output layer multiclass
- σ(z)ᵢ = e^(zᵢ) / Σe^(zⱼ)
- Outputs sum to 1 (probability distribution)
```

### Regularization
```
DROPOUT:
- Randomly drop p% neurons during training
- Inference: Use all neurons (với scaling)
- Prevent co-adaptation
- p típico: 0.2-0.5

BATCH NORMALIZATION:
- Normalize activations layer-wise
- Mean=0, Variance=1
- Giúp training nhanh hơn, stable hơn
- Có learnable parameters (γ, β)

L2 REGULARIZATION:
- Add λΣw² to loss
- Penalize large weights

EARLY STOPPING:
- Monitor validation loss
- Stop when validation starts increasing
```

### Optimizers
```
SGD (Stochastic Gradient Descent):
w = w - η∇L

MOMENTUM:
v = βv + ∇L
w = w - ηv
→ Accelerate in relevant direction

ADAM (Adaptive Moment Estimation):
- Combines momentum + adaptive learning rate
- Most popular default choice
- Hyperparameters: lr, β₁, β₂
```

### Training Issues
```
VANISHING GRADIENT:
- Gradient → 0 qua nhiều layers
- Sigmoid/tanh saturation
- Solution: ReLU, Batch Norm, Residual connections

EXPLODING GRADIENT:
- Gradient → ∞
- Solution: Gradient clipping, proper initialization

OVERFITTING:
- Solution: Dropout, L2, Early stopping, More data

UNDERFITTING:
- Solution: Deeper network, More neurons, Train longer
```

---

## 3.5 Transfer Learning & GenAI

### Transfer Learning
```
Idea: Reuse pretrained model

Steps:
1. Load pretrained model (trained on large dataset)
2. Freeze early layers (keep low-level features)
3. Replace/fine-tune later layers for new task
4. Train on new dataset

Ứng dụng:
- Computer Vision: ImageNet pretrained
- NLP: BERT, GPT pretrained

Benefits:
- Less data needed
- Faster training
- Better performance
```

### Fine-Tuning Strategies
```
FREEZE ALL + NEW HEAD:
- Freeze all pretrained layers
- Add new output layer
- Train only new layer
- Good: Very little data

FREEZE SOME + FINE-TUNE:
- Freeze early layers
- Fine-tune later layers
- Good: Moderate data

FINE-TUNE ALL:
- Start from pretrained weights
- Update all layers (small learning rate)
- Good: Large dataset, different domain
```

### LoRA (Low-Rank Adaptation)
```
Parameter-Efficient Fine-Tuning (PEFT)

Idea:
- Freeze original model weights W
- Learn small matrices ΔW = BA (low-rank)
- Updated weight: W' = W + ΔW

Benefits:
- Much fewer parameters to train
- Less memory
- Faster training
- Can swap adapters for different tasks
```

### Catastrophic Forgetting
```
Problem: Model forgets old tasks when learning new

Solutions:
- Replay old data
- Regularization (EWC)
- Progressive networks
- Use adapters (LoRA)
```

### Large Language Models (LLMs)
```
Architecture: Transformer (attention mechanism)

Key concepts:
- Tokens: Text → integer IDs
- Embeddings: Tokens → dense vectors
- Context window: Max tokens model can process
- Temperature: Controls randomness (0=greedy, high=creative)

Fine-tuning vs Prompting:
- Prompting: No weight updates, just clever input
- Fine-tuning: Update weights on task data
```

### Prompt Engineering
```
SYSTEM PROMPT:
Set behavior/persona

USER PROMPT:
Your question/instruction

FEW-SHOT LEARNING:
Provide examples in prompt

CHAIN-OF-THOUGHT:
Ask model to "think step by step"

TIPS:
- Be specific and clear
- Provide context
- Break complex tasks
- Iterate and refine
```

### RAG (Retrieval Augmented Generation)
```
Pipeline:
1. RETRIEVAL: Search relevant docs from knowledge base
2. CONTEXT: Add retrieved docs to prompt
3. GENERATION: LLM generates answer with context

Components:
- Vector database (embeddings)
- Retriever (semantic search)
- Generator (LLM)

Benefits:
- Up-to-date information
- Reduce hallucination
- Citations/grounding

Challenges:
- Retrieval quality
- Context length limits
- Latency
```

---

# PHẦN 4: AI PRODUCT & ETHICS (20 câu)

## 4.1 AI Product Building

### Problem Framing
```
Before building model, define:

1. WHO: End user, decision maker
2. WHAT: Decision to make, action to take
3. WHEN: Timing, frequency
4. WHY: Success metrics, business value
5. HOW: Current process (baseline)

RED FLAGS:
- "Use AI to increase revenue" (too vague)
- No clear user
- No measurable outcome
- No baseline to beat
```

### Baseline Importance
```
Always start with simple baseline:

- Majority class classifier
- Random classifier
- Current manual process
- Simple heuristic

Why:
- Measure if ML adds value
- Avoid unnecessary complexity
- Quick reality check
- Communicate value to stakeholders
```

### Build vs Buy
```
BUILD when:
- Unique problem/data
- Core competitive advantage
- Have ML expertise
- Long-term investment

BUY when:
- Standard problem (email spam, sentiment)
- Limited resources
- Fast time-to-market
- Not core business
```

### MVP (Minimum Viable Product)
```
HYPOTHESIS-DRIVEN:
1. Form hypothesis about user problem
2. Design simplest test
3. Build MVP
4. Measure outcome
5. Learn & iterate

MVP TYPES:

CONCIERGE:
- Human does AI's job manually
- Validate demand before building
- Example: Manual recommendations before ML

WIZARD OF OZ:
- Looks automated, humans behind scenes
- Test UX before building ML
- Example: Chatbot backed by humans

PROTOTYPE:
- Working but limited-scope model
- Single use case
- Small user group
```

### Success Metrics
```
NORTH STAR METRIC:
Single metric that matters most

Examples:
- E-commerce: Revenue per user
- Social: Daily active users
- SaaS: Monthly recurring revenue

GUARDRAIL METRICS:
Protect against unintended harm

Examples:
- Latency < 200ms
- False positive rate < 5%
- User satisfaction > 4/5
```

### A/B Testing
```
Compare two versions:

CONTROL (A): Baseline
TREATMENT (B): New model

Steps:
1. Random split users
2. Measure metric for both
3. Statistical test (t-test)
4. Decision: Ship B or keep A

Requirements:
- Sufficient sample size
- Random assignment
- Single metric focus
- Statistical significance
```

### Model Lifecycle
```
STAGES:

1. DISCOVERY & FRAMING
   - Problem definition
   - Feasibility study
   - Baseline

2. DATA STRATEGY
   - Collection plan
   - Labeling strategy
   - Quality checks

3. PROTOTYPE
   - Experiment tracking
   - Model development
   - Offline evaluation

4. PRODUCTION
   - Deployment
   - Monitoring
   - A/B testing

5. MAINTENANCE
   - Drift detection
   - Retraining
   - Feedback loop
```

### Monitoring & Drift
```
DATA DRIFT:
- Input distribution changes
- X different from training

CONCEPT DRIFT:
- Relationship X→y changes
- Model predictions degrade

MONITORING:
- Track prediction distribution
- Compare to training stats
- Alert on significant shift
- Automatic retraining triggers
```

### Feature Flags
```
Control feature rollout:

- Gradual rollout (1% → 10% → 100%)
- A/B testing
- Kill switch (disable quickly if issue)
- User targeting (beta users)

Benefits:
- Safe deployment
- Fast rollback
- Experimentation
```

---

## 4.2 Enterprise AI

### RAG for Enterprise
```
SECURITY REQUIREMENTS:

SSO (Single Sign-On):
- Corporate login (Google, Azure AD)
- Centralized access control

ACL (Access Control List):
- Check permissions BEFORE retrieval
- User can only see authorized docs
- Filter search results by permission

DENY-BY-DEFAULT:
- Explicit permission required
- No access unless granted

CITATION:
- Every answer links to source
- User can verify information
- Build trust

AUDIT TRAIL:
- Log all queries
- Track doc access
- Compliance requirements
```

### Cross-Department Data Leak
```
Problem: User A (Dept X) sees Dept Y's confidential data

Testing:
- Create test users per department
- Query confidential topics
- Verify ACL enforcement
- Test edge cases (shared projects)

Prevention:
- ACL at document level
- Filter BEFORE retrieval
- Regular security audits
- Penetration testing
```

### Staged Rollout
```
PHASES:

1. INTERNAL ALPHA (Dev team)
   - Basic functionality
   - Find obvious bugs

2. INTERNAL BETA (Company employees)
   - Dogfooding
   - Real usage patterns
   - Feedback collection

3. EXTERNAL BETA (Selected users)
   - Limited group
   - Close monitoring
   - Feature flags enabled

4. GRADUAL PUBLIC (1% → 10% → 50% → 100%)
   - Monitor metrics
   - Ready to rollback
   - A/B test vs old version

5. GENERAL AVAILABILITY
   - Full rollout
   - Continuous monitoring
```

---

## 4.3 AI Ethics & Governance

### Privacy & Security
```
DATA ANONYMIZATION:
- Remove PII (names, emails, IDs)
- K-anonymity (group size ≥ k)
- Differential privacy (add noise)

GDPR COMPLIANCE:
- Right to access data
- Right to deletion
- Right to explanation (model decisions)
- Consent required

SECURE BY DESIGN:
- Encryption at rest & transit
- Access controls
- Regular security audits
- Principle of least privilege
```

### Fairness & Bias
```
PROTECTED ATTRIBUTES:
- Race, gender, age
- Religion, nationality
- Disability status

DISPARATE IMPACT:
- Model performs worse for certain groups
- Example: Face recognition less accurate for dark skin

BIAS SOURCES:
- Historical bias in data
- Representation bias (some groups under-represented)
- Measurement bias (labels)
- Aggregation bias (one model for all)

MITIGATION:
- Collect balanced data
- Evaluate metrics per group
- Re-weight samples
- Post-processing adjustments
- Human oversight
```

### Model Governance
```
MODEL CARDS:
Document model details:
- Intended use
- Training data
- Performance metrics (overall + per group)
- Limitations
- Ethical considerations

EXPLAINABILITY:
- Feature importance
- SHAP values
- Attention weights (transformers)
- Example-based explanations

HUMAN-IN-THE-LOOP:
- Human review high-stakes decisions
- Audit sample of predictions
- Override capability
- Feedback loop

AUDIT TRAILS:
- Log all predictions
- Track model versions
- Record human overrides
- Enable investigation
```

### Logic & Critical Thinking
```
LOGICAL FALLACIES:

Correlation ≠ Causation:
- Ice cream sales and drowning both high in summer
- Common cause (temperature)

Post hoc ergo propter hoc:
- "After AI, revenue increased"
- Maybe due to other factors

Survivorship bias:
- Only looking at successful cases
- Ignoring failures

Confirmation bias:
- Only seeking evidence that supports hypothesis
```

---

## 📚 TÀI NGUYÊN HỌC TẬP BỔ SUNG

### Websites/Documentation
```
NumPy/Pandas:
- numpy.org/doc
- pandas.pydata.org/docs

Scikit-learn:
- scikit-learn.org (especially metrics, preprocessing)

Machine Learning:
- Coursera: Andrew Ng's ML course
- fast.ai: Practical deep learning

GenAI/LLMs:
- OpenAI documentation
- Anthropic Claude docs
- LangChain docs (RAG)

AI Ethics:
- AI Ethics Guidelines by EU
- Responsible AI by Google
- AI Fairness 360 by IBM
```

### Practice Resources
```
Coding:
- Kaggle (datasets + competitions)
- LeetCode (NumPy/Pandas problems)

Math:
- 3Blue1Brown (YouTube - Linear Algebra, Calculus)
- Khan Academy (Statistics)

Projects:
- Iris classification (beginner)
- House price prediction (intermediate)
- Sentiment analysis with transformers (advanced)
```

---

## ✅ FINAL CHECKLIST

### Phải Nhớ Tuyệt Đối:
```
□ Confusion matrix: TP, TN, FP, FN
□ Accuracy, Precision, Recall, F1 formulas
□ axis=0 (cột) vs axis=1 (hàng) trong NumPy
□ .loc[] vs .iloc[] trong Pandas
□ Train/Val/Test split purpose
□ Overfitting vs Underfitting signs
□ Data le