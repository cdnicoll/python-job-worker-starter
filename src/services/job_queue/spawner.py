"""Modal job spawner."""
import modal

from src.models.config import load_settings
from src.models.jobs.job_status import JobType

# Map job types to Modal function names
JOB_TIER_MAPPING = {
    JobType.SAMPLE_TASK.value: "process_sample_job",
}


async def spawn_job(job_id: str, job_type: str, user_id: str, job_parameters: dict) -> None:
    """Spawn job to Modal worker."""
    func_name = JOB_TIER_MAPPING.get(job_type, "process_sample_job")
    settings = load_settings()
    app_name = f"Job-Worker-{settings.environment.capitalize()}"

    try:
        func = modal.Function.from_name(app_name, func_name)
        func.spawn(job_id, job_type, user_id, job_parameters)
    except Exception as e:
        raise RuntimeError(f"Failed to spawn job: {e}") from e
