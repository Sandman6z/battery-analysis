import pytest
from unittest.mock import Mock, patch
from battery_analysis.main.controllers.validation_controller import ValidationController


class TestValidationController:
    def setup_method(self):
        self.controller = ValidationController()

    def test_validate_data(self):
        data = {
            "voltage": [4.2, 4.1, 4.0],
            "current": [0.5, 0.5, 0.5]
        }
        with patch('battery_analysis.main.controllers.validation_controller.ValidationService') as mock_validation_service:
            mock_instance = Mock()
            mock_validation_service.return_value = mock_instance
            mock_instance.validate_data.return_value = {"valid": True}
            result = self.controller.validate_data(data)
            assert result is not None

    def test_validate_configuration(self):
        config = {
            "name": "Test Config",
            "parameters": {}
        }
        with patch('battery_analysis.main.controllers.validation_controller.ValidationService') as mock_validation_service:
            mock_instance = Mock()
            mock_validation_service.return_value = mock_instance
            mock_instance.validate_configuration.return_value = {"valid": True}
            result = self.controller.validate_configuration(config)
            assert result is not None

    def test_validate_file(self):
        file_path = "test_file.xlsx"
        with patch('battery_analysis.main.controllers.validation_controller.ValidationService') as mock_validation_service:
            mock_instance = Mock()
            mock_validation_service.return_value = mock_instance
            mock_instance.validate_file.return_value = {"valid": True}
            result = self.controller.validate_file(file_path)
            assert result is not None