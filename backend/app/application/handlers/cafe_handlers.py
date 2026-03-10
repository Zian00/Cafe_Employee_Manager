from sqlalchemy import func
from sqlalchemy.orm import Session

from app.application.commands.cafes.create_cafe import CreateCafeCommand
from app.application.commands.cafes.delete_cafe import DeleteCafeCommand
from app.application.commands.cafes.update_cafe import UpdateCafeCommand
from app.application.dtos.cafe_dto import CafeResponse
from app.application.queries.cafes.get_cafes import GetCafesQuery
from app.domain.entities.cafe import Cafe
from app.domain.exceptions import NotFoundError
from app.domain.repositories.cafe_repository import CafeRepository
from app.infrastructure.db.models.assignment_model import AssignmentModel
from app.infrastructure.db.models.cafe_model import CafeModel
from app.infrastructure.storage.supabase_storage import SupabaseStorageClient


class GetCafesQueryHandler:
    """Read-side: queries DB directly, bypassing repository."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def handle(self, query: GetCafesQuery) -> list[CafeResponse]:
        emp_count = func.count(AssignmentModel.employee_id).label("emp_count")
        q = (
            self._db.query(CafeModel, emp_count)
            .outerjoin(AssignmentModel, CafeModel.id == AssignmentModel.cafe_id)
            .group_by(CafeModel.id)
            .order_by(emp_count.desc())
        )
        if query.location is not None:
            q = q.filter(CafeModel.location == query.location)

        return [
            CafeResponse(
                id=cafe.id,
                name=cafe.name,
                description=cafe.description,
                employees=count,
                logo=cafe.logo,
                location=cafe.location,
            )
            for cafe, count in q.all()
        ]


class CreateCafeHandler:
    def __init__(self, repo: CafeRepository) -> None:
        self._repo = repo

    def handle(self, cmd: CreateCafeCommand) -> CafeResponse:
        cafe = Cafe(
            name=cmd.name,
            description=cmd.description,
            location=cmd.location,
            logo=cmd.logo,
        )
        created = self._repo.create(cafe)
        return CafeResponse(
            id=created.id,
            name=created.name,
            description=created.description,
            employees=0,
            logo=created.logo,
            location=created.location,
        )


class UpdateCafeHandler:
    def __init__(self, repo: CafeRepository) -> None:
        self._repo = repo

    def handle(self, cmd: UpdateCafeCommand) -> CafeResponse:
        if self._repo.get_by_id(cmd.id) is None:
            raise NotFoundError(f"Cafe '{cmd.id}' not found.")
        cafe = Cafe(
            id=cmd.id,
            name=cmd.name,
            description=cmd.description,
            location=cmd.location,
            logo=cmd.logo,
        )
        updated = self._repo.update(cafe)
        count = self._repo.get_employee_count(updated.id)
        return CafeResponse(
            id=updated.id,
            name=updated.name,
            description=updated.description,
            employees=count,
            logo=updated.logo,
            location=updated.location,
        )


class DeleteCafeHandler:
    def __init__(
        self, repo: CafeRepository, storage: SupabaseStorageClient
    ) -> None:
        self._repo = repo
        self._storage = storage

    def handle(self, cmd: DeleteCafeCommand) -> None:
        cafe = self._repo.get_by_id(cmd.id)
        if cafe is None:
            raise NotFoundError(f"Cafe '{cmd.id}' not found.")
        # Clean up logo from Supabase Storage if present
        if cafe.logo:
            try:
                self._storage.delete_by_url(cafe.logo)
            except Exception:
                pass  # Storage cleanup failure must not block DB delete
        self._repo.delete(cmd.id)
