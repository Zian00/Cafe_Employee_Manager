from pydantic import BaseModel, field_validator


class CafeResponse(BaseModel):
    id: str
    name: str
    description: str
    employees: int
    logo: str | None
    location: str


class CreateCafeRequest(BaseModel):
    name: str
    description: str
    location: str
    logo: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not (6 <= len(v) <= 10):
            raise ValueError("Name must be between 6 and 10 characters.")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        if len(v) > 256:
            raise ValueError("Description must not exceed 256 characters.")
        return v


class UpdateCafeRequest(BaseModel):
    name: str
    description: str
    location: str
    logo: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not (6 <= len(v) <= 10):
            raise ValueError("Name must be between 6 and 10 characters.")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        if len(v) > 256:
            raise ValueError("Description must not exceed 256 characters.")
        return v
