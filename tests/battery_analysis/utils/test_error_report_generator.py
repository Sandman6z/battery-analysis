import pytest
from unittest.mock import Mock, patch
from battery_analysis.utils.error_report_generator import ErrorReportGenerator


class TestErrorReportGenerator:
    def setup_method(self):
        self.generator = ErrorReportGenerator()

    def test_generate_report(self):
        error = Exception("Test error")
        context = {"module": "test_module"}
        result = self.generator.generate_report(error, context)
        assert isinstance(result, dict)

    def test_save_report(self):
        report_data = {"error": "Test error"}
        file_path = "error_report.json"
        result = self.generator.save_report(report_data, file_path)
        assert result is True

    def test_format_error_message(self):
        error = Exception("Test error")
        result = self.generator.format_error_message(error)
        assert isinstance(result, str)