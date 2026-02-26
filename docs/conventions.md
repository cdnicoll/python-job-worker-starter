# Development Conventions

Patterns and conventions for this project. See `_local/starter-kit/` for full architecture documentation.

## Patterns

- **Service → DAO**: Services orchestrate logic; DAOs encapsulate data access (Supabase or asyncpg).
- **Job lifecycle**: Create → PGMQ backup → Modal spawn → process → update status.
- **Auth**: Use `get_validated_jwt_user` for job routes (user_id only; no company).

## Adding Features

1. **New route**: Create `src/api/routes/{domain}/router.py`, register in `main.py`.
2. **New service**: Create `src/services/{domain}/service.py`, add `get_*_service()` in dependencies.
3. **New job type**: Add to `JobType` enum, map in spawner, implement in `JobQueueService.process_job()`.

## Error Handling

- Use `HTTPException` for expected errors (400, 401, 404).
- Global handler returns `ErrorResponse` with `request_id` for 500s.

## Logging

- Structured JSON format; include `request_id` when available.
- Use `get_logger(__name__)` from `src.utils.logging`.
