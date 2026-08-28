from unittest.mock import patch

from battery_analysis.utils.file_validator import FileValidator


class TestFileValidator:
    def setup_method(self):
        self.validator = FileValidator()

    def test_validate_file_exists(self):
        file_path = "test_file.txt"
        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = True
            result = self.validator.validate_file_exists(file_path)
            assert result == (True, "")

    def test_validate_file_extension(self):
        file_path = "test_file.xlsx"
        valid_extensions = [".xlsx", ".xls"]
        result = self.validator.validate_file_extension(file_path, valid_extensions)
        assert result == (True, "")

    def test_validate_filename(self):
        file_path = "test_file.txt"
        result = self.validator.validate_filename(file_path)
        assert result[0] is True
