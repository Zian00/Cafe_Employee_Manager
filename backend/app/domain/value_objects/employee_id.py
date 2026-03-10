import random
import re
import string


class EmployeeId:
    PATTERN = re.compile(r"^UI[A-Za-z0-9]{7}$")

    def __init__(self, value: str) -> None:
        if not self.PATTERN.match(value):
            raise ValueError(
                f"Invalid employee ID '{value}'. "
                "Must be 'UI' followed by 7 alphanumeric characters."
            )
        self._value = value

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"EmployeeId('{self._value}')"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, EmployeeId):
            return self._value == other._value
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._value)

    @classmethod
    def generate(cls) -> "EmployeeId":
        chars = string.ascii_uppercase + string.digits
        suffix = "".join(random.choices(chars, k=7))
        return cls(f"UI{suffix}")
