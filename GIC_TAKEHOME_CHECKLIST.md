# GIC Cafe Employee Manager - Step-by-Step Implementation Checklist

## 0. Locked Decisions
- [x] Backend stack: `FastAPI` (`Python 3.9+`, recommended `3.12`).
- [x] RDBMS: `PostgreSQL`.
- [x] Cafe `logo` persistence: file URL/path in DB (not binary/blob), backed by Supabase Storage.
- [x] Cafe delete behavior: delete cafe and all employees under that cafe.
- [x] Deployment architecture:
  - [x] Frontend: `Vercel`.
  - [x] Backend (FastAPI): `Railway` (Dockerized web service).
  - [x] Database: `Supabase Postgres`.
  - [x] File storage for logos: `Supabase Storage`.

## 1. Repository and Project Setup
- [x] Create a mono-repo structure:
  - [x] `backend/`
  - [x] `frontend/`
  - [x] `infra/` (docker-compose, env samples)
  - [x] `README.md`
- [x] Add `.editorconfig`, `.gitignore`, and consistent lint/format tooling.
- [x] Create `.env.example` files for backend and frontend:
  - [x] Backend vars: `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_BUCKET`, `ALLOWED_ORIGINS`
  - [x] Frontend vars: `VITE_API_BASE_URL`

### 1.1 Concrete Folder Tree

**Backend**
```
backend/
├── app/
│   ├── domain/
│   │   ├── entities/            # cafe.py, employee.py
│   │   ├── value_objects/       # employee_id.py, phone_number.py (validation logic)
│   │   └── repositories/        # abstract interfaces (ports): cafe_repository.py, employee_repository.py
│   ├── application/
│   │   ├── commands/
│   │   │   ├── cafes/           # create_cafe.py, update_cafe.py, delete_cafe.py
│   │   │   └── employees/       # create_employee.py, update_employee.py, delete_employee.py
│   │   ├── queries/
│   │   │   ├── cafes/           # get_cafes.py
│   │   │   └── employees/       # get_employees.py
│   │   ├── handlers/            # mediator handlers for each command/query
│   │   └── dtos/                # cafe_dto.py, employee_dto.py
│   ├── infrastructure/
│   │   ├── db/
│   │   │   ├── models/          # SQLAlchemy ORM models (cafe_model.py, employee_model.py, assignment_model.py)
│   │   │   ├── repositories/    # concrete implementations of domain ports
│   │   │   └── session.py       # SQLAlchemy engine + session factory
│   │   └── storage/             # supabase_storage.py (logo upload client)
│   └── api/
│       ├── routers/             # cafes.py, employees.py
│       ├── middleware/          # error_handler.py, logging.py
│       ├── dependencies.py      # DI wiring
│       └── main.py
├── alembic/                     # Alembic root (must be alongside alembic.ini)
│   ├── versions/                # migration files e.g. 0001_create_cafes.py, 0002_create_employees.py
│   ├── env.py                   # connects Alembic to SQLAlchemy models
│   └── script.py.mako
├── tests/
│   ├── unit/
│   └── integration/
├── seed/                        # seed.py
├── Dockerfile
├── requirements.txt
├── alembic.ini                  # Alembic config — points to alembic/ folder above
└── .env.example
```

**Frontend**
```
frontend/
├── src/
│   ├── components/              # ReusableTextbox.tsx, ConfirmModal.tsx, FormActions.tsx
│   ├── pages/
│   │   ├── cafes/               # CafesPage.tsx, CafeFormPage.tsx
│   │   └── employees/           # EmployeesPage.tsx, EmployeeFormPage.tsx
│   ├── api/                     # cafesApi.ts, employeesApi.ts (axios/fetch wrappers)
│   ├── hooks/                   # TanStack Query hooks (useCafes, useEmployees, etc.)
│   ├── types/                   # cafe.ts, employee.ts (TypeScript interfaces)
│   ├── router.tsx
│   └── App.tsx
├── public/
├── Dockerfile
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── .env.example
```

**Infra**
```
infra/
├── docker-compose.yml           # includes postgres + backend + frontend services (local dev)
└── .env.example
```

**`docker-compose.yml` services (local dev):**
```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: cafe_manager
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"

  backend:
    build: ../backend
    ports:
      - "8000:8000"
    env_file: ../backend/.env
    depends_on:
      - db

  frontend:
    build: ../frontend
    ports:
      - "5173:80"
    env_file: ../frontend/.env
```
> Note: In production, `db` is replaced by Supabase Postgres — the backend only needs `DATABASE_URL` swapped via env var.

