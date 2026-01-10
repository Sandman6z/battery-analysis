# -*- coding: utf-8 -*-
"""
环境适配器模块

该模块负责检测运行环境（IDE、容器、生产），并进行相应的适配处理，
将环境检测逻辑与主窗口UI逻辑分离，便于跨平台适配。
"""

import logging


class EnvironmentAdapter:
    """
    环境适配器类
    负责检测和适配不同的运行环境
    """
    
    def __init__(self, main_window):
        """
        初始化环境适配器
        
        Args:
            main_window: 主窗口实例，用于访问服务和配置
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        self.env_info = main_window.env_info
        self.task_duration_threshold = 30  # 默认阈值
    
    def initialize_environment_detector(self):
        """
        初始化环境检测器
        
        Returns:
            环境检测器实例或None
        """
        try:
            env_service = self.main_window._get_service("environment")
            if env_service:
                if hasattr(env_service, 'initialize'):
                    env_service.initialize()
                if hasattr(env_service, 'get_environment_detector'):
                    return env_service.get_environment_detector()
        except (AttributeError, TypeError, ImportError, OSError) as e:
            self.logger.warning("Failed to initialize environment service: %s", e)
        return None
    
    def handle_environment_adaptation(self):
        """
        处理环境适配逻辑
        """
        # 通过环境服务获取 EnvironmentType
        try:
            env_service = self.main_window._get_service("environment")
            if env_service and hasattr(env_service, 'EnvironmentType'):
                EnvironmentType = env_service.EnvironmentType
            else:
                # 降级到直接导入
                from battery_analysis.utils.environment_utils import EnvironmentType
        except (AttributeError, TypeError, ImportError) as e:
            self.logger.warning("Failed to get EnvironmentType: %s", e)
            from battery_analysis.utils.environment_utils import EnvironmentType
        
        # 确保环境信息包含必要的键
        if 'environment_type' not in self.env_info:
            self.env_info['environment_type'] = EnvironmentType.IDE
            self.logger.warning("environment_type not found in env_info, using IDE as default")
        
        if 'gui_available' not in self.env_info:
            self.env_info['gui_available'] = True
        
        # 获取环境类型
        env_type = self.env_info['environment_type']
        
        # 根据环境类型进行适配
        if env_type == EnvironmentType.IDE:
            self.logger.debug("IDE环境：调整UI行为以适应开发环境")
            self.adapt_for_ide_environment()
        elif env_type == EnvironmentType.CONTAINER:
            self.logger.debug("容器环境：调整UI行为以适应容器环境")
            self.adapt_for_container_environment()
        elif env_type == EnvironmentType.PRODUCTION:
            self.logger.debug("生产环境：优化UI性能")
            self.adapt_for_production_environment()
        
        # GUI可用性检查
        if not self.env_info['gui_available']:
            self.logger.warning("GUI环境不可用，应用可能无法正常显示")
            self.handle_gui_unavailable()
    
    def adapt_for_ide_environment(self):
        """
        IDE环境适配
        """
        # 在IDE中可能没有显示，添加调试信息
        self.logger.debug("在IDE环境中运行，某些功能可能受限")
        
        # 调整任务阈值，在IDE中通常任务较快
        self.task_duration_threshold = 15
        self.main_window.task_duration_threshold = self.task_duration_threshold
    
    def adapt_for_container_environment(self):
        """
        容器环境适配
        """
        self.logger.debug("在容器环境中运行，调整路径和资源管理")
        
        # 容器环境中的资源路径可能不同
        # 禁用某些容器中可能不支持的功能
        self.task_duration_threshold = 45
        self.main_window.task_duration_threshold = self.task_duration_threshold
    
    def adapt_for_production_environment(self):
        """
        生产环境适配
        """
        self.logger.debug("在生产环境中运行，优化性能和稳定性")
        
        # 生产环境中启用更多优化
        self.task_duration_threshold = 30
        self.main_window.task_duration_threshold = self.task_duration_threshold
    
    def handle_gui_unavailable(self):
        """
        处理GUI不可用的情况
        """
        self.logger.error("GUI环境不可用，尝试使用无头模式")
        # 在GUI不可用时，可以考虑切换到命令行模式
        # 或者显示错误信息并退出
