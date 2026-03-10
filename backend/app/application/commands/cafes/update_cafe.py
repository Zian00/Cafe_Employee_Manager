from dataclasses import dataclass


@dataclass
class UpdateCafeCommand:
    id: str
    name: str
    description: str
    location: str
    logo: str | None = None
