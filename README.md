# CMR Backend

FastAPI backend with background jobs, Modal workers, and Supabase. A starter application for building async job-processing APIs.

## Overview

This project provides:

- **REST API** — FastAPI with health checks, JWT auth, and job management
- **Background jobs** — Create jobs via `POST /jobs`; workers process them asynchronously on Modal
- **Job lifecycle** — Jobs flow through `pending` → `processing` → `completed` or `failed`; a scheduled recovery worker marks stuck/orphaned jobs as failed
- **Sample worker** — `sample_task` demonstrates the pattern for adding new job types (GPU, browser, LLM, API tiers)

All job endpoints require JWT authentication. Jobs are user-scoped (you only see your own).

## Prerequisites

- **Python 3.11+**
- **uv** — `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Supabase project** — URL, publishable key, secret key, transaction pooler URL
- **Modal account** (for deployment; optional for local-only)

## Getting Started

### 1. Clone and install

```bash
git clone <repo-url>
cd cmr-backend_v2
uv sync
```

### 2. Environment

```bash
cp .env.example .env
# Edit .env with your Supabase and Modal credentials
```

Required variables: `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_SECRET_KEY`, `TRANSACTION_POOLER_URL`. Optional: `ENVIRONMENT`, `JOB_STUCK_TIMEOUT_MINUTES`, `MODAL_PROJECT`.

### 3. Database migration

```bash
uv run python scripts/migrate.py
```

Creates the `jobs` table and PGMQ `job_queue`.

### 4. Run locally

```bash
uv run python scripts/dev.py
```

API: **http://localhost:8000** · Docs: **http://localhost:8000/docs**

### Verify

| Action      | Command / URL                          |
|-------------|----------------------------------------|
| Health      | `curl http://localhost:8000/health`    |
| DB health   | `curl http://localhost:8000/health/db` |
| Create job  | `POST /jobs` with `Authorization: Bearer <JWT>` and `{"job_type":"sample_task","job_parameters":{}}` |

## Project Structure

```
src/
├── api/              # FastAPI app, routes, dependencies
├── config/           # Supabase, database connection
├── deployment/       # Modal app, workers, deploy script
├── middleware/      # CORS, metrics, request ID
├── models/          # Config, jobs, responses
├── services/        # Job queue (database, queue, spawner, service)
└── utils/            # Logging
scripts/              # migrate.py, dev.py, create_modal_secrets.sh
docs/                 # quickstart.md, conventions.md
```

## Deploy to Modal

```bash
uv run deploy_dev   # or deploy_prod
```

Before first deploy, create Modal secrets:

```bash
source .env
./scripts/create_modal_secrets.sh   # prints exact commands
# Run the printed modal secret create commands
```

## Documentation

- **[docs/quickstart.md](docs/quickstart.md)** — Detailed setup and troubleshooting
- **[docs/conventions.md](docs/conventions.md)** — Patterns for adding routes, services, job types

## License

See repository.
