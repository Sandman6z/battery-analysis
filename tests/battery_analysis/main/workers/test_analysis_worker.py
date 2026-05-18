from battery_analysis.main.workers.analysis_worker import AnalysisWorker


class TestAnalysisWorker:
    def setup_method(self):
        self.worker = AnalysisWorker()

    def test_set_info(self):
        self.worker.set_info("path", "input", "output", ["info"])
        assert self.worker.str_path == "path"

    def test_request_cancel(self):
        self.worker.request_cancel()
        assert self.worker.b_cancel_requested is True
