"""
help_manager测试
"""

from unittest.mock import MagicMock, Mock, patch

from battery_analysis.main.business_logic.help_manager import HelpManager


class TestHelpManager:
    """帮助管理器测试类"""

    def setup_method(self):
        """设置测试环境"""
        # 创建模拟主窗口对象
        self.mock_main_window = Mock()
        self.mock_main_window.current_directory = "."

        # 创建帮助管理器实例
        self.help_manager = HelpManager(self.mock_main_window)

    def test_show_user_manual(self):
        """测试显示用户手册（在线文档）"""
        # 模拟QDesktopServices.openUrl
        with patch("PyQt6.QtGui.QDesktopServices.openUrl") as mock_open_url:
            # 调用方法
            self.help_manager.show_user_manual()

            # 验证结果
            mock_open_url.assert_called_once()

    def test_show_user_manual_with_exception(self):
        """测试显示用户手册（发生异常）"""
        # 模拟QDesktopServices.openUrl抛出异常
        with patch("PyQt6.QtGui.QDesktopServices.openUrl", side_effect=ImportError("Test error")):
            with patch(
                "battery_analysis.main.business_logic.help_manager.QW.QMessageBox.warning"
            ) as mock_warning:
                # 调用方法
                self.help_manager.show_user_manual()

                # 验证结果
                mock_warning.assert_called_once()

    def test_show_online_help(self):
        """测试显示在线帮助"""
        # 模拟QDesktopServices.openUrl
        with patch("PyQt6.QtGui.QDesktopServices.openUrl") as mock_open_url:
            # 调用方法
            self.help_manager.show_online_help()

            # 验证结果
            mock_open_url.assert_called_once()

    def test_show_online_help_with_exception(self):
        """测试显示在线帮助（发生异常）"""
        # 模拟QDesktopServices.openUrl抛出异常
        with patch("PyQt6.QtGui.QDesktopServices.openUrl", side_effect=ImportError("Test error")):
            with patch(
                "battery_analysis.main.business_logic.help_manager.QW.QMessageBox.warning"
            ) as mock_warning:
                # 调用方法
                self.help_manager.show_online_help()

                # 验证结果
                mock_warning.assert_called_once()
