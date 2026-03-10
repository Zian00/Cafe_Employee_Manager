import pytest
from pydantic import ValidationError

from app.application.dtos.cafe_dto import CreateCafeRequest
from app.application.dtos.employee_dto import CreateEmployeeRequest


class TestCreateCafeRequest:
    def test_valid(self):
        req = CreateCafeRequest(
            name="CafeABC", description="A nice place", location="CBD"
        )
        assert req.name == "CafeABC"
        assert req.location == "CBD"

    def test_name_exactly_6_chars(self):
        req = CreateCafeRequest(name="CafeXX", description="desc", location="CBD")
        assert len(req.name) == 6

    def test_name_exactly_10_chars(self):
        req = CreateCafeRequest(name="CafeXXXXXX", description="desc", location="CBD")
        assert len(req.name) == 10

    def test_name_too_short_raises(self):
        with pytest.raises(ValidationError, match="Name must be between 6 and 10 characters"):
            CreateCafeRequest(name="Cafe", description="desc", location="CBD")

    def test_name_too_long_raises(self):
        with pytest.raises(ValidationError, match="Name must be between 6 and 10 characters"):
            CreateCafeRequest(name="CafeTooLongX", description="desc", location="CBD")

    def test_description_exactly_256_chars(self):
        req = CreateCafeRequest(name="CafeABC", description="x" * 256, location="CBD")
        assert len(req.description) == 256

    def test_description_too_long_raises(self):
        with pytest.raises(
            ValidationError, match="Description must not exceed 256 characters"
        ):
            CreateCafeRequest(name="CafeABC", description="x" * 257, location="CBD")

    def test_logo_optional(self):
        req = CreateCafeRequest(name="CafeABC", description="desc", location="CBD")
        assert req.logo is None

    def test_logo_can_be_set(self):
        req = CreateCafeRequest(
            name="CafeABC",
            description="desc",
            location="CBD",
            logo="https://example.com/logo.png",
        )
        assert req.logo == "https://example.com/logo.png"


class TestCreateEmployeeRequest:
    def test_valid_no_cafe(self):
        req = CreateEmployeeRequest(
            name="AliceB",
            email_address="alice@example.com",
            phone_number="81234567",
            gender="Female",
        )
        assert req.name == "AliceB"
        assert req.cafe_id is None

    def test_valid_with_cafe(self):
        req = CreateEmployeeRequest(
            name="AliceB",
            email_address="alice@example.com",
            phone_number="81234567",
            gender="Female",
            cafe_id="some-uuid-value",
        )
        assert req.cafe_id == "some-uuid-value"

    def test_name_exactly_6_chars(self):
        req = CreateEmployeeRequest(
            name="AliceB",
            email_address="a@b.com",
            phone_number="81234567",
            gender="Male",
        )
        assert len(req.name) == 6

    def test_name_too_short_raises(self):
        with pytest.raises(
            ValidationError, match="Name must be between 6 and 10 characters"
        ):
            CreateEmployeeRequest(
                name="Ali",
                email_address="a@b.com",
                phone_number="81234567",
                gender="Male",
            )

    def test_name_too_long_raises(self):
        with pytest.raises(
            ValidationError, match="Name must be between 6 and 10 characters"
        ):
            CreateEmployeeRequest(
                name="AliceTooLongName",
                email_address="a@b.com",
                phone_number="81234567",
                gender="Male",
            )

    def test_invalid_phone_prefix_raises(self):
        with pytest.raises(
            ValidationError, match="Phone number must start with 8 or 9"
        ):
            CreateEmployeeRequest(
                name="AliceB",
                email_address="a@b.com",
                phone_number="71234567",
                gender="Female",
            )

    def test_invalid_phone_length_raises(self):
        with pytest.raises(ValidationError):
            CreateEmployeeRequest(
                name="AliceB",
                email_address="a@b.com",
                phone_number="8123456",  # 7 digits
                gender="Female",
            )

    def test_invalid_gender_raises(self):
        with pytest.raises(ValidationError, match="Gender must be"):
            CreateEmployeeRequest(
                name="AliceB",
                email_address="a@b.com",
                phone_number="81234567",
                gender="Other",
            )

    def test_male_gender_accepted(self):
        req = CreateEmployeeRequest(
            name="AliceB",
            email_address="a@b.com",
            phone_number="81234567",
            gender="Male",
        )
        assert req.gender == "Male"

    def test_invalid_email_raises(self):
        with pytest.raises(ValidationError):
            CreateEmployeeRequest(
                name="AliceB",
                email_address="not-an-email",
                phone_number="81234567",
                gender="Female",
            )
