# -*- coding: utf-8 -*-
"""
应用服务模块

负责管理应用生命周期、依赖注入和服务协调
实现控制反转和依赖注入模式
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path

from battery_analysis.main.factories.visualizer_factory import VisualizerFactory
from battery_analysis.main.interfaces.ivisualizer import IVisualizer
from battery_analysis.main.services.service_container import get_service_container
from battery_analysis.utils.config_utils import find_config_file
from battery_analysis.utils.environment_utils import get_environment_detector


class ApplicationService:
    """
    应用服务类
    负责管理应用生命周期和服务依赖
    """
    
    def __init__(self):
        """
        初始化应用服务
        """
        self.logger = logging.getLogger(__name__)
        
        # 获取服务容器
        self.service_container = get_service_container()
        
        # 从服务容器获取服务实例
        self.event_bus = self.service_container.get("event_bus")
        self.environment_service = self.service_container.get("environment")
        self.config_service = self.service_container.get("config")
        self.i18n_service = self.service_container.get("i18n")
        self.progress_service = self.service_container.get("progress")
        self.file_service = self.service_container.get("file")
        self.validation_service = self.service_container.get("validation")
        
        # 初始化可视化器工厂
        self.visualizer_factory = VisualizerFactory()
        self.current_visualizer: Optional[IVisualizer] = None
        
        # 应用状态
        self.is_initialized = False
        self.project_path = ""
        self.input_path = ""
        self.output_path = ""
        
        # 控制器将在initialize方法中延迟初始化
        self.main_controller = None
        self.file_controller = None
        self.validation_controller = None
        self.visualizer_controller = None
        
        # 连接事件监听器
        self._setup_event_listeners()
        
        self.logger.info("ApplicationService initialized")

    def _setup_event_listeners(self):
        """
        设置事件监听器
        """
        # 监听进度更新事件
        self.event_bus.subscribe("progress_updated", self._on_progress_updated)
        
        # 监听状态变化事件
        self.event_bus.subscribe("status_changed", self._on_status_changed)
        
        # 监听分析完成事件
        self.event_bus.subscribe("analysis_completed", self._on_analysis_completed)

    def initialize(self, project_path: Optional[str] = None) -> bool:
        """
        初始化应用服务

        Args:
            project_path: 项目路径

        Returns:
            bool: 初始化是否成功
        """
        try:
            self.logger.info("Starting application initialization...")
            
            # 设置项目路径
            if project_path:
                self.project_path = project_path
            
            # 初始化环境服务
            self.environment_service.initialize()
            
            # 初始化配置服务
            config_path = find_config_file()
            self.config_service.load_config(config_path)
            
            # 初始化国际化服务
            self.i18n_service.initialize()
            
            # 初始化进度服务
            self.progress_service.initialize()
            
            # 从服务容器获取控制器实例
            self.main_controller = self.service_container.get("main_controller")
            self.file_controller = self.service_container.get("file_controller")
            self.validation_controller = self.service_container.get("validation_controller")
            self.visualizer_controller = self.service_container.get("visualizer_controller")
            
            # 设置控制器上下文
            self._setup_controller_contexts()
            
            # 连接控制器事件到事件总线
            self._connect_controller_events()
            
            self.is_initialized = True
            self.logger.info("ApplicationService initialized successfully")
            return True
            
        except (ImportError, TypeError, ValueError, OSError, AttributeError) as e:
            self.logger.error("Failed to initialize ApplicationService: %s", e)
            return False

    def _setup_controller_contexts(self):
        """
        设置控制器上下文
        """
        # 设置主控制器项目上下文
        self.main_controller.set_project_context(
            project_path=self.project_path,
            input_path=self.input_path,
            output_path=self.output_path
        )

    def _connect_controller_events(self):
        """
        连接控制器事件到事件总线
        """
        from battery_analysis.main.services.event_bus import EventType
        
        # 连接主控制器信号到事件总线
        self.main_controller.progress_updated.connect(
            lambda progress, status: self.event_bus.legacy_emit_progress_updated(progress, status)
        )
        self.main_controller.status_changed.connect(
            lambda status, code, message: self.event_bus.legacy_emit_status_changed(status, code, message)
        )
        self.main_controller.analysis_completed.connect(
            lambda: self.event_bus.legacy_emit_analysis_completed()
        )
        # 订阅事件
        self.event_bus.subscribe(EventType.PROGRESS_UPDATED, self._on_progress_updated)
        self.event_bus.subscribe(EventType.STATUS_CHANGED, self._on_status_changed)
        self.event_bus.subscribe(EventType.ANALYSIS_COMPLETED, self._on_analysis_completed)

    def _on_progress_updated(self, event):
        """
        处理进度更新事件

        Args:
            event: 事件对象，包含进度和状态信息
        """
        progress = event.data["progress"]
        status = event.data["status"]
        self.progress_service.update_progress(progress, status)
        self.logger.debug("Progress updated: %s%% - %s", progress, status)

    def _on_status_changed(self, event):
        """
        处理状态变化事件

        Args:
            event: 事件对象，包含状态、状态码和消息
        """
        status = event.data["status"]
        code = event.data["code"]
        message = event.data["message"]
        self.logger.info("Status changed: %s, Code: %s, Message: %s", status, code, message)

    def _on_analysis_completed(self, event):
        """
        处理分析完成事件
        
        Args:
            event: 事件对象
        """
        self.logger.info("Analysis completed")
        self.event_bus.legacy_emit_visualizer_requested()

    def create_visualizer(self, name: str = "battery_chart", **kwargs) -> Optional[IVisualizer]:
        """
        创建可视化器

        Args:
            name: 可视化器名称
            **kwargs: 可视化器参数

        Returns:
            IVisualizer: 可视化器实例
        """
        if not self.is_initialized:
            self.logger.error("ApplicationService not initialized")
            return None
        
        self.current_visualizer = self.visualizer_factory.create_visualizer(name, **kwargs)
        if self.current_visualizer:
            self.logger.info("Created visualizer: %s", name)
        else:
            self.logger.error("Failed to create visualizer: %s", name)
        
        return self.current_visualizer

    def get_service(self, service_type: str) -> Optional[Any]:
        """
        获取服务实例

        Args:
            service_type: 服务类型

        Returns:
            Any: 服务实例
        """
        # 先尝试从服务容器获取
        service = self.service_container.get(service_type)
        if service is not None:
            return service
        
        # 对于本地管理的服务，使用备份映射
        service_map = {
            "visualizer_factory": self.visualizer_factory,
            "current_visualizer": self.current_visualizer
        }
        
        return service_map.get(service_type)

    def shutdown(self):
        """
        关闭应用服务
        """
        self.logger.info("Shutting down ApplicationService...")
        
        # 关闭进度服务
        if hasattr(self, 'progress_service'):
            self.progress_service.shutdown()
        
        # 清理当前可视化器
        if self.current_visualizer:
            self.current_visualizer.clear_data()
            self.current_visualizer = None
        
        self.is_initialized = False
        self.logger.info("ApplicationService shutdown complete")
