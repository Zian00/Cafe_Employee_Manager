import re


class PhoneNumber:
    PATTERN = re.compile(r"^[89]\d{7}$")

    def __init__(self, value: str) -> None:
        if not self.PATTERN.match(value):
            raise ValueError(
                f"Invalid SG phone number '{value}'. "
                "Must start with 8 or 9 and be exactly 8 digits."
            )
        self._value = value

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, PhoneNumber):
            return self._value == other._value
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._value)
