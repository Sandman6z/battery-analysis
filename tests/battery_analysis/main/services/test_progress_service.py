from unittest.mock import Mock, patch, MagicMock


class TestProgressService:
    def setup_method(self):
        # ProgressService extends QObject and requires QApplication.
        # We patch the pyqtSignal to avoid the Qt dependency.
        patcher = patch(
            'battery_analysis.main.services.progress_service.pyqtSignal',
            return_value=MagicMock()
        )
        patcher.start()
        from battery_analysis.main.services.progress_service import ProgressService
        self.service = ProgressService()
        patcher.stop()
        # Manually set initial state
        self.service._progress = 0
        self.service._status = ""
        self.service._is_completed = False
        self.service._is_active = False
        self.service._progress_callbacks = {}

    def test_update_progress(self):
        result = self.service.update_progress(50, "Test status")
        assert result is True

    def test_get_progress(self):
        result = self.service.get_progress()
        assert isinstance(result, int)

    def test_reset_progress(self):
        result = self.service.reset_progress()
        assert result is True