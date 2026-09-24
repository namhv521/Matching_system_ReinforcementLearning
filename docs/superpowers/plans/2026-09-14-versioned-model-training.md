# Versioned Model Training Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Xây pipeline tái lập được để benchmark, tự chọn engine đạt gate, train checkpoint theo milestone và phát hành từng phiên bản lên GitHub Releases.

**Architecture:** Giữ code Python hiện có làm lõi; bổ sung module provenance/promotion thuần Python và một CLI orchestration mỏng. Exact optimizer là mặc định cho batch matching; PPO/DQN chỉ được promotion khi validation nhiều seed chứng minh tốt hơn mà không vi phạm constraint. Model binary nằm trong GitHub Release, còn manifest/config/metrics tóm tắt nằm trong Git.

**Tech Stack:** Python 3.12, pandas, NumPy, SciPy, scikit-learn, Gymnasium, Stable-Baselines3, sb3-contrib, pytest, Git và GitHub CLI.

**Spec:** `docs/superpowers/specs/2026-09-14-versioned-model-training-design.md`

## Global Constraints

- Không commit raw data, PII, `.env`, logs, output experiment hoặc checkpoint.
- Không tuning trên test set; test chỉ chạy cho ứng viên đã thắng validation.
- Constraint violations phải bằng 0 trước promotion.
- PPO không được promotion chỉ vì là thuật toán chính của luận văn.
- Train dài chạy trong cửa sổ PowerShell/CMD riêng và Codex chờ tiến trình kết thúc.
- Không thêm MLflow, model-registry service, Git LFS hoặc dependency mới.

---

### Task 1: Dataset fingerprint và model manifest

**Files:**
- Create: `src/rl/model_registry.py`
- Create: `tests/test_model_registry.py`
- Modify: `.gitignore`

**Interfaces:**
- Produces: `fingerprint_files(paths: Sequence[Path]) -> str`
- Produces: `build_manifest(version: str, algorithm: str, checkpoint: Path | None, metrics: Mapping, config: Mapping, dataset_paths: Sequence[Path], commit_sha: str) -> dict`
- Produces: `write_manifest(manifest: Mapping, destination: Path) -> Path`

- [ ] **Step 1: Cho phép commit test source nhưng vẫn ignore artifacts**

Xóa dòng `tests/` khỏi `.gitignore`; giữ nguyên `data/`, `outputs/`, `*.zip`, `*.csv`, `*.jsonl`.

- [ ] **Step 2: Viết test fail cho fingerprint và manifest**

```python
def test_fingerprint_is_order_independent(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    a.write_bytes(b"a"); b.write_bytes(b"b")
    assert fingerprint_files([a, b]) == fingerprint_files([b, a])

def test_manifest_contains_reproducibility_fields(tmp_path):
    data = tmp_path / "data.csv"; data.write_bytes(b"rows")
    manifest = build_manifest("model-v0.1.0", "exact", None, {"quota_violations": 0}, {"seed": 42}, [data], "abc123")
    assert set(manifest) >= {"version", "algorithm", "dataset_fingerprint", "metrics", "config", "commit_sha", "created_at_utc"}
```

- [ ] **Step 3: Chạy test và xác nhận fail**

Run: `python -m pytest tests/test_model_registry.py -v`
Expected: FAIL vì `src.rl.model_registry` chưa tồn tại.

- [ ] **Step 4: Implement tối thiểu bằng `hashlib`, `json`, `datetime` và `pathlib`**

Fingerprint phải hash cặp `(tên file tương đối ổn định, SHA-256 nội dung)` theo thứ tự đã sort. `write_manifest` tạo parent directory và ghi UTF-8 JSON indent 2.

- [ ] **Step 5: Chạy test và commit**

Run: `python -m pytest tests/test_model_registry.py -v`
Expected: PASS.

```powershell
git add .gitignore src/rl/model_registry.py tests/test_model_registry.py
git commit -m "Add reproducible model manifests"
```

### Task 2: Promotion gate và lựa chọn engine

**Files:**
- Create: `src/rl/promotion.py`
- Create: `tests/test_promotion.py`

**Interfaces:**
- Consumes: benchmark rows có `algorithm`, `mean_compatibility`, `load_variance`, `quota_violations`, `invalid_proposals`.
- Produces: `aggregate_runs(payloads: Sequence[Mapping]) -> dict[str, dict]`
- Produces: `select_engine(summary: Mapping, min_improvement: float = 0.01) -> dict`

- [ ] **Step 1: Viết test fail cho hard gate và fallback**

```python
def test_ppo_with_violation_cannot_win():
    result = select_engine({
        "exact": {"mean_compatibility_mean": .70, "quota_violations": 0},
        "ppo_maskable": {"mean_compatibility_mean": .90, "quota_violations": 1},
    })
    assert result["selected"] == "exact"

def test_ppo_needs_meaningful_improvement():
    result = select_engine({
        "exact": {"mean_compatibility_mean": .70, "quota_violations": 0},
        "ppo_maskable": {"mean_compatibility_mean": .705, "quota_violations": 0},
    })
    assert result["selected"] == "exact"
```

