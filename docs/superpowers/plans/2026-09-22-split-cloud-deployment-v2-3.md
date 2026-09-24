# Split Cloud Deployment v2.3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deploy React/Vite on Vercel, FastAPI on Render, and public application data on Supabase PostgreSQL with pgvector enabled.

**Architecture:** Vercel serves the SPA and calls Render over HTTPS. Render is the only database client and connects through the Supabase IPv4 shared session pooler with SSL. Supabase is the source of truth; sanitized snapshots remain reproducibility inputs and controlled read-only fallback data.

**Tech Stack:** React 18, Vite 6, TypeScript, FastAPI, SQLAlchemy 2, Alembic, PostgreSQL/Supabase, pgvector, Docker, GitHub Actions, Render, Vercel.

**Spec:** `docs/superpowers/specs/2026-09-22-split-cloud-deployment-design.md`

## Global Constraints

- Keep React + Vite and preserve TF-IDF, benchmark results, and Exact promotion.
- Never upload raw or curated private identifiers.
- Create `docs/complete_kltn_v2_3.md`; do not modify v1.
- Keep database credentials server-side.
- Leave `KE_HOACH_CHECKLIST_KLTN_RL_MATCHING.xlsx` untouched and outside all commits.

---

### Task 1: Close public-data privacy gaps

**Files:** Modify `scripts/build_public_data.py`, `tests/test_public_data.py`; create `scripts/audit_public_data.py`; regenerate `data/public/theses.csv`.

**Interfaces:** Produce `sanitize_source_file(value: str, record_id: str) -> str` and `audit_public_data(public_dir: Path, curated_dir: Path) -> list[str]`.

- [ ] **Step 1: Add a failing test that scans every public string column for normalized original student IDs and names.**

```python
def test_public_audit_reports_no_leaks():
    assert audit_public_data(PUBLIC, CURATED) == []
```

- [ ] **Step 2: Run `python -m pytest tests/test_public_data.py -v`; expect failure on `source_file`.**

- [ ] **Step 3: Replace source filenames with deterministic neutral provenance.**

```python
def sanitize_source_file(value: str, record_id: str) -> str:
    suffix = Path(value).suffix.lower() or ".pdf"
    return f"source-{record_id}{suffix}"
```

- [ ] **Step 4: Regenerate with `python scripts/build_public_data.py`, run the audit and focused tests; require 198 rows and zero leaks.**

- [ ] **Step 5: Commit only privacy script, test, and regenerated public data files.**

---

### Task 2: Harden Supabase PostgreSQL connection and health

**Files:** Modify `requirements.txt`, `backend/app/core/config.py`, `backend/app/db/session.py`, `backend/app/main.py`; create `tests/test_database_health.py`.

**Interfaces:** Produce `database_health() -> dict[str, str]`; `/health` reports `ok` or `degraded` without exception details.

- [ ] **Step 1: Write failing connected/degraded health tests.**

```python
def test_health_is_degraded_without_database(monkeypatch, client):
    monkeypatch.setattr(session, "probe_database", lambda: False)
    assert client.get("/health").json()["status"] == "degraded"
```

- [ ] **Step 2: Run `python -m pytest tests/test_database_health.py -v`; confirm failure.**

- [ ] **Step 3: Add `psycopg[binary]`, normalize PostgreSQL URLs, require SSL, and use `pool_pre_ping=True`, `pool_size=3`, `max_overflow=2`, `pool_recycle=300`.**

- [ ] **Step 4: Implement a caught `SELECT 1` probe without logging connection strings.**

- [ ] **Step 5: Run focused tests and `python -m pytest -q`; commit as `feat: support pooled Supabase PostgreSQL`.**

---

### Task 3: Add pgvector migration and idempotent seed

**Files:** Modify `backend/app/db/migrations/env.py`; create `backend/app/db/migrations/versions/20260922_01_cloud_schema.py`, `scripts/seed_cloud_database.py`, `tests/test_cloud_seed.py`.

**Interfaces:** Produce `seed_public_database(session: Session, public_dir: Path, results_dir: Path) -> dict[str, int]`.

- [ ] **Step 1: Write a failing repeated-seed test.**

```python
def test_seed_is_idempotent(db_session):
    first = seed_public_database(db_session, PUBLIC, RESULTS)
    second = seed_public_database(db_session, PUBLIC, RESULTS)
    assert first == second
    assert second["theses"] == 198
    assert second["advisors"] == 39
```

- [ ] **Step 2: Run `python -m pytest tests/test_cloud_seed.py -v`; confirm importer is missing.**

- [ ] **Step 3: Create a reversible migration beginning with `CREATE EXTENSION IF NOT EXISTS vector`; keep the extension on downgrade.**

- [ ] **Step 4: Implement one-transaction SQLAlchemy upserts for catalog, skills, benchmarks, and curves; normalize NaN to `None`; never concatenate SQL.**

- [ ] **Step 5: On empty PostgreSQL, run Alembic upgrade and the seed command twice; verify counts do not change.**

