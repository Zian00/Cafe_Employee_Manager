import re

from pydantic import BaseModel, EmailStr, field_validator


class EmployeeResponse(BaseModel):
    id: str
    name: str
    email_address: str
    phone_number: str
    days_worked: int
    cafe: str  # blank string if unassigned


class CreateEmployeeRequest(BaseModel):
    name: str
    email_address: EmailStr
    phone_number: str
    gender: str
    cafe_id: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not (6 <= len(v) <= 10):
            raise ValueError("Name must be between 6 and 10 characters.")
        return v

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r"^[89]\d{7}$", v):
            raise ValueError(
                "Phone number must start with 8 or 9 and be exactly 8 digits."
            )
        return v

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        if v not in ("Male", "Female"):
            raise ValueError("Gender must be 'Male' or 'Female'.")
        return v


class UpdateEmployeeRequest(BaseModel):
    name: str
    email_address: EmailStr
    phone_number: str
    gender: str
    cafe_id: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not (6 <= len(v) <= 10):
            raise ValueError("Name must be between 6 and 10 characters.")
        return v

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r"^[89]\d{7}$", v):
            raise ValueError(
                "Phone number must start with 8 or 9 and be exactly 8 digits."
            )
        return v

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        if v not in ("Male", "Female"):
            raise ValueError("Gender must be 'Male' or 'Female'.")
        return v
