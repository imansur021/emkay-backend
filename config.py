"""
App configuration — all values loaded from .env file.
Copy .env.example to .env and fill in your real values.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # ── Database ────────────────────────────────────────────────────────────
    # SQLite for dev, swap for PostgreSQL in production:
    # DATABASE_URL=postgresql://user:password@localhost/emkay_db
    DATABASE_URL: str = "sqlite:///./emkay.db"

    # ── Admin credentials ────────────────────────────────────────────────────
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "emkay2025!"

    # ── CORS origins (your frontend URLs) ───────────────────────────────────
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:5500", "*"]

    # ── Email / SMTP ─────────────────────────────────────────────────────────
    # Set SMTP_ENABLED=false to disable emails (useful during dev)
    SMTP_ENABLED  : bool = False
    SMTP_HOST     : str  = "smtp.gmail.com"
    SMTP_PORT     : int  = 465
    SMTP_USER     : str  = "your-gmail@gmail.com"
    SMTP_PASSWORD : str  = "your-app-password"    # Gmail App Password
    SMTP_FROM     : str  = "Emkay Surveys <your-gmail@gmail.com>"
    NOTIFY_EMAIL  : str  = "Emkaysurveys@gmail.com"   # Where enquiries are sent

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
