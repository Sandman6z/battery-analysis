# -*- coding: utf-8 -*-
"""
语言初始化步骤
"""

from battery_analysis.main.initialization.initialization_step import InitializationStep
from battery_analysis.main.ui.language_handler import LanguageHandler
from battery_analysis.i18n.language_manager import get_language_manager


class LanguageInitializationStep(InitializationStep):
    """语言初始化步骤"""
    
    def __init__(self):
        """初始化语言初始化步骤"""
        super().__init__("language", priority=90)
    
    def execute(self, main_window) -> bool:
        """
        执行语言初始化
        
        Args:
            main_window: 主窗口实例
            
        Returns:
            是否执行成功
        """
        try:
            # 初始化语言处理器
            main_window.language_handler = LanguageHandler(main_window)
            
            # 连接语言管理器信号
            self._connect_language_signals(main_window)
            
            # 现在初始化环境信息，因为environment_manager已经创建
            if hasattr(main_window, '_initialize_environment_info'):
                main_window._initialize_environment_info()
            # 确保环境信息包含必要的键
            if hasattr(main_window, '_ensure_env_info_keys'):
                main_window._ensure_env_info_keys()
            
            self.logger.info("语言初始化完成")
            return True
        except Exception as e:
            self.logger.exception("语言初始化失败")
            return False
    
    def _connect_language_signals(self, main_window) -> None:
        """
        连接语言管理器的信号
        
        Args:
            main_window: 主窗口实例
        """
        try:
            # 初始化语言管理器
            main_window.language_manager = get_language_manager()
            if main_window.language_manager and hasattr(main_window, '_on_language_changed'):
                main_window.language_manager.language_changed.connect(main_window._on_language_changed)
        except (ImportError, AttributeError, TypeError, RuntimeError) as e:
            self.logger.warning("Failed to initialize language manager: %s", e)
    
    def can_execute(self, main_window) -> bool:
        """
        检查是否可以执行此步骤
        
        Args:
            main_window: 主窗口实例
            
        Returns:
            是否可以执行
        """
        return hasattr(main_window, 'presenter')
