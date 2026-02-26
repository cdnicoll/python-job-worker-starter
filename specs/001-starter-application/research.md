# Research: Starter Application

**Feature**: 001-starter-application  
**Date**: 2025-02-26 | **Phase**: 0

## Context

The starter application is built from `_local/starter-kit` blueprint. No unknowns were marked as NEEDS CLARIFICATION — the starter-kit provides full architecture and technology choices. This document consolidates decisions, rationale, and alternatives for traceability.

---

## 1. Framework & Runtime

**Decision**: FastAPI, Python 3.11+

**Rationale**: Async HTTP API, OpenAPI docs, dependency injection. Fast startup; strong typing. Python 3.11+ for performance and modern syntax.

**Alternatives considered**:
- Flask/Django: Synchronous; async support less mature.
- Node/Express: Different ecosystem; starter-kit targets Python stack.

---

## 2. Database & Storage

**Decision**: Supabase (PostgreSQL) with dual access: Supabase Client (PostgREST, RLS) + asyncpg (transaction pooler, PGMQ, jobs).

**Rationale**: Supabase provides PostgREST, RLS, and auth. asyncpg needed for raw SQL, PGMQ, and transactional job logic. Shared Pooler (IPv4-compatible) for Modal compatibility.

**Alternatives considered**:
- Supabase-only: Cannot handle PGMQ, multi-statement transactions, or jobs table efficiently.
- SQLAlchemy ORM models: Starter-kit uses Pydantic + raw SQL; Supabase/PostgREST for CRUD.

---

## 3. Authentication

**Decision**: Supabase Auth (JWT) with JWKS verification.

**Rationale**: Asymmetric verification via JWKS; no shared secret. Cached 10 min. `get_current_user` (profile lookup) vs `get_validated_jwt_user` (identity only) for flexibility.

**Alternatives considered**:
- API key: Less granular; no user context.
- Symmetric JWT: Requires secret sharing; JWKS is more secure.

---

## 4. Background Jobs

**Decision**: Modal workers + PGMQ backup. Immediate spawn; PGMQ for recovery.

**Rationale**: Modal provides serverless compute; tiered workers (GPU, browser, LLM, API). PGMQ stores messages as backup; recovery worker handles orphans. Single sample worker (`sample_task`) as pattern.

**Alternatives considered**:
- Celery/Redis: Additional infra; Modal is serverless, no broker to manage.
- PGMQ-only: No immediate spawn; Modal gives faster feedback.

---

## 5. Deployment & Hosting

**Decision**: Modal for API and workers; environment-driven (develop/production).

**Rationale**: Single platform for API and workers; secrets via Modal Secrets; env-specific app names.

**Alternatives considered**:
- Vercel/Railway: No native worker support; would need separate job queue.
- AWS Lambda + SQS: More infra; Modal simplifies deployment.

---

## 6. Configuration & Secrets

**Decision**: pydantic-settings; Infisical + Modal Secrets for env-specific secrets.

**Rationale**: Validation on load; no hardcoded values. Secrets via env or secrets manager.

**Alternatives considered**:
- .env only: Insufficient for production; Infisical/Modal Secrets for deploy.

---

## 7. Observability

**Decision**: Request ID middleware (X-Request-ID); structured logging; metrics middleware.

**Rationale**: Constitution requires request tracing; structured logs support aggregation.

**Alternatives considered**:
- Ad-hoc logging: No correlation; request ID is minimal and effective.

---

## 8. Package Manager

**Decision**: uv for dependencies and scripts.

**Rationale**: Fast, reliable; `uv run` for single-command execution.

---

## Summary

| Area | Decision | Key Rationale |
|------|----------|---------------|
| Framework | FastAPI | Async, OpenAPI, DI |
| DB | Supabase + asyncpg | Supabase for CRUD/RLS; asyncpg for jobs, PGMQ |
| Auth | JWT + JWKS | Asymmetric, cached |
| Jobs | Modal + PGMQ | Serverless + backup |
| Deploy | Modal | API + workers unified |
| Config | pydantic-settings | Validation, env-driven |
| Observability | X-Request-ID, structured logs | Tracing, aggregation |
| Package | uv | Fast, single-command |
