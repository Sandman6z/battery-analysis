from battery_analysis.utils.environment_utils import EnvironmentDetector


class TestEnvironmentDetector:
    def setup_method(self):
        self.detector = EnvironmentDetector()

    def test_get_environment_info(self):
        result = self.detector.get_environment_info()
        assert isinstance(result, dict)
        assert "platform" in result
        assert "environment_type" in result
        assert "gui_available" in result
        assert "display_available" in result
        assert "python_executable" in result
        assert "python_version" in result
        assert "is_frozen" in result
        assert "meipass" in result
        assert "working_directory" in result
        assert "current_file_dir" in result
        assert "project_root" in result

    def test_is_gui_mode(self):
        result = self.detector.is_gui_mode()
        assert isinstance(result, bool)

    def test_is_cli_mode(self):
        result = self.detector.is_cli_mode()
        assert isinstance(result, bool)
        assert result != self.detector.is_gui_mode()

    def test_get_project_root(self):
        result = self.detector.get_project_root()
        assert result.exists()

    def test_get_resource_path(self):
        result = self.detector.get_resource_path("test")
        assert isinstance(result, type(self.detector.get_project_root()))

    def test_get_locale_path(self):
        result = self.detector.get_locale_path()
        assert result is None or result.exists()
