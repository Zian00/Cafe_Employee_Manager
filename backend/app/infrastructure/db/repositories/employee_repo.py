from datetime import date

from sqlalchemy.orm import Session

from app.domain.entities.employee import Employee, Gender
from app.domain.exceptions import ConflictError, NotFoundError
from app.domain.repositories.employee_repository import EmployeeRepository
from app.infrastructure.db.models.assignment_model import AssignmentModel
from app.infrastructure.db.models.employee_model import EmployeeModel


class SqlAlchemyEmployeeRepository(EmployeeRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, id: str) -> Employee | None:
        model = self._session.get(EmployeeModel, id)
        return self._to_entity(model) if model else None

    def exists_by_email(
        self, email: str, exclude_id: str | None = None
    ) -> bool:
        q = self._session.query(EmployeeModel).filter(
            EmployeeModel.email_address == email
        )
        if exclude_id:
            q = q.filter(EmployeeModel.id != exclude_id)
        return q.first() is not None

    def create(self, employee: Employee, cafe_id: str | None = None) -> Employee:
        if self.exists_by_email(employee.email_address):
            raise ConflictError(
                f"Email '{employee.email_address}' is already in use."
            )
        model = EmployeeModel(
            id=employee.id,
            name=employee.name,
            email_address=employee.email_address,
            phone_number=employee.phone_number,
            gender=employee.gender.value,
        )
        self._session.add(model)
        self._session.flush()

        if cafe_id:
            self._session.add(
                AssignmentModel(
                    employee_id=employee.id,
                    cafe_id=cafe_id,
                    start_date=date.today(),
                )
            )
        self._session.commit()
        return employee

    def update(
        self, employee: Employee, cafe_id: str | None = None
    ) -> Employee:
        model = self._session.get(EmployeeModel, employee.id)
        if model is None:
            raise NotFoundError(f"Employee '{employee.id}' not found.")
        if self.exists_by_email(employee.email_address, exclude_id=employee.id):
            raise ConflictError(
                f"Email '{employee.email_address}' is already in use."
            )

        model.name = employee.name
        model.email_address = employee.email_address
        model.phone_number = employee.phone_number
        model.gender = employee.gender.value

        existing = self._session.get(AssignmentModel, employee.id)
        if cafe_id is None:
            if existing:
                self._session.delete(existing)
        else:
            if existing and existing.cafe_id == cafe_id:
                pass  # same cafe — preserve original start_date
            else:
                if existing:
                    self._session.delete(existing)
                    self._session.flush()
                self._session.add(
                    AssignmentModel(
                        employee_id=employee.id,
                        cafe_id=cafe_id,
                        start_date=date.today(),
                    )
                )
        self._session.commit()
        return employee

    def delete(self, id: str) -> None:
        model = self._session.get(EmployeeModel, id)
        if model is None:
            raise NotFoundError(f"Employee '{id}' not found.")
        self._session.delete(model)
        self._session.commit()

    def _to_entity(self, model: EmployeeModel) -> Employee:
        return Employee(
            id=model.id,
            name=model.name,
            email_address=model.email_address,
            phone_number=model.phone_number,
            gender=Gender(model.gender),
        )
