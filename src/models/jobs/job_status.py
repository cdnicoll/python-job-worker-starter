"""Job status and type enums."""
from enum import Enum


class JobStatus(str, Enum):
    """Job status values."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobType(str, Enum):
    """Job type values."""

    SAMPLE_TASK = "sample_task"
