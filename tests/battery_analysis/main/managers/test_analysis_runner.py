import pytest
from unittest.mock import Mock, patch
from battery_analysis.main.managers.analysis_runner import AnalysisRunner


class TestAnalysisRunner:
    def setup_method(self):
        self.runner = AnalysisRunner()

    def test_run_analysis(self):
        test_data = {
            "voltage": [4.2, 4.1, 4.0],
            "current": [0.5, 0.5, 0.5]
        }
        with patch('battery_analysis.main.managers.analysis_runner.DataProcessor') as mock_data_processor:
            mock_instance = Mock()
            mock_data_processor.return_value = mock_instance
            mock_instance.process.return_value = {"results": []}
            result = self.runner.run_analysis(test_data)
            assert result is not None

    def test_cancel_analysis(self):
        with patch('battery_analysis.main.managers.analysis_runner.DataProcessor') as mock_data_processor:
            mock_instance = Mock()
            mock_data_processor.return_value = mock_instance
            mock_instance.cancel.return_value = True
            result = self.runner.cancel_analysis()
            assert result is True

    def test_get_analysis_status(self):
        result = self.runner.get_analysis_status()
        assert isinstance(result, dict)