# Implementation Plan: Starter Application

**Branch**: `001-starter-application` | **Date**: 2025-02-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-starter-application/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Build a starter application from `_local/starter-kit` blueprint: FastAPI API with health checks, JWT auth, Supabase + asyncpg data layer, Modal workers for background jobs, and a sample worker pattern. Delivers: `/health`, `/health/db`, job CRUD; recovery via scheduled worker, idempotent migration script, and full stack wiring per starter-kit architecture.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI, uvicorn, supabase, modal, pyjwt, cryptography, sqlalchemy, asyncpg, pydantic, pydantic-settings, httpx, python-dotenv  
**Storage**: Supabase (PostgreSQL), PostgREST, PGMQ  
**Testing**: pytest (unit, integration, contract)  
**Target Platform**: Linux server (Modal serverless), local dev via uvicorn  
**Project Type**: web-service (REST API + background workers)  
**Performance Goals**: Stateless API; jobs scale via Modal workers  
**Constraints**: 10-minute setup; secrets via env/Infisical/Modal Secrets; no hardcoded deployment targets  
**Scale/Scope**: Starter scaffold; single sample worker; extensible for future job types and domain features  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify alignment with `.specify/memory/constitution.md`:

- **Quick Start**: Setup path remains under 10 minutes; minimal prerequisites; one-command run; documented in quickstart.md
- **REST API**: Health check (`GET /health`, `GET /health/db`) and automatic API docs (`/docs`) planned
- **Cloud-Ready**: Stateless design; Modal deployment; environment-driven config
- **Observability**: Structured logging; X-Request-ID middleware; request tracing in place
- **Developer Guidance**: Patterns in `_local/starter-kit/`; conventions for routes, services, DAOs, jobs

**Gate**: PASS — all principles addressed by starter-kit design.

**Post–Phase 1 re-check**: PASS — data-model.md, contracts/, quickstart.md align with Constitution. No new violations.

## Project Structure

### Documentation (this feature)

```text
specs/001-starter-application/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── api/
│   ├── main.py               # App entry, lifespan, middleware, route registration
│   ├── dependencies.py      # Auth, services, config Depends()
│   ├── routes/
│   │   ├── health.py        # /health, /health/db
│   │   └── jobs/
│   │       └── router.py    # POST/GET /jobs (recovery is scheduled worker, not API)
│   └── schemas/
├── config/
│   ├── supabase.py          # get_supabase_client()
│   └── database.py          # Transaction pooler, AsyncSession
├── deployment/
│   ├── modal_app.py         # API ASGI wrapper
│   ├── modal_workers.py     # Sample worker + recovery
│   └── deploy.py
├── middleware/
├── models/
│   ├── config.py            # Settings, load_settings()
│   ├── common.py            # ErrorResponse
│   ├── responses.py         # ValidatedJWTUser (user_id only; no company)
│   └── jobs/
│       ├── job.py           # JobCreateRequest, JobResponse
│       └── job_status.py     # JobStatus, JobType
├── services/
│   ├── supabase/            # Optional: BaseDAO for future CRUD (not used by jobs starter)
│   ├── job_queue/           # service, spawner, database, queue
│   └── database/
└── utils/                   # logging, rate_limiter

tests/
├── contract/
├── integration/
└── unit/

scripts/
├── dev.py                   # Local uvicorn run
└── migrate.py               # DB migration

docs/
└── db/
    └── migrations/          # 001_initial.sql or equivalent
```

**Structure Decision**: Single-project layout per starter-kit `project-structure.md`. API, config, deployment, models, services, and utils under `src/`. Tests and scripts at repo root.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | — | — |
