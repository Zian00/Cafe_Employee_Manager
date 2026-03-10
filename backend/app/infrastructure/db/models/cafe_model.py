import uuid

from sqlalchemy import CheckConstraint, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.models.base import Base


class CafeModel(Base):
    __tablename__ = "cafes"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(10), nullable=False)
    description: Mapped[str] = mapped_column(String(256), nullable=False)
    logo: Mapped[str | None] = mapped_column(String(512), nullable=True)
    location: Mapped[str] = mapped_column(String(100), nullable=False)

    assignments: Mapped[list["AssignmentModel"]] = relationship(  # noqa: F821
        "AssignmentModel", back_populates="cafe", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("length(name) >= 6", name="ck_cafes_name_min_length"),
        Index("ix_cafes_location", "location"),
    )
