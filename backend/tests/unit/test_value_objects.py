import pytest

from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.phone_number import PhoneNumber


class TestEmployeeId:
    def test_valid_id(self):
        eid = EmployeeId("UI1234567")
        assert eid.value == "UI1234567"

    def test_generate_returns_valid_id(self):
        eid = EmployeeId.generate()
        assert eid.value.startswith("UI")
        assert len(eid.value) == 9
        assert eid.value[2:].isalnum()

    def test_generate_produces_unique_ids(self):
        ids = {EmployeeId.generate().value for _ in range(50)}
        assert len(ids) == 50

    def test_invalid_prefix_raises(self):
        with pytest.raises(ValueError, match="Invalid employee ID"):
            EmployeeId("AB1234567")

    def test_too_short_raises(self):
        with pytest.raises(ValueError):
            EmployeeId("UI123456")  # 6 chars after UI — one too few

    def test_too_long_raises(self):
        with pytest.raises(ValueError):
            EmployeeId("UI12345678")  # 8 chars after UI — one too many

    def test_special_chars_rejected(self):
        with pytest.raises(ValueError):
            EmployeeId("UI123@567")

    def test_lowercase_letters_accepted(self):
        eid = EmployeeId("UIabcde12")
        assert eid.value == "UIabcde12"

    def test_equality(self):
        assert EmployeeId("UI1234567") == EmployeeId("UI1234567")

    def test_inequality(self):
        assert EmployeeId("UI1234567") != EmployeeId("UI7654321")

    def test_str(self):
        assert str(EmployeeId("UI1234567")) == "UI1234567"

    def test_hash(self):
        a = EmployeeId("UI1234567")
        b = EmployeeId("UI1234567")
        assert hash(a) == hash(b)


class TestPhoneNumber:
    def test_valid_8_prefix(self):
        ph = PhoneNumber("81234567")
        assert ph.value == "81234567"

    def test_valid_9_prefix(self):
        ph = PhoneNumber("91234567")
        assert ph.value == "91234567"

    def test_invalid_7_prefix_raises(self):
        with pytest.raises(ValueError, match="Invalid SG phone"):
            PhoneNumber("71234567")

    def test_invalid_0_prefix_raises(self):
        with pytest.raises(ValueError):
            PhoneNumber("01234567")

    def test_too_short_raises(self):
        with pytest.raises(ValueError):
            PhoneNumber("8123456")  # 7 digits

    def test_too_long_raises(self):
        with pytest.raises(ValueError):
            PhoneNumber("812345678")  # 9 digits

    def test_non_digits_raises(self):
        with pytest.raises(ValueError):
            PhoneNumber("8123456a")

    def test_equality(self):
        assert PhoneNumber("81234567") == PhoneNumber("81234567")

    def test_inequality(self):
        assert PhoneNumber("81234567") != PhoneNumber("91234567")

    def test_hash(self):
        assert hash(PhoneNumber("81234567")) == hash(PhoneNumber("81234567"))
