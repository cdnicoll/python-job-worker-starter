"""Job queue service."""
from datetime import datetime
from uuid import UUID

from src.models.jobs.job_status import JobStatus, JobType

from . import database
from . import queue
from . import spawner


class JobQueueService:
    """Orchestrates job creation, processing, and listing."""

    def __init__(self) -> None:
        pass

    async def create_job(self, job_type: str, user_id: str, job_parameters: dict) -> dict:
        """Create job, send to PGMQ, spawn Modal worker."""
        self.validate_job_parameters(job_type, job_parameters)

        job = await database.create_job(job_type, user_id, job_parameters)
        job_id = str(job["id"])

        await queue.send_job_message(job_id, job_type, user_id, job_parameters)
        await spawner.spawn_job(job_id, job_type, user_id, job_parameters)

        return job

    def validate_job_parameters(self, job_type: str, job_parameters: dict) -> None:
        """Validate parameters per job type. No duplicate check for sample_task."""
        if job_type not in [t.value for t in JobType]:
            raise ValueError(f"Invalid job_type: {job_type}")
        # sample_task has no required params; no duplicate check per spec

    async def process_job(self, job_id: str, job_type: str, user_id: str, job_parameters: dict) -> None:
        """Process job (called from Modal worker)."""
        await database.update_job_status(job_id, JobStatus.PROCESSING.value, started_at=datetime.utcnow())

        try:
            if job_type == JobType.SAMPLE_TASK.value:
                # Minimal logic for sample worker
                await database.store_data_references(job_id, {"completed": True})
                await database.update_job_status(
                    job_id,
                    JobStatus.COMPLETED.value,
                    started_at=datetime.utcnow(),
                    completed_at=datetime.utcnow(),
                )
            else:
                raise ValueError(f"Unknown job_type: {job_type}")
        except Exception as e:
            await database.store_error_info(job_id, str(e), type(e).__name__, {"job_parameters": job_parameters})
            await database.update_job_status(job_id, JobStatus.FAILED.value)

    async def get_job(self, job_id: str, user_id: str) -> dict | None:
        """Get job by ID (user-scoped)."""
        return await database.get_job_by_id(job_id, user_id)

    async def list_jobs(
        self,
        user_id: str,
        status: str | None = None,
        job_type: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[dict], int]:
        """List jobs (user-scoped)."""
        return await database.list_jobs(user_id, status, job_type, limit, offset)
