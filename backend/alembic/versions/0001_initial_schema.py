"""Initial schema: cafes, employees, employee_cafe_assignments

Revision ID: 0001
Revises:
Create Date: 2026-03-10
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── cafes ────────────────────────────────────────────────────────────────
    op.create_table(
        "cafes",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("name", sa.String(10), nullable=False),
        sa.Column("description", sa.String(256), nullable=False),
        sa.Column("logo", sa.String(512), nullable=True),
        sa.Column("location", sa.String(100), nullable=False),
        sa.CheckConstraint("length(name) >= 6", name="ck_cafes_name_min_length"),
    )
    op.create_index("ix_cafes_location", "cafes", ["location"])

    # ── employees ────────────────────────────────────────────────────────────
    op.create_table(
        "employees",
        sa.Column("id", sa.String(9), primary_key=True, nullable=False),
        sa.Column("name", sa.String(10), nullable=False),
        sa.Column(
            "email_address", sa.String(255), nullable=False, unique=True
        ),
        sa.Column("phone_number", sa.String(8), nullable=False),
        sa.Column("gender", sa.String(6), nullable=False),
        sa.CheckConstraint(
            "id ~ '^UI[A-Za-z0-9]{7}$'", name="ck_employees_id_format"
        ),
        sa.CheckConstraint(
            "length(name) >= 6", name="ck_employees_name_min_length"
        ),
        sa.CheckConstraint(
            "phone_number ~ '^[89][0-9]{7}$'",
            name="ck_employees_phone_format",
        ),
        sa.CheckConstraint(
            "gender IN ('Male', 'Female')", name="ck_employees_gender"
        ),
    )

    # ── employee_cafe_assignments ─────────────────────────────────────────────
    # employee_id is the sole PK — enforces one-cafe-per-employee at DB level
    op.create_table(
        "employee_cafe_assignments",
        sa.Column(
            "employee_id",
            sa.String(9),
            sa.ForeignKey("employees.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "cafe_id",
            sa.String(36),
            sa.ForeignKey("cafes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("start_date", sa.Date, nullable=False),
    )
    op.create_index(
        "ix_assignments_cafe_start",
        "employee_cafe_assignments",
        ["cafe_id", "start_date"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_assignments_cafe_start",
        table_name="employee_cafe_assignments",
    )
    op.drop_table("employee_cafe_assignments")
    op.drop_table("employees")
    op.drop_index("ix_cafes_location", table_name="cafes")
    op.drop_table("cafes")
