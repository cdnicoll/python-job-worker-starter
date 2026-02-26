# Tasks: Starter Application

**Input**: Design documents from `/specs/001-starter-application/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Not requested in spec — omitted.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- Single project: `src/`, `tests/`, `scripts/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project directory structure per plan: `src/api/`, `src/config/`, `src/deployment/`, `src/middleware/`, `src/models/`, `src/models/jobs/`, `src/services/`, `src/services/job_queue/`, `src/utils/`, `tests/`, `scripts/`, `docs/db/migrations/`
- [ ] T002 Create `pyproject.toml` with uv, dependencies: fastapi, uvicorn, supabase, modal, pyjwt, cryptography, sqlalchemy, asyncpg, pydantic, pydantic-settings, httpx, python-dotenv
- [ ] T003 Create `.env.example` with ENVIRONMENT, SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY, SUPABASE_SECRET_KEY, TRANSACTION_POOLER_URL, JOB_STUCK_TIMEOUT_MINUTES, MODAL_APP_NAME
- [ ] T004 [P] Configure ruff in `pyproject.toml` for linting and formatting

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story. Includes migration script (US4).

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 [US4] Create idempotent migration script `scripts/migrate.py` creating `jobs` table (per data-model.md), PGMQ extension, `job_queue` queue
- [ ] T006 Create `src/models/config.py` with Settings (pydantic-settings), load_settings(), JOB_STUCK_TIMEOUT_MINUTES (default 15)
- [ ] T007 Create `src/config/supabase.py` with get_supabase_client() factory
- [ ] T008 Create `src/config/database.py` with transaction pooler, AsyncSession, check_transaction_pooler_health()
- [ ] T009 Create `src/utils/logging.py` with get_logger(), setup_logging(); logging MUST be structured (JSON or key-value) and include request_id when available
- [ ] T010 Create `src/api/dependencies.py` with get_settings(), get_validated_jwt_user() (JWKS, no company lookup)
- [ ] T011 Create `src/middleware/` with CORS, metrics, rate limiter, request ID (X-Request-ID) middleware
- [ ] T012 Create `src/models/common.py` with ErrorResponse model (MUST include request_id for correlation)
- [ ] T013 Create `src/models/responses.py` with ValidatedJWTUser (user_id only)
- [ ] T014 Create `src/api/main.py` with FastAPI app, lifespan, middleware order, global error handler that MUST pass request_id into ErrorResponse
- [ ] T015 Create `scripts/dev.py` to run uvicorn with `src.api.main:app` on port 8000 with reload

**Checkpoint**: Foundation ready — migration runnable, config loaded, auth and middleware in place

---

## Phase 3: User Story 1 - Verify API Health (Priority: P1) 🎯 MVP

**Goal**: Health endpoints confirm API and database are running.

**Independent Test**: `curl http://localhost:8000/health` and `curl http://localhost:8000/health/db` return 200 with `{"status":"ok"}`.

### Implementation for User Story 1

- [ ] T016 [P] [US1] Create `src/api/routes/health.py` with GET /health (liveness) and GET /health/db (DB connectivity via check_transaction_pooler_health; return 503 when DB unreachable)
- [ ] T017 [US1] Register health router in `src/api/main.py`; ensure /docs available

**Checkpoint**: User Story 1 complete — health endpoints return 200 when deps healthy

---

## Phase 4: User Story 2 - Create and Monitor Background Jobs (Priority: P1)

**Goal**: Clients can create jobs via POST /jobs, list via GET /jobs, get by ID via GET /jobs/{id}; user-scoped; JWT required.

**Independent Test**: POST /jobs with JWT and `{"job_type":"sample_task","job_parameters":{}}` returns job; GET /jobs/{id} returns status; sample worker processes job.

### Implementation for User Story 2

