# BioQC Portal

A web application for reviewing NGS sequencing run quality. Upload sample manifests and QC metric files, then explore per-sample quality dashboards with charts, filters, and summary reports.

Please see the related project, bioinformatics workflow platform for Python CLI + Nextflow setup: [kamwro/bioinformatics-workflow-platform](https://github.com/kamwro/bioinformatics-workflow-platform).

It pairs a Python/FastAPI backend, React/Vite frontend, PostgreSQL persistence, clean architecture, and CI workflows in a life sciences context.

---

## What it does

1. **Manage projects** — group sequencing runs under named research projects.
2. **Track sequencing runs** — record runs with platform info (e.g. Illumina NovaSeq 6000).
3. **Import QC data** — three import paths (see below).
4. **Automatic QC classification** — each sample is classified as **PASS / WARN / FAIL** based on configurable thresholds.
5. **Dashboard** — per-run summary cards, sample table with status filter, and four charts (status distribution, Q30, GC content, duplication rate).
6. **Reports** — JSON report endpoint with aggregate stats and worst-performing samples.

> **Domain note:** The app mimics the kind of per-sample QC summary you'd see in a MultiQC report, without requiring real FASTQ files. See [ADR-004](docs/adr/004-mock-multiqc-data.md) for the rationale.

---

## Tech stack

| Layer      | Technology                                                 |
| ---------- | ---------------------------------------------------------- |
| Backend    | Python 3.14, FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic |
| Database   | PostgreSQL 18                                              |
| Frontend   | React 19, TypeScript, Vite 8, Tailwind CSS v4              |
| Data fetch | TanStack Query v5, Axios                                   |
| Forms      | React Hook Form + Zod                                      |
| Charts     | Recharts                                                   |
| Monorepo   | pnpm workspaces                                            |
| Containers | Docker, Docker Compose                                     |
| CI         | GitHub Actions                                             |

---

## Architecture overview

```
┌─────────────────────────────────────────────────────────────┐
│  Browser (React/Vite :5173)                                 │
│    TanStack Query → axios → /api/*                          │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP
┌───────────────────────────▼─────────────────────────────────┐
│  FastAPI (:8000)                                            │
│    routes → services → repositories → SQLAlchemy ORM       │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│  PostgreSQL (:5433)                                         │
│    projects, sequencing_runs, samples, qc_metrics           │
└─────────────────────────────────────────────────────────────┘
```

**Backend layers:**

- `api/routes/` — thin FastAPI routers, HTTP in/out only
- `services/` — business logic, raises HTTP exceptions
- `repositories/` — database queries via SQLAlchemy sessions
- `models/` — SQLAlchemy ORM models
- `schemas/` — Pydantic v2 request/response models

---

## Quick start

```bash
# 1. Install dependencies
pip install uv                        # Python package manager (once)
make install                          # API .venv + Node deps

# 2. Start all services
make docker-up                        # PostgreSQL + API + Web via Docker Compose

# 3. Apply DB schema (first time only)
make api-migrate                      # runs alembic upgrade head

# 4. Load demo data
make api-seed                         # creates project + run + imports 20 samples
```

Open **http://localhost:5173** — the demo data is ready to explore.

> If the API container was already running before `make api-migrate`, restart it:
> `docker compose restart api`

---

## Local setup

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (recommended path)
- Or: Python 3.14, [uv](https://docs.astral.sh/uv/), Node.js 24+, pnpm 10+

### Option A — Docker Compose (all-in-one)

```bash
make docker-up
make api-migrate   # first time only
make api-seed
make docker-logs   # tail logs
```

Then open [http://localhost:5173](http://localhost:5173).

### Option B — local dev (separate terminals)

```bash
# Terminal 1 — start the database only
docker compose up -d db

# Terminal 2 — backend
make api-install       # sync Python deps into apps/api/.venv
make api-migrate       # run DB migrations
make api-dev           # start FastAPI on :8000

# Terminal 3 — frontend
pnpm install           # install Node deps
make web-dev           # start Vite on :5173

# (Optional) seed demo data once the API is up
make api-seed
```

The API uses an `uv`-managed virtual environment at `apps/api/.venv`. Makefile
commands run through `uv run`, so you do not need to activate the venv manually.

### Environment variables

Copy the example file and adjust as needed:

```bash
cp apps/api/.env.example apps/api/.env
```

Key variables:

| Variable       | Default                                                       | Description                |
| -------------- | ------------------------------------------------------------- | -------------------------- |
| `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5433/bio_qc_portal` | Postgres connection string |
| `CORS_ORIGINS` | `["http://localhost:5173"]`                                   | Allowed CORS origins       |
| `VITE_API_URL` | _(empty — uses Vite proxy)_                                   | Override API base URL      |

---

## Commands

| Command              | Description                   |
| -------------------- | ----------------------------- |
| `make docker-up`     | Start all Docker services     |
| `make docker-down`   | Stop all Docker services      |
| `make api-install`   | Sync API dependencies         |
| `make api-dev`       | Run FastAPI dev server        |
| `make api-migrate`   | Apply DB migrations           |
| `make api-seed`      | Load demo data                |
| `make api-test`      | Run pytest                    |
| `make api-lint`      | Run ruff linter               |
| `make web-dev`       | Run Vite dev server           |
| `make web-build`     | Build frontend for production |
| `make web-lint`      | Run ESLint on frontend        |
| `make web-typecheck` | TypeScript type-check         |

---

## Dependency updates

### API dependencies

API dependencies are declared in `apps/api/pyproject.toml` and resolved in
`apps/api/uv.lock`.

For routine updates, refresh the lockfile while keeping the declared dependency
ranges unchanged:

```bash
cd apps/api
uv lock --upgrade
uv sync --extra dev
```

To update one locked package:

```bash
cd apps/api
uv lock --upgrade-package fastapi
uv sync --extra dev
```

To intentionally raise the minimum supported version in `pyproject.toml`, use
`uv add`:

```bash
cd apps/api
uv add "fastapi>=0.137.0"
uv add --optional dev "pytest>=9.1.0"
```

Use lockfile updates for normal maintenance. Raise `pyproject.toml` minimums
only when the project no longer supports older versions.

### Web dependencies

Web dependency checks use `npm-check-updates`:

```bash
pnpm deps:check:major
pnpm deps:update:minor
```

---

## API docs

FastAPI auto-generates interactive API docs:

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI JSON:** [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

### Main endpoints

```
GET  /api/health

GET    /api/projects
POST   /api/projects
GET    /api/projects/{id}
DELETE /api/projects/{id}

GET  /api/projects/{project_id}/runs
POST /api/projects/{project_id}/runs
GET  /api/runs/{run_id}

POST /api/runs/{run_id}/import           — JSON body (simple format)
POST /api/runs/{run_id}/import/files     — multipart: manifest CSV + QC JSON
GET  /api/runs/{run_id}/samples
GET  /api/runs/{run_id}/qc-summary
GET  /api/runs/{run_id}/report

GET  /api/samples/{sample_id}
```

---

## Import options

There are three ways to get QC data into a run:

### 1. File upload (UI) — recommended

Open a run's **Import** tab in the browser and choose **Upload files**:

1. Select a **manifest CSV** (`samples/sample_manifest.csv` as example) with columns:
   `sample_name, organism, assay_type`
2. Select a **QC metrics JSON** file and pick the format:
   - **MultiQC-like JSON** (`samples/multiqc_like_data.json`) — realistic external-tool format
   - **Simple JSON** (`samples/qc_metrics.json`) — internal flat format
3. Click **Import files**. Only samples present in _both_ files are imported.

### 2. JSON paste (UI)

Open a run's **Import** tab, choose **Paste JSON**, and paste a payload like:

```json
{
  "samples": [
    {
      "sample_name": "SAMP001",
      "total_reads": 50000000,
      "q30_score": 85.2,
      "gc_content": 48.5,
      "duplication_rate": 12.3,
      "adapter_content": 1.8,
      "mean_read_quality": 37.1
    }
  ]
}
```

### 3. curl / API

**Simple JSON** (existing endpoint):

```bash
curl -X POST http://localhost:8000/api/runs/{run_id}/import \
  -H "Content-Type: application/json" \
  -d @samples/qc_metrics.json
```

**File upload** (multipart):

```bash
curl -X POST http://localhost:8000/api/runs/{run_id}/import/files \
  -F "manifest_file=@samples/sample_manifest.csv;type=text/csv" \
  -F "qc_file=@samples/multiqc_like_data.json;type=application/json" \
  -F "qc_format=multiqc_like"
```

---

## Sample data

`samples/` contains realistic but entirely synthetic NGS QC data (no patient/clinical data):

| File                             | Description                                                  |
| -------------------------------- | ------------------------------------------------------------ |
| `samples/sample_manifest.csv`    | 20 samples with `sample_name, organism, assay_type` columns  |
| `samples/qc_metrics.json`        | 20-sample QC metrics in simple JSON format (used by seed)    |
| `samples/multiqc_like_data.json` | 10-sample QC metrics in MultiQC-like JSON format             |

The `make api-seed` command creates a demo project, a run, and imports all 20 samples automatically.

**QC thresholds used:**

| Metric              | PASS    | WARN                  | FAIL         |
| ------------------- | ------- | --------------------- | ------------ |
| Q30 score (%)       | ≥ 80    | 70 – 79.9             | < 70         |
| GC content (%)      | 40 – 60 | 35 – 39.9 / 60.1 – 65 | < 35 or > 65 |
| Duplication (%)     | ≤ 20    | 20.1 – 50             | > 50         |
| Adapter content (%) | ≤ 5     | 5.1 – 10              | > 10         |

---

## Testing

### Backend

```bash
make api-test
```

Tests use SQLite in-memory (no database required) and cover:

- QC status calculation logic (unit tests)
- All main API endpoints (integration tests via `TestClient`)

### Frontend

```bash
make web-typecheck   # TypeScript type check
make web-build       # Vite build (fails on type errors)
make web-lint        # ESLint
```

---

## Future improvements

- [ ] Pagination on sample lists for large runs
- [ ] User authentication (JWT)
- [ ] Configurable QC thresholds per project
- [ ] Export run report as PDF
- [ ] WebSocket live updates during import
- [ ] Playwright E2E tests
- [ ] Helm chart / Kubernetes deployment

---

## Project scope

BioQC Portal is a focused quality review system for sequencing run summaries. It models the workflows around ingesting precomputed QC metrics, classifying sample quality, and reviewing run-level results without pretending to replace an upstream bioinformatics pipeline. See the [ADRs](docs/adr/) for design decisions.
