"""Jobs API routes."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import get_validated_jwt_user
from src.models.jobs.job import JobCreateRequest, JobResponse, JobListResponse
from src.models.responses import ValidatedJWTUser
from src.services.job_queue.service import JobQueueService

router = APIRouter(prefix="/jobs", tags=["jobs"])


def get_job_queue_service() -> JobQueueService:
    """Get job queue service."""
    return JobQueueService()


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    request: JobCreateRequest,
    current_user: ValidatedJWTUser = Depends(get_validated_jwt_user),
    service: JobQueueService = Depends(get_job_queue_service),
) -> JobResponse:
    """Create a job."""
    try:
        job = await service.create_job(
            job_type=request.job_type,
            user_id=current_user.user_id,
            job_parameters=request.job_parameters,
        )
        return JobResponse(**job)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID,
    current_user: ValidatedJWTUser = Depends(get_validated_jwt_user),
    service: JobQueueService = Depends(get_job_queue_service),
) -> JobResponse:
    """Get job by ID (user-scoped)."""
    job = await service.get_job(str(job_id), current_user.user_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse(**job)


@router.get("", response_model=JobListResponse)
async def list_jobs(
    status: str | None = None,  # noqa: A002
    job_type: str | None = None,
    limit: int = 20,
    offset: int = 0,
    current_user: ValidatedJWTUser = Depends(get_validated_jwt_user),
    service: JobQueueService = Depends(get_job_queue_service),
) -> JobListResponse:
    """List jobs (user-scoped)."""
    items, total = await service.list_jobs(
        user_id=current_user.user_id,
        status=status,
        job_type=job_type,
        limit=limit,
        offset=offset,
    )
    return JobListResponse(items=[JobResponse(**j) for j in items], total=total)
