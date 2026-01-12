# -*- coding: utf-8 -*-
"""
管理器初始化步骤
"""

from battery_analysis.main.initialization.initialization_step import InitializationStep
from battery_analysis.main.factories.visualizer_factory import VisualizerFactory
from battery_analysis.main.ui_components import (
    ConfigManager, UIManager, MenuManager, DialogManager, 
    TableManager, MessageManager
)
from battery_analysis.main.business_logic.help_manager import HelpManager
from battery_analysis.main.business_logic.version_manager import VersionManager
from battery_analysis.main.utils import SignalConnector


class ManagersInitializationStep(InitializationStep):
    """管理器初始化步骤"""
    
    def __init__(self):
        """初始化管理器初始化步骤"""
        super().__init__("managers", priority=50)
    
    def execute(self, main_window) -> bool:
        """
        执行管理器初始化
        
        Args:
            main_window: 主窗口实例
            
        Returns:
            是否执行成功
        """
        try:
            # 初始化可视化器工厂
            main_window.visualizer_factory = VisualizerFactory()
            
            # 初始化配置管理器
            main_window.config_manager = ConfigManager(main_window)
            main_window.b_has_config = main_window.config_manager.b_has_config
            main_window.config = main_window.config_manager.config
            main_window.config_path = main_window.config_manager.config_path
            
            # 初始化UI管理器
            main_window.ui_manager = UIManager(main_window)
            
            # 初始化菜单管理器
            main_window.menu_manager = MenuManager(main_window)
            
            # 初始化对话框管理器
            main_window.dialog_manager = DialogManager(main_window)
            
            # 初始化表格管理器
            main_window.table_manager = TableManager(main_window)
            
            # 初始化消息管理器
            main_window.message_manager = MessageManager(main_window)
            
            # 初始化帮助管理器
            main_window.help_manager = HelpManager(main_window)
            
            # 初始化版本管理器
            main_window.version_manager = VersionManager(main_window)
            
            # 初始化信号连接器
            main_window.signal_connector = SignalConnector(main_window)
            
            # 连接菜单动作
            main_window.menu_manager.connect_menu_actions()
            
            # 设置菜单快捷键
            main_window.menu_manager.setup_menu_shortcuts()
            
            # 连接控制器信号（在manager初始化之后）
            main_window.signal_connector.connect_controllers()
            
            self.logger.info("管理器初始化完成")
            return True
        except Exception as e:
            self.logger.exception("管理器初始化失败")
            return False
    
    def can_execute(self, main_window) -> bool:
        """
        检查是否可以执行此步骤
        
        Args:
            main_window: 主窗口实例
            
        Returns:
            是否可以执行
        """
        return hasattr(main_window, 'setupUi')
