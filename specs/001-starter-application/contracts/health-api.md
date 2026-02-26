# Health API Contract

**Base path**: `/health`  
**Auth**: None (public)

## Endpoints

### GET /health

API liveness check.

**Response**: `200 OK`

```json
{
  "status": "ok"
}
```

**Errors**: None expected (if API is up, returns 200).

---

### GET /health/db

Database connectivity check (Supabase and/or transaction pooler).

**Response**: `200 OK`

```json
{
  "status": "ok"
}
```

**Errors**:
- `503 Service Unavailable` — Database unreachable
