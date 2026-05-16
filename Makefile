.PHONY: help docker-up docker-down docker-logs \
        api-install api-dev api-migrate api-seed api-test api-lint api-typecheck \
        web-dev web-build web-lint web-typecheck \
        install

help:
	@echo "BioQC Portal — available targets:"
	@echo ""
	@echo "  Docker"
	@echo "    docker-up       Start all services (db + api + web)"
	@echo "    docker-down     Stop all services"
	@echo "    docker-logs     Tail service logs"
	@echo ""
	@echo "  Backend (apps/api)"
	@echo "    api-install     Sync Python dependencies into apps/api/.venv (requires uv)"
	@echo "    api-dev         Run FastAPI dev server on :8000"
	@echo "    api-migrate     Run Alembic migrations"
	@echo "    api-seed        Seed demo data into running API"
	@echo "    api-test        Run pytest"
	@echo "    api-lint        Run ruff check"
	@echo "    api-typecheck   Run mypy"
	@echo ""
	@echo "  Frontend (apps/web)"
	@echo "    web-dev         Run Vite dev server on :5173"
	@echo "    web-build       Build for production"
	@echo "    web-lint        Run ESLint"
	@echo "    web-typecheck   Run TypeScript type-check"
	@echo ""
	@echo "  install           Install all deps (Python + Node)"

# ── Docker ────────────────────────────────────────────────────────────────────

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

# ── Backend ───────────────────────────────────────────────────────────────────

api-install:
	cd apps/api && uv sync --extra dev

api-dev:
	cd apps/api && uv run uvicorn app.main:app --reload --port 8000

api-migrate:
	cd apps/api && uv run alembic upgrade head

api-seed:
	cd apps/api && uv run python seed.py

api-test:
	cd apps/api && uv run pytest -v

api-lint:
	cd apps/api && uv run ruff check .

api-typecheck:
	cd apps/api && uv run mypy app

# ── Frontend ──────────────────────────────────────────────────────────────────

web-dev:
	pnpm --filter web dev

web-build:
	pnpm --filter web build

web-lint:
	pnpm --filter web lint

web-typecheck:
	pnpm --filter web typecheck

# ── All ───────────────────────────────────────────────────────────────────────

install: api-install
	pnpm install
