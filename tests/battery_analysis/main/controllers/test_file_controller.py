import pytest
from unittest.mock import Mock, patch
from battery_analysis.main.controllers.file_controller import FileController


class TestFileController:
    def setup_method(self):
        self.controller = FileController()

    def test_open_file(self):
        file_path = "test_file.xlsx"
        with patch('battery_analysis.main.controllers.file_controller.FileService') as mock_file_service:
            mock_instance = Mock()
            mock_file_service.return_value = mock_instance
            mock_instance.read_file.return_value = {"data": []}
            result = self.controller.open_file(file_path)
            assert result is not None

    def test_save_file(self):
        file_path = "test_file.xlsx"
        data = {"data": []}
        with patch('battery_analysis.main.controllers.file_controller.FileService') as mock_file_service:
            mock_instance = Mock()
            mock_file_service.return_value = mock_instance
            mock_instance.write_file.return_value = True
            result = self.controller.save_file(file_path, data)
            assert result is True

    def test_export_data(self):
        file_path = "export_file.xlsx"
        data = {"data": []}
        with patch('battery_analysis.main.controllers.file_controller.FileService') as mock_file_service:
            mock_instance = Mock()
            mock_file_service.return_value = mock_instance
            mock_instance.export_data.return_value = True
            result = self.controller.export_data(file_path, data)
            assert result is True