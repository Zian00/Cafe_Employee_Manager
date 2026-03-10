from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.handlers.cafe_handlers import (
    CreateCafeHandler,
    DeleteCafeHandler,
    GetCafesQueryHandler,
    UpdateCafeHandler,
)
from app.application.handlers.employee_handlers import (
    CreateEmployeeHandler,
    DeleteEmployeeHandler,
    GetEmployeesQueryHandler,
    UpdateEmployeeHandler,
)
from app.application.mediator import Mediator
from app.application.commands.cafes.create_cafe import CreateCafeCommand
from app.application.commands.cafes.update_cafe import UpdateCafeCommand
from app.application.commands.cafes.delete_cafe import DeleteCafeCommand
from app.application.commands.employees.create_employee import CreateEmployeeCommand
from app.application.commands.employees.update_employee import UpdateEmployeeCommand
from app.application.commands.employees.delete_employee import DeleteEmployeeCommand
from app.application.queries.cafes.get_cafes import GetCafesQuery
from app.application.queries.employees.get_employees import GetEmployeesQuery
from app.infrastructure.db.repositories.cafe_repo import SqlAlchemyCafeRepository
from app.infrastructure.db.repositories.employee_repo import SqlAlchemyEmployeeRepository
from app.infrastructure.db.session import get_db
from app.infrastructure.storage.supabase_storage import SupabaseStorageClient


def get_mediator(db: Session = Depends(get_db)) -> Mediator:
    cafe_repo = SqlAlchemyCafeRepository(db)
    employee_repo = SqlAlchemyEmployeeRepository(db)
    storage = SupabaseStorageClient()

    mediator = Mediator()
    mediator.register(GetCafesQuery, GetCafesQueryHandler(db))
    mediator.register(GetEmployeesQuery, GetEmployeesQueryHandler(db))
    mediator.register(CreateCafeCommand, CreateCafeHandler(cafe_repo))
    mediator.register(UpdateCafeCommand, UpdateCafeHandler(cafe_repo))
    mediator.register(DeleteCafeCommand, DeleteCafeHandler(cafe_repo, storage))
    mediator.register(CreateEmployeeCommand, CreateEmployeeHandler(employee_repo))
    mediator.register(UpdateEmployeeCommand, UpdateEmployeeHandler(employee_repo))
    mediator.register(DeleteEmployeeCommand, DeleteEmployeeHandler(employee_repo))

    return mediator


MediatorDep = Annotated[Mediator, Depends(get_mediator)]
