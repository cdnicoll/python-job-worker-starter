"""Job request/response models."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.models.jobs.job_status import JobType


class JobCreateRequest(BaseModel):
    """Request to create a job."""

    job_type: str = Field(..., description="Job type (e.g. sample_task)")
    job_parameters: dict = Field(default_factory=dict, description="Job parameters")


class JobResponse(BaseModel):
    """Job response."""

    id: UUID
    job_type: str
    status: str
    user_id: UUID
    job_parameters: dict | None
    retry_count: int
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None
    error_type: str | None
    data_references: dict | None


class JobListResponse(BaseModel):
    """Paginated job list response."""

    items: list[JobResponse]
    total: int
