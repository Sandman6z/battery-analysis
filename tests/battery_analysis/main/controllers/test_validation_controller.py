from unittest.mock import Mock, patch, MagicMock
from battery_analysis.main.controllers.validation_controller import ValidationController


class TestValidationController:
    def setup_method(self):
        mock_validation_service = Mock()
        mock_validation_service.validate_test_info.return_value = (True, "")
        mock_validation_service.validate_directory_path.return_value = (True, "")

        mock_container = Mock()
        mock_container.get.return_value = mock_validation_service

        patcher = patch(
            'battery_analysis.main.services.service_container.get_service_container',
            return_value=mock_container
        )
        patcher.start()
        self.controller = ValidationController()
        patcher.stop()

    def test_sanitize_file_name_colon(self):
        result = self.controller.sanitize_file_name('test:name.xlsx')
        assert result == 'test_name.xlsx'

    def test_sanitize_file_name_angle_bracket(self):
        result = self.controller.sanitize_file_name('test<name>.xlsx')
        assert result == 'test_name_.xlsx'

    def test_sanitize_file_name_no_change(self):
        result = self.controller.sanitize_file_name('normal-file.name.xlsx')
        assert result == 'normal-file.name.xlsx'