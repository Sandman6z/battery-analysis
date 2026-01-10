# -*- coding: utf-8 -*-
"""
初始化管理器

负责处理主窗口的初始化逻辑，包括：
- 基本属性初始化
- 环境信息初始化
- 管理器和处理器初始化
- 服务和控制器初始化
"""

# 标准库导入
import logging
import os
import sys
from pathlib import Path

# 第三方库导入
import PyQt6.QtCore as QC
import PyQt6.QtGui as QG
import PyQt6.QtWidgets as QW

# 本地应用/库导入
from battery_analysis.main.business_logic.data_processor import DataProcessor
from battery_analysis.main.factories.visualizer_factory import VisualizerFactory
from battery_analysis.main.handlers.temperature_handler import TemperatureHandler
from battery_analysis.main.managers.analysis_runner import AnalysisRunner
from battery_analysis.main.managers.environment_manager import EnvironmentManager
from battery_analysis.main.managers.path_manager import PathManager
from battery_analysis.main.managers.report_manager import ReportManager
from battery_analysis.main.managers.test_profile_manager import TestProfileManager
from battery_analysis.main.managers.visualization_manager import VisualizationManager
from battery_analysis.main.presenters.main_presenter import MainPresenter
from battery_analysis.main.ui.language_handler import LanguageHandler
from battery_analysis.main.utils import Checker, EnvironmentAdapter
from battery_analysis.main.ui_components import ConfigManager, DialogManager, MenuManager, MessageManager, TableManager, UIManager
from battery_analysis.main.utils import SignalConnector
from battery_analysis.main.services.service_container import get_service_container
from battery_analysis.i18n.language_manager import _, get_language_manager


