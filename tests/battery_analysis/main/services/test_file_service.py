import pytest
from unittest.mock import Mock, patch
from battery_analysis.main.services.file_service import FileService


class TestFileService:
    def setup_method(self):
        self.service = FileService()

    def test_read_file(self):
        file_path = "test_file.xlsx"
        with patch('battery_analysis.main.services.file_service.pandas') as mock_pandas:
            mock_pandas.read_excel.return_value = Mock()
            result = self.service.read_file(file_path)
            assert result is not None

    def test_write_file(self):
        file_path = "test_file.xlsx"
        data = {"data": []}
        with patch('battery_analysis.main.services.file_service.pandas') as mock_pandas:
            mock_df = Mock()
            mock_df.to_excel.return_value = None
            mock_pandas.DataFrame.return_value = mock_df
            result = self.service.write_file(file_path, data)
            assert result is True

    def test_export_data(self):
        file_path = "export_file.xlsx"
        data = {"data": []}
        with patch('battery_analysis.main.services.file_service.pandas') as mock_pandas:
            mock_df = Mock()
            mock_df.to_excel.return_value = None
            mock_pandas.DataFrame.return_value = mock_df
            result = self.service.export_data(file_path, data)
            assert result is True