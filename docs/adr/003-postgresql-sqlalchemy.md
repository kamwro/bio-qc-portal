# ADR-003: Use PostgreSQL + SQLAlchemy 2.x for persistence

**Date:** 2026-05-16
**Status:** Accepted

## Context

We need a relational database to store projects, runs, samples, and QC metrics. The relationships are straightforward (project → runs → samples → metrics), and the current data volume is modest.

## Decision

Use **PostgreSQL 18** with **SQLAlchemy 2.x ORM** and **Alembic** for migrations.

## Rationale

- PostgreSQL is a mature open-source relational database with strong support for structured data, constraints, transactions, and production-style application workflows.
- The domain model is naturally relational: projects contain sequencing runs, runs contain samples, and samples have QC metrics.
- SQLAlchemy 2.x's `Mapped[]` / `mapped_column()` style keeps ORM models explicit, typed, and easier to read.
- Alembic provides schema migration management for SQLAlchemy-based projects, which keeps database changes versioned and reviewable.
- UUID primary keys are used to avoid exposing sequential internal IDs in URLs and API responses.
- For the MVP, UUIDs are stored as `String(36)` to keep the same model definitions portable between PostgreSQL and SQLite-based tests.

## Alternatives considered

- **MongoDB:** No strong reason to go document-store for well-structured tabular QC data.
- **SQLite only:** Useful for tests, but too limited as the main database for a service intended to model production-style relational workflows.

## Consequences

- The `psycopg2-binary` driver is synchronous, which keeps the MVP simple but means database access is blocking.
- If high concurrency becomes important, the backend can migrate selected paths to `asyncpg` and SQLAlchemy async.
- `String(36)` UUIDs are portable across SQLite tests and PostgreSQL, but they do not use PostgreSQL's native `uuid` type.
- SQLite-based tests are fast, but they may miss PostgreSQL-specific behavior, so PostgreSQL integration tests should be added for critical database flows.
