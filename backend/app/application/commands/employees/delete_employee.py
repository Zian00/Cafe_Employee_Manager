from dataclasses import dataclass


@dataclass
class DeleteEmployeeCommand:
    id: str
