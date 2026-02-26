# Feature Specification: Starter Application

**Feature Branch**: `001-starter-application`  
**Created**: 2025-02-26  
**Status**: Draft  
**Input**: User description: "using _local/starter-kit we need to create a starter application"

## Clarifications

### Session 2025-02-26

- Q: Who may call `POST /jobs/recover`? → A: Recovery is not an API endpoint; it is a scheduled Modal worker that runs every 15 minutes to recover orphaned/stuck jobs.
- Q: What does `GET /jobs` return? → A: User-scoped — only jobs created by the authenticated user.
- Q: Is JWT auth required for all job endpoints? → A: Yes — JWT required for all job endpoints; no unauthenticated mode.
- Q: For sample_task, should the system prevent duplicate jobs? → A: No — allow unlimited sample_task jobs; no duplicate check.
- Q: What is the default JOB_STUCK_TIMEOUT_MINUTES for recovery? → A: 15 minutes; configurable via .env variable.
- Q: Is the profiles table required for the starter? → A: Optional — if profile missing, allow auth with company_id=null. Remove all company-related concepts; keep starter agnostic.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Verify API Health (Priority: P1)

As a developer or operator, I need to verify the API and its dependencies are running so I can confirm deployment success and troubleshoot connectivity issues.

**Why this priority**: Health checks are foundational for deployment probes, monitoring, and first-run validation.

**Independent Test**: Can be fully tested by calling `GET /health` and `GET /health/db` and receiving 200 responses with `{"status": "ok"}`.

**Acceptance Scenarios**:

1. **Given** the API is running, **When** I call `GET /health`, **Then** I receive 200 and `{"status": "ok"}`
2. **Given** the API and database are reachable, **When** I call `GET /health/db`, **Then** I receive 200 and `{"status": "ok"}`

---

### User Story 2 - Create and Monitor Background Jobs (Priority: P1)

As a client application, I need to create background jobs via the API and monitor their status so I can offload long-running work and track completion.

**Why this priority**: Jobs are the core async pattern; sample worker demonstrates the full lifecycle for future workers.

**Independent Test**: Can be tested by `POST /jobs` with `{"job_type": "sample_task", "job_parameters": {}}`, then `GET /jobs/{id}` to poll status until completed.

**Acceptance Scenarios**:

1. **Given** I am authenticated, **When** I `POST /jobs` with valid `job_type` and `job_parameters`, **Then** I receive a job object with `id`, `status`, `created_at`
2. **Given** a job exists, **When** I call `GET /jobs/{job_id}`, **Then** I receive the job with current status
3. **Given** jobs exist for the current user, **When** I call `GET /jobs` with optional filters, **Then** I receive a list of my jobs with pagination (user-scoped)

---

### User Story 3 - Recover Stuck or Orphaned Jobs (Priority: P2)

As the system, a scheduled Modal worker runs every 15 minutes to mark stuck or orphaned jobs as failed, so jobs do not remain indefinitely in `processing` or `pending`.

**Why this priority**: Automated recovery ensures cleanup without manual intervention or API exposure.

**Independent Test**: Can be tested by creating jobs, simulating stuck state (e.g. worker crash), waiting for the scheduled run, and verifying jobs are marked failed.

**Acceptance Scenarios**:

1. **Given** jobs exist with `status='processing'` and `updated_at` older than timeout, **When** the recovery worker runs, **Then** those jobs are marked failed
2. **Given** jobs exist with `status='pending'` and `created_at` older than timeout, **When** the recovery worker runs, **Then** those jobs are marked failed

---

### User Story 4 - Bootstrap Database Schema (Priority: P1)

As a developer, I need to run a migration script to create the minimum schema so I can set up a new environment in one command.

**Why this priority**: Without schema, the API cannot function; idempotent migrations enable repeatable setup.

**Independent Test**: Can be tested by running `uv run python scripts/migrate.py` and verifying `jobs` table and PGMQ `job_queue` exist.

**Acceptance Scenarios**:

1. **Given** a fresh database, **When** I run the migration script, **Then** `jobs` table and PGMQ `job_queue` exist
2. **Given** schema already exists, **When** I run the migration script again, **Then** it completes without error (idempotent)

---

### Edge Cases

- What happens when JWT is invalid or expired? → 401 with `WWW-Authenticate: Bearer`
- What happens when job parameters are invalid for the job type? → 400 with validation error
- Can users create duplicate sample_task jobs? → Yes — no duplicate check for sample_task; future job types may add entity-based deduplication
- What happens when database is unreachable? → `/health/db` returns non-200; API may degrade gracefully
- What happens when Modal spawn fails? → Job remains pending; recovery worker can mark as failed

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST expose `GET /health` returning 200 when the app is up
- **FR-002**: System MUST expose `GET /health/db` returning 200 when Supabase and/or transaction pooler are reachable
- **FR-003**: System MUST provide a sample Modal worker (`process_sample_job` / `sample_task`) as the reference pattern for future workers
- **FR-004**: System MUST expose `POST /jobs` to create jobs — validates params, inserts into DB, spawns worker, returns job ID and status
- **FR-005**: System MUST expose `GET /jobs/{job_id}` to get job status by ID; users MAY access only their own jobs (404 if job belongs to another user)
- **FR-006**: System MUST expose `GET /jobs` to list jobs with optional filters (status, type, pagination); results MUST be user-scoped (only jobs created by the authenticated user)
- **FR-007**: System MUST run a scheduled Modal recovery worker every 15 minutes to mark stuck (`processing` + timeout) and orphaned (`pending` + timeout) jobs as failed; timeout configurable via `JOB_STUCK_TIMEOUT_MINUTES` (default 15)
- **FR-008**: System MUST provide an idempotent database migration script creating `jobs` table and PGMQ queue (no `profiles` table; no company-related schema)
- **FR-009**: System MUST use JWT auth via JWKS for all job routes; no unauthenticated access; use `get_validated_jwt_user` (user_id only; no company lookup)
- **FR-010**: System MUST include middleware: CORS, metrics, rate limiter, request ID (X-Request-ID)

### Key Entities

- **Job**: `id`, `job_type`, `status`, `user_id`, `job_parameters`, `error_message`, `error_type`, `error_context`, `data_references`, `retry_count`, `created_at`, `updated_at`, `started_at`, `completed_at`

*No company-related entities or fields; starter remains domain-agnostic.*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: New developer can clone, run migration, and have API responding to `/health` in under 10 minutes
- **SC-002**: Health check endpoints return 200 when dependencies are healthy
- **SC-003**: Sample job can be created via `POST /jobs` and completes via Modal worker
- **SC-004**: Scheduled recovery worker (every 15 min) correctly identifies and marks stuck/orphaned jobs as failed
- **SC-005**: OpenAPI docs available at `/docs`; setup documented in quickstart
