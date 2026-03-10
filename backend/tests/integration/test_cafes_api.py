"""Integration tests for /cafes endpoints."""
from datetime import date, timedelta

import pytest

from app.infrastructure.db.models.assignment_model import AssignmentModel
from app.infrastructure.db.models.cafe_model import CafeModel
from app.infrastructure.db.models.employee_model import EmployeeModel


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_cafe(db, name="CafeOne", description="A cafe", location="CBD", logo=None):
    cafe = CafeModel(
        name=name, description=description, location=location, logo=logo
    )
    db.add(cafe)
    db.commit()
    db.refresh(cafe)
    return cafe


def _make_employee(db, emp_id="UIABCDE01", name="JohnDoe", email="john@example.com"):
    emp = EmployeeModel(
        id=emp_id,
        name=name,
        email_address=email,
        phone_number="81234567",
        gender="Male",
    )
    db.add(emp)
    db.flush()
    return emp


def _assign(db, employee_id, cafe_id, days_ago=0):
    asgn = AssignmentModel(
        employee_id=employee_id,
        cafe_id=cafe_id,
        start_date=date.today() - timedelta(days=days_ago),
    )
    db.add(asgn)
    db.commit()
    return asgn


# ---------------------------------------------------------------------------
# GET /cafes
# ---------------------------------------------------------------------------

class TestGetCafes:
    def test_empty_list(self, client):
        resp = client.get("/cafes")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_returns_all_cafes(self, client, db_session):
        _make_cafe(db_session, name="CafeOne", location="CBD")
        _make_cafe(db_session, name="CafeTwo", location="Orchard")

        resp = client.get("/cafes")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_sorted_by_employees_desc(self, client, db_session):
        cafe1 = _make_cafe(db_session, name="CafeOne", location="CBD")
        cafe2 = _make_cafe(db_session, name="CafeTwo", location="Orchard")

        emp = _make_employee(db_session)
        _assign(db_session, emp.id, cafe2.id)

        resp = client.get("/cafes")
        data = resp.json()
        assert data[0]["name"] == "CafeTwo"
        assert data[0]["employees"] == 1
        assert data[1]["name"] == "CafeOne"
        assert data[1]["employees"] == 0

    def test_filter_by_location(self, client, db_session):
        _make_cafe(db_session, name="CafeOne", location="CBD")
        _make_cafe(db_session, name="CafeTwo", location="Orchard")

        resp = client.get("/cafes?location=CBD")
        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "CafeOne"

    def test_filter_unknown_location_returns_empty(self, client, db_session):
        _make_cafe(db_session, name="CafeOne", location="CBD")

        resp = client.get("/cafes?location=Nowhere")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_response_fields(self, client, db_session):
        _make_cafe(db_session, name="CafeABC", description="Nice place", location="CBD")

        data = client.get("/cafes").json()
        cafe = data[0]
        assert set(cafe.keys()) >= {"id", "name", "description", "employees", "logo", "location"}
        assert cafe["name"] == "CafeABC"
        assert cafe["employees"] == 0
        assert cafe["logo"] is None


# ---------------------------------------------------------------------------
# POST /cafes
# ---------------------------------------------------------------------------

class TestCreateCafe:
    def test_create_valid_returns_201(self, client):
        resp = client.post(
            "/cafes",
            data={"name": "CafeABC", "description": "Nice place", "location": "CBD"},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["name"] == "CafeABC"
        assert body["location"] == "CBD"
        assert "id" in body

    def test_create_persists_to_db(self, client, db_session):
        client.post(
            "/cafes",
            data={"name": "CafeABC", "description": "desc", "location": "CBD"},
        )
        assert db_session.query(CafeModel).count() == 1

    def test_name_too_short_returns_422(self, client):
        resp = client.post(
            "/cafes",
            data={"name": "Cafe", "description": "desc", "location": "CBD"},
        )
        assert resp.status_code == 422

    def test_name_too_long_returns_422(self, client):
        resp = client.post(
            "/cafes",
            data={"name": "ThisNameIsWayTooLong", "description": "desc", "location": "CBD"},
        )
        assert resp.status_code == 422

    def test_description_too_long_returns_422(self, client):
        resp = client.post(
            "/cafes",
            data={"name": "CafeABC", "description": "x" * 257, "location": "CBD"},
        )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# PUT /cafes/{id}
# ---------------------------------------------------------------------------

class TestUpdateCafe:
    def test_update_existing_returns_200(self, client, db_session):
        cafe = _make_cafe(db_session, name="OldName", description="Old", location="CBD")

        resp = client.put(
            f"/cafes/{cafe.id}",
            data={"name": "NewName", "description": "New desc", "location": "Orchard"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["name"] == "NewName"
        assert body["location"] == "Orchard"

    def test_update_not_found_returns_404(self, client):
        resp = client.put(
            "/cafes/nonexistent-id",
            data={"name": "CafeABC", "description": "desc", "location": "CBD"},
        )
        assert resp.status_code == 404

    def test_update_invalid_name_returns_422(self, client, db_session):
        cafe = _make_cafe(db_session)

        resp = client.put(
            f"/cafes/{cafe.id}",
            data={"name": "X", "description": "desc", "location": "CBD"},
        )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# DELETE /cafes/{id}
# ---------------------------------------------------------------------------

class TestDeleteCafe:
    def test_delete_existing_returns_204(self, client, db_session):
        cafe = _make_cafe(db_session)

        resp = client.delete(f"/cafes/{cafe.id}")
        assert resp.status_code == 204

    def test_delete_removes_from_db(self, client, db_session):
        cafe = _make_cafe(db_session)
        cafe_id = cafe.id

        client.delete(f"/cafes/{cafe.id}")
        db_session.expire_all()
        assert db_session.get(CafeModel, cafe_id) is None

    def test_delete_not_found_returns_404(self, client):
        resp = client.delete("/cafes/nonexistent-id")
        assert resp.status_code == 404

    def test_delete_cascades_employees(self, client, db_session):
        """Deleting a cafe must also delete its assigned employees (spec requirement)."""
        cafe = _make_cafe(db_session)
        emp = _make_employee(db_session, emp_id="UIABCDE99", email="emp99@example.com")
        _assign(db_session, emp.id, cafe.id)

        resp = client.delete(f"/cafes/{cafe.id}")
        assert resp.status_code == 204

        db_session.expire_all()
        assert db_session.get(EmployeeModel, emp.id) is None

    def test_delete_does_not_affect_unrelated_employees(self, client, db_session):
        cafe1 = _make_cafe(db_session, name="CafeOne")
        cafe2 = _make_cafe(db_session, name="CafeTwo")

        emp1 = _make_employee(db_session, emp_id="UIABCDE01", email="e1@example.com")
        emp2 = _make_employee(db_session, emp_id="UIABCDE02", email="e2@example.com")
        _assign(db_session, emp1.id, cafe1.id)
        _assign(db_session, emp2.id, cafe2.id)

        client.delete(f"/cafes/{cafe1.id}")
        db_session.expire_all()

        # emp1 (under cafe1) should be deleted
        assert db_session.get(EmployeeModel, emp1.id) is None
        # emp2 (under cafe2) should still exist
        assert db_session.get(EmployeeModel, emp2.id) is not None
