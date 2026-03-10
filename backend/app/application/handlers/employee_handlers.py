from datetime import date

from sqlalchemy.orm import Session

from app.application.commands.employees.create_employee import CreateEmployeeCommand
from app.application.commands.employees.delete_employee import DeleteEmployeeCommand
from app.application.commands.employees.update_employee import UpdateEmployeeCommand
from app.application.dtos.employee_dto import EmployeeResponse
from app.application.queries.employees.get_employees import GetEmployeesQuery
from app.domain.entities.employee import Employee, Gender
from app.domain.exceptions import NotFoundError
from app.domain.repositories.employee_repository import EmployeeRepository
from app.domain.value_objects.employee_id import EmployeeId
from app.infrastructure.db.models.assignment_model import AssignmentModel
from app.infrastructure.db.models.cafe_model import CafeModel
from app.infrastructure.db.models.employee_model import EmployeeModel


class GetEmployeesQueryHandler:
    """Read-side: queries DB directly, bypassing repository."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def handle(self, query: GetEmployeesQuery) -> list[EmployeeResponse]:
        today = date.today()

        q = (
            self._db.query(EmployeeModel, AssignmentModel, CafeModel)
            .outerjoin(
                AssignmentModel,
                EmployeeModel.id == AssignmentModel.employee_id,
            )
            .outerjoin(CafeModel, AssignmentModel.cafe_id == CafeModel.id)
        )
        if query.cafe is not None:
            q = q.filter(AssignmentModel.cafe_id == query.cafe)

        def _days(asgn: AssignmentModel | None) -> int:
            if asgn is None or asgn.start_date is None:
                return 0
            return (today - asgn.start_date).days

        results = [
            EmployeeResponse(
                id=emp.id,
                name=emp.name,
                email_address=emp.email_address,
                phone_number=emp.phone_number,
                days_worked=_days(asgn),
                cafe=cafe.name if cafe else "",
            )
            for emp, asgn, cafe in q.all()
        ]
        return sorted(results, key=lambda r: r.days_worked, reverse=True)


class CreateEmployeeHandler:
    def __init__(self, repo: EmployeeRepository) -> None:
        self._repo = repo

    def handle(self, cmd: CreateEmployeeCommand) -> EmployeeResponse:
        employee = Employee(
            id=EmployeeId.generate().value,
            name=cmd.name,
            email_address=cmd.email_address,
            phone_number=cmd.phone_number,
            gender=Gender(cmd.gender),
        )
        created = self._repo.create(employee, cafe_id=cmd.cafe_id)
        return EmployeeResponse(
            id=created.id,
            name=created.name,
            email_address=created.email_address,
            phone_number=created.phone_number,
            days_worked=0,
            cafe="",
        )


class UpdateEmployeeHandler:
    def __init__(self, repo: EmployeeRepository) -> None:
        self._repo = repo

    def handle(self, cmd: UpdateEmployeeCommand) -> EmployeeResponse:
        if self._repo.get_by_id(cmd.id) is None:
            raise NotFoundError(f"Employee '{cmd.id}' not found.")
        employee = Employee(
            id=cmd.id,
            name=cmd.name,
            email_address=cmd.email_address,
            phone_number=cmd.phone_number,
            gender=Gender(cmd.gender),
        )
        updated = self._repo.update(employee, cafe_id=cmd.cafe_id)
        return EmployeeResponse(
            id=updated.id,
            name=updated.name,
            email_address=updated.email_address,
            phone_number=updated.phone_number,
            days_worked=0,  # caller should re-fetch via GET for accurate value
            cafe="",
        )


class DeleteEmployeeHandler:
    def __init__(self, repo: EmployeeRepository) -> None:
        self._repo = repo

    def handle(self, cmd: DeleteEmployeeCommand) -> None:
        self._repo.delete(cmd.id)