- [ ] **Step 6: Commit as `feat: add Supabase schema and idempotent seed`.**

---

### Task 4: Make PostgreSQL the runtime source of truth

**Files:** Modify matching/analytics services, API dependencies, advisor/thesis repositories; create `tests/test_database_backed_matching.py`.

**Interfaces:** Produce `MatchingService.from_session(db: Session, seed: int) -> MatchingService`; keep existing API response schemas.

- [ ] **Step 1: Add a failing seeded-database overview test requiring 198 theses and 39 advisors.**

- [ ] **Step 2: Run the focused test and confirm the file-backed constructor fails the contract.**

- [ ] **Step 3: Add repository-to-dataframe adapters; converters contain no query logic.**

- [ ] **Step 4: Inject request sessions and lazy-load vectorizer/PPO only on matching routes.**

- [ ] **Step 5: Permit file fallback only with `ALLOW_FILE_FALLBACK=true`; production default is false.**

- [ ] **Step 6: Run matching/API tests and full Python tests; commit as `feat: serve matching data from PostgreSQL`.**

---

### Task 5: Prepare and optimize Vercel frontend

**Files:** Modify `frontend/src/services/api/client.ts`, `frontend/src/App.tsx`, chart-heavy feature imports; create `frontend/vercel.json`, `frontend/.env.example`, `frontend/src/services/api/client.test.ts`.

**Interfaces:** Consume HTTPS `VITE_API_URL`; produce `apiUrl(path: string, origin?: string) -> string`.

- [ ] **Step 1: Write the failing URL join test.**

```typescript
it('joins API origin and path', () => {
  expect(apiUrl('/health', 'https://api.example.com/')).toBe('https://api.example.com/health')
})
```

- [ ] **Step 2: Run `npm --prefix frontend run test:run`; confirm failure.**

- [ ] **Step 3: Validate production API origin and allow an empty origin only in development.**

- [ ] **Step 4: Lazy-load only the Recharts-heavy analytics feature with an accessible Suspense state.**

- [ ] **Step 5: Add SPA rewrite, immutable asset cache, and CSP limited to the Render API.**

- [ ] **Step 6: Run Vitest, production build, and `npm audit --omit=dev`; require a separate analytics chunk and zero audit vulnerabilities.**

- [ ] **Step 7: Commit as `feat: prepare frontend for Vercel`.**

---

### Task 6: Split deployment and extend CI

**Files:** Modify `Dockerfile`, `.dockerignore`, `render.yaml`, `.github/workflows/ci.yml`, `.env.example`; create `tests/test_deployment_config.py`.

**Interfaces:** Render image exposes FastAPI only; CI PostgreSQL is available at `postgresql+psycopg://postgres:postgres@localhost:5432/kltn_test`.

- [ ] **Step 1: Write failing configuration tests.**

```python
def test_render_is_backend_only():
    dockerfile = Path("Dockerfile").read_text()
    assert "FROM node:" not in dockerfile
    assert "frontend/dist" not in dockerfile
```

- [ ] **Step 2: Run the test; confirm current multi-stage Dockerfile fails.**

- [ ] **Step 3: Remove frontend build/copy stages while retaining ML artifacts and health check.**

- [ ] **Step 4: Add Render database secret, strict CORS, PostgreSQL CI service, privacy audit, Alembic migration, double seed, frontend build, and Docker build.**

- [ ] **Step 5: Run all tests/builds and `docker build -t kltn-backend:v2.3 .`; commit as `ci: split Render backend and Vercel frontend`.**

---

### Task 7: Provision, deploy, verify, and report

**Files:** Create `docs/complete_kltn_v2_3.md`; modify deployment config only if production evidence requires correction.

**Interfaces:** Produce verified Render/Vercel URLs, Supabase counts, CI URL, and final remote SHA.

- [ ] **Step 1: After user login handoff, create a nearby Supabase project, enable `vector`, and put the Shared Pooler Session Mode URL directly into Render secrets without printing or saving its password.**

- [ ] **Step 2: Apply Alembic and idempotent seed to Supabase; verify 198 theses, 39 advisors, related counts, and zero private-identifier leakage.**

- [ ] **Step 3: Deploy backend-only Render image and verify health, overview, directory, recommendation, and matching endpoints.**

- [ ] **Step 4: Import the repo into Vercel with root `frontend`, Vite preset, branch `KLTN`, build `npm run build`, output `dist`, and `VITE_API_URL` set to Render.**

- [ ] **Step 5: Add exact Vercel production origin to Render CORS; never use wildcard CORS.**

- [ ] **Step 6: Smoke-test production dashboard, directory, figures, recommendation, and cohort matching.**

- [ ] **Step 7: Create `docs/complete_kltn_v2_3.md` with architecture, schema, privacy audit, secrets policy, URLs, counts, CI, smoke evidence, limits, rollback, and future pgvector work; leave v1 unchanged.**

- [ ] **Step 8: Run full tests/build, `git diff --check`, push `KLTN`, verify remote SHA, and keep the unrelated Excel edit outside commits.**
