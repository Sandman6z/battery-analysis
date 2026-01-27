# -*- coding: utf-8 -*-
"""
help_manager测试
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
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

    def test_show_user_manual_with_valid_manual(self):
        """测试显示用户手册（找到有效手册）"""
        # 模拟FileUtils.get_manual_paths返回有效的手册路径
        mock_manual_path = Mock()
        mock_manual_path.exists.return_value = True
        mock_manual_path.is_file.return_value = True
        mock_manual_path.__str__.return_value = "test_manual.pdf"
        
        # 模拟os.startfile
        with patch('battery_analysis.main.business_logic.help_manager.FileUtils.get_manual_paths', return_value=[mock_manual_path]):
            with patch('os.startfile') as mock_startfile:
                # 调用方法
                self.help_manager.show_user_manual()
                
                # 验证结果
                mock_startfile.assert_called_once_with("test_manual.pdf")

    def test_show_user_manual_with_no_manual(self):
        """测试显示用户手册（找不到手册）"""
        # 模拟FileUtils.get_manual_paths返回无效的手册路径
        mock_manual_path = Mock()
        mock_manual_path.exists.return_value = False
        
        # 模拟QW.QMessageBox.information
        with patch('battery_analysis.main.business_logic.help_manager.FileUtils.get_manual_paths', return_value=[mock_manual_path]):
            with patch('battery_analysis.main.business_logic.help_manager.QW.QMessageBox.information') as mock_information:
                # 调用方法
                self.help_manager.show_user_manual()
                
                # 验证结果
                mock_information.assert_called_once()

    def test_show_user_manual_with_exception(self):
        """测试显示用户手册（发生异常）"""
        # 模拟FileUtils.get_manual_paths抛出异常
        with patch('battery_analysis.main.business_logic.help_manager.FileUtils.get_manual_paths', side_effect=OSError("Test error")):
            with patch('battery_analysis.main.business_logic.help_manager.QW.QMessageBox.warning') as mock_warning:
                # 调用方法
                self.help_manager.show_user_manual()
                
                # 验证结果
                mock_warning.assert_called_once()

    def test_show_online_help(self):
        """测试显示在线帮助"""
        # 模拟QDesktopServices.openUrl
        with patch('battery_analysis.main.business_logic.help_manager.QDesktopServices.openUrl') as mock_open_url:
            # 调用方法
            self.help_manager.show_online_help()
            
            # 验证结果
            mock_open_url.assert_called_once()

    def test_show_online_help_with_exception(self):
        """测试显示在线帮助（发生异常）"""
        # 模拟QDesktopServices.openUrl抛出异常
        with patch('battery_analysis.main.business_logic.help_manager.QDesktopServices.openUrl', side_effect=ImportError("Test error")):
            with patch('battery_analysis.main.business_logic.help_manager.QW.QMessageBox.warning') as mock_warning:
                # 调用方法
                self.help_manager.show_online_help()
                
                # 验证结果
                mock_warning.assert_called_once()
