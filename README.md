# Cafe Employee Manager

A full-stack web application for managing cafes and employees.

## Live Demo

| Service | URL |
|---|---|
| Frontend | https://cafe-employee-manager-kappa.vercel.app/ |
| Backend API | https://cafeemployeemanager-production.up.railway.app |
| API Docs | https://cafeemployeemanager-production.up.railway.app/docs |

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python 3.12), SQLAlchemy, Alembic |
| Database | PostgreSQL (Supabase in production) |
| File Storage | Supabase Storage |
| Frontend | React + Vite, Ant Design, AG Grid |
| Deployment | Railway (backend), Vercel (frontend) |

## Architecture

Clean Architecture + CQRS + Mediator pattern.

```
backend/app/
├── domain/          # Entities, value objects, repository interfaces
├── application/     # Commands, queries, handlers (CQRS + Mediator)
├── infrastructure/  # ORM models, repository implementations, Supabase storage
└── api/             # FastAPI routers, middleware, DI
```

## Local Setup

### Prerequisites
- Python 3.12+
- Node.js 22+
- Docker + Docker Compose

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # fill in values
alembic upgrade head            # run migrations
python seed/seed.py             # seed data
uvicorn app.api.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env            # fill in values
npm run dev
```

### Full Stack via Docker

```bash
cd infra
cp .env.example .env            # fill in values
docker compose up --build
```

## Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1
```

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/cafes` | List cafes (filter by `?location=`) |
| POST | `/cafes` | Create cafe |
| PUT | `/cafes/{id}` | Update cafe |
| DELETE | `/cafes/{id}` | Delete cafe + employees |
| GET | `/employees` | List employees (filter by `?cafe=`) |
| POST | `/employees` | Create employee |
| PUT | `/employees/{id}` | Update employee |
| DELETE | `/employees/{id}` | Delete employee |
| GET | `/health` | Health check |

API docs available at `/docs` (Swagger UI) when running locally.

## Trade-offs and Assumptions

### Architecture Decisions

**CQRS + Mediator pattern**
Commands (writes) and queries (reads) are separated into distinct handlers dispatched via a simple type-based mediator. This keeps handlers small and focused, but the synchronous implementation blocks on I/O. An async event-driven approach would scale better but adds complexity beyond the scope of this project.

**Read-side query bypass**
`GetCafesQueryHandler` and `GetEmployeesQueryHandler` bypass the repository abstraction and query the database directly with aggregations (employee counts, days-worked). This is intentional — computing these in SQL is far more efficient than loading all rows into Python. The trade-off is a slight inconsistency in the access pattern, but it's documented and isolated to the query handlers.

**Per-request mediator instantiation**
A new mediator and set of handlers are created for each request, sharing the same SQLAlchemy session. This keeps the implementation stateless and simple at the cost of minor overhead per request.

**Storage failures are non-blocking**
If Supabase Storage fails during a logo deletion, the error is caught and the database operation proceeds. This prevents orphaned DB records but may leave orphaned files in storage. Acceptable given the low frequency of deletions and the absence of a retry/cleanup job.

**Dual validation (Pydantic + DB constraints)**
Input is validated at the Pydantic DTO level and enforced again via PostgreSQL CHECK constraints. This is intentional defence-in-depth: the DB constraint is the last line of defence if validation is ever bypassed.

### Data Model Assumptions

- **One cafe per employee**: An employee can be assigned to at most one cafe at a time. The `employee_cafe_assignments` table uses `employee_id` as its sole primary key to enforce this at the schema level.
- **Cascade delete on cafe**: Deleting a cafe deletes all employees assigned to it. This matches the spec requirement and simplifies referential integrity.
- **Server-generated employee IDs**: IDs follow the `UIXXXXXXX` format and are generated server-side. Clients cannot choose or supply their own.
- **Gender is binary**: The spec defines `Male`/`Female` only. The enum is enforced at both application and DB level.
- **Logo stored as URL**: Cafe logos are uploaded to Supabase Storage; only the public URL is stored in the database. No binary blobs in the DB.
- **Single tenant**: All data lives in a single PostgreSQL database with no multi-tenancy isolation.

### Simplifications (Known Limitations)

- No soft deletes — cascade deletes are permanent and irreversible.
- No API versioning — a single `/` prefix is used for all endpoints.
- No pagination — list endpoints return all records. Suitable for the seed data volume but would need `limit`/`offset` for production scale.
- No authentication or authorisation — all endpoints are public. Adding an auth layer (e.g. JWT) would be the first production hardening step.
- No connection pooling configuration — relies on SQLAlchemy defaults.
- No retry logic for storage operations.
- Frontend has no offline support or client-side caching beyond React Query's in-memory cache.