class InitializationManager:
    """
    初始化管理器
    负责处理主窗口的初始化逻辑
    """
    
    def __init__(self, main_window):
        """
        初始化初始化管理器
        
        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
    
    def initialize(self):
        """
        执行完整的初始化流程
        """
        self._initialize_basic_attributes()
        self._initialize_services()
        self._initialize_environment()
        self._setup_ui()
        self._initialize_managers()
        self._initialize_processors()
        self._initialize_handlers()
        self._initialize_presenters()
        self._initialize_language()
        self._load_styles()
    
    def _initialize_basic_attributes(self):
        """
        初始化基本属性
        """
        from battery_analysis import __version__
        self.main_window.version = __version__
        
        # 初始化日志记录器
        self.main_window.logger = logging.getLogger(__name__)
        
        # 延迟加载的服务缓存
        self.main_window._services = {}
        self.main_window._controllers = {}
        
        # 初始化语言管理器
        self.main_window.language_manager = None
        
        # 初始化配置相关属性
        self.main_window.b_has_config = True
        self.main_window.checker_battery_type = Checker()
        self.main_window.checker_table = Checker()
        self.main_window.checker_input_xlsx = Checker()
        self.main_window.checker_update_config = Checker()
        self.main_window.construction_method = ""
        self.main_window.test_information = ""
        self.main_window.specification_type = ""
        self.main_window.cc_current = ""
        self.main_window.md5_checksum = ""
        self.main_window.md5_checksum_run = ""
    
    def _initialize_services(self):
        """
        初始化服务容器
        """
        # 获取服务容器
        self.main_window._service_container = get_service_container()
    
    def _initialize_environment(self):
        """
        初始化环境信息
        """
        # 初始化环境信息
        self.main_window.env_info = {}
        
        # 初始化环境适配器（在env_info初始化之后）
        self.main_window.environment_adapter = EnvironmentAdapter(self.main_window)
        # 使用环境适配器初始化环境检测器
        self.main_window.env_detector = self.main_window.environment_adapter.initialize_environment_detector()

        # 环境适配处理 - 使用环境适配器
        self.main_window.environment_adapter.handle_environment_adaptation()

        if sys.platform == "win32":
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("bt")

        # 获取项目根路径
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        self.main_window.current_directory = str(project_root)
        self.main_window.path = str(project_root)
    
    def _setup_ui(self):
        """
        设置UI
        """
        # 设置控制器的项目上下文
        try:
            main_controller = self.main_window._get_controller("main_controller")
            if main_controller and hasattr(main_controller, 'set_project_context'):
                main_controller.set_project_context(
                    project_path=self.main_window.path,
                    input_path="",  # 初始empty，后续会更新
                    output_path=""  # 初始empty，后续会更新
                )
        except (AttributeError, TypeError, ValueError) as e:
            self.logger.warning("Failed to set project context: %s", e)

        self.main_window.setupUi(self.main_window)
    
    def _initialize_managers(self):
        """
        初始化各种管理器
        """
        # 初始化可视化器工厂
        self.main_window.visualizer_factory = VisualizerFactory()
        # 移除current_visualizer实例属性，viewer应该完全独立
        
        # 初始化管理器 - 在调用任何依赖管理器的方法之前
        # 初始化配置管理器
        self.main_window.config_manager = ConfigManager(self.main_window)
        self.main_window.b_has_config = self.main_window.config_manager.b_has_config
        self.main_window.config = self.main_window.config_manager.config
        self.main_window.config_path = self.main_window.config_manager.config_path
        
        # 初始化UI管理器
        self.main_window.ui_manager = UIManager(self.main_window)
        
        # 初始化菜单管理器
        self.main_window.menu_manager = MenuManager(self.main_window)
        
        # 初始化对话框管理器
        self.main_window.dialog_manager = DialogManager(self.main_window)
        
        # 初始化表格管理器
        self.main_window.table_manager = TableManager(self.main_window)
        
        # 初始化消息管理器
        self.main_window.message_manager = MessageManager(self.main_window)
        
        # 初始化信号连接器
        self.main_window.signal_connector = SignalConnector(self.main_window)
        
        # 连接菜单动作
        self.main_window.menu_manager.connect_menu_actions()
        
        # 设置菜单快捷键
        self.main_window.menu_manager.setup_menu_shortcuts()
        
        # 连接控制器信号（在manager初始化之后）
        self.main_window.signal_connector.connect_controllers()
    
    def _initialize_processors(self):
        """
        初始化数据处理器
        """
        # 初始化数据处理器（使用优化的pandas版本）
        self.main_window.data_processor = DataProcessor(self.main_window)
    
    def _initialize_handlers(self):
        """
        初始化各种处理器
        """
        # 初始化自定义管理器和处理器
        self.main_window.temperature_handler = TemperatureHandler(self.main_window)
        self.main_window.report_manager = ReportManager(self.main_window)
        self.main_window.path_manager = PathManager(self.main_window)
        self.main_window.test_profile_manager = TestProfileManager(self.main_window)
        self.main_window.environment_manager = EnvironmentManager(self.main_window)
        self.main_window.visualization_manager = VisualizationManager(self.main_window)
        self.main_window.analysis_runner = AnalysisRunner(self.main_window)
    
    def _initialize_presenters(self):
        """
        初始化Presenter
        """
        # 初始化Presenter
        self.main_window.presenter = MainPresenter(self.main_window)
        self.main_window.presenter.initialize()
    
    def _initialize_language(self):
        """
        初始化语言相关功能
        """
        # 初始化语言处理器
        self.main_window.language_handler = LanguageHandler(self.main_window)
        
        # 连接语言管理器信号
        self._connect_language_signals()
        
        # 现在初始化环境信息，因为environment_manager已经创建
        self.main_window._initialize_environment_info()
        # 确保环境信息包含必要的键
        self.main_window._ensure_env_info_keys()
    
    def _load_styles(self):
        """
        加载并应用QSS样式
        """
        try:
            from battery_analysis.ui.styles import style_manager
            app = QW.QApplication.instance()
            if app:
                style_manager.apply_global_style(app, "modern")
        except (ImportError, AttributeError, TypeError, RuntimeError) as e:
            self.logger.warning("Failed to load QSS styles: %s", e)
    
    def _connect_language_signals(self):
        """
        连接语言管理器的信号
        """
        try:
            # 初始化语言管理器
            self.main_window.language_manager = get_language_manager()
            if self.main_window.language_manager:
                self.main_window.language_manager.language_changed.connect(self.main_window._on_language_changed)
        except (ImportError, AttributeError, TypeError, RuntimeError) as e:
            self.logger.warning("Failed to initialize language manager: %s", e)
