"""
Emkay Surveys Nigeria Limited — Backend API
FastAPI + SQLite + Email Notifications
"""

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List

from database import SessionLocal, engine, Base
import models
import schemas
from config import settings

# Create all DB tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Emkay Surveys Nigeria Limited — API",
    description="Backend for contact form submissions, message management, and email notifications.",
    version="1.0.0"
)

# ── CORS (allow your frontend origin) ──────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static files (admin dashboard) ─────────────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")

# ── HTTP Basic Auth for admin routes ───────────────────────────────────────
security = HTTPBasic()

def require_admin(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, settings.ADMIN_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, settings.ADMIN_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials.",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# ── DB dependency ───────────────────────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════════════════
#  EMAIL HELPER
# ═══════════════════════════════════════════════════════════════════════════

def send_notification_email(msg: models.Message):
    """Send an email to the company when a new enquiry is received."""
    if not settings.SMTP_ENABLED:
        print(f"[EMAIL SKIPPED] SMTP disabled. New message from {msg.first_name} {msg.last_name}")
        return

    body_html = f"""
    <div style="font-family:sans-serif;max-width:600px;margin:0 auto;background:#0b1a2e;color:#f8f5ef;padding:30px;border-radius:8px;">
      <h2 style="color:#c8922a;margin-bottom:4px;">New Enquiry Received</h2>
      <p style="color:#9aacbe;font-size:12px;margin-top:0;">{msg.submitted_at.strftime('%d %B %Y, %I:%M %p')}</p>
      <hr style="border-color:rgba(200,146,42,0.2);margin:20px 0;">
      <table style="width:100%;border-collapse:collapse;">
        <tr><td style="padding:10px 0;color:#9aacbe;width:160px;">Name</td><td style="color:#f8f5ef;font-weight:600;">{msg.first_name} {msg.last_name}</td></tr>
        <tr><td style="padding:10px 0;color:#9aacbe;">Email</td><td><a href="mailto:{msg.email}" style="color:#e6ad47;">{msg.email}</a></td></tr>
        <tr><td style="padding:10px 0;color:#9aacbe;">Phone</td><td style="color:#f8f5ef;">{msg.phone or '—'}</td></tr>
        <tr><td style="padding:10px 0;color:#9aacbe;">Service</td><td style="color:#f8f5ef;">{msg.service or '—'}</td></tr>
        <tr><td style="padding:10px 0;color:#9aacbe;vertical-align:top;">Message</td><td style="color:#f8f5ef;">{msg.message}</td></tr>
      </table>
      <hr style="border-color:rgba(200,146,42,0.2);margin:20px 0;">
      <p style="color:#9aacbe;font-size:11px;text-align:center;">Emkay Surveys Nigeria Limited · RC: 6951225</p>
    </div>
    """

    email_msg = MIMEMultipart("alternative")
    email_msg["Subject"] = f"[Emkay Surveys] New Enquiry from {msg.first_name} {msg.last_name}"
    email_msg["From"]    = settings.SMTP_FROM
    email_msg["To"]      = settings.NOTIFY_EMAIL
    email_msg.attach(MIMEText(body_html, "html"))

    try:
        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM, settings.NOTIFY_EMAIL, email_msg.as_string())
        print(f"[EMAIL SENT] Notification sent to {settings.NOTIFY_EMAIL}")
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send notification: {e}")

