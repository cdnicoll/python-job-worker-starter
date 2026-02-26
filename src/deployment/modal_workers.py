"""Modal worker functions."""
import os
import sys

# Ensure src is on path when running in Modal
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import modal

# Create Modal app for workers
app = modal.App("Job-Worker-develop")

# Default image
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "fastapi",
    "uvicorn",
    "supabase",
    "pyjwt[crypto]",
    "cryptography",
    "sqlalchemy[asyncio]",
    "asyncpg",
    "pydantic",
    "pydantic-settings",
    "httpx",
    "python-dotenv",
)


@app.function(
    image=image,
    timeout=300,
    secrets=[],  # Will use modal.Secret.from_name("supabase-credentials-develop") etc.
)
async def process_sample_job(job_id: str, job_type: str, user_id: str, job_parameters: dict) -> None:
    """Process sample_task job."""
    await _process_job(job_id, job_type, user_id, job_parameters)


@app.function(
    image=image,
    timeout=300,
    schedule=modal.Period(minutes=15),
    secrets=[],
)
async def recover_orphaned_jobs() -> None:
    """Scheduled recovery: mark stuck and orphaned jobs as failed."""
    from src.services.job_queue import database

    stuck = await database.find_stuck_jobs()
    orphaned = await database.find_orphaned_jobs()

    for job in stuck:
        await database.mark_job_failed(
            str(job["id"]),
            "Job exceeded maximum processing time",
            "JobTimeoutError",
        )
    for job in orphaned:
        await database.mark_job_failed(
            str(job["id"]),
            "Job never started (pending timeout)",
            "PendingTimeoutError",
        )


async def _process_job(job_id: str, job_type: str, user_id: str, job_parameters: dict) -> None:
    """Shared job processing logic."""
    from src.services.job_queue.service import JobQueueService

    svc = JobQueueService()
    await svc.process_job(job_id, job_type, user_id, job_parameters)
