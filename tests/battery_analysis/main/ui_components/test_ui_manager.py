from unittest.mock import Mock, patch

import pytest

from battery_analysis.main.ui_components.ui_manager import UIManager


class TestUIManager:
    def setup_method(self):
        mock_main = Mock()
        mock_main.tableWidget_TestInformation = Mock()
        mock_main.scrollArea = Mock()
        self.manager = UIManager(mock_main)

    def test_init_window(self):
        with patch.object(self.manager, "_load_application_icon", return_value=Mock()):
            self.manager.init_window()

    @pytest.mark.skip(reason="需要 Qt 运行环境")
    def test_init_widget(self):
        self.manager.init_widget()
