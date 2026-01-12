# -*- coding: utf-8 -*-
"""
初始化管理器

负责处理主窗口的初始化逻辑，使用模块化的初始化步骤
"""

# 标准库导入
import logging

# 本地应用/库导入
from battery_analysis.main.initialization.initialization_orchestrator import InitializationOrchestrator
from battery_analysis.main.initialization.steps.basic_attributes_step import BasicAttributesInitializationStep
from battery_analysis.main.initialization.steps.services_initialization_step import ServicesInitializationStep
from battery_analysis.main.initialization.steps.environment_initialization_step import EnvironmentInitializationStep
from battery_analysis.main.initialization.steps.ui_setup_step import UISetupStep
from battery_analysis.main.initialization.steps.managers_initialization_step import ManagersInitializationStep
from battery_analysis.main.initialization.steps.processors_initialization_step import ProcessorsInitializationStep
from battery_analysis.main.initialization.steps.handlers_initialization_step import HandlersInitializationStep
from battery_analysis.main.initialization.steps.presenters_initialization_step import PresentersInitializationStep
from battery_analysis.main.initialization.steps.command_manager_initialization_step import CommandManagerInitializationStep
from battery_analysis.main.initialization.steps.language_initialization_step import LanguageInitializationStep
from battery_analysis.main.initialization.steps.styles_initialization_step import StylesInitializationStep


class InitializationManager:
    """
    初始化管理器
    负责处理主窗口的初始化逻辑，使用模块化的初始化步骤
    """
    
    def __init__(self, main_window):
        """
        初始化初始化管理器
        
        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        self._orchestrator = InitializationOrchestrator()
        self._register_all_steps()
    
    def initialize(self):
        """
        执行完整的初始化流程
        """
        self.logger.info("开始执行模块化初始化流程")
        return self._orchestrator.execute_all(self.main_window)
    
    def _register_all_steps(self):
        """
        注册所有初始化步骤
        """
        steps = [
            BasicAttributesInitializationStep(),
            ServicesInitializationStep(),
            EnvironmentInitializationStep(),
            UISetupStep(),
            ManagersInitializationStep(),
            ProcessorsInitializationStep(),
            HandlersInitializationStep(),
            PresentersInitializationStep(),
            CommandManagerInitializationStep(),
            LanguageInitializationStep(),
            StylesInitializationStep()
        ]
        
        self._orchestrator.register_steps(steps)
        self.logger.info("已注册 %d 个初始化步骤", self._orchestrator.get_total_steps())
    
    def get_executed_steps(self):
        """
        获取已执行步骤的结果
        
        Returns:
            已执行步骤的结果字典
        """
        return self._orchestrator.get_executed_steps()
    
    def get_total_steps(self):
        """
        获取总步骤数
        
        Returns:
            总步骤数
        """
        return self._orchestrator.get_total_steps()
