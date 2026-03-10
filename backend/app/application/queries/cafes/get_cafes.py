from dataclasses import dataclass


@dataclass
class GetCafesQuery:
    location: str | None = None
