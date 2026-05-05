"""
Pydantic schemas — request validation and response serialization.
"""

from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional


# ── Incoming contact form payload ───────────────────────────────────────────
class MessageCreate(BaseModel):
    first_name : str
    last_name  : str
    email      : EmailStr
    phone      : Optional[str] = None
    service    : Optional[str] = None
    message    : str

    @field_validator("first_name", "last_name", "message")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("This field cannot be empty.")
        return v

    @field_validator("message")
    @classmethod
    def min_length(cls, v: str) -> str:
        if len(v.strip()) < 10:
            raise ValueError("Message must be at least 10 characters.")
        return v


# ── Outgoing message response ────────────────────────────────────────────────
class MessageOut(BaseModel):
    id           : int
    first_name   : str
    last_name    : str
    email        : str
    phone        : Optional[str]
    service      : Optional[str]
    message      : str
    submitted_at : datetime
    is_read      : bool

    model_config = {"from_attributes": True}


# ── Admin stats response ─────────────────────────────────────────────────────
class StatsOut(BaseModel):
    total  : int
    unread : int
    read   : int