- [ ] T018 [P] [US2] Create `src/models/jobs/job_status.py` with JobStatus, JobType enums (include sample_task)
- [ ] T019 [P] [US2] Create `src/models/jobs/job.py` with JobCreateRequest, JobResponse, JobListResponse per contracts
- [ ] T020 [US2] Create `src/services/job_queue/database.py` with create_job, get_job_by_id, update_job_status, list_jobs (user-scoped), store_error_info, store_data_references
- [ ] T021 [US2] Create `src/services/job_queue/queue.py` with PGMQ send_job_message, read_job_messages, delete_job_message
- [ ] T022 [US2] Create `src/services/job_queue/spawner.py` with spawn_job() routing sample_task to Modal
- [ ] T023 [US2] Create `src/services/job_queue/service.py` with JobQueueService.create_job, process_job (sample_task logic), validate_job_parameters (no duplicate check for sample_task)
- [ ] T024 [US2] Create `src/deployment/modal_workers.py` with process_sample_job worker (job_id, job_type, user_id, job_parameters); _process_job helper
- [ ] T025 [US2] Create `src/api/routes/jobs/router.py` with POST /jobs, GET /jobs/{job_id}, GET /jobs (filters: status, job_type, limit, offset); Depends(get_validated_jwt_user)
- [ ] T026 [US2] Register jobs router in `src/api/main.py`; add get_job_queue_service in dependencies

**Checkpoint**: User Story 2 complete — jobs CRUD works; sample_task completes via Modal worker

---

## Phase 5: User Story 3 - Recover Stuck or Orphaned Jobs (Priority: P2)

**Goal**: Scheduled Modal worker runs every 15 minutes to mark stuck (processing + timeout) and orphaned (pending + timeout) jobs as failed.

**Independent Test**: Create job, simulate stuck state, wait for scheduled run; verify job marked failed.

### Implementation for User Story 3

- [ ] T027 [US3] Add find_stuck_jobs, find_orphaned_jobs in `src/services/job_queue/database.py` using JOB_STUCK_TIMEOUT_MINUTES
- [ ] T028 [US3] Add recover_orphaned_jobs scheduled function in `src/deployment/modal_workers.py` with Period(minutes=15); call recovery logic to mark jobs failed

**Checkpoint**: User Story 3 complete — recovery worker runs every 15 min

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Deployment and validation

- [ ] T029 [P] Create `src/deployment/modal_app.py` with @asgi_app() wrapping FastAPI app for Modal
- [ ] T030 [P] Create `src/deployment/deploy.py` (or pyproject script) for deploy_dev/deploy_prod
- [ ] T031 [P] Add create_modal_secrets.sh or document Modal secrets setup
- [ ] T032 [P] Create `docs/quickstart.md` (or README) with setup steps per specs/001-starter-application/quickstart.md
- [ ] T033 [P] Add docs/conventions.md or README section referencing patterns from `_local/starter-kit/`; ensure developer guidance per constitution
- [ ] T034 Run quickstart validation: clone, uv sync, migrate, dev, verify /health and /health/db

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational
- **User Story 2 (Phase 4)**: Depends on Foundational (migration, auth, config)
- **User Story 3 (Phase 5)**: Depends on Foundational and US2 (jobs table, recovery logic)
- **Polish (Phase 6)**: Depends on all user stories

### User Story Dependencies

- **US1**: No dependencies on other stories — can start after Foundational
- **US2**: No dependencies on US1 — can start after Foundational
- **US3**: Depends on US2 (jobs table, JobQueueService) — run after US2

### Parallel Opportunities

- Phase 1: T004 [P] with T001–T003
- Phase 2: T006–T013 can be parallelized (different files)
- Phase 3: T016 [P]
- Phase 4: T018, T019 [P]; T029–T033 [P] in Phase 6
- US1 and US2 can be worked in parallel after Foundational (different developers)

---

## Parallel Example: User Story 2

```bash
# Models in parallel:
Task T018: "Create job_status.py in src/models/jobs/"
Task T019: "Create job.py in src/models/jobs/"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (Health)
4. **STOP and VALIDATE**: curl /health, /health/db
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → migration works, config and auth ready
2. Add US1 → Health endpoints → Deploy/Demo (minimal MVP)
3. Add US2 → Jobs CRUD + sample worker → Deploy/Demo
4. Add US3 → Recovery worker → Deploy/Demo
5. Polish → Modal deploy, quickstart validation

### Parallel Team Strategy

- Team completes Setup + Foundational together
- Developer A: US1 (Health)
- Developer B: US2 (Jobs) — can start in parallel with A
- Developer C: US3 (Recovery) — after US2

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to user story for traceability
- No duplicate check for sample_task (per clarification)
- Use get_validated_jwt_user (no company) for job routes
- JOB_STUCK_TIMEOUT_MINUTES in .env (default 15)
