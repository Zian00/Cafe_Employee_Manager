import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.middleware.error_handler import add_exception_handlers
from app.api.middleware.logging import LoggingMiddleware
from app.api.routers import cafes, employees
from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

app = FastAPI(
    title="Cafe Employee Manager API",
    description="RESTful API for managing cafes and employees.",
    version="1.0.0",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.allowed_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request / response logging ────────────────────────────────────────────────
app.add_middleware(LoggingMiddleware)

# ── Domain exception → HTTP status mapping ───────────────────────────────────
add_exception_handlers(app)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(cafes.router, tags=["Cafes"])
app.include_router(employees.router, tags=["Employees"])


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health() -> dict:
    return {"status": "ok"}
