# Jobs API Contract

**Base path**: `/jobs`  
**Auth**: JWT required (`Authorization: Bearer <token>`) for create, list, get. Recovery may use admin auth.

---

## POST /jobs

Create a new job.

**Request**:

```json
{
  "job_type": "sample_task",
  "job_parameters": {}
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| job_type | string | Yes | Must be valid JobType (e.g. `sample_task`) |
| job_parameters | object | Yes | Parameters for the job type |

**Response**: `201 Created`

```json
{
  "id": "uuid",
  "job_type": "sample_task",
  "status": "pending",
  "user_id": "uuid",
  "job_parameters": {},
  "retry_count": 0,
  "created_at": "ISO8601",
  "updated_at": "ISO8601",
  "started_at": null,
  "completed_at": null,
  "error_message": null,
  "error_type": null,
  "data_references": null
}
```

**Errors**:
- `400 Bad Request` — Invalid job_type or job_parameters
- `401 Unauthorized` — Missing or invalid JWT
- `409 Conflict` — Duplicate job (if applicable)

---

## GET /jobs/{job_id}

Get job by ID. User-scoped: returns only jobs created by the authenticated user.

**Path params**: `job_id` (UUID)

**Response**: `200 OK`

```json
{
  "id": "uuid",
  "job_type": "sample_task",
  "status": "completed",
  "user_id": "uuid",
  "job_parameters": {},
  "retry_count": 0,
  "created_at": "ISO8601",
  "updated_at": "ISO8601",
  "started_at": "ISO8601",
  "completed_at": "ISO8601",
  "error_message": null,
  "error_type": null,
  "data_references": {}
}
```

**Errors**:
- `401 Unauthorized` — Missing or invalid JWT
- `404 Not Found` — Job not found or not owned by the authenticated user

---

## GET /jobs

List jobs with optional filters. User-scoped: returns only jobs created by the authenticated user.

**Query params**:
| Param | Type | Description |
|-------|------|-------------|
| status | string | Filter by status (pending, processing, completed, failed) |
| job_type | string | Filter by job type |
| limit | int | Page size (default 20) |
| offset | int | Pagination offset (default 0) |

**Response**: `200 OK`

```json
{
  "items": [
    {
      "id": "uuid",
      "job_type": "sample_task",
      "status": "completed",
      "created_at": "ISO8601",
      ...
    }
  ],
  "total": 42
}
```

**Errors**:
- `401 Unauthorized` — Missing or invalid JWT

---

## Recovery (scheduled worker, not an API)

Orphan and stuck job recovery is performed by a **scheduled Modal worker** that runs every 15 minutes. There is no API endpoint for recovery.

- **Stuck**: `status='processing'` and `updated_at` older than `JOB_STUCK_TIMEOUT_MINUTES` (env var, default 15)
- **Orphaned**: `status='pending'` and `created_at` older than timeout