## 2. Data Model and Schema
- [x] Design tables/entities:
  - [x] `cafes` (`id` UUID PK, `name`, `description`, `logo` nullable, `location`).
  - [x] `employees` (`id` string PK in `UIXXXXXXX`, `name`, `email_address`, `phone_number`, `gender`).
  - [x] `employee_cafe_assignments` (`employee_id`, `cafe_id`, `start_date`).
- [x] Enforce constraints:
  - [x] Employee ID format: `UI` + 7 alphanumeric chars.
  - [x] Valid email format.
  - [x] SG phone format: starts with `8`/`9`, exactly 8 digits.
  - [x] Gender only `Male` or `Female`.
  - [x] One employee can belong to at most one cafe at a time.
- [x] Add indexes for query paths:
  - [x] `cafes(location)`
  - [x] `employee_cafe_assignments(cafe_id, start_date)`
- [x] Create migration scripts.
- [x] Add seed data for cafes, employees, and assignments.

## 3. Backend Architecture (Clean + CQRS)
- [x] Create layered structure per §1.1 folder tree:
  - [x] `app/domain/` — entities, value objects, abstract repository interfaces (no framework dependencies)
  - [x] `app/application/` — CQRS commands, queries, handlers (mediator targets), DTOs
  - [x] `app/infrastructure/` — SQLAlchemy ORM models, concrete repository implementations, Supabase storage client
  - [x] `alembic/` + `alembic.ini` — migration scripts at the backend root (alongside `alembic.ini`, not inside `app/`)
  - [x] `app/api/` — FastAPI routers, middleware, DI wiring
- [x] Add Mediator pattern: each command/query in `application/commands|queries/` has a matching handler in `application/handlers/`; a mediator/bus dispatches to the correct handler.
- [x] Add dependency injection container wiring (`dependency-injector` or FastAPI DI).
  <!-- Note: Assignment assessment criteria lists "Autofac" which is .NET-specific; `dependency-injector` / FastAPI DI is the Python equivalent -->
- [x] Add CORS middleware in `app/api/main.py` — allow Vercel frontend origin (required for Railway backend + Vercel frontend cross-origin calls).
- [x] Add central exception handling and validation error response model (`app/api/middleware/error_handler.py`).
- [x] Add request/response logging (`app/api/middleware/logging.py`) and health endpoint.

## 4. Backend API Implementation
- [x] `GET /cafes?location=<location>`:
  - [x] Return cafes sorted by `employees` desc.
  - [x] Filter by location when valid location provided.
  - [x] Return empty list if invalid location provided.
  - [x] Return all cafes when no location.
  - [x] Response fields: `name`, `description`, `employees`(int), `logo`(optional), `location`, `id`.
- [x] `GET /employees?cafe=<cafe>`:
  - [x] Return all employees sorted by `days_worked` desc.
  - [x] If cafe provided, return only employees under that cafe.
  - [x] Compute `days_worked` = current date - assignment start date.
  - [x] Response fields: `id`, `name`, `email_address`, `phone_number`, `days_worked`(int), `cafe`(blank if unassigned).
- [x] `POST /cafes`: create cafe.
- [x] `PUT /cafes/{id}`: update existing cafe.
- [x] `DELETE /cafes/{id}`: delete cafe and cascade delete employees under that cafe (as per your decision).
- [x] `POST /employees`: create employee; cafe assignment is optional (employee can exist unassigned).
- [x] `PUT /employees/{id}`: update employee and assignment.
- [x] `DELETE /employees/{id}`: delete employee.
- [x] Add API contract docs (OpenAPI/Swagger preferred — auto-generated by FastAPI at `/docs`).

## 5. Frontend Setup
- [x] Initialize React app with Vite (preferred) or CRA.
- [x] Add required libraries:
  - [x] AgGrid for data tables.
  - [x] Ant Design for UI framework (required by spec).
  - [x] Tailwind CSS — use alongside Ant Design (disable Tailwind preflight in `tailwind.config.js` to prevent style conflicts with Ant Design).
  - [x] Optional: TanStack Query for server state.
  - [x] Optional: Day.js for date handling.
- [x] Configure routing for:
  - [x] `/cafes`
  - [x] `/employees`
  - [x] `/cafes/new`, `/cafes/:id/edit`
  - [x] `/employees/new`, `/employees/:id/edit`
- [x] Define reusable UI components (textbox, modal confirm, form actions).
- [x] Apply custom styling beyond default framework theme.

