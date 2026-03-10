"""Integration tests for /employees endpoints."""
from datetime import date, timedelta

import pytest

from app.infrastructure.db.models.assignment_model import AssignmentModel
from app.infrastructure.db.models.cafe_model import CafeModel
from app.infrastructure.db.models.employee_model import EmployeeModel


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_cafe(db, name="CafeOne", location="CBD"):
    cafe = CafeModel(name=name, description="A cafe", location=location)
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


def _assign(db, employee_id, cafe_id, days_ago=10):
    asgn = AssignmentModel(
        employee_id=employee_id,
        cafe_id=cafe_id,
        start_date=date.today() - timedelta(days=days_ago),
    )
    db.add(asgn)
    db.commit()
    return asgn


_VALID_BODY = {
    "name": "AliceB",
    "email_address": "alice@example.com",
    "phone_number": "81234567",
    "gender": "Female",
}


# ---------------------------------------------------------------------------
# GET /employees
# ---------------------------------------------------------------------------

class TestGetEmployees:
    def test_empty_list(self, client):
        resp = client.get("/employees")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_returns_all_employees(self, client, db_session):
        _make_employee(db_session, emp_id="UIABCDE01", email="a@example.com")
        _make_employee(db_session, emp_id="UIABCDE02", email="b@example.com")
        db_session.commit()

        resp = client.get("/employees")
        assert len(resp.json()) == 2

    def test_sorted_by_days_worked_desc(self, client, db_session):
        cafe = _make_cafe(db_session)

        emp1 = _make_employee(db_session, emp_id="UIABCDE01", email="e1@example.com", name="JohnDoe")
        emp2 = _make_employee(db_session, emp_id="UIABCDE02", email="e2@example.com", name="JaneDoe")

        _assign(db_session, emp1.id, cafe.id, days_ago=5)
        _assign(db_session, emp2.id, cafe.id, days_ago=20)

        resp = client.get("/employees")
        data = resp.json()
        assert data[0]["days_worked"] >= data[1]["days_worked"]
        assert data[0]["days_worked"] == 20
        assert data[1]["days_worked"] == 5

    def test_filter_by_cafe(self, client, db_session):
        cafe1 = _make_cafe(db_session, name="CafeOne")
        cafe2 = _make_cafe(db_session, name="CafeTwo")

        emp1 = _make_employee(db_session, emp_id="UIABCDE01", email="e1@example.com")
        emp2 = _make_employee(db_session, emp_id="UIABCDE02", email="e2@example.com")
        _assign(db_session, emp1.id, cafe1.id)
        _assign(db_session, emp2.id, cafe2.id)

        resp = client.get(f"/employees?cafe={cafe1.id}")
        data = resp.json()
        assert len(data) == 1
        assert data[0]["cafe"] == "CafeOne"

    def test_days_worked_calculation(self, client, db_session):
        cafe = _make_cafe(db_session)
        emp = _make_employee(db_session)
        _assign(db_session, emp.id, cafe.id, days_ago=30)

        data = client.get("/employees").json()
        assert data[0]["days_worked"] == 30

    def test_unassigned_employee_has_zero_days_and_blank_cafe(self, client, db_session):
        _make_employee(db_session)
        db_session.commit()

        data = client.get("/employees").json()
        assert data[0]["days_worked"] == 0
        assert data[0]["cafe"] == ""

    def test_response_fields(self, client, db_session):
        _make_employee(db_session)
        db_session.commit()

        emp = client.get("/employees").json()[0]
        assert set(emp.keys()) >= {
            "id", "name", "email_address", "phone_number",
            "gender", "days_worked", "cafe", "cafe_id",
        }


# ---------------------------------------------------------------------------
# POST /employees
# ---------------------------------------------------------------------------

