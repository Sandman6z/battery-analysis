from battery_analysis.utils.error_report_generator import ErrorReportGenerator


class TestErrorReportGenerator:
    def setup_method(self):
        self.generator = ErrorReportGenerator()

    def test_generate_error_report(self):
        result = self.generator.generate_error_report()
        # In CI without logs, may return None; locally might return a path
        assert result is None or isinstance(result, str)

    def test_get_report_info(self):
        result = self.generator.get_report_info()
        assert isinstance(result, dict)
        assert "log_directory" in result
