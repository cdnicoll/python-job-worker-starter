# Data Model: Starter Application

**Feature**: 001-starter-application  
**Date**: 2025-02-26 | **Phase**: 1

## Entities

### 1. Job

Background job record stored in `public.jobs`.

| Field | Type | Nullable | Description |
|-------|------|---------|-------------|
| id | UUID | No | Primary key |
| job_type | TEXT | No | Enum: `sample_task`, etc. |
| status | TEXT | No | `pending`, `processing`, `completed`, `failed` |
| user_id | UUID | No | Creator (references auth.users) |
| job_parameters | JSONB | Yes | Input parameters |
| error_message | TEXT | Yes | Failure message |
| error_type | TEXT | Yes | Error class name |
| error_context | JSONB | Yes | Additional error details |
| data_references | JSONB | Yes | Output references (e.g. file IDs) |
| retry_count | INT | No | For recovery logic (default 0) |
| created_at | TIMESTAMPTZ | No | Insert time |
| updated_at | TIMESTAMPTZ | No | Last update |
| started_at | TIMESTAMPTZ | Yes | When processing began |
| completed_at | TIMESTAMPTZ | Yes | When finished |

**Indexes**:
- `jobs_status_idx` on `(status)`
- `jobs_user_id_idx` on `(user_id)`
- `jobs_created_at_idx` on `(created_at)` for recovery queries

**State transitions**:
- `pending` → `processing` (worker starts)
- `processing` → `completed` (success)
- `processing` → `failed` (error or timeout)
- `pending` → `failed` (orphan recovery)

---

### 2. PGMQ Queue (job_queue)

Not a table — PGMQ extension queue for job backup.

- **Queue name**: `job_queue` (configurable)
- **Message payload**: `{ job_id, job_type, user_id, job_parameters }`
- **Purpose**: Backup for jobs; recovery worker can reconcile orphans
- **Lifecycle**: Message sent on job create; deleted on successful processing

*No profiles table or company-related schema; starter is domain-agnostic.*

---

## Validation Rules

### Job

- `job_type` MUST be a valid `JobType` enum value
- `status` MUST be one of: `pending`, `processing`, `completed`, `failed`
- `job_parameters` MUST conform to per-type validation in `JobQueueService.validate_job_parameters()`
- `retry_count` >= 0

## Migration Script

**Location**: `scripts/migrate.py` or `docs/db/migrations/001_initial.sql`

**Idempotent operations**:
- `CREATE EXTENSION IF NOT EXISTS pgmq`
- `CREATE TABLE IF NOT EXISTS jobs (...)`
- `SELECT pgmq.create('job_queue')` (or equivalent, with existence check)
