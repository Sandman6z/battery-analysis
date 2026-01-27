# -*- coding: utf-8 -*-
"""
application_service测试
"""

import pytest
from unittest.mock import Mock, patch
from battery_analysis.main.services.application_service import ApplicationService


class TestApplicationService:
    """应用服务测试类"""

    def setup_method(self):
        """设置测试环境"""
        # 模拟服务容器和相关服务
        with patch('battery_analysis.main.services.application_service.get_service_container') as mock_get_service_container:
            # 创建模拟服务容器
            mock_service_container = Mock()
            
            # 创建模拟服务
            mock_event_bus = Mock()
            mock_event_bus.subscribe = Mock()
            mock_event_bus.emit = Mock()
            mock_event_bus.legacy_emit_progress_updated = Mock()
            mock_event_bus.legacy_emit_status_changed = Mock()
            mock_event_bus.legacy_emit_analysis_completed = Mock()
            mock_event_bus.legacy_emit_visualizer_requested = Mock()
            
            mock_environment_service = Mock()
            mock_environment_service.initialize = Mock()
            
            mock_config_service = Mock()
            mock_config_service.load_config = Mock()
            
            mock_i18n_service = Mock()
            mock_i18n_service.initialize = Mock()
            
            mock_progress_service = Mock()
            mock_progress_service.initialize = Mock()
            mock_progress_service.update_progress = Mock()
            mock_progress_service.shutdown = Mock()
            
            mock_file_service = Mock()
            
            mock_validation_service = Mock()
            
            # 模拟控制器
            mock_main_controller = Mock()
            mock_main_controller.set_project_context = Mock()
            mock_main_controller.progress_updated = Mock()
            mock_main_controller.status_changed = Mock()
            mock_main_controller.analysis_completed = Mock()
            
            mock_file_controller = Mock()
            mock_validation_controller = Mock()
            mock_visualizer_controller = Mock()
            
            # 设置服务容器的get方法
            mock_service_container.get.side_effect = lambda service_type: {
                "event_bus": mock_event_bus,
                "environment": mock_environment_service,
                "config": mock_config_service,
                "i18n": mock_i18n_service,
                "progress": mock_progress_service,
                "file": mock_file_service,
                "validation": mock_validation_service,
                "main_controller": mock_main_controller,
                "file_controller": mock_file_controller,
                "validation_controller": mock_validation_controller,
                "visualizer_controller": mock_visualizer_controller
            }.get(service_type)
            
            mock_get_service_container.return_value = mock_service_container
            
            # 模拟VisualizerFactory
            with patch('battery_analysis.main.services.application_service.VisualizerFactory') as mock_visualizer_factory_class:
                mock_visualizer_factory = Mock()
                mock_visualizer_factory.create_visualizer = Mock(return_value=Mock())
                mock_visualizer_factory_class.return_value = mock_visualizer_factory
                
                # 创建ApplicationService实例
                self.application_service = ApplicationService()
                
                # 保存模拟对象以供后续测试使用
                self.mock_event_bus = mock_event_bus
                self.mock_environment_service = mock_environment_service
                self.mock_config_service = mock_config_service
                self.mock_i18n_service = mock_i18n_service
                self.mock_progress_service = mock_progress_service
                self.mock_visualizer_factory = mock_visualizer_factory
                self.mock_main_controller = mock_main_controller

    def test_initialization(self):
        """测试初始化"""
        # 验证初始化
        assert self.application_service is not None
        assert not self.application_service.is_initialized
        assert self.application_service.service_container is not None

    def test_setup_event_listeners(self):
        """测试设置事件监听器"""
        # 验证事件监听器设置
        assert self.mock_event_bus.subscribe.called
        # 验证至少订阅了三个事件
        assert self.mock_event_bus.subscribe.call_count >= 3

    def test_initialize(self):
        """测试初始化应用服务"""
        # 调用初始化方法
        result = self.application_service.initialize("test/project/path")
        
        # 验证结果
        assert result is True
        assert self.application_service.is_initialized
        assert self.application_service.project_path == "test/project/path"
        
        # 验证相关方法被调用
        self.mock_environment_service.initialize.assert_called_once()
        self.mock_config_service.load_config.assert_called_once()
        self.mock_i18n_service.initialize.assert_called_once()
        self.mock_progress_service.initialize.assert_called_once()
        self.mock_main_controller.set_project_context.assert_called_once()

    def test_initialize_with_exception(self):
        """测试初始化应用服务（发生异常）"""
        # 模拟初始化过程中发生异常
        self.mock_environment_service.initialize.side_effect = Exception("Test error")
        
        # 调用初始化方法
        result = self.application_service.initialize()
        
        # 验证结果
        assert result is False
        assert not self.application_service.is_initialized

    def test_create_visualizer(self):
        """测试创建可视化器"""
        # 模拟应用服务已初始化
        self.application_service.is_initialized = True
        
        # 调用创建可视化器方法
        visualizer = self.application_service.create_visualizer("test_visualizer")
        
        # 验证结果
        assert visualizer is not None
        self.mock_visualizer_factory.create_visualizer.assert_called_once_with("test_visualizer")

    def test_create_visualizer_not_initialized(self):
        """测试创建可视化器（应用服务未初始化）"""
        # 确保应用服务未初始化
        self.application_service.is_initialized = False
        
        # 调用创建可视化器方法
        visualizer = self.application_service.create_visualizer("test_visualizer")
        
        # 验证结果
        assert visualizer is None

    def test_get_service(self):
        """测试获取服务实例"""
        # 测试获取服务容器中的服务
        service = self.application_service.get_service("event_bus")
        assert service is not None
        
        # 测试获取本地管理的服务
        service = self.application_service.get_service("visualizer_factory")
        assert service is not None

    def test_shutdown(self):
        """测试关闭应用服务"""
        # 模拟当前可视化器
        mock_current_visualizer = Mock()
        mock_current_visualizer.clear_data = Mock()
        self.application_service.current_visualizer = mock_current_visualizer
        
        # 调用关闭方法
        self.application_service.shutdown()
        
        # 验证结果
        self.mock_progress_service.shutdown.assert_called_once()
        mock_current_visualizer.clear_data.assert_called_once()
        assert not self.application_service.is_initialized

    def test_on_progress_updated(self):
        """测试处理进度更新事件"""
        # 创建模拟事件
        mock_event = Mock()
        mock_event.data = {"progress": 50, "status": "Processing"}
        
        # 调用事件处理方法
        self.application_service._on_progress_updated(mock_event)
        
        # 验证结果
        self.mock_progress_service.update_progress.assert_called_once_with(50, "Processing")

    def test_on_status_changed(self):
        """测试处理状态变化事件"""
        # 创建模拟事件
        mock_event = Mock()
        mock_event.data = {"status": "Success", "code": "200", "message": "Operation completed"}
        
        # 调用事件处理方法
        self.application_service._on_status_changed(mock_event)
        
        # 验证方法被调用（通过日志记录，这里我们至少验证方法执行了）
        assert True

    def test_on_analysis_completed(self):
        """测试处理分析完成事件"""
        # 创建模拟事件
        mock_event = Mock()
        
        # 调用事件处理方法
        self.application_service._on_analysis_completed(mock_event)
        
        # 验证结果
        self.mock_event_bus.legacy_emit_visualizer_requested.assert_called_once()
