from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class Cafe:
    name: str
    description: str
    location: str
    logo: str | None = None
    id: str = field(default_factory=lambda: str(uuid4()))
