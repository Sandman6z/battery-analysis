import pytest
from unittest.mock import Mock, patch
from battery_analysis.main.workers.analysis_worker import AnalysisWorker


class TestAnalysisWorker:
    def setup_method(self):
        self.worker = AnalysisWorker()

    def test_start(self):
        test_data = {
            "voltage": [4.2, 4.1, 4.0],
            "current": [0.5, 0.5, 0.5]
        }
        result = self.worker.start(test_data)
        assert result is True

    def test_stop(self):
        result = self.worker.stop()
        assert result is True

    def test_get_progress(self):
        result = self.worker.get_progress()
        assert isinstance(result, int)

    def test_get_result(self):
        result = self.worker.get_result()
        assert isinstance(result, dict)