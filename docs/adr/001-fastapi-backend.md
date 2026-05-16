# ADR-001: Use FastAPI for the backend API

**Date:** 2026-05-16
**Status:** Accepted

## Context

We need a REST API backend that can serve a React dashboard. The domain is life sciences / NGS QC data. The primary language requirement is Python.

## Decision

Use **FastAPI** with **Uvicorn** as the ASGI server.

## Rationale

- FastAPI auto-generates OpenAPI docs from type annotations, which keeps the API contract easy to inspect while building and testing the frontend.
- Pydantic v2 integration provides fast, declarative request/response validation with clear error messages.
- Python type hints throughout make the codebase easier to read and suitable for optional static checking with mypy.
- SQLAlchemy 2.x + Alembic is the well-established Python ORM/migration stack.
- FastAPI keeps the option open to move selected endpoints to async later, but v1 intentionally uses synchronous SQLAlchemy + psycopg2 for simplicity.
- Faster to bootstrap than Django (no ORM opinions, no admin, no templates).
- FastAPI is a good fit for a data-oriented application where typed schemas, validation, and automatically generated API docs are useful during frontend/backend iteration

## Alternatives considered

- **Django REST Framework:** More batteries-included, but heavier and opinions on ORM conflict with SQLAlchemy preference.
- **Flask:** Simpler, but no built-in validation or OpenAPI generation.

## Consequences

- The API is synchronous in v1, using SQLAlchemy with `psycopg2`, which keeps the backend simpler and easier to reason about.
- If concurrency becomes a bottleneck, selected parts of the API can later move toward `asyncpg` and async SQLAlchemy.
- FastAPI's DI system (`Depends`) is used for DB session injection, which keeps routes thin.
- The team needs to understand FastAPI's dependency injection and Pydantic request/response models, but the learning curve is acceptable for this project.
