# Emkay Surveys Nigeria Limited — Backend API

FastAPI backend powering the Emkay Surveys website with:
- ✅ Contact form submission endpoint
- ✅ SQLite database (drop-in PostgreSQL for production)
- ✅ Email notifications to company + auto-reply to client
- ✅ Protected admin dashboard to view / manage messages
- ✅ Auto-generated API docs at `/docs`

---

## 📁 Project Structure

```
emkay-backend/
├── main.py          ← FastAPI app, all routes
├── database.py      ← SQLAlchemy engine & session
├── models.py        ← Database ORM models
├── schemas.py       ← Pydantic request/response schemas
├── config.py        ← Settings loaded from .env
├── requirements.txt ← Python dependencies
├── .env.example     ← Copy to .env and fill in values
└── static/
    └── admin.html   ← Admin dashboard (served at /admin)
```

---

## 🚀 Quick Start

### 1. Clone / place files in a folder

```bash
mkdir emkay-backend && cd emkay-backend
# copy all project files here
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env with your admin credentials, SMTP details, etc.
```

### 5. Run the server

```bash
uvicorn main:app --reload
```

The API is now live at **http://localhost:8000**

---

## 🔗 Key Endpoints

| Method | URL | Description | Auth |
|--------|-----|-------------|------|
| `POST` | `/api/contact` | Submit contact form | Public |
| `GET`  | `/api/admin/messages` | List all messages | Admin |
| `GET`  | `/api/admin/messages/{id}` | Get single message | Admin |
| `PATCH`| `/api/admin/messages/{id}/read` | Mark as read | Admin |
| `DELETE`| `/api/admin/messages/{id}` | Delete message | Admin |
| `GET`  | `/api/admin/stats` | Message statistics | Admin |
| `GET`  | `/admin` | Admin dashboard UI | Admin |
| `GET`  | `/docs` | Auto API docs (Swagger) | Public |

---

## 🖥️ Admin Dashboard

Visit **http://localhost:8000/admin**  
Default credentials (change in `.env`):
- **Username:** `admin`  
- **Password:** `emkay2025!`

---

## 📧 Email Setup (Gmail)

1. Enable **2-Step Verification** on your Gmail account
2. Go to Google Account → Security → **App Passwords**
3. Generate a new App Password (select "Mail")
4. Copy the 16-character password into `.env`:

```env
SMTP_ENABLED=true
SMTP_USER=your-gmail@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
SMTP_FROM=Emkay Surveys <your-gmail@gmail.com>
NOTIFY_EMAIL=Emkaysurveys@gmail.com
```

---

## 🌐 Connect the Frontend

In `emkay_surveys_website.html`, update the `fetch` call in the form's submit handler:

```javascript
const response = await fetch('http://localhost:8000/api/contact', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(formData)
});
```

---

## 🗄️ Switch to PostgreSQL (Production)

```env
DATABASE_URL=postgresql://user:password@localhost/emkay_db
```

Install the driver:
```bash
pip install psycopg2-binary
```

---

## 🔒 Production Checklist

- [ ] Change `ADMIN_PASSWORD` to a strong password
- [ ] Set `ALLOWED_ORIGINS` to your real frontend domain
- [ ] Switch `DATABASE_URL` to PostgreSQL
- [ ] Set `SMTP_ENABLED=true` and configure Gmail App Password
- [ ] Run behind Nginx + HTTPS (Let's Encrypt / Certbot)
- [ ] Use `uvicorn main:app --host 0.0.0.0 --port 8000` or `gunicorn`
