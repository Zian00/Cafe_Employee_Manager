"""Seed the database with sample cafes, employees, and assignments.

Usage (from backend/ directory):
    python seed/seed.py
"""

import os
import random
import string
import sys
import uuid
from datetime import date, timedelta

# Ensure the backend root is on sys.path when run directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.infrastructure.db.models import (  # noqa: E402
    AssignmentModel,
    CafeModel,
    EmployeeModel,
)


def _generate_employee_id() -> str:
    chars = string.ascii_uppercase + string.digits
    return "UI" + "".join(random.choices(chars, k=7))


def main() -> None:
    engine = create_engine(os.environ["DATABASE_URL"])
    Session = sessionmaker(bind=engine)

    with Session() as session:
        # Clear in FK-safe order
        session.query(AssignmentModel).delete()
        session.query(EmployeeModel).delete()
        session.query(CafeModel).delete()
        session.commit()

        # ── Cafes ─────────────────────────────────────────────────────────────
        cafes = [
            CafeModel(
                id=str(uuid.uuid4()),
                name="Brewhouse",
                description="Specialty coffee and artisan pastries in the heart of the city.",
                logo=None,
                location="CBD",
            ),
            CafeModel(
                id=str(uuid.uuid4()),
                name="The Grind",
                description="Cozy neighborhood cafe known for its cold brew and waffles.",
                logo=None,
                location="Tampines",
            ),
            CafeModel(
                id=str(uuid.uuid4()),
                name="Roast & Co",
                description="Premium single-origin roasts with a warm, minimalist interior.",
                logo=None,
                location="Orchard",
            ),
            CafeModel(
                id=str(uuid.uuid4()),
                name="Bean Scene",
                description="A laid-back spot perfect for remote work and weekend brunches.",
                logo=None,
                location="Jurong",
            ),
        ]
        session.add_all(cafes)
        session.commit()

        # ── Employees ─────────────────────────────────────────────────────────
        employees = [
            EmployeeModel(
                id=_generate_employee_id(),
                name="Alice Tan",
                email_address="alice.tan@email.com",
                phone_number="91234567",
                gender="Female",
            ),
            EmployeeModel(
                id=_generate_employee_id(),
                name="Bob Lim",
                email_address="bob.lim@email.com",
                phone_number="82345678",
                gender="Male",
            ),
            EmployeeModel(
                id=_generate_employee_id(),
                name="Carol Ng",
                email_address="carol.ng@email.com",
                phone_number="93456789",
                gender="Female",
            ),
            EmployeeModel(
                id=_generate_employee_id(),
                name="David Koh",
                email_address="david.koh@email.com",
                phone_number="84567890",
                gender="Male",
            ),
            EmployeeModel(
                id=_generate_employee_id(),
                name="Eva Chen",
                email_address="eva.chen@email.com",
                phone_number="95678901",
                gender="Female",
            ),
            EmployeeModel(
                id=_generate_employee_id(),
                name="Frank Yeo",
                email_address="frank.yeo@email.com",
                phone_number="86789012",
                gender="Male",
            ),
            EmployeeModel(
                id=_generate_employee_id(),
                name="Grace Ong",
                email_address="grace.ong@email.com",
                phone_number="97890123",
                gender="Female",
            ),
        ]
        session.add_all(employees)
        session.commit()

        # ── Assignments ───────────────────────────────────────────────────────
        # Grace Ong (index 6) is intentionally left unassigned to test
        # the "blank cafe name" display case in GET /employees.
        today = date.today()
        assignments = [
            AssignmentModel(
                employee_id=employees[0].id,
                cafe_id=cafes[0].id,
                start_date=today - timedelta(days=365),
            ),
            AssignmentModel(
                employee_id=employees[1].id,
                cafe_id=cafes[0].id,
                start_date=today - timedelta(days=180),
            ),
            AssignmentModel(
                employee_id=employees[2].id,
                cafe_id=cafes[1].id,
                start_date=today - timedelta(days=90),
            ),
            AssignmentModel(
                employee_id=employees[3].id,
                cafe_id=cafes[2].id,
                start_date=today - timedelta(days=200),
            ),
            AssignmentModel(
                employee_id=employees[4].id,
                cafe_id=cafes[2].id,
                start_date=today - timedelta(days=45),
            ),
            AssignmentModel(
                employee_id=employees[5].id,
                cafe_id=cafes[3].id,
                start_date=today - timedelta(days=30),
            ),
        ]
        session.add_all(assignments)
        session.commit()

        print(
            f"Seeded {len(cafes)} cafes, {len(employees)} employees, "
            f"{len(assignments)} assignments."
        )
        print("Grace Ong is unassigned — tests the blank cafe display case.")


if __name__ == "__main__":
    main()
