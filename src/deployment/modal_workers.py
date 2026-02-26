"""Modal worker functions."""
import os
import sys

# Ensure src is on path when running in Modal
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import modal

# Environment-driven app name (set by deploy script or .env)
_env = os.environ.get("ENVIRONMENT", "develop")
app = modal.App(f"Job-Worker-{_env}")

# Base image for all workers
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

# Modal secrets for DB/config (create via scripts/create_modal_secrets.sh)
_secrets = [
    modal.Secret.from_name(f"supabase-credentials-{_env}"),
    modal.Secret.from_name(f"app-config-{_env}"),
]


@app.function(
    image=image,
    timeout=300,
    secrets=_secrets,
)
async def process_sample_job(job_id: str, job_type: str, user_id: str, job_parameters: dict) -> None:
    """Process sample_task job."""
    await _process_job(job_id, job_type, user_id, job_parameters)


# Tiered workers (stubs for future job types per modal-jobs.md)
@app.function(
    image=image,
    timeout=900,  # 15 min
    cpu=4,
    memory=8192,  # 8GB
    secrets=_secrets,
)
async def process_gpu_job(job_id: str, job_type: str, user_id: str, job_parameters: dict) -> None:
    """Process GPU-tier jobs (e.g. document_index)."""
    await _process_job(job_id, job_type, user_id, job_parameters)


@app.function(
    image=image,
    timeout=300,  # 5 min
    cpu=2,
    memory=2048,  # 2GB
    secrets=_secrets,
)
async def process_browser_job(job_id: str, job_type: str, user_id: str, job_parameters: dict) -> None:
    """Process browser-tier jobs (e.g. web_crawl)."""
    await _process_job(job_id, job_type, user_id, job_parameters)


@app.function(
    image=image,
    timeout=300,  # 5 min
    cpu=1,
    memory=1024,  # 1GB
    secrets=_secrets,
)
async def process_llm_job(job_id: str, job_type: str, user_id: str, job_parameters: dict) -> None:
    """Process LLM-tier jobs (e.g. document_process, llm_task)."""
    await _process_job(job_id, job_type, user_id, job_parameters)


@app.function(
    image=image,
    timeout=120,  # 2 min
    cpu=0.5,
    memory=512,
    secrets=_secrets,
)
async def process_api_job(job_id: str, job_type: str, user_id: str, job_parameters: dict) -> None:
    """Process API-tier jobs (e.g. company_enrich)."""
    await _process_job(job_id, job_type, user_id, job_parameters)


@app.function(
    image=image,
    timeout=300,
    schedule=modal.Period(minutes=15),
    secrets=_secrets,
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