- [ ] **Step 2: Chạy test và xác nhận fail**

Run: `python -m pytest tests/test_promotion.py -v`
Expected: FAIL vì module chưa tồn tại.

- [ ] **Step 3: Implement aggregation mean/std và policy chọn engine**

Chỉ các engine có tổng `quota_violations == 0` mới hợp lệ. Exact thắng mặc định; PPO chỉ thắng khi compatibility trung bình lớn hơn exact ít nhất `min_improvement` và `invalid_proposals == 0`. Nếu không có exact hợp lệ, chọn engine hợp lệ có compatibility cao nhất và ghi `reason`.

- [ ] **Step 4: Chạy test và commit**

Run: `python -m pytest tests/test_promotion.py -v`
Expected: PASS.

```powershell
git add src/rl/promotion.py tests/test_promotion.py
git commit -m "Add model promotion quality gate"
```

### Task 3: Benchmark validation-first và exact baseline

**Files:**
- Modify: `src/rl/benchmark.py`
- Create: `tests/test_benchmark.py`

**Interfaces:**
- Produces: `run_benchmark(timesteps: int, seed: int, evaluation_split: str = "validation") -> dict`
- Consumes: `optimal_assignment`, `deferred_acceptance`, PPO/DQN rollout hiện có.
- Output: `outputs/results/benchmark_<split>_seed<seed>_steps<timesteps>.json` với `evaluation_split` và dataset split metadata.

- [ ] **Step 1: Viết test fail cho exact feasibility và validation default**

```python
def test_optimal_assignment_respects_capacity():
    matrix = np.array([[1, 0], [.9, .8], [.7, .6]])
    actions = optimal_assignment(matrix, np.array([1, 2]))
    assert np.bincount(actions, minlength=2).tolist() == [1, 2]

def test_optimal_assignment_rejects_insufficient_capacity():
    with pytest.raises(ValueError, match="capacity"):
        optimal_assignment(np.ones((3, 2)), np.array([1, 1]))
```

- [ ] **Step 2: Chạy test và xác nhận fail thứ hai**

Run: `python -m pytest tests/test_benchmark.py -v`
Expected: FAIL vì exact solver chưa báo infeasible rõ ràng.

- [ ] **Step 3: Tách `run_benchmark`, thêm `--evaluation-split validation|test`**

Mặc định dùng validation. Chỉ command promotion cuối mới gọi `--evaluation-split test`. Đổi tên exact row thành `exact`; không tạo hai row giống nhau cho Gale–Shapley/SPA nếu cùng implementation, chỉ giữ `deferred_acceptance`.

- [ ] **Step 4: Chạy unit test và smoke benchmark**

Run: `python -m pytest tests/test_benchmark.py -v`
Expected: PASS.

Run: `python -m src.rl.benchmark --timesteps 512 --seed 42 --evaluation-split validation`
Expected: JSON có exact, greedy, deferred acceptance, PPO, DQN; mọi assignment cuối có quota violations bằng 0.

- [ ] **Step 5: Commit**

```powershell
git add src/rl/benchmark.py tests/test_benchmark.py
git commit -m "Evaluate matching engines on validation first"
```

### Task 4: CLI chạy experiment và tạo candidate version

**Files:**
- Create: `scripts/run_versioned_experiment.py`
- Create: `tests/test_versioned_experiment.py`
- Modify: `src/rl/train.py`

**Interfaces:**
- Consumes: `run_benchmark`, `aggregate_runs`, `select_engine`, `build_manifest`.
- Produces: CLI `python scripts/run_versioned_experiment.py --version model-v0.1.0 --milestones 200000 500000 1000000 --seeds 1 2 3 42 100`.
- Produces: local `outputs/releases/<version>/manifest.json`, summary JSON và checkpoint được chọn nếu RL thắng.

- [ ] **Step 1: Viết test fail cho version validation và dry-run command plan**

```python
def test_version_requires_model_semver():
    with pytest.raises(ValueError):
        validate_version("v1")
    assert validate_version("model-v1.2.3") == "model-v1.2.3"

def test_dry_run_lists_all_seed_milestone_pairs():
    plan = experiment_plan([200, 500], [1, 2])
    assert plan == [(1, 200), (1, 500), (2, 200), (2, 500)]
```

- [ ] **Step 2: Chạy test và xác nhận fail**

Run: `python -m pytest tests/test_versioned_experiment.py -v`
Expected: FAIL vì script chưa tồn tại.

- [ ] **Step 3: Implement orchestration tối thiểu**

CLI chạy smoke trước, benchmark validation cho từng seed/milestone, tổng hợp gate, rồi chỉ train/save checkpoint ứng viên cần thiết. Thêm `--dry-run`, `--smoke-steps 512`, `--min-improvement 0.01`. Mỗi lỗi trả exit code khác 0 và không tạo manifest đạt chuẩn.

- [ ] **Step 4: Bảo đảm checkpoint load lại được**

Trong `src/rl/train.py`, thêm `load_checkpoint(algorithm: str, path: Path, env: GymMatchingEnv)` và test smoke save/load với milestone nhỏ.