def send_confirmation_email(msg: models.Message):
    """Send an auto-reply confirmation email to the enquirer."""
    if not settings.SMTP_ENABLED:
        print(f"[EMAIL SKIPPED] SMTP disabled. Auto-reply skipped for {msg.email}")
        return

    body_html = f"""
    <div style="font-family:sans-serif;max-width:600px;margin:0 auto;background:#0b1a2e;color:#f8f5ef;padding:30px;border-radius:8px;">
      <h2 style="color:#c8922a;">Thank You, {msg.first_name}!</h2>
      <p style="color:#9aacbe;line-height:1.8;">
        We have received your enquiry and a member of our team will be in touch with you shortly.
      </p>
      <div style="background:#122540;border:1px solid rgba(200,146,42,0.25);border-radius:6px;padding:20px;margin:24px 0;">
        <p style="color:#9aacbe;font-size:12px;margin:0 0 10px;text-transform:uppercase;letter-spacing:.1em;">Your Enquiry Summary</p>
        <p style="margin:6px 0;"><span style="color:#9aacbe;">Service:</span> <strong style="color:#f8f5ef;">{msg.service or 'Not specified'}</strong></p>
        <p style="margin:6px 0;"><span style="color:#9aacbe;">Reference ID:</span> <strong style="color:#e6ad47;">#{msg.id:06d}</strong></p>
      </div>
      <hr style="border-color:rgba(200,146,42,0.2);margin:20px 0;">
      <p style="color:#9aacbe;font-size:13px;">📍 201T, Novare Central Mall, Wuse Zone 5, Abuja</p>
      <p style="color:#9aacbe;font-size:13px;">📞 +234 806 077 2573 &nbsp;|&nbsp; +234 701 885 6666</p>
      <p style="color:#9aacbe;font-size:11px;text-align:center;margin-top:24px;">Emkay Surveys Nigeria Limited · RC: 6951225</p>
    </div>
    """

    email_msg = MIMEMultipart("alternative")
    email_msg["Subject"] = "Thank you for contacting Emkay Surveys Nigeria Limited"
    email_msg["From"]    = settings.SMTP_FROM
    email_msg["To"]      = msg.email
    email_msg.attach(MIMEText(body_html, "html"))

    try:
        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM, msg.email, email_msg.as_string())
        print(f"[EMAIL SENT] Confirmation sent to {msg.email}")
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send confirmation: {e}")


# ═══════════════════════════════════════════════════════════════════════════
#  PUBLIC ROUTES
# ═══════════════════════════════════════════════════════════════════════════

import os
from fastapi.staticfiles import StaticFiles

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
frontend_path = os.path.join(BASE_DIR, "frontend")

app.mount("/static", StaticFiles(directory=frontend_path), name="frontend")

@app.post(
    "/api/contact",
    response_model=schemas.MessageOut,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a contact form enquiry",
    tags=["Contact"]
)
def submit_contact(payload: schemas.MessageCreate, db: Session = Depends(get_db)):
    """
    Accepts a contact form submission, saves it to the database,
    sends a notification email to the company, and a confirmation
    auto-reply to the enquirer.
    """
    new_msg = models.Message(
        first_name   = payload.first_name.strip(),
        last_name    = payload.last_name.strip(),
        email        = payload.email.strip().lower(),
        phone        = payload.phone.strip() if payload.phone else None,
        service      = payload.service,
        message      = payload.message.strip(),
        submitted_at = datetime.utcnow(),
        is_read      = False,
    )
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)

    # Fire-and-forget emails (non-blocking in production, use background tasks)
    send_notification_email(new_msg)
    send_confirmation_email(new_msg)

    return new_msg


# ═══════════════════════════════════════════════════════════════════════════
#  ADMIN ROUTES  (HTTP Basic Auth protected)
# ═══════════════════════════════════════════════════════════════════════════

@app.get(
    "/admin",
    response_class=FileResponse,
    include_in_schema=False
)
def admin_dashboard():
    return FileResponse("static/admin.html")


@app.get(
    "/api/admin/messages",
    response_model=List[schemas.MessageOut],
    summary="Get all contact messages",
    tags=["Admin"]
)
def get_messages(
    skip: int = 0,
    limit: int = 100,
    unread_only: bool = False,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin)
):
    """Retrieve all submitted contact messages. Supports pagination and unread filter."""
    query = db.query(models.Message)
    if unread_only:
        query = query.filter(models.Message.is_read == False)
    return query.order_by(models.Message.submitted_at.desc()).offset(skip).limit(limit).all()


