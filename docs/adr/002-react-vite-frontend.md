# ADR-002: Use React + Vite for the frontend dashboard

**Date:** 2026-05-16
**Status:** Accepted

## Context

We need a data dashboard that lists projects, shows per-run QC tables, and renders charts. The tech stack requires React + TypeScript.

## Decision

Use **React 19** with **Vite 8** as the build tool, **Tailwind CSS v4** for styling, **TanStack Query v5** for server state, and **Recharts** for charts.

## Rationale

- **Vite** gives fast local development, simple SPA builds, and avoids framework overhead because SSR/SSG are not required for this dashboard.
- **React 19** aligns with the modern React ecosystem and matches the frontend stack expected for the project.
- **Tailwind CSS v4** integrates cleanly with Vite through the first-party `@tailwindcss/vite` plugin.
- **TanStack Query** is a good fit for server-state management: fetching, caching, refetching, and loading/error states.
- **Recharts** is enough for the dashboard's initial bar and pie charts without introducing lower-level charting complexity.
- **React Hook Form + Zod** provides client-side form validation with type-safe schemas and minimal form boilerplate.

## Alternatives considered

- **Next.js:** SSR/SSG are not needed for an internal dashboard; Vite is simpler and faster for SPAs.
- **Vue / Svelte:** React matches the existing frontend direction and has broad ecosystem support for dashboard applications.
- **Chart.js / D3:** Recharts are React-native; D3 requires more setup for simple charts.

## Consequences

- The app is a pure SPA. Vite's dev proxy forwards `/api/*` to the FastAPI server, avoiding CORS issues in development.
- For production, the built static files are served by nginx, which also proxies `/api/` to the API container.
