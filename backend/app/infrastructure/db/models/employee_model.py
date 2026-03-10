from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.models.base import Base


class EmployeeModel(Base):
    __tablename__ = "employees"

    id: Mapped[str] = mapped_column(String(9), primary_key=True)
    name: Mapped[str] = mapped_column(String(10), nullable=False)
    email_address: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    phone_number: Mapped[str] = mapped_column(String(8), nullable=False)
    gender: Mapped[str] = mapped_column(String(6), nullable=False)

    # uselist=False — one employee has at most one assignment at a time
    assignment: Mapped["AssignmentModel | None"] = relationship(  # noqa: F821
        "AssignmentModel",
        back_populates="employee",
        uselist=False,
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint(
            "id ~ '^UI[A-Za-z0-9]{7}$'", name="ck_employees_id_format"
        ),
        CheckConstraint(
            "length(name) >= 6", name="ck_employees_name_min_length"
        ),
        CheckConstraint(
            "phone_number ~ '^[89][0-9]{7}$'", name="ck_employees_phone_format"
        ),
        CheckConstraint(
            "gender IN ('Male', 'Female')", name="ck_employees_gender"
        ),
    )
