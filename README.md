# Appointment Booking System (API)

Django REST API for providers, clients, and admins: availability, bookings, JWT auth, and role-based access.

## Live API

After deploy on Render, your base URL looks like:

`https://appointment-system-be.onrender.com`

- Swagger: `/api/docs/`
- Health: `/api/health/`
- Schema: `/api/schema/`

## Local setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Docker

```bash
docker compose up --build
```

API: `http://localhost:8000/api/`

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes (production) | Django secret key |
| `DEBUG` | No | `True` local, `False` production |
| `DATABASE_URL` | Render | Postgres connection string (Render sets this) |
| `POSTGRES_*` | Local | Used when `DATABASE_URL` is empty |
| `ALLOWED_HOSTS` | Production | Comma-separated hostnames |
| `CORS_ALLOWED_ORIGINS` | Yes | Frontend URLs, comma-separated |
| `EMAIL_BACKEND` | No | SMTP for real mail |
| `EMAIL_HOST_USER` | SMTP | Gmail address |
| `EMAIL_HOST_PASSWORD` | SMTP | Gmail app password |
| `BOOKING_REMINDER_HOURS` | No | Default `24` |
| `BOOKING_DEFAULT_MINUTES` | No | Default `60` |

Render also sets `RENDER_EXTERNAL_HOSTNAME` automatically.

## Email

| Event | Recipients |
|-------|------------|
| Booking confirmed | Client + provider |
| Booking cancelled | Client + provider |
| Reminder | Client (run `python manage.py send_booking_reminders` on a schedule) |

## Authentication

- Login: `POST /api/token/` with `email` and `password`
- Refresh: `POST /api/token/refresh/`
- Header: `Authorization: Bearer <access>`

## Deploy on Render

### Fix: `connection to localhost refused`

Docker build succeeded but deploy failed because **`DATABASE_URL` is not set** on the web service.

1. Render → **New** → **PostgreSQL**
2. Web service → **Environment** → add **`DATABASE_URL`** (link from your Postgres — use Internal URL)
3. Set `DEBUG=False`, `SECRET_KEY`, `CORS_ALLOWED_ORIGINS`
4. **Manual Deploy**
5. Check `https://YOUR-SERVICE.onrender.com/api/health/`

**Alternatives:** [Railway](https://railway.app) (easiest), [Fly.io](https://fly.io), [PythonAnywhere](https://www.pythonanywhere.com)

The build failed with **"Publish directory build does not exist"** because the service was created as a **Static Site**. This API must be a **Web Service**.

### Option A: Blueprint (recommended)

1. Push this repo to GitHub.
2. Render Dashboard → **New** → **Blueprint** → connect repo.
3. Render reads `render.yaml` and creates web service + Postgres.
4. In the web service environment, set:
   - `CORS_ALLOWED_ORIGINS` = your frontend URL(s)
   - `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`
5. Deploy.

### Option B: Fix existing service manually

1. Delete the static site (or create a new **Web Service**).
2. Connect your GitHub repo.
3. Settings:

| Field | Value |
|-------|-------|
| Runtime | Python 3 |
| Build Command | `./build.sh` |
| Start Command | `./start.sh` |
| Publish Directory | **leave empty** |

4. Add a **PostgreSQL** database and set `DATABASE_URL` on the web service (Render can link it).
5. Environment variables:

```
DEBUG=False
SECRET_KEY=<long random string>
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your@gmail.com
```

6. Deploy. Check `https://your-service.onrender.com/api/health/` returns `{"status":"ok"}`.

## CI/CD

GitHub Actions (`.github/workflows/ci.yml`) runs on push/PR:

1. Tests with Postgres
2. Docker image build

## API overview

| Area | Path |
|------|------|
| Auth | `/api/token/`, `/api/token/refresh/` |
| Register | `/api/auth/register/` |
| Profile | `/api/me/` |
| Providers | `/api/providers/` |
| Services | `/api/services/` |
| Availability | `/api/availability-slots/` |
| Bookings | `/api/bookings/` |
| Admin users | `/api/admin/users/` |
| Openings | `/api/providers/{id}/openings/?date=YYYY-MM-DD` |

Full schemas: `/api/docs/`

## Project phases

| Phase | Status |
|-------|--------|
| 0 Architecture | Done |
| 1 Data modeling | Done |
| 2 JWT auth | Done |
| 3 RBAC | Done |
| 4 Booking logic | Done |
| 5 API polish | Done |
| 6 Email notifications | Done |
| 7 Tests (26+) | Done |
| 8 Docker + CI/CD | Done |
| 9 Deployment + README | Done (set your live URL above after deploy) |

## Reminders (production)

Schedule daily or hourly on Render cron or your host:

```bash
python manage.py send_booking_reminders
```
