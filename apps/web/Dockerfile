FROM node:24.15.0-bookworm-slim AS base
ENV CI=true
RUN npm install -g pnpm@11.1.2
WORKDIR /app

# Install workspace deps from the lockfile
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY apps/web/package.json apps/web/package.json
RUN pnpm install --frozen-lockfile --filter web...
WORKDIR /app/apps/web

# ── dev target ────────────────────────────────────────────────────────────────
FROM base AS dev
COPY apps/web/ .
EXPOSE 5173
CMD ["pnpm", "dev", "--host", "0.0.0.0"]

# ── builder ───────────────────────────────────────────────────────────────────
FROM base AS builder
COPY apps/web/ .
RUN pnpm build

# ── production (nginx) ────────────────────────────────────────────────────────
FROM nginx:alpine AS runtime
COPY --from=builder /app/apps/web/dist /usr/share/nginx/html
COPY apps/web/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