@app.get(
    "/api/admin/messages/{message_id}",
    response_model=schemas.MessageOut,
    summary="Get a single message by ID",
    tags=["Admin"]
)
def get_message(
    message_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin)
):
    msg = db.query(models.Message).filter(models.Message.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found.")
    # Auto-mark as read
    if not msg.is_read:
        msg.is_read = True
        db.commit()
        db.refresh(msg)
    return msg


@app.patch(
    "/api/admin/messages/{message_id}/read",
    response_model=schemas.MessageOut,
    summary="Mark a message as read",
    tags=["Admin"]
)
def mark_read(
    message_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin)
):
    msg = db.query(models.Message).filter(models.Message.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found.")
    msg.is_read = True
    db.commit()
    db.refresh(msg)
    return msg


@app.delete(
    "/api/admin/messages/{message_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a message",
    tags=["Admin"]
)
def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin)
):
    msg = db.query(models.Message).filter(models.Message.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found.")
    db.delete(msg)
    db.commit()
    return None


@app.post("/api/suggestion", status_code=201, tags=["Contact"])
def submit_suggestion(payload: dict, db: Session = Depends(get_db)):
    """Save a visitor suggestion."""
    from models import Suggestion
    s = Suggestion(name=payload.get("name","Anonymous"), suggestion=payload.get("suggestion",""), submitted_at=datetime.utcnow())
    db.add(s); db.commit()
    return {"status": "received"}

@app.post("/api/schedule", status_code=201, tags=["Contact"])
def schedule_call(payload: dict, db: Session = Depends(get_db)):
    """Save a scheduled call request."""
    from models import ScheduledCall
    c = ScheduledCall(name=payload.get("name"), phone=payload.get("phone"), date=payload.get("date"), time=payload.get("time"), topic=payload.get("topic"), submitted_at=datetime.utcnow())
    db.add(c); db.commit()
    send_schedule_email(c)
    return {"status": "scheduled"}

@app.post("/api/chat-handoff", status_code=201, tags=["Contact"])
def chat_handoff(payload: dict):
    """Notify team when someone requests a human from the chatbot."""
    name  = payload.get("name", "Unknown")
    phone = payload.get("phone", "Unknown")
    print(f"[CHAT HANDOFF] {name} requested human chat. Phone: {phone}")
    if settings.SMTP_ENABLED:
        try:
            body = f"<h3>Chat Handoff Request</h3><p><b>Name:</b> {name}</p><p><b>Phone:</b> {phone}</p>"
            msg = MIMEMultipart("alternative"); msg["Subject"] = f"[Emkay Chat] {name} wants to speak to a human"
            msg["From"] = settings.SMTP_FROM; msg["To"] = settings.NOTIFY_EMAIL
            msg.attach(MIMEText(body,"html"))
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as s:
                s.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                s.sendmail(settings.SMTP_FROM, settings.NOTIFY_EMAIL, msg.as_string())
        except Exception as e:
            print(f"[EMAIL ERROR] {e}")
    return {"status": "notified"}

def send_schedule_email(c):
    if not settings.SMTP_ENABLED: print(f"[SCHEDULE] {c.name} booked a call on {c.date} at {c.time}"); return
    try:
        body = f"<h3>New Call Scheduled</h3><p><b>Name:</b> {c.name}</p><p><b>Phone:</b> {c.phone}</p><p><b>Date:</b> {c.date}</p><p><b>Time:</b> {c.time}</p><p><b>Topic:</b> {c.topic}</p>"
        msg = MIMEMultipart("alternative"); msg["Subject"] = f"[Emkay] Call Scheduled — {c.name}"
        msg["From"] = settings.SMTP_FROM; msg["To"] = settings.NOTIFY_EMAIL
        msg.attach(MIMEText(body,"html"))
        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as s:
            s.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            s.sendmail(settings.SMTP_FROM, settings.NOTIFY_EMAIL, msg.as_string())
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")

@app.get(
    "/api/admin/stats",
    response_model=schemas.StatsOut,
    summary="Get message statistics",
    tags=["Admin"]
)
def get_stats(
    db: Session = Depends(get_db),
    _: str = Depends(require_admin)
):
    total  = db.query(models.Message).count()
    unread = db.query(models.Message).filter(models.Message.is_read == False).count()
    return schemas.StatsOut(total=total, unread=unread, read=total - unread)
