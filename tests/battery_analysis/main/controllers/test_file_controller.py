from unittest.mock import Mock, patch

from battery_analysis.main.controllers.file_controller import FileController


class TestFileController:
    def setup_method(self):
        mock_config_service = Mock()
        mock_config_service.load_config.return_value = True
        mock_config_service.get_all_sections.return_value = ["Section1"]
        # 重构后 load_config 使用 get_config_sections（旧 get_all_sections 已移除）
        mock_config_service.get_config_sections.return_value = {"Section1": {}}
        mock_config_service.get_section_options.return_value = ["option1"]
        mock_config_service.get_config_value.return_value = "value1"

        mock_file_service = Mock()

        mock_container = Mock()
        mock_container.get.side_effect = lambda name: {
            "file": mock_file_service,
            "config": mock_config_service,
        }.get(name)

        patcher = patch(
            "battery_analysis.main.services.service_container.get_service_container",
            return_value=mock_container,
        )
        patcher.start()
        self.controller = FileController()
        patcher.stop()

    def test_get_project_path(self):
        result = self.controller.get_project_path()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_load_config(self):
        result = self.controller.load_config()
        assert isinstance(result, dict)

    def test_validate_directory_valid(self):
        import os

        result = self.controller.validate_directory(os.getcwd())
        assert result[0] is True

    def test_validate_directory_invalid(self):
        result = self.controller.validate_directory("")
        assert result[0] is False

    def test_ensure_directory_exists(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            import os

            test_path = os.path.join(tmpdir, "new_dir")
            result = self.controller.ensure_directory_exists(test_path)
            assert result[0] is True
            assert os.path.exists(test_path)
