from abc import ABC, abstractmethod

from app.domain.entities.cafe import Cafe


class CafeRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: str) -> Cafe | None: ...

    @abstractmethod
    def get_employee_count(self, cafe_id: str) -> int: ...

    @abstractmethod
    def create(self, cafe: Cafe) -> Cafe: ...

    @abstractmethod
    def update(self, cafe: Cafe) -> Cafe: ...

    @abstractmethod
    def delete(self, id: str) -> None: ...
