# AGENTS.md

## Project Overview

BioQC Portal is a full-stack application for reviewing NGS sequencing run quality. It ingests precomputed sample QC metrics, classifies samples as PASS, WARN, or FAIL, and provides run-level dashboards and reports.

## Repository Layout

- `apps/api/` - FastAPI REST API, SQLAlchemy models, Alembic migrations, service logic, and pytest tests.
- `apps/web/` - React 19 + TypeScript + Vite SPA with TanStack Query, Axios, Tailwind CSS v4, and Recharts.
- `docs/adr/` - architecture decision records.
- `samples/` - synthetic sample manifest and QC metrics used by the seed script.
- `docker-compose.yml` - PostgreSQL, API, and web dev services.
- `Makefile` - common local commands for Docker, API, and web workflows.

## Runtime And Tooling

- Python version is controlled by `apps/api/.python-version` and `apps/api/pyproject.toml`.
- Node version is controlled by `pnpm-workspace.yaml` and `package.json` engines.
- Use `uv` for Python dependency installation and the local API virtual environment at `apps/api/.venv`.
- Use `pnpm` workspaces for frontend dependency management.
- PostgreSQL is the development database; API tests use in-memory SQLite overrides.

## Common Commands

- Install everything: `make install`
- Start Docker services: `make docker-up`
- Stop Docker services: `make docker-down`
- Tail Docker logs: `make docker-logs`
- Run API locally: `make api-dev`
- Apply migrations: `make api-migrate`
- Seed demo data: `make api-seed`
- Run API tests: `make api-test`
- Lint API: `make api-lint`
- Type-check API: `make api-typecheck`
- Run web locally: `make web-dev`
- Build web: `make web-build`
- Lint web: `make web-lint`
- Type-check web: `make web-typecheck`
- Format supported files: `pnpm format`

## Backend Conventions

- Keep FastAPI route handlers in `apps/api/app/api/routes/` thin. HTTP concerns belong there.
- Put business logic in `apps/api/app/services/`.
- Put database queries in `apps/api/app/repositories/`.
- Define persistent tables in `apps/api/app/models/`.
- Define request and response contracts in `apps/api/app/schemas/`.
- Keep QC threshold logic pure and tested in `apps/api/app/services/qc.py`.
- Keep file parsers in `apps/api/app/services/parsers/`. Each parser is a standalone function with no DB access; raise `ValueError` on bad input.
- Add or update Alembic migrations under `apps/api/alembic/versions/` when models change.
- Prefer typed SQLAlchemy 2.x `Mapped[]` model declarations, matching existing models.

## Frontend Conventions

- Keep API calls in `apps/web/src/api/` and shared API-facing types in `apps/web/src/types.ts`.
- Use TanStack Query for server state and Axios through the shared `apiClient`.
- Keep page-level composition in `apps/web/src/pages/` and reusable UI in `apps/web/src/components/`.
- Match the existing dashboard style before introducing new visual patterns.
- When API response shapes change, update frontend types, API clients, and affected components together.

## Import Paths

There are two import endpoints:

1. `POST /api/runs/{run_id}/import` — accepts a JSON body (`ImportRequest`), the simple format.
2. `POST /api/runs/{run_id}/import/files` — accepts multipart form-data with a manifest CSV (`manifest_file`), a QC JSON (`qc_file`), and a format selector (`qc_format`: `simple_json` | `multiqc_like`).

The file-based endpoint parses each file with the parsers in `services/parsers/`, then calls `import_samples()` with only the samples whose `sample_name` appears in both files.

## Data And Privacy

- Sample files under `samples/` are synthetic. Do not add real patient, clinical, or identifiable sequencing data.
- This app consumes QC summaries from upstream tools; do not fold heavy FASTQ processing into the portal without a separate design decision.

## Verification Guidance

- For backend changes, run `make api-test` and, when relevant, `make api-lint` or `make api-typecheck`.
- For frontend changes, run `make web-typecheck`, `make web-lint`, and `make web-build` as appropriate.
- For docs-only changes, no full test run is required unless commands or examples changed.
- Before finishing, check `git status --short` and keep unrelated user changes intact.
