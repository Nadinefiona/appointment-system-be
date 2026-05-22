# Appointment Booking System (API)

Django REST API for providers, clients, and admins: availability, bookings, JWT auth, and role-based access.

## Interactive API docs

After starting the server, open:

- **Swagger UI:** [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
- **OpenAPI schema:** [http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/)

Each endpoint in Swagger is grouped by **tag** and has a short **summary** and **description**.

## Local setup

```bash
cd appointment_system
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env`, fill in values, then:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Environment variables

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key (use a long random string in production). |
| `POSTGRES_DB` | Database name |
| `POSTGRES_USER` | Database user |
| `POSTGRES_PASSWORD` | Database password |
| `POSTGRES_HOST` | Host (default `localhost`) |
| `POSTGRES_PORT` | Port (default `5432`) |
| `EMAIL_NOTIFICATIONS_ENABLED` | `True` / `False` — master switch for booking emails |
| `EMAIL_BACKEND` | Django mail backend (dev: `django.core.mail.backends.console.EmailBackend`) |
| `DEFAULT_FROM_EMAIL` | Sender address for outgoing mail |
| `BOOKING_REMINDER_HOURS` | How many hours before `start_time` to send reminders (default `24`) |
| `BOOKING_REMINDER_WINDOW_MINUTES` | Tolerance window for the reminder job (default `30`) |

## Email

- **Confirmation** — sent after `POST /api/bookings/` (client + provider). Dev: prints in the `runserver` console (`EMAIL_BACKEND=console`).
- **Reminder** — run on a schedule: `python manage.py send_booking_reminders` (default ~24h before `start_time`).
- **SMTP** — set `EMAIL_BACKEND` to `django.core.mail.backends.smtp.EmailBackend` and `EMAIL_HOST` / credentials in `.env`.

## Authentication

- **JWT:** `POST /api/token/` with `email` and `password`. Response includes `access`, `refresh`, and `user` (`id`, `email`, `role`).
- **Refresh:** `POST /api/token/refresh/` with `refresh`.

Use the `access` token in the header: `Authorization: Bearer <access>`.

In Swagger, use **Authorize** and enter: `Bearer <your_access_token>`.

## User flows (endpoints)

### Client

1. **Register** — `POST /api/auth/register/` (no auth). Creates a **client** account.
2. **Login** — `POST /api/token/` with email + password.

### Provider (promoted by admin)

1. Admin sets user **role** to `provider` in Django admin (`/admin/`); a `ServiceProvider` profile is created automatically.
2. **Login** — same `POST /api/token/` with email + password.
3. **Current user** — `GET /api/me/`.
4. **Own profile (bio, buffer)** — `GET /api/me/provider-profile/` and `PATCH /api/me/provider-profile/` (provider role only).
5. **Catalog** — `GET /api/providers/` (read-only for non-admin).
6. **Availability (working hours)** — `POST /api/availability-slots/` without `provider` in the body (server assigns your profile). List, update, delete your slots via the same resource.
7. **Schedule (with client details)** — `GET /api/providers/{id}/schedule/?from=...&to=...` (provider: own id only; admin: any).
8. **Openings for a day** — `GET /api/providers/{id}/openings/?date=YYYY-MM-DD` (optional `service` query for suggested starts).

## Endpoint map (short)

| Area | Base path | Notes |
|------|-----------|--------|
| Auth | `/api/token/`, `/api/token/refresh/` | JWT |
| Registration | `/api/auth/register/` | Public client signup |
| Current user | `/api/me/`, `/api/me/provider-profile/` | Profile for provider role |
| Providers | `/api/providers/` | CRUD rules by role; `schedule`, `openings` actions |
| Services | `/api/services/` | Service types per provider |
| Availability | `/api/availability-slots/` | Weekly slots + optional date range |
| Bookings | `/api/bookings/` | Create (client); `cancel` action |

Full request/response schemas are in Swagger.
