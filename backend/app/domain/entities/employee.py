from dataclasses import dataclass
from enum import Enum


class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"


@dataclass
class Employee:
    id: str
    name: str
    email_address: str
    phone_number: str
    gender: Gender
