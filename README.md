# Appointment Booking System

Book appointments with service providers. Clients can browse providers and services, see open time slots, and make or cancel bookings. Providers manage their availability, and email notifications are sent for confirmations, cancellations, and reminders.

## Live API

Base URL: `https://appointment-system-be.onrender.com`

Interactive docs (try every endpoint here): **`/api/docs/`**

## Getting started

1. **Register:** `POST /api/auth/register/` with your email and password.
2. **Log in:** `POST /api/token/` with your `email` and `password` to get an access token.
3. **Use it:** send the token on every request as a header:

```
Authorization: Bearer <access-token>
```

In the docs page (`/api/docs/`), click **Authorize** and paste your token to try requests directly.

A confirmation email is sent automatically when you book, and a cancellation email when you cancel.

## Run locally (optional)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py runserver
```

Then open `http://localhost:8000/api/docs/`.
