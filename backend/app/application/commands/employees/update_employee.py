from dataclasses import dataclass


@dataclass
class UpdateEmployeeCommand:
    id: str
    name: str
    email_address: str
    phone_number: str
    gender: str
    cafe_id: str | None = None
