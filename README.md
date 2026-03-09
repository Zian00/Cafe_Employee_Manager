# Cafe Employee Manager

A full-stack web application for managing cafes and employees.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python 3.12), SQLAlchemy, Alembic |
| Database | PostgreSQL (Supabase in production) |
| File Storage | Supabase Storage |
| Frontend | React + Vite, Ant Design, Tailwind CSS, AG Grid |
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

_To be filled in during finalisation._