- [ ] **Step 5: Chạy test, dry-run và commit**

Run: `python -m pytest tests/test_versioned_experiment.py -v`
Expected: PASS.

Run: `python scripts/run_versioned_experiment.py --version model-v0.1.0 --milestones 200000 500000 1000000 --seeds 1 2 3 42 100 --dry-run`
Expected: in đúng kế hoạch, không train.

```powershell
git add scripts/run_versioned_experiment.py src/rl/train.py tests/test_versioned_experiment.py
git commit -m "Add versioned training orchestration"
```

### Task 5: GitHub release gate

**Files:**
- Create: `scripts/release_model.py`
- Create: `tests/test_release_model.py`
- Modify: `README.md`

**Interfaces:**
- Consumes: `outputs/releases/<version>/manifest.json`, optional checkpoint, clean Git worktree và authenticated `gh` CLI.
- Produces: annotated Git tag và GitHub Release qua `gh release create`.
- CLI: `python scripts/release_model.py --version model-v0.1.0 --manifest <path> --checkpoint <optional-path>`.

- [ ] **Step 1: Viết test fail cho preflight**

```python
def test_release_rejects_failed_gate(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text('{"version":"model-v0.1.0","promotion":{"passed":false}}')
    with pytest.raises(ValueError, match="promotion"):
        release_preflight(manifest, expected_version="model-v0.1.0")
```

- [ ] **Step 2: Chạy test và xác nhận fail**

Run: `python -m pytest tests/test_release_model.py -v`
Expected: FAIL vì script chưa tồn tại.

- [ ] **Step 3: Implement preflight và lệnh release**

Dùng `subprocess.run` với argument list, không shell string. Kiểm tra manifest version, gate, checkpoint hash, clean worktree, tag chưa tồn tại, `gh auth status`. Hỗ trợ `--dry-run`; chỉ khi không dry-run mới chạy `git tag -a`, `git push origin main`, `git push origin <tag>` và `gh release create`.

- [ ] **Step 4: Cập nhật README bằng command vận hành ngắn**

Ghi rõ validation-first, PowerShell train command, vị trí artifact local, quality gate và release command. Không đưa checkpoint/data vào Git.

- [ ] **Step 5: Chạy test và commit**

Run: `python -m pytest tests/test_release_model.py -v`
Expected: PASS.

```powershell
git add scripts/release_model.py tests/test_release_model.py README.md
git commit -m "Gate GitHub model releases"
```

### Task 6: Verification, visible training và phát hành từng version

**Files:**
- Modify only if failures reveal an implementation defect.
- Generate locally: `outputs/releases/model-v0.1.0/**`, later milestone version directories.

**Interfaces:**
- Consumes all earlier CLIs.
- Produces GitHub tags/releases `model-v0.1.0`, `model-v0.2.0`, and only after multi-seed final gate `model-v1.0.0`.

- [ ] **Step 1: Chạy verification trước train**

Run: `python -m compileall -q src scripts`
Expected: exit 0.

Run: `python -m pytest -q`
Expected: all tests pass.

Run: `git diff --check`
Expected: no output.

- [ ] **Step 2: Mở PowerShell riêng để chạy candidate đầu**

```powershell
Start-Process powershell -WindowStyle Normal -Wait -ArgumentList '-NoExit','-Command','cd C:\Su\KLTN\KLTN; .\.venv\Scripts\python.exe scripts\run_versioned_experiment.py --version model-v0.1.0 --milestones 200000 --seeds 42; Write-Host "TRAINING FINISHED"'
```

Codex không gọi tool/poll trong lúc `-Wait` đang chạy. Khi cửa sổ hoàn tất, đọc manifest và log một lần.

- [ ] **Step 3: Phát hành version chỉ khi gate pass**

Run dry-run trước: `python scripts/release_model.py --version model-v0.1.0 --manifest outputs/releases/model-v0.1.0/manifest.json --dry-run`
Expected: danh sách thao tác Git/GitHub hợp lệ.

Run release: `python scripts/release_model.py --version model-v0.1.0 --manifest outputs/releases/model-v0.1.0/manifest.json`
Expected: tag và GitHub Release tồn tại; checkpoint chỉ được attach nếu RL là engine thắng.

- [ ] **Step 4: Lặp với milestone đã được validation quyết định**

Chỉ tạo `model-v0.2.0` cho milestone tiếp theo nếu learning curve còn cải thiện. Chỉ tạo `model-v1.0.0` sau nhiều seed và một lần test cuối. Nếu PPO thua, manifest ghi engine thắng (`exact`, `greedy`, hoặc `deferred_acceptance`) và không tiếp tục đốt compute cho PPO.

- [ ] **Step 5: Kiểm chứng remote**

Run: `git status --short`
Expected: clean, ngoại trừ artifacts đã ignore.

Run: `git ls-remote --tags origin`
Expected: hiển thị các tag vừa phát hành.

Run: `gh release view <version> --json tagName,name,assets,url`
Expected: version, assets và URL khớp manifest.
