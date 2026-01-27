# -*- coding: utf-8 -*-
"""
environment_manager测试
"""

import pytest
from unittest.mock import Mock, patch
from battery_analysis.main.business_logic.environment_manager import EnvironmentManager


class TestEnvironmentManager:
    """环境管理器测试类"""

    def setup_method(self):
        """设置测试环境"""
        # 创建模拟主窗口对象
        self.mock_main_window = Mock()
        self.mock_main_window.env_info = {}
        
        # 创建环境管理器实例
        self.environment_manager = EnvironmentManager(self.mock_main_window)

    def test_initialize_environment_info_with_valid_service(self):
        """测试初始化环境信息（有效的服务）"""
        # 创建模拟环境服务
        mock_environment_service = Mock()
        mock_environment_service.env_info = {"test_key": "test_value"}
        
        # 模拟主窗口的_get_service方法
        self.mock_main_window._get_service.return_value = mock_environment_service
        
        # 调用初始化方法
        self.environment_manager._initialize_environment_info()
        
        # 验证结果
        assert "test_key" in self.mock_main_window.env_info
        assert self.mock_main_window.env_info["test_key"] == "test_value"

    def test_initialize_environment_info_with_initialize_method(self):
        """测试初始化环境信息（带有initialize方法的服务）"""
        # 创建模拟环境服务
        mock_environment_service = Mock()
        mock_environment_service.initialize.return_value = True
        mock_environment_service.env_info = {"test_key": "test_value"}
        
        # 模拟主窗口的_get_service方法
        self.mock_main_window._get_service.return_value = mock_environment_service
        
        # 调用初始化方法
        self.environment_manager._initialize_environment_info()
        
        # 验证结果
        assert "test_key" in self.mock_main_window.env_info
        assert self.mock_main_window.env_info["test_key"] == "test_value"

    def test_initialize_environment_info_with_exception(self):
        """测试初始化环境信息（发生异常）"""
        # 模拟主窗口的_get_service方法抛出异常
        self.mock_main_window._get_service.side_effect = AttributeError("Test error")
        
        # 调用初始化方法
        self.environment_manager._initialize_environment_info()
        
        # 验证结果（应该不会崩溃）
        assert True

    def test_ensure_env_info_keys_without_environment_type(self):
        """测试确保环境信息键（缺少environment_type）"""
        # 确保env_info为空
        self.mock_main_window.env_info = {}
        
        # 调用方法
        self.environment_manager._ensure_env_info_keys()
        
        # 验证结果
        assert "environment_type" in self.mock_main_window.env_info
        assert "gui_available" in self.mock_main_window.env_info
        assert self.mock_main_window.env_info["gui_available"] is True

    def test_ensure_env_info_keys_without_gui_available(self):
        """测试确保环境信息键（缺少gui_available）"""
        # 设置env_info，包含environment_type但缺少gui_available
        self.mock_main_window.env_info = {"environment_type": "DEVELOPMENT"}
        
        # 调用方法
        self.environment_manager._ensure_env_info_keys()
        
        # 验证结果
        assert "gui_available" in self.mock_main_window.env_info
        assert self.mock_main_window.env_info["gui_available"] is True

    def test_ensure_env_info_keys_with_all_keys(self):
        """测试确保环境信息键（所有键都存在）"""
        # 设置env_info，包含所有必要的键
        self.mock_main_window.env_info = {
            "environment_type": "DEVELOPMENT",
            "gui_available": True
        }
        
        # 调用方法
        self.environment_manager._ensure_env_info_keys()
        
        # 验证结果（应该保持不变）
        assert "environment_type" in self.mock_main_window.env_info
        assert "gui_available" in self.mock_main_window.env_info
        assert self.mock_main_window.env_info["environment_type"] == "DEVELOPMENT"
        assert self.mock_main_window.env_info["gui_available"] is True
