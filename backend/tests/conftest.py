# IMPORTANT: set env vars BEFORE any app module is imported.
# `settings = Settings()` executes at module level in app/config.py.
import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_cafe_manager.db")
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "test-key")
os.environ.setdefault("SUPABASE_BUCKET", "logos")
os.environ.setdefault("ALLOWED_ORIGINS", "http://localhost:5173")

from unittest.mock import MagicMock  # noqa: E402

import sqlalchemy as sa  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

# Import all ORM models so Base.metadata is fully populated
from app.infrastructure.db.models.base import Base  # noqa: E402
from app.infrastructure.db.models.cafe_model import CafeModel  # noqa: E402, F401
from app.infrastructure.db.models.employee_model import EmployeeModel  # noqa: E402, F401
from app.infrastructure.db.models.assignment_model import AssignmentModel  # noqa: E402, F401

# Strip PostgreSQL `~` regex CHECK constraints — unsupported by SQLite.
# Must happen BEFORE create_all().
for _tbl in Base.metadata.sorted_tables:
    _pg_checks = [
        c
        for c in list(_tbl.constraints)
        if isinstance(c, sa.CheckConstraint) and "~" in str(c.sqltext)
    ]
    for _c in _pg_checks:
        _tbl.constraints.discard(_c)

from app.api.main import app  # noqa: E402
from app.infrastructure.db.session import get_db  # noqa: E402

_DB_FILE = "./test_cafe_manager.db"
_TEST_DB_URL = f"sqlite:///{_DB_FILE}"

_engine = create_engine(
    _TEST_DB_URL,
    connect_args={"check_same_thread": False},
)
_TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    """Create all tables once per test session; drop + remove file afterwards."""
    Base.metadata.create_all(bind=_engine)
    yield
    Base.metadata.drop_all(bind=_engine)
    _engine.dispose()  # release file handle before deletion (required on Windows)
    if os.path.exists(_DB_FILE):
        try:
            os.remove(_DB_FILE)
        except PermissionError:
            pass  # best-effort; file will be overwritten on next run


@pytest.fixture
def db_session(create_tables):
    """Provide a DB session that cleans up all rows after each test."""
    session = _TestingSessionLocal()
    yield session
    session.rollback()
    # Delete in FK-safe order (assignments first, then employees, then cafes)
    session.execute(sa.text("DELETE FROM employee_cafe_assignments"))
    session.execute(sa.text("DELETE FROM employees"))
    session.execute(sa.text("DELETE FROM cafes"))
    session.commit()
    session.close()


@pytest.fixture
def mock_storage():
    storage = MagicMock()
    storage.upload.return_value = "https://test.supabase.co/logos/test.png"
    storage.delete_by_url.return_value = None
    return storage


@pytest.fixture
def client(db_session, mock_storage, monkeypatch):
    """FastAPI TestClient wired to the test DB with Supabase storage mocked."""
    # Patch both places that call SupabaseStorageClient()
    monkeypatch.setattr(
        "app.api.routers.cafes.SupabaseStorageClient", lambda: mock_storage
    )
    monkeypatch.setattr(
        "app.api.dependencies.SupabaseStorageClient", lambda: mock_storage
    )

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # raise_server_exceptions=False: prevents BaseHTTPMiddleware/anyio from
    # re-raising HTTPException in tests; ExceptionMiddleware still converts it
    # to the correct HTTP response (422 etc.) before it reaches the client.
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c

    app.dependency_overrides.clear()
