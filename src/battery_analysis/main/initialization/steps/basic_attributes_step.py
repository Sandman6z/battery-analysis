# -*- coding: utf-8 -*-
"""
基本属性初始化步骤
"""

import logging
from battery_analysis.main.initialization.initialization_step import InitializationStep
from battery_analysis.main.utils import Checker


class BasicAttributesInitializationStep(InitializationStep):
    """基本属性初始化步骤"""
    
    def __init__(self):
        """初始化基本属性初始化步骤"""
        super().__init__("basic_attributes", priority=10)
    
    def execute(self, main_window) -> bool:
        """
        执行基本属性初始化
        
        Args:
            main_window: 主窗口实例
            
        Returns:
            是否执行成功
        """
        try:
            from battery_analysis import __version__
            main_window.version = __version__
            
            # 初始化日志记录器
            main_window.logger = logging.getLogger(__name__)
            
            # 延迟加载的服务缓存
            main_window._services = {}
            main_window._controllers = {}
            
            # 初始化语言管理器
            main_window.language_manager = None
            
            # 初始化配置相关属性
            main_window.b_has_config = True
            main_window.checker_battery_type = Checker()
            main_window.checker_table = Checker()
            main_window.checker_input_xlsx = Checker()
            main_window.checker_update_config = Checker()
            main_window.construction_method = ""
            main_window.test_information = ""
            main_window.specification_type = ""
            main_window.cc_current = ""
            main_window.sha256_checksum = ""
            main_window.sha256_checksum_run = ""
            
            self.logger.info("基本属性初始化完成")
            return True
        except Exception as e:
            self.logger.exception("基本属性初始化失败")
            return False
    
    def can_execute(self, main_window) -> bool:
        """
        检查是否可以执行此步骤
        
        Args:
            main_window: 主窗口实例
            
        Returns:
            是否可以执行
        """
        return True
