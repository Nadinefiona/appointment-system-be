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

## Authentication

- **JWT:** `POST /api/token/` with `username` and `password` (SimpleJWT default field names).
- **Refresh:** `POST /api/token/refresh/` with `refresh`.

Use the `access` token in the header: `Authorization: Bearer <access>`.

In Swagger, use **Authorize** and enter: `Bearer <your_access_token>`.

## Provider flow (endpoints)

1. **Register** — `POST /api/auth/register/provider/` (no auth). Creates a provider user and `ServiceProvider` profile.
2. **Login** — `POST /api/token/` with username + password.
3. **Current user** — `GET /api/me/`.
4. **Own profile (bio, buffer)** — `GET /api/me/provider-profile/` and `PATCH /api/me/provider-profile/`.
5. **Catalog** — `GET /api/providers/` (read-only for non-admin).
6. **Availability (working hours)** — `POST /api/availability-slots/` without `provider` in the body (server assigns your profile). List, update, delete your slots via the same resource.
7. **Schedule (with client details)** — `GET /api/providers/{id}/schedule/?from=...&to=...` (provider: own id only; admin: any).
8. **Openings for a day** — `GET /api/providers/{id}/openings/?date=YYYY-MM-DD` (optional `service` query for suggested starts).

## Endpoint map (short)

| Area | Base path | Notes |
|------|-----------|--------|
| Auth | `/api/token/`, `/api/token/refresh/` | JWT |
| Registration | `/api/auth/register/provider/` | Public provider signup |
| Current user | `/api/me/`, `/api/me/provider-profile/` | Profile for provider role |
| Providers | `/api/providers/` | CRUD rules by role; `schedule`, `openings` actions |
| Services | `/api/services/` | Service types per provider |
| Availability | `/api/availability-slots/` | Weekly slots + optional date range |
| Bookings | `/api/bookings/` | Create (client); `cancel` action |

Full request/response schemas are in Swagger.
