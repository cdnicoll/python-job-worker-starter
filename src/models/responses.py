"""Response models."""
from pydantic import BaseModel


class ValidatedJWTUser(BaseModel):
    """Authenticated user from JWT (user_id only; no company)."""

    user_id: str
