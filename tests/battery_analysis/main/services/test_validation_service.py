import unittest.mock
from unittest.mock import Mock, patch
from battery_analysis.main.services.validation_service import ValidationService


class TestValidationService:
    def setup_method(self):
        self.service = ValidationService()

    def test_validate_test_info_success(self):
        test_info = ["项目A", "规格1", "磷酸铁锂", "1000", "", "", "", "", "", "", "", "", "", "", "", "", "v1.0"]
        is_valid, msg = self.service.validate_test_info(test_info)
        assert is_valid is True
        assert msg == ""

    def test_validate_test_info_empty(self):
        is_valid, msg = self.service.validate_test_info([])
        assert is_valid is False
        assert "Test information cannot be empty" in msg

    def test_validate_test_info_missing_field(self):
        test_info = ["项目A", "规格1", "", "1000"]
        is_valid, msg = self.service.validate_test_info(test_info)
        assert is_valid is False

    def test_validate_file_path_success(self):
        with patch('os.path.exists', return_value=True), \
             patch('os.path.isfile', return_value=True), \
             patch('builtins.open', unittest.mock.mock_open()):
            is_valid, msg = self.service.validate_file_path("test.xlsx")
            assert is_valid is True

    def test_validate_file_path_empty(self):
        is_valid, msg = self.service.validate_file_path("")
        assert is_valid is False

    def test_validate_file_path_not_found(self):
        with patch('os.path.exists', return_value=False):
            is_valid, msg = self.service.validate_file_path("nonexistent.xlsx")
            assert is_valid is False
            assert "File does not exist" in msg

    def test_validate_directory_path_success(self):
        with patch('os.path.exists', return_value=True), \
             patch('os.path.isdir', return_value=True), \
             patch('os.listdir', return_value=[]):
            is_valid, msg = self.service.validate_directory_path("output")
            assert is_valid is True

    def test_validate_directory_path_empty(self):
        is_valid, msg = self.service.validate_directory_path("")
        assert is_valid is False

    def test_validate_numeric_value_in_range(self):
        is_valid, msg = self.service.validate_numeric_value(50, 0, 100)
        assert is_valid is True

    def test_validate_numeric_value_below_min(self):
        is_valid, msg = self.service.validate_numeric_value(-1, 0, 100)
        assert is_valid is False

    def test_validate_numeric_value_above_max(self):
        is_valid, msg = self.service.validate_numeric_value(200, 0, 100)
        assert is_valid is False

    def test_validate_numeric_value_invalid(self):
        is_valid, msg = self.service.validate_numeric_value("abc")
        assert is_valid is False

    def test_validate_email_valid(self):
        is_valid, msg = self.service.validate_email("test@example.com")
        assert is_valid is True

    def test_validate_email_invalid(self):
        is_valid, msg = self.service.validate_email("not-an-email")
        assert is_valid is False

    def test_validate_email_empty(self):
        is_valid, msg = self.service.validate_email("")
        assert is_valid is False

    def test_validate_phone_number_valid(self):
        is_valid, msg = self.service.validate_phone_number("13800138000")
        assert is_valid is True

    def test_validate_phone_number_invalid(self):
        is_valid, msg = self.service.validate_phone_number("1234")
        assert is_valid is False

    def test_validate_battery_type_valid(self):
        is_valid, msg = self.service.validate_battery_type("磷酸铁锂")
        assert is_valid is True

    def test_validate_battery_type_invalid(self):
        is_valid, msg = self.service.validate_battery_type("未知电池")
        assert is_valid is False

    def test_validate_capacity_value_valid(self):
        is_valid, msg = self.service.validate_capacity_value("1000")
        assert is_valid is True

    def test_validate_capacity_value_invalid(self):
        is_valid, msg = self.service.validate_capacity_value("0")
        assert is_valid is False
