# Quickstart: Starter Application

**Target**: New developer runs API locally in under 10 minutes.

---

## Prerequisites

- **Python 3.11+**
- **uv** — `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Supabase project** — URL, publishable key, secret key, transaction pooler URL
- **Modal account** (for deployment; optional for local-only)

---

## Setup

### 1. Clone and install

```bash
git clone <repo-url>
cd cmr-backend_v2
uv sync
```

### 2. Environment

Copy `.env.example` to `.env` and set:

```bash
cp .env.example .env
# Edit .env with:
# ENVIRONMENT=develop
# SUPABASE_URL=https://xxx.supabase.co
# SUPABASE_PUBLISHABLE_KEY=...
# SUPABASE_SECRET_KEY=...
# TRANSACTION_POOLER_URL=postgresql://...  # IPv4-compatible
# JOB_STUCK_TIMEOUT_MINUTES=15              # Recovery worker timeout (optional, default 15)
# MODAL_PROJECT=cody-99083                  # Modal workspace/project (for deploy & secrets)
```

### 3. Database migration

```bash
uv run python scripts/migrate.py
```

Creates: `jobs` table, PGMQ `job_queue`.

### 4. Run API locally

```bash
uv run python scripts/dev.py
# or: uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

API: `http://localhost:8000`

---

## Verify

| Action | Command / URL |
|--------|---------------|
| Health | `curl http://localhost:8000/health` |
| DB health | `curl http://localhost:8000/health/db` |
| API docs | Open `http://localhost:8000/docs` |
| Create job | `curl -X POST http://localhost:8000/jobs -H "Authorization: Bearer <JWT>" -H "Content-Type: application/json" -d '{"job_type":"sample_task","job_parameters":{}}'` |

**Note**: Orphan/stuck job recovery is handled by a scheduled Modal worker (every 15 min), not an API endpoint.

---

## Deploy (Modal)

```bash
uv run deploy_dev   # or deploy_prod
```

Requires `modal setup`, `MODAL_PROJECT` in .env, and Modal secrets. Create secrets before first deploy:

```bash
source .env   # or export vars
./scripts/create_modal_secrets.sh   # prints exact commands
# Then run the printed modal secret create commands
```

---

## Troubleshooting

- **DB connection fails**: Ensure `TRANSACTION_POOLER_URL` uses IPv4; Supabase pooler may require it.
- **JWT 401**: Use a valid Supabase Auth token; check `SUPABASE_URL` for JWKS.
- **Migration fails**: Ensure PGMQ extension is available; use `CREATE EXTENSION IF NOT EXISTS pgmq`.
