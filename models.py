"""
Database models for Emkay Surveys backend.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from database import Base
from datetime import datetime


class Message(Base):
    __tablename__ = "messages"

    id           = Column(Integer, primary_key=True, index=True)
    first_name   = Column(String(80),  nullable=False)
    last_name    = Column(String(80),  nullable=False)
    email        = Column(String(150), nullable=False, index=True)
    phone        = Column(String(30),  nullable=True)
    service      = Column(String(100), nullable=True)
    message      = Column(Text,        nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_read      = Column(Boolean, default=False, nullable=False)
