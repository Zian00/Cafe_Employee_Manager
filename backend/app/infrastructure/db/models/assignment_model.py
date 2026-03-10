from datetime import date

from sqlalchemy import Date, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.models.base import Base


class AssignmentModel(Base):
    __tablename__ = "employee_cafe_assignments"

    # employee_id as sole PK enforces one-cafe-per-employee at the DB level
    employee_id: Mapped[str] = mapped_column(
        String(9),
        ForeignKey("employees.id", ondelete="CASCADE"),
        primary_key=True,
    )
    cafe_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("cafes.id", ondelete="CASCADE"),
        nullable=False,
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)

    employee: Mapped["EmployeeModel"] = relationship(  # noqa: F821
        "EmployeeModel", back_populates="assignment"
    )
    cafe: Mapped["CafeModel"] = relationship(  # noqa: F821
        "CafeModel", back_populates="assignments"
    )

    __table_args__ = (
        Index("ix_assignments_cafe_start", "cafe_id", "start_date"),
    )
