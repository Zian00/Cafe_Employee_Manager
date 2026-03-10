from sqlalchemy import func
from sqlalchemy.orm import Session

from app.domain.entities.cafe import Cafe
from app.domain.exceptions import NotFoundError
from app.domain.repositories.cafe_repository import CafeRepository
from app.infrastructure.db.models.assignment_model import AssignmentModel
from app.infrastructure.db.models.cafe_model import CafeModel


class SqlAlchemyCafeRepository(CafeRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, id: str) -> Cafe | None:
        model = self._session.get(CafeModel, id)
        return self._to_entity(model) if model else None

    def get_employee_count(self, cafe_id: str) -> int:
        return (
            self._session.query(func.count(AssignmentModel.employee_id))
            .filter(AssignmentModel.cafe_id == cafe_id)
            .scalar()
            or 0
        )

    def create(self, cafe: Cafe) -> Cafe:
        model = CafeModel(
            id=cafe.id,
            name=cafe.name,
            description=cafe.description,
            logo=cafe.logo,
            location=cafe.location,
        )
        self._session.add(model)
        self._session.commit()
        return cafe

    def update(self, cafe: Cafe) -> Cafe:
        model = self._session.get(CafeModel, cafe.id)
        if model is None:
            raise NotFoundError(f"Cafe '{cafe.id}' not found.")
        model.name = cafe.name
        model.description = cafe.description
        model.logo = cafe.logo
        model.location = cafe.location
        self._session.commit()
        return cafe

    def delete(self, id: str) -> None:
        model = self._session.get(CafeModel, id)
        if model is None:
            raise NotFoundError(f"Cafe '{id}' not found.")
        # Spec: deleting a cafe also deletes all employees under it.
        # Use list() snapshot to avoid mutating the collection mid-iteration.
        for asgn in list(model.assignments):
            self._session.delete(asgn.employee)
        self._session.flush()
        self._session.delete(model)
        self._session.commit()

    def _to_entity(self, model: CafeModel) -> Cafe:
        return Cafe(
            id=model.id,
            name=model.name,
            description=model.description,
            logo=model.logo,
            location=model.location,
        )
