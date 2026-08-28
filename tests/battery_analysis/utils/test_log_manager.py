from battery_analysis.utils.log_manager import LogManager


class TestLogManager:
    def setup_method(self):
        self.manager = LogManager()

    def test_init(self):
        assert hasattr(self.manager, "logger")

    def test_log_environment_info(self):
        # Should not throw
        self.manager.log_environment_info()

    def test_get_logger(self):
        logger = self.manager.get_logger("test")
        assert logger is not None

    def test_get_log_directory(self):
        log_dir = self.manager.get_log_directory()
        from pathlib import Path

        assert isinstance(log_dir, Path)
