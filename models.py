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

class Suggestion(Base):
    __tablename__ = "suggestions"
    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(String(100), nullable=True)
    suggestion   = Column(Text, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class ScheduledCall(Base):
    __tablename__ = "scheduled_calls"
    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(String(100), nullable=False)
    phone        = Column(String(30),  nullable=False)
    date         = Column(String(20),  nullable=False)
    time         = Column(String(10),  nullable=False)
    topic        = Column(String(100), nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