## 6. Cafes Page
- [x] Build table columns: `Logo`, `Name`, `Description`, `Employees`, `Location`, `Actions`.
- [x] Call `GET /cafes` on load.
- [x] Add location filter input and re-query behavior.
- [x] Make `Employees` clickable to navigate to employee page filtered by cafe.
- [x] Add `Add New Cafe` button.
- [x] Add row-level `Edit` and `Delete` with confirm modal.
- [x] Refresh table after delete.

## 7. Employees Page
- [x] Build table columns: `Employee ID`, `Name`, `Email`, `Phone`, `Days Worked`, `Cafe Name`, `Actions`.
- [x] Call `GET /employees` on load.
- [x] Support cafe-filtered view when navigated from cafe page.
- [x] Add `Add New Employee` button.
- [x] Add row-level `Edit` and `Delete` with confirm modal.
- [x] Refresh table after delete.

## 8. Add/Edit Cafe Form Page
- [x] Fields and validation (use `ReusableTextbox` component where tagged):
  - [x] Name `[ReusableTextbox]`: min 6, max 10.
  - [x] Description `[ReusableTextbox]`: max 256.
  - [x] Logo file: max 2MB.
  - [x] Location `[ReusableTextbox]`.
- [x] Submit button:
  - [x] `POST /cafes` for create.
  - [x] `PUT /cafes` for edit.
- [x] Cancel button navigates back to cafe page.
- [x] Warn on unsaved changes before navigation.
- [x] On edit route, prefill form from existing cafe data.

## 9. Add/Edit Employee Form Page
- [x] Fields and validation (use `ReusableTextbox` component where tagged):
  - [x] Name `[ReusableTextbox]`: min 6, max 10.
  - [x] Email `[ReusableTextbox]`: valid email format.
  - [x] Phone: SG format (`8|9` + 7 digits).
  - [x] Gender: radio group (`Male`, `Female`).
  - [x] Assigned Cafe: dropdown.
- [x] Submit button:
  - [x] `POST /employees` for create — must also create the employee-cafe assignment record.
  - [x] `PUT /employees` for edit — must also update the employee-cafe assignment record.
- [x] Cancel button navigates back to employee page.
- [x] Warn on unsaved changes before navigation.
- [x] On edit route, prefill form from existing employee data.

## 10. Testing and Quality
- [x] Backend unit tests:
  - [x] Validation rules (`EmployeeId`, `PhoneNumber` value objects; `CreateCafeRequest`, `CreateEmployeeRequest` DTOs).
  - [x] Query sorting/filter behavior (GET /cafes sorted by employees desc, GET /employees sorted by days_worked desc, location/cafe filter).
  - [x] Delete cascade behavior (DELETE /cafes deletes employees under it).
  - [x] `days_worked` calculation (current date − assignment start_date).
- [x] Backend integration tests for all required endpoints (82 tests, all pass; SQLite in-memory via `conftest.py`).
- [x] Frontend tests:
  - [x] Form validation (CafeFormPage: name min/max, required fields; EmployeeFormPage: name, phone, gender).
  - [x] Component rendering (ReusableTextbox label/input/textarea; ConfirmModal open/close/actions).
  - [x] Correct mutation called on valid submit (createCafe, createEmployee with correct payload).
- [ ] Manual UAT checklist for all assignment scenarios.

## 11. Docker and Deployment
- [x] Create backend Dockerfile.
- [x] Create frontend Dockerfile.
- [x] Create `docker-compose.yml` including database.
- [ ] Verify full stack runs via Docker locally.
- [ ] Deploy frontend to `Vercel`.
- [ ] Deploy backend Docker service to `Railway`.
- [ ] Provision `Supabase` project (Postgres + Storage bucket) and connect backend.
- [ ] Verify production URLs and end-to-end flows.

## 12. Documentation and Submission
- [ ] Write README with:
  - [ ] Tech stack and architecture choices.
  - [ ] Local setup and run instructions.
  - [ ] Docker commands.
  - [ ] DB migration and seed steps.
  - [ ] API endpoint summary.
  - [ ] Trade-offs and assumptions.
- [ ] Push complete code to GitHub.
- [ ] Share GitHub repo URL and deployed app URL.
- [ ] Final smoke test: app runs, APIs pass, UI flows complete.

## 13. Final Acceptance Gate
- [ ] All required endpoints implemented and behavior matches spec.
- [ ] Frontend contains all required pages, forms, validations, and delete confirmations.
- [ ] Data constraints and seed data are present.
- [ ] Clean architecture principles and code readability demonstrated.
- [ ] App is dockerized, deployed, and documented.
