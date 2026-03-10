from dataclasses import dataclass


@dataclass
class GetEmployeesQuery:
    cafe: str | None = None  # filter by cafe_id
