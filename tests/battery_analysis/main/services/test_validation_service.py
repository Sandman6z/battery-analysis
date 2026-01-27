import pytest
from unittest.mock import Mock, patch
from battery_analysis.main.services.validation_service import ValidationService


class TestValidationService:
    def setup_method(self):
        self.service = ValidationService()

    def test_validate_data(self):
        data = {
            "voltage": [4.2, 4.1, 4.0],
            "current": [0.5, 0.5, 0.5]
        }
        result = self.service.validate_data(data)
        assert isinstance(result, dict)

    def test_validate_configuration(self):
        config = {
            "name": "Test Config",
            "parameters": {}
        }
        result = self.service.validate_configuration(config)
        assert isinstance(result, dict)

    def test_validate_file(self):
        file_path = "test_file.xlsx"
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True
            result = self.service.validate_file(file_path)
            assert isinstance(result, dict)