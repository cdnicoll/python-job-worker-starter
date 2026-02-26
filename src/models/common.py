"""Common models."""
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response; MUST include request_id for correlation."""

    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable message")
    request_id: str | None = Field(None, description="Request ID for correlation")
