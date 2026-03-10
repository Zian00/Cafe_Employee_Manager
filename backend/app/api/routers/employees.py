from fastapi import APIRouter

from app.api.dependencies import MediatorDep
from app.application.commands.employees.create_employee import CreateEmployeeCommand
from app.application.commands.employees.delete_employee import DeleteEmployeeCommand
from app.application.commands.employees.update_employee import UpdateEmployeeCommand
from app.application.dtos.employee_dto import (
    CreateEmployeeRequest,
    EmployeeResponse,
    UpdateEmployeeRequest,
)
from app.application.queries.employees.get_employees import GetEmployeesQuery

router = APIRouter()


@router.get("/employees", response_model=list[EmployeeResponse])
def get_employees(
    mediator: MediatorDep,
    cafe: str | None = None,
):
    """List all employees sorted by days_worked desc. Filter by cafe_id if provided."""
    return mediator.send(GetEmployeesQuery(cafe=cafe))


@router.post("/employees", response_model=EmployeeResponse, status_code=201)
def create_employee(body: CreateEmployeeRequest, mediator: MediatorDep):
    """Create a new employee. Optionally assign to a cafe via cafe_id."""
    return mediator.send(
        CreateEmployeeCommand(
            name=body.name,
            email_address=str(body.email_address),
            phone_number=body.phone_number,
            gender=body.gender,
            cafe_id=body.cafe_id,
        )
    )


@router.put("/employees/{id}", response_model=EmployeeResponse)
def update_employee(id: str, body: UpdateEmployeeRequest, mediator: MediatorDep):
    """Update an existing employee and their cafe assignment."""
    return mediator.send(
        UpdateEmployeeCommand(
            id=id,
            name=body.name,
            email_address=str(body.email_address),
            phone_number=body.phone_number,
            gender=body.gender,
            cafe_id=body.cafe_id,
        )
    )


@router.delete("/employees/{id}", status_code=204)
def delete_employee(id: str, mediator: MediatorDep):
    """Delete an employee."""
    mediator.send(DeleteEmployeeCommand(id=id))
