import pytest
from unittest.mock import Mock, patch
from battery_analysis.utils.file_validator import FileValidator


class TestFileValidator:
    def setup_method(self):
        self.validator = FileValidator()

    def test_validate_file_exists(self):
        file_path = "test_file.txt"
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True
            result = self.validator.validate_file_exists(file_path)
            assert result is True

    def test_validate_file_extension(self):
        file_path = "test_file.xlsx"
        valid_extensions = [".xlsx", ".xls"]
        result = self.validator.validate_file_extension(file_path, valid_extensions)
        assert result is True

    def test_validate_file_size(self):
        file_path = "test_file.txt"
        max_size = 1024  # 1KB
        with patch('os.path.getsize') as mock_getsize:
            mock_getsize.return_value = 512
            result = self.validator.validate_file_size(file_path, max_size)
            assert result is True