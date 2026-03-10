from abc import ABC, abstractmethod

from app.domain.entities.employee import Employee


class EmployeeRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: str) -> Employee | None: ...

    @abstractmethod
    def exists_by_email(self, email: str, exclude_id: str | None = None) -> bool: ...

    @abstractmethod
    def create(self, employee: Employee, cafe_id: str | None = None) -> Employee: ...

    @abstractmethod
    def update(self, employee: Employee, cafe_id: str | None = None) -> Employee: ...

    @abstractmethod
    def delete(self, id: str) -> None: ...
