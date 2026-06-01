# System Design — Appointment Booking API

Use this file for your submission diagram link (GitHub raw URL, or export PNG from [mermaid.live](https://mermaid.live)).

## Architecture

```mermaid
flowchart TB
    subgraph Client
        FE[Next.js Frontend]
    end

    subgraph Render
        WEB[Django + DRF + Gunicorn]
        PG[(PostgreSQL)]
    end

    subgraph External
        SMTP[Gmail SMTP]
    end

    FE -->|HTTPS JWT REST| WEB
    WEB --> PG
    WEB --> SMTP
```

## Components

```mermaid
flowchart LR
    subgraph config
        URLs[config/urls.py]
        SET[config/settings.py]
    end

    subgraph apps
        ACC[accounts\nUser JWT register]
        PRO[providers\nServiceProvider]
        SVC[services\nServiceType M2M]
        BOK[bookings\nSlots Bookings Email]
        CORE[core\nPermissions pagination]
    end

    URLs --> ACC
    URLs --> PRO
    URLs --> SVC
    URLs --> BOK
    SET --> CORE
    ACC --> PRO
    SVC --> PRO
    BOK --> PRO
    BOK --> SVC
    BOK --> ACC
```

## Booking flow

```mermaid
sequenceDiagram
    participant C as Client
    participant API as Django API
    participant DB as PostgreSQL
    participant M as SMTP

    C->>API: POST /api/bookings/
    API->>DB: select_for_update conflict check
    API->>DB: insert booking
    API->>M: confirmation email on_commit
    API-->>C: 201 booking details
```

## Data model

```mermaid
erDiagram
    User ||--o| ServiceProvider : has
    ServiceProvider ||--o{ AvailabilitySlot : owns
    ServiceProvider }o--o{ ServiceType : offers
    User ||--o{ Booking : client
    ServiceProvider ||--o{ Booking : provider
    ServiceType ||--o{ Booking : service

    User {
        uuid id
        string email
        string role
    }
    ServiceProvider {
        uuid id
        int buffer_time
    }
    ServiceType {
        uuid id
        string name
    }
    AvailabilitySlot {
        uuid id
        int weekday
        time start_time
        time end_time
    }
    Booking {
        uuid id
        datetime start_time
        datetime end_time
        string status
    }
```

## Roles

| Role | Access |
|------|--------|
| client | book, view own bookings, cancel own |
| provider | manage availability, view schedule |
| admin | users, services, all bookings |

## Stack

| Layer | Technology |
|-------|------------|
| API | Django 5.2, DRF, SimpleJWT |
| Database | PostgreSQL |
| Docs | drf-spectacular Swagger |
| Deploy | Docker, Render, GitHub Actions |
| Email | SMTP + management command reminders |
