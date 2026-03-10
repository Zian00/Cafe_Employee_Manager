from dataclasses import dataclass


@dataclass
class CreateCafeCommand:
    name: str
    description: str
    location: str
    logo: str | None = None