class TestCreateEmployee:
    def test_create_valid_returns_201(self, client):
        resp = client.post("/employees", json=_VALID_BODY)
        assert resp.status_code == 201
        body = resp.json()
        assert body["name"] == "AliceB"
        assert body["id"].startswith("UI")
        assert len(body["id"]) == 9

    def test_create_with_cafe_assignment(self, client, db_session):
        cafe = _make_cafe(db_session)

        body = {**_VALID_BODY, "cafe_id": cafe.id}
        resp = client.post("/employees", json=body)
        assert resp.status_code == 201
        assert resp.json()["cafe_id"] == cafe.id

        # Assignment record should exist in DB
        emp_id = resp.json()["id"]
        db_session.expire_all()
        asgn = db_session.get(AssignmentModel, emp_id)
        assert asgn is not None
        assert asgn.cafe_id == cafe.id

    def test_duplicate_email_returns_409(self, client):
        client.post("/employees", json=_VALID_BODY)
        resp = client.post("/employees", json=_VALID_BODY)
        assert resp.status_code == 409

    def test_invalid_phone_returns_422(self, client):
        body = {**_VALID_BODY, "phone_number": "71234567"}
        resp = client.post("/employees", json=body)
        assert resp.status_code == 422

    def test_invalid_gender_returns_422(self, client):
        body = {**_VALID_BODY, "gender": "Unknown"}
        resp = client.post("/employees", json=body)
        assert resp.status_code == 422

    def test_invalid_email_returns_422(self, client):
        body = {**_VALID_BODY, "email_address": "not-an-email"}
        resp = client.post("/employees", json=body)
        assert resp.status_code == 422

    def test_name_too_short_returns_422(self, client):
        body = {**_VALID_BODY, "name": "Ali"}
        resp = client.post("/employees", json=body)
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# PUT /employees/{id}
# ---------------------------------------------------------------------------

class TestUpdateEmployee:
    def test_update_existing_returns_200(self, client, db_session):
        emp = _make_employee(db_session)
        db_session.commit()

        update_body = {
            "name": "AliceB",
            "email_address": "alice@example.com",
            "phone_number": "91234567",
            "gender": "Female",
        }
        resp = client.put(f"/employees/{emp.id}", json=update_body)
        assert resp.status_code == 200
        assert resp.json()["phone_number"] == "91234567"

    def test_update_not_found_returns_404(self, client):
        resp = client.put(
            "/employees/UIXXXXXXX",
            json={
                "name": "AliceB",
                "email_address": "alice@example.com",
                "phone_number": "81234567",
                "gender": "Female",
            },
        )
        assert resp.status_code == 404

    def test_update_changes_cafe_assignment(self, client, db_session):
        cafe1 = _make_cafe(db_session, name="CafeOne")
        cafe2 = _make_cafe(db_session, name="CafeTwo")
        emp = _make_employee(db_session)
        _assign(db_session, emp.id, cafe1.id)

        update_body = {
            "name": "JohnDoe",
            "email_address": "john@example.com",
            "phone_number": "81234567",
            "gender": "Male",
            "cafe_id": cafe2.id,
        }
        resp = client.put(f"/employees/{emp.id}", json=update_body)
        assert resp.status_code == 200

        db_session.expire_all()
        asgn = db_session.get(AssignmentModel, emp.id)
        assert asgn.cafe_id == cafe2.id

    def test_update_remove_cafe_assignment(self, client, db_session):
        cafe = _make_cafe(db_session)
        emp = _make_employee(db_session)
        _assign(db_session, emp.id, cafe.id)

        update_body = {
            "name": "JohnDoe",
            "email_address": "john@example.com",
            "phone_number": "81234567",
            "gender": "Male",
            "cafe_id": None,
        }
        resp = client.put(f"/employees/{emp.id}", json=update_body)
        assert resp.status_code == 200

        db_session.expire_all()
        asgn = db_session.get(AssignmentModel, emp.id)
        assert asgn is None


# ---------------------------------------------------------------------------
# DELETE /employees/{id}
# ---------------------------------------------------------------------------

class TestDeleteEmployee:
    def test_delete_existing_returns_204(self, client, db_session):
        emp = _make_employee(db_session)
        db_session.commit()

        resp = client.delete(f"/employees/{emp.id}")
        assert resp.status_code == 204

    def test_delete_removes_from_db(self, client, db_session):
        emp = _make_employee(db_session)
        db_session.commit()
        emp_id = emp.id

        client.delete(f"/employees/{emp.id}")
        db_session.expire_all()
        assert db_session.get(EmployeeModel, emp_id) is None

    def test_delete_also_removes_assignment(self, client, db_session):
        cafe = _make_cafe(db_session)
        emp = _make_employee(db_session)
        _assign(db_session, emp.id, cafe.id)
        emp_id = emp.id

        client.delete(f"/employees/{emp.id}")
        db_session.expire_all()
        assert db_session.get(AssignmentModel, emp_id) is None

    def test_delete_not_found_returns_404(self, client):
        resp = client.delete("/employees/UIXXXXXXX")
        assert resp.status_code == 404
