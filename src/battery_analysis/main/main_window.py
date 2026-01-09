"""
电池分析主窗口模块

这个模块实现了电池分析应用的主窗口界面和核心功能，包括：
- 窗口初始化和布局设置
- 配置文件管理
- 控制器连接和信号处理
- 用户交互界面
"""

# 标准库导入
import csv
import hashlib
import logging
import multiprocessing
import os
import re
import subprocess
import sys
import time
import warnings
from pathlib import Path
from typing import Any

# 第三方库导入
import matplotlib
import PyQt6.QtCore as QC
import PyQt6.QtGui as QG
import PyQt6.QtWidgets as QW

# 本地应用/库导入
from battery_analysis.i18n.language_manager import _, get_language_manager
from battery_analysis.main.factories.visualizer_factory import VisualizerFactory
from battery_analysis.main.interfaces.ivisualizer import IVisualizer
from battery_analysis.main.services.service_container import get_service_container
from battery_analysis.main.ui_components.config_manager import ConfigManager
from battery_analysis.main.ui_components.dialog_manager import DialogManager
from battery_analysis.main.ui_components.menu_manager import MenuManager
from battery_analysis.main.ui_components.progress_dialog import ProgressDialog
from battery_analysis.main.ui_components.ui_manager import UIManager
from battery_analysis.main.utils.environment_adapter import EnvironmentAdapter
from battery_analysis.main.utils.signal_connector import SignalConnector
from battery_analysis.resources import resources_rc
from battery_analysis.ui import ui_main_window
from battery_analysis.utils import temperature_utils

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')





def run_visualizer_function():
    """在模块级别定义的可视化工具运行函数（已废弃，使用工厂模式）"""
    # 此函数已废弃，现在通过 Main 类的 run_visualizer 方法使用工厂模式
    # 保留以保持向后兼容性
    logging.warning("run_visualizer_function 已废弃，请使用 Main.run_visualizer 方法")
    return False


class Checker:
    def __init__(self) -> None:
        self.b_check_pass = True
        self.str_error_msg = ""

    def clear(self):
        self.b_check_pass = True
        self.str_error_msg = ""

    def set_error(self, error_msg: str):
        self.b_check_pass = False
        self.str_error_msg = error_msg



class Main(QW.QMainWindow, ui_main_window.Ui_MainWindow):
    sigSetVersion = QC.pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        from battery_analysis import __version__
        self.version = __version__
        
        # 初始化日志记录器
        self.logger = logging.getLogger(__name__)
        
        # 获取服务容器
        self._service_container = get_service_container()
        
        # 延迟加载的服务缓存
        self._services = {}
        self._controllers = {}
        
        # 初始化语言管理器
        self.language_manager = None

        # 初始化可视化器工厂
        self.visualizer_factory = VisualizerFactory()
        # 移除current_visualizer实例属性，viewer应该完全独立
        
        # 初始化数据处理器（使用优化的pandas版本）
        from battery_analysis.main.business_logic.data_processor import DataProcessor
        self.data_processor = DataProcessor(self)

        self.b_has_config = True
        self.checker_battery_type = Checker()
        self.checker_table = Checker()
        self.checker_input_xlsx = Checker()
        self.checker_update_config = Checker()
        self.construction_method = ""
        self.test_information = ""
        self.specification_type = ""
        self.cc_current = ""
        self.md5_checksum = ""
        self.md5_checksum_run = ""

        # 初始化环境信息
        self.env_info = {}
        self._initialize_environment_info()
        
        # 确保环境信息包含必要的键
        self._ensure_env_info_keys()
        
        # 初始化环境适配器（在env_info初始化之后）
        self.environment_adapter = EnvironmentAdapter(self)
        # 使用环境适配器初始化环境检测器
        self.env_detector = self.environment_adapter.initialize_environment_detector()

        # 环境适配处理 - 使用环境适配器
        self.environment_adapter.handle_environment_adaptation()

        if sys.platform == "win32":
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("bt")

        # 获取项目根路径
        project_root = Path(__file__).resolve().parent.parent.parent

        self.current_directory = str(project_root)
        self.path = str(project_root)

        # 设置控制器的项目上下文
        try:
            main_controller = self._get_controller("main_controller")
            if hasattr(main_controller, 'set_project_context'):
                main_controller.set_project_context(
                    project_path=self.path,
                    input_path="",  # 初始empty，后续会更新
                    output_path=""  # 初始empty，后续会更新
                )
        except (AttributeError, TypeError, ValueError) as e:
            self.logger.warning("Failed to set project context: %s", e)

        self.setupUi(self)
        
        # 初始化管理器 - 在调用任何依赖管理器的方法之前
        self._initialize_managers()
        
        # 连接控制器信号（在manager初始化之后）
        self.signal_connector.connect_controllers()
        
        # 加载并应用QSS样式
        try:
            from battery_analysis.ui.styles import style_manager
            app = QW.QApplication.instance()
            if app:
                style_manager.apply_global_style(app, "modern")
        except (ImportError, AttributeError, TypeError, RuntimeError) as e:
            self.logger.warning("Failed to load QSS styles: %s", e)

        # 连接语言管理器信号
        self._connect_language_signals()
        
        # 初始化语言处理器
        from battery_analysis.main.ui.language_handler import LanguageHandler
        self.language_handler = LanguageHandler(self)
        
        # 初始化Presenter
        from battery_analysis.main.presenters.main_presenter import MainPresenter
        self.presenter = MainPresenter(self)
        self.presenter.initialize()
        
        self.init_window()
        self.init_widget()

        listPulseCurrent = self.get_config("BatteryConfig/PulseCurrent")
        listCutoffVoltage = self.get_config("BatteryConfig/CutoffVoltage")
        
        # 使用新的配置解析工具
        from battery_analysis.utils.config_parser import safe_int_convert, safe_float_convert
        
        # 处理可能包含浮点数的电流值
        try:
            self.listCurrentLevel = [safe_int_convert(listPulseCurrent[c].strip())
                                     for c in range(len(listPulseCurrent))]
        except (ValueError, TypeError):
            # 如果转换失败，使用默认值
            self.listCurrentLevel = [0] * len(listPulseCurrent)
            
        self.listVoltageLevel = [
            safe_float_convert(listCutoffVoltage[c].strip()) for c in range(len(listCutoffVoltage))]
    
    def _initialize_managers(self):
        """
        初始化各个管理器
        """
        # 初始化配置管理器
        self.config_manager = ConfigManager(self)
        self.b_has_config = self.config_manager.b_has_config
        self.config = self.config_manager.config
        self.config_path = self.config_manager.config_path
        
        # 初始化UI管理器
        self.ui_manager = UIManager(self)
        
        # 初始化菜单管理器
        self.menu_manager = MenuManager(self)
        
        # 初始化对话框管理器
        self.dialog_manager = DialogManager(self)
        
        # 初始化信号连接器
        self.signal_connector = SignalConnector(self)
        
        # 连接菜单动作
        self.menu_manager.connect_menu_actions()
        
        # 设置菜单快捷键
        self.menu_manager.setup_menu_shortcuts()

    def _get_service(self, service_name):
        """
        懒加载获取服务
        
        Args:
            service_name: 服务名称
            
        Returns:
            服务实例或None
        """
        if service_name not in self._services:
            try:
                self._services[service_name] = self._service_container.get(service_name)
            except (TypeError, AttributeError, OSError, ValueError, ImportError) as e:
                self.logger.warning("Failed to get service %s: %s", service_name, e)
                self._services[service_name] = None
        return self._services[service_name]
    
    def _get_controller(self, controller_name):
        """
        懒加载获取控制器
        
        Args:
            controller_name: 控制器名称
            
        Returns:
            控制器实例或None
        """
        if controller_name not in self._controllers:
            try:
                self._controllers[controller_name] = self._service_container.get(controller_name)
            except (TypeError, AttributeError, OSError, ValueError, ImportError) as e:
                self.logger.warning("Failed to get controller %s: %s", controller_name, e)
                self._controllers[controller_name] = None
        return self._controllers[controller_name]
    
    def get_config(self, config_key):
        """
        获取配置值并处理为列表格式，委托给config_manager
        """
        return self.config_manager.get_config(config_key)

    def init_window(self) -> None:
        """
        初始化窗口设置，委托给ui_manager
        """
        self.ui_manager.init_window()
    
    def show_message(self, title: str, message: str) -> None:
        """
        显示信息消息框
        
        Args:
            title: 消息框标题
            message: 消息内容
        """
        from PyQt6 import QtWidgets as QW
        from battery_analysis.i18n.language_manager import _
        QW.QMessageBox.information(self, title, message)
    
    def show_warning(self, title: str, message: str) -> None:
        """
        显示警告消息框
        
        Args:
            title: 消息框标题
            message: 警告内容
        """
        from PyQt6 import QtWidgets as QW
        from battery_analysis.i18n.language_manager import _
        QW.QMessageBox.warning(self, title, message)
    
    def show_error(self, title: str, message: str) -> None:
        """
        显示错误消息框
        
        Args:
            title: 消息框标题
            message: 错误内容
        """
        from PyQt6 import QtWidgets as QW
        from battery_analysis.i18n.language_manager import _
        QW.QMessageBox.critical(self, title, message)
    
    def _load_application_icon(self) -> QG.QIcon:
        """
        加载应用程序图标，使用环境检测器来找到正确的路径
        
        Returns:
            QIcon: 应用程序图标
        """
        try:
            # 尝试多个可能的图标路径（优先使用环境检测器，否则使用固定路径）
            icon_paths = []
            
            # 如果环境检测器可用，使用它来解析路径
            if self.env_detector:
                icon_paths = [
                    self.env_detector.get_resource_path("config/resources/icons/Icon_BatteryTestGUI.ico"),
                    self.env_detector.get_resource_path("resources/icons/Icon_BatteryTestGUI.ico"),
                ]
            
            # 始终尝试相对路径（工程中的图标）
            icon_paths.extend([
                Path(self.current_directory) / "config" / "resources" / "icons" / "Icon_BatteryTestGUI.ico",
                Path(self.current_directory) / "resources" / "icons" / "Icon_BatteryTestGUI.ico",
            ])
            
            # 遍历所有可能的路径，找到第一个存在的
            for icon_path in icon_paths:
                if icon_path.exists():
                    self.logger.debug("找到应用图标: %s", icon_path)
                    return QG.QIcon(str(icon_path))
            
            # 如果都找不到，使用默认图标
            self.logger.warning("未找到应用图标文件，使用默认图标")
            return QG.QIcon()
            
        except (OSError, TypeError, ValueError, RuntimeError, ImportError) as e:
            # 捕获所有可能的异常，确保应用能正常启动
            self.logger.error("加载应用图标失败: %s", e)
            return QG.QIcon()

    def _connect_language_signals(self):
        """连接语言管理器的信号"""
        try:
            # 初始化语言管理器
            self.language_manager = get_language_manager()
            if self.language_manager:
                self.language_manager.language_changed.connect(self._on_language_changed)
        except (ImportError, AttributeError, TypeError, RuntimeError) as e:
            self.logger.warning("Failed to initialize language manager: %s", e)

    def _on_language_changed(self, language_code):
        """语言切换处理"""
        window_title = f"Battery Analyzer v{self.version}"
        self.setWindowTitle(window_title)
        
        # 更新UI文本
        self._update_ui_texts()
        
        # 更新状态栏消息
        self._update_statusbar_messages()
        
        # 刷新所有对话框
        self._refresh_dialogs()
        
        logging.info("界面语言已切换到: %s", language_code)

    def _update_ui_texts(self):
        """更新UI文本为当前语言"""
        if hasattr(self, 'signal_connector') and self.signal_connector.progress_dialog:
            self.signal_connector.progress_dialog.setWindowTitle(_("progress_title", "Battery Analysis Progress"))
            self.signal_connector.progress_dialog.status_label.setText(_("progress_ready", "Ready to start analysis..."))
    
    def _update_statusbar_messages(self):
        """更新状态栏消息为当前语言（委托给menu_manager）"""
        self.menu_manager.update_statusbar_messages()
    
    def _refresh_dialogs(self):
        """刷新所有对话框以应用新语言"""
        # 关闭并重新创建首选项对话框（如果正在显示）
        # 如果需要刷新其他对话框，也在这里处理
        pass

    def init_widget(self) -> None:
        """
        初始化部件设置，委托给ui_manager
        """
        self.ui_manager.init_widget()
        self.pushButton_Run.setFocus()
    
    def connect_widget(self) -> None:
        # 调用ui_manager中的connect_widget方法，连接基础控件信号
        self.ui_manager.connect_widget()
        
        # 连接ui_manager中没有的信号
        self.pushButton_Run.clicked.connect(self.run)
        self.sigSetVersion.connect(self.get_version)

        # 菜单和工具栏管理功能已委托给menu_manager
        # 所有菜单连接、快捷键设置等都在menu_manager中处理
        self.menu_manager.connect_menu_actions()
        self.setup_menu_shortcuts()

    def handle_exit(self) -> None:
        """
        处理退出操作，委托给dialog_manager
        """
        self.dialog_manager.handle_exit()

    def handle_about(self) -> None:
        """
        显示关于对话框，委托给dialog_manager
        """
        self.dialog_manager.handle_about()

    def show_preferences(self) -> None:
        """显示首选项对话框，委托给dialog_manager"""
        self.dialog_manager.show_preferences()

    def on_preferences_applied(self) -> None:
        """首选项应用后的处理"""
        try:
            # 这里可以添加首选项应用后的特殊处理
            # 比如重新加载某些设置、更新界面等
            self.logger.info("首选项已应用")
            
        except (OSError, ValueError, ImportError) as e:
            self.logger.error("应用首选项后处理时发生错误: %s", e)

    def toggle_toolbar_safe(self) -> None:
        """安全地切换工具栏的显示/隐藏状态（委托给menu_manager）"""
        self.menu_manager.toggle_toolbar_safe()

    def toggle_statusbar_safe(self) -> None:
        """安全地切换状态栏的显示/隐藏状态（委托给menu_manager）"""
        self.menu_manager.toggle_statusbar_safe()

    def setup_menu_shortcuts(self) -> None:
        # 安全地设置所有菜单的快捷键（委托给menu_manager）
        self.menu_manager.setup_menu_shortcuts()

    def show_user_manual(self) -> None:
        """显示用户手册"""
        try:
            # 首先尝试从当前目录查找手册
            manual_paths = [
                # 相对路径
                Path(self.current_directory) / "docs" / "user_manual.pdf",
                Path(self.current_directory) / "user_manual.pdf",
                # 绝对路径 - 项目目录
                Path(__file__).parent.parent.parent / "docs" / "user_manual.pdf",
                Path(__file__).parent.parent.parent / "user_manual.pdf",
                # 常见的文档位置
                Path(os.getcwd()) / "docs" / "user_manual.pdf",
                Path(os.getcwd()) / "user_manual.pdf",
            ]
            
            manual_found = False
            for manual_path in manual_paths:
                if manual_path.exists() and manual_path.is_file():
                    try:
                        # 使用安全的文件打开方式
                        os.startfile(str(manual_path))
                        manual_found = True
                        self.logger.info("成功打开用户手册: %s", manual_path)
                        break
                    except (OSError, ValueError, RuntimeError, PermissionError) as open_error:
                        self.logger.warning("打开手册文件失败 %s: %s", manual_path, open_error)
                        continue
            
            if not manual_found:
                # 如果找不到手册文件，显示提示并提供解决方案
                QW.QMessageBox.information(
                    self,
                    "用户手册",
                    "未找到用户手册文件。\n\n"
                    "请确保以下文件存在：\n"
                    "• docs/user_manual.pdf\n"
                    "• user_manual.pdf\n\n"
                    "如需帮助，请联系技术支持。",
                    QW.QMessageBox.StandardButton.Ok
                )
                
        except (OSError, TypeError, ValueError, RuntimeError) as e:
            self.logger.error("打开用户手册失败: %s", e)
            QW.QMessageBox.warning(
                self,
                _("error", "错误"),
                f"{_('cannot_open_user_manual', '无法打开用户手册')}: {str(e)}",
                QW.QMessageBox.StandardButton.Ok
            )

    def show_online_help(self) -> None:
        """
        显示在线帮助，委托给dialog_manager
        """
        self.dialog_manager.show_online_help()

    def copy_selected_text(self) -> None:
        """复制选中的文本"""
        focused_widget = self.focusWidget()
        if isinstance(focused_widget, QW.QLineEdit) or isinstance(focused_widget, QW.QTextEdit):
            focused_widget.copy()

    def paste_text(self) -> None:
        """粘贴文本"""
        focused_widget = self.focusWidget()
        if isinstance(focused_widget, QW.QLineEdit) or isinstance(focused_widget, QW.QTextEdit):
            focused_widget.paste()

    def cut_selected_text(self) -> None:
        """剪切选中的文本"""
        focused_widget = self.focusWidget()
        if isinstance(focused_widget, QW.QLineEdit) or isinstance(focused_widget, QW.QTextEdit):
            focused_widget.cut()

    def calculate_battery(self) -> None:
        """执行电池计算，委托给Presenter"""
        self.presenter.on_calculate_battery()

    def analyze_data(self) -> None:
        """分析数据，委托给Presenter"""
        self.presenter.on_analyze_data()

    def generate_report(self) -> None:
        """生成报告，委托给Presenter"""
        self.presenter.on_generate_report()
    
    def _initialize_environment_info(self):
        """
        初始化环境信息
        """
        try:
            environment_service = self._get_service("environment")
            if environment_service:
                if hasattr(environment_service, 'env_info'):
                    self.env_info = environment_service.env_info
                elif hasattr(environment_service, 'initialize'):
                    if environment_service.initialize() and hasattr(environment_service, 'env_info'):
                        self.env_info = environment_service.env_info
        except (AttributeError, TypeError, ImportError, OSError) as e:
            self.logger.warning("Failed to initialize environment service: %s", e)
    
    def _ensure_env_info_keys(self):
        """
        确保环境信息包含必要的键
        """
        if 'environment_type' not in self.env_info:
            try:
                environment_service = self._get_service("environment")
                if environment_service and hasattr(environment_service, 'EnvironmentType'):
                    self.env_info['environment_type'] = environment_service.EnvironmentType.DEVELOPMENT
                else:
                    # 降级到直接导入
                    from battery_analysis.utils.environment_utils import EnvironmentType
                    self.env_info['environment_type'] = EnvironmentType.DEVELOPMENT
            except (AttributeError, TypeError, ImportError) as e:
                self.logger.warning("Failed to get EnvironmentType: %s", e)
                from battery_analysis.utils.environment_utils import EnvironmentType
                self.env_info['environment_type'] = EnvironmentType.DEVELOPMENT
        
        if 'gui_available' not in self.env_info:
            self.env_info['gui_available'] = True
    
    def run_visualizer(self, xml_path=None) -> None:
        """运行可视化工具，使用工厂模式解耦依赖"""
        logging.info("进入main_window.run_visualizer方法")
        
        # 检查xml_path是否为布尔值，如果是，则忽略（可能来自QAction的triggered信号）
        if isinstance(xml_path, bool):
            logging.info("检测到布尔类型的xml_path参数，忽略它")
            xml_path = None
        
        # viewer是独立工具，不需要从主UI获取数据路径，让其自行处理数据搜索
        
        self.statusBar_BatteryAnalysis.showMessage(_("starting_visualizer", "启动可视化工具..."))

        try:
            # 确保所有matplotlib资源都被释放（只清理全局资源，不涉及实例）
            try:
                import matplotlib.pyplot as plt
                plt.close('all')  # 关闭所有打开的matplotlib窗口
            except (ImportError, RuntimeError) as e:
                logging.warning("清理matplotlib全局资源时出错: %s", e)
            
            # 使用工厂模式创建可视化器（使用局部变量，不存储为实例属性）
            logging.info("使用工厂模式创建可视化器")
            visualizer = self.visualizer_factory.create_visualizer("battery_chart")
            
            if visualizer is None:
                raise RuntimeError("无法创建可视化器实例")

            # 显示可视化（不传递数据路径，让viewer自行处理数据搜索和加载）
            logging.info("显示可视化，让viewer独立处理数据")
            show_success = visualizer.show_figure()
            
            if show_success:
                # 更新状态栏
                self.statusBar_BatteryAnalysis.showMessage(_("visualizer_started", "可视化工具已启动"))
                logging.info("可视化工具启动完成")
            else:
                raise RuntimeError("显示可视化失败")

        except (AttributeError, TypeError, OSError, ValueError, RuntimeError, ImportError, PermissionError, subprocess.SubprocessError) as e:
            error_msg = str(e)
            logging.error("启动可视化工具时出错: %s", error_msg)
            import traceback
            logging.error("异常堆栈: %s", traceback.format_exc())
            
            # 判断是否为数据相关错误
            data_error_keywords = ['data', 'csv', 'load', 'file', 'path', 'config', 'info_image', '数据']
            is_data_error = any(keyword in error_msg.lower() for keyword in data_error_keywords)
            
            if is_data_error:
                # 对于数据相关错误，提供恢复选项
                self._handle_data_error_recovery(error_msg)
            else:
                # 对于其他错误，显示标准错误对话框
                QW.QMessageBox.critical(
                    self,
                    "错误",
                    f"启动可视化工具时出错:\n\n{error_msg}\n\n请检查配置文件或联系技术支持。",
                    QW.QMessageBox.StandardButton.Ok
                )
            
            self.statusBar_BatteryAnalysis.showMessage("状态:就绪")
    
    def _handle_data_error_recovery(self, error_msg: str):
        """处理数据相关错误的恢复选项"""
        # 创建自定义对话框
        dialog = QW.QDialog(self)
        dialog.setWindowTitle("数据加载错误 - 恢复选项")
        dialog.setModal(True)
        dialog.resize(500, 300)
        
        layout = QW.QVBoxLayout(dialog)
        
        # 错误信息标签
        error_label = QW.QLabel("无法加载电池数据，请选择如何继续:")
        error_label.setWordWrap(True)
        error_label.setStyleSheet("font-weight: bold; color: red;")
        layout.addWidget(error_label)
        
        # 详细错误信息
        details_label = QW.QLabel(f"错误详情: {error_msg}")
        details_label.setWordWrap(True)
        details_label.setStyleSheet("background-color: #f0f0f0; padding: 10px; border: 1px solid #ccc;")
        layout.addWidget(details_label)
        
        # 恢复选项说明
        help_label = QW.QLabel("请选择以下恢复选项之一:")
        help_label.setStyleSheet("margin-top: 10px; font-weight: bold;")
        layout.addWidget(help_label)
        
        # 按钮组
        button_group = QW.QButtonGroup(dialog)
        
        # 选项1: 重新选择数据目录
        self.retry_option = QW.QRadioButton("重新选择数据目录")
        self.retry_option.setChecked(True)
        button_group.addButton(self.retry_option, 1)
        layout.addWidget(self.retry_option)
        
        # 选项2: 使用默认配置
        self.default_option = QW.QRadioButton("使用默认配置重新启动")
        button_group.addButton(self.default_option, 2)
        layout.addWidget(self.default_option)
        
        # 选项3: 取消操作
        self.cancel_option = QW.QRadioButton("取消操作")
        button_group.addButton(self.cancel_option, 3)
        layout.addWidget(self.cancel_option)
        
        # 添加按钮
        button_layout = QW.QHBoxLayout()
        
        ok_button = QW.QPushButton("确定")
        ok_button.clicked.connect(dialog.accept)
        button_layout.addWidget(ok_button)
        
        cancel_button = QW.QPushButton("取消")
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        # 显示对话框
        if dialog.exec() == QW.QDialog.DialogCode.Accepted:
            selected_id = button_group.checkedId()
            
            if selected_id == 1:
                # 重新选择数据目录
                self.statusBar_BatteryAnalysis.showMessage("正在打开数据目录选择...")
                self._open_data_directory_dialog()
                
            elif selected_id == 2:
                # 使用默认配置重新启动
                self.statusBar_BatteryAnalysis.showMessage("使用默认配置重新启动...")
                QW.QMessageBox.information(
                    self,
                    "重新启动",
                    "应用将使用默认配置重新启动。\n\n请确保您有有效的数据文件可用。",
                    QW.QMessageBox.StandardButton.Ok
                )
                # 清空配置字段并重新启动
                if hasattr(self, 'lineEdit_TestProfile'):
                    self.lineEdit_TestProfile.clear()
                # 递归调用，但使用默认配置
                self.run_visualizer(xml_path=None)
                
            else:
                # 取消操作
                self.statusBar_BatteryAnalysis.showMessage("操作已取消")
                QW.QMessageBox.information(
                    self,
                    "取消",
                    "操作已取消。您可以通过菜单 'File -> Open Data' 重新尝试。",
                    QW.QMessageBox.StandardButton.Ok
                )
        else:
            self.statusBar_BatteryAnalysis.showMessage("操作已取消")
    
    def _open_data_directory_dialog(self):
        """打开数据目录选择对话框"""
        try:
            # 打开目录选择对话框
            directory = QW.QFileDialog.getExistingDirectory(
                self,
                "选择包含电池数据的目录",
                "",
                QW.QFileDialog.Option.ShowDirsOnly | QW.QFileDialog.Option.DontResolveSymlinks
            )
            
            if directory:
                self.statusBar_BatteryAnalysis.showMessage(f"已选择目录: {directory}")
                
                # 检查目录中是否有Info_Image.csv文件
                info_image_path = os.path.join(directory, "Info_Image.csv")
                if os.path.exists(info_image_path):
                    QW.QMessageBox.information(
                        self,
                        "数据目录确认",
                        f"找到数据文件: {info_image_path}\n\n应用将尝试使用此数据重新启动可视化工具。",
                        QW.QMessageBox.StandardButton.Ok
                    )
                    
                    # 更新界面上的配置路径
                    if hasattr(self, 'lineEdit_TestProfile'):
                        self.lineEdit_TestProfile.setText(directory)
                    
                    # 重新运行可视化工具
                    self.run_visualizer(xml_path=directory)
                else:
                    QW.QMessageBox.warning(
                        self,
                        "数据目录无效",
                        f"在选择的目录中没有找到 Info_Image.csv 文件:\n\n{directory}\n\n请确保选择的目录包含有效的电池数据文件。",
                        QW.QMessageBox.StandardButton.Ok
                    )
                    self.statusBar_BatteryAnalysis.showMessage("无效的数据目录")
            else:
                self.statusBar_BatteryAnalysis.showMessage("未选择目录")
                
        except (OSError, TypeError, ValueError, RuntimeError, PermissionError, FileNotFoundError) as e:
            logging.error("打开数据目录对话框时出错: %s", str(e))
            QW.QMessageBox.critical(
                self,
                "错误",
                f"打开目录选择对话框时出错:\n\n{str(e)}",
                QW.QMessageBox.StandardButton.Ok
            )
            self.statusBar_BatteryAnalysis.showMessage(_("status_ready", "状态:就绪"))

    def show_visualizer_error(self, error_msg: str):
        """在主线程中显示可视化工具错误消息"""
        QW.QMessageBox.critical(
            self,
            _("error", "错误"),
            f"{_('visualizer_start_error', '启动可视化工具时发生错误')}: {error_msg}",
            QW.QMessageBox.StandardButton.Ok
        )
        self.statusBar_BatteryAnalysis.showMessage(_("status_ready", "状态:就绪"))

    def batch_processing(self) -> None:
        """批量处理，委托给Presenter"""
        self.presenter.on_batch_processing()

    def save_settings(self) -> None:
        """保存当前设置到用户配置文件"""
        try:
            # 显示保存状态
            self.statusBar_BatteryAnalysis.showMessage(_("saving_settings", "正在保存设置..."))

            # 创建用户配置文件路径（与原始配置文件同目录，使用不同名称）
            user_config_path = os.path.join(os.path.dirname(
                self.config_path), "user_settings.ini") if self.b_has_config else None

            if user_config_path:
                # 创建用户配置QSettings实例
                user_settings = QC.QSettings(
                    user_config_path, QC.QSettings.Format.IniFormat)

                # 保存用户可修改的设置项
                # 电池类型相关设置
                battery_type = self.comboBox_BatteryType.currentText()
                if battery_type:
                    user_settings.setValue(
                        "UserConfig/BatteryType", battery_type)

                construction_method = self.comboBox_ConstructionMethod.currentText()
                if construction_method:
                    user_settings.setValue(
                        "UserConfig/ConstructionMethod", construction_method)

                specification_type = self.comboBox_Specification_Type.currentText()
                if specification_type:
                    user_settings.setValue(
                        "UserConfig/SpecificationType", specification_type)

                specification_method = self.comboBox_Specification_Method.currentText()
                if specification_method:
                    user_settings.setValue(
                        "UserConfig/SpecificationMethod", specification_method)

                manufacturer = self.comboBox_Manufacturer.currentText()
                if manufacturer:
                    user_settings.setValue(
                        "UserConfig/Manufacturer", manufacturer)

                tester_location = self.comboBox_TesterLocation.currentText()
                if tester_location:
                    user_settings.setValue(
                        "UserConfig/TesterLocation", tester_location)

                tested_by = self.comboBox_TestedBy.currentText()
                if tested_by:
                    user_settings.setValue("UserConfig/TestedBy", tested_by)
                
                # 保存ReportedBy设置
                reported_by = self.comboBox_ReportedBy.currentText()
                if reported_by:
                    user_settings.setValue("UserConfig/ReportedBy", reported_by)

                # 温度设置 - 使用comboBox_Temperature的值代替lineEdit_Temperature
                temperature_type = self.comboBox_Temperature.currentText()
                if temperature_type == "Freezer Temperature":
                    temperature = f"{temperature_type}:{self.spinBox_Temperature.value()}"
                else:
                    temperature = temperature_type
                user_settings.setValue(
                    "UserConfig/Temperature", temperature)
                
                # 保存温度类型设置
                temperature_type = self.comboBox_Temperature.currentText()
                user_settings.setValue(
                    "UserConfig/TemperatureType", temperature_type)
                
                # 保存冷冻温度数值设置（无论是否启用）
                freezer_temp = self.spinBox_Temperature.value()
                user_settings.setValue(
                    "UserConfig/FreezerTemperature", freezer_temp)

                # 输出路径设置
                output_path = self.lineEdit_OutputPath.text()
                if output_path:
                    user_settings.setValue(
                        "UserConfig/OutputPath", output_path)

                # 同步保存到内存中的配置实例
                self.config = user_settings

                self.statusBar_BatteryAnalysis.showMessage(_("settings_saved", "设置已保存"))
                QW.QMessageBox.information(
                    self,
                    "保存设置",
                    "当前配置已成功保存到用户配置文件。",
                    QW.QMessageBox.StandardButton.Ok
                )
            else:
                # 如果没有原始配置文件，显示错误消息
                QW.QMessageBox.warning(
                    self,
                    "错误",
                    "无法找到配置文件路径，无法保存设置。",
                    QW.QMessageBox.StandardButton.Ok
                )
                self.statusBar_BatteryAnalysis.showMessage(_("save_settings_failed", "保存设置失败"))

        except (IOError, OSError, PermissionError, ValueError, TypeError, configparser.Error) as e:
            logging.error("保存设置失败: %s", e)
            QW.QMessageBox.warning(
                self,
                "错误",
                f"无法保存设置: {str(e)}",
                QW.QMessageBox.StandardButton.Ok
            )
            self.statusBar_BatteryAnalysis.showMessage(_("save_settings_failed", "保存设置失败"))

    def export_report(self) -> None:
        """导出报告，委托给Presenter"""
        self.presenter.on_export_report()

    def set_theme(self, theme_name) -> None:
        """设置应用程序主题，委托给theme_manager处理"""
        self.theme_manager.set_theme(theme_name)

    def toggle_statusbar(self) -> None:
        """切换状态栏的显示/隐藏状态，委托给menu_manager处理"""
        self.menu_manager.toggle_statusbar()

    def validate_version(self) -> None:
        """验证版本号格式并提供实时反馈，委托给ValidationManager"""
        from battery_analysis.main.business_logic.validation_manager import ValidationManager
        validation_manager = ValidationManager(self)
        validation_manager.validate_version()

    def validate_input_path(self) -> None:
        """验证输入路径是否存在，委托给ValidationManager"""
        from battery_analysis.main.business_logic.validation_manager import ValidationManager
        validation_manager = ValidationManager(self)
        validation_manager.validate_input_path()

    def validate_required_fields(self) -> None:
        """验证必填字段是否为空，委托给ValidationManager"""
        from battery_analysis.main.business_logic.validation_manager import ValidationManager
        validation_manager = ValidationManager(self)
        validation_manager.validate_required_fields()

    def check_batterytype(self) -> None:
        """检查电池类型并更新相关UI组件，委托给ValidationManager"""
        from battery_analysis.main.business_logic.validation_manager import ValidationManager
        validation_manager = ValidationManager(self)
        validation_manager.check_batterytype()
        return
        self.checker_battery_type.clear()
        if self.comboBox_BatteryType.currentText() == "Coin Cell":
            self.comboBox_ConstructionMethod.setEnabled(False)
            self.comboBox_ConstructionMethod.setCurrentIndex(-1)
            self.lineEdit_DatasheetNominalCapacity.setText("")
            self.lineEdit_CalculationNominalCapacity.setText("")
            self.lineEdit_RequiredUseableCapacity.setText("")
            self.comboBox_Specification_Type.currentIndexChanged.disconnect(
                self.check_specification)
            self.comboBox_Specification_Method.currentIndexChanged.disconnect(
                self.check_specification)
            self.comboBox_Specification_Type.clear()
            self.comboBox_Specification_Type.addItems(
                self.get_config("BatteryConfig/SpecificationTypeCoinCell"))
            self.comboBox_Specification_Type.setCurrentIndex(-1)
            self.comboBox_Specification_Type.currentIndexChanged.connect(
                self.check_specification)
            self.comboBox_Specification_Method.currentIndexChanged.connect(
                self.check_specification)
            for t in range(self.comboBox_Specification_Type.count()):
                if self.specification_type == self.comboBox_Specification_Type.itemText(t):
                    self.comboBox_Specification_Type.setCurrentIndex(t)
                    break
        elif self.comboBox_BatteryType.currentText() == "Pouch Cell":
            self.comboBox_ConstructionMethod.setEnabled(True)
            for c in range(self.comboBox_ConstructionMethod.count()):
                if self.construction_method == self.comboBox_ConstructionMethod.itemText(c):
                    self.comboBox_ConstructionMethod.setCurrentIndex(c)
                    self.construction_method = ""
                    break
            self.lineEdit_DatasheetNominalCapacity.setText("")
            self.lineEdit_CalculationNominalCapacity.setText("")
            self.lineEdit_RequiredUseableCapacity.setText("")
            self.comboBox_Specification_Type.currentIndexChanged.disconnect(
                self.check_specification)
            self.comboBox_Specification_Method.currentIndexChanged.disconnect(
                self.check_specification)
            self.comboBox_Specification_Type.clear()
            self.comboBox_Specification_Type.addItems(
                self.get_config("BatteryConfig/SpecificationTypePouchCell"))
            self.comboBox_Specification_Type.setCurrentIndex(-1)
            self.comboBox_Specification_Type.currentIndexChanged.connect(
                self.check_specification)
            self.comboBox_Specification_Method.currentIndexChanged.connect(
                self.check_specification)
            for t in range(self.comboBox_Specification_Type.count()):
                if self.specification_type == self.comboBox_Specification_Type.itemText(t):
                    self.comboBox_Specification_Type.setCurrentIndex(t)
                    break
        elif not self.comboBox_BatteryType.currentText():
            pass
        else:
            self.checker_battery_type.set_error(
                f"No battery type named {self.comboBox_BatteryType.currentText()}")
            self.statusBar_BatteryAnalysis.showMessage(
                f"[Error]: No battery type named {self.comboBox_BatteryType.currentText()}")

    def check_specification(self) -> None:
        """检查规格并更新相关UI组件，委托给ValidationManager"""
        from battery_analysis.main.business_logic.validation_manager import ValidationManager
        validation_manager = ValidationManager(self)
        validation_manager.check_specification()
        return
        self.specification_type = self.comboBox_Specification_Type.currentText()
        coin_cell_types = self.get_config(
            "BatteryConfig/SpecificationTypeCoinCell")
        pouch_cell_types = self.get_config(
            "BatteryConfig/SpecificationTypePouchCell")

        for coin_type in coin_cell_types:
            if self.specification_type == coin_type:
                self.comboBox_BatteryType.setCurrentIndex(0)

        for pouch_type in pouch_cell_types:
            if self.specification_type == pouch_type:
                self.comboBox_BatteryType.setCurrentIndex(1)

        specification_method = self.comboBox_Specification_Method.currentText()
        if not self.specification_type or not specification_method:
            return

        rules = self.get_config("BatteryConfig/Rules")
        for rule in rules:
            rule_parts = rule.split("/")
            if rule_parts[0] == self.specification_type:
                if specification_method == rule_parts[1]:
                    self.lineEdit_DatasheetNominalCapacity.setText(
                        f"{rule_parts[2]}")
                    self.lineEdit_CalculationNominalCapacity.setText(
                        f"{rule_parts[3]}")
                    listRequiredUseableCapacityPercentage = re.findall(
                        r"(\d+)%", rule_parts[4])
                    if (listRequiredUseableCapacityPercentage != []
                            and len(listRequiredUseableCapacityPercentage) == 1):
                        nominal_capacity = int(rule_parts[3])
                        percentage = int(
                            listRequiredUseableCapacityPercentage[0])
                        required_capacity = int(
                            nominal_capacity * percentage / 100)
                        self.lineEdit_RequiredUseableCapacity.setText(
                            f"{required_capacity}")
                    else:
                        self.lineEdit_RequiredUseableCapacity.setText(
                            f"{rule_parts[4]}")
                else:
                    self.lineEdit_DatasheetNominalCapacity.setText("")
                    self.lineEdit_CalculationNominalCapacity.setText("")
                    self.lineEdit_RequiredUseableCapacity.setText("")
                break
            elif rule_parts[0] in self.specification_type:
                if specification_method == rule_parts[1]:
                    self.lineEdit_DatasheetNominalCapacity.setText(
                        f"{rule_parts[2]}")
                    self.lineEdit_CalculationNominalCapacity.setText(
                        f"{rule_parts[3]}")
                    listRequiredUseableCapacityPercentage = re.findall(
                        r"(\d+)%", rule_parts[4])
                    if (listRequiredUseableCapacityPercentage != []
                            and len(listRequiredUseableCapacityPercentage) == 1):
                        nominal_capacity = int(rule_parts[3])
                        percentage = int(
                            listRequiredUseableCapacityPercentage[0])
                        required_capacity = int(
                            nominal_capacity * percentage / 100)
                        self.lineEdit_RequiredUseableCapacity.setText(
                            f"{required_capacity}")
                    else:
                        self.lineEdit_RequiredUseableCapacity.setText(
                            f"{rule_parts[4]}")
                else:
                    self.lineEdit_DatasheetNominalCapacity.setText("")
                    self.lineEdit_CalculationNominalCapacity.setText("")
                    self.lineEdit_RequiredUseableCapacity.setText("")
            else:
                pass

    def set_table(self) -> None:
        self.checker_table.clear()
        # 不再重新创建QSettings实例，而是重新读取配置
        # 这样可以确保使用与初始化when相同的配置文件路径和设置
        self.config.sync()  # 确保配置文件被correct加载

        test_information_groups = []
        child_groups = self.config.childGroups()

        for group in child_groups:
            if "TestInformation." in group:
                test_information_groups.append(group)

        if not test_information_groups:
            self.checker_table.set_error("No TestInformation in setting.ini")
            self.statusBar_BatteryAnalysis.showMessage(
                "[Error]: No TestInformation in setting.ini")
            return

        self.test_information = ""
        for group in test_information_groups:
            group_parts = group.split(".")
            if len(group_parts) != 3:
                self.checker_table.set_error(
                    f"Wrong TestInformation section format:[{group}] in setting.ini")
                self.statusBar_BatteryAnalysis.showMessage(
                    f"[Error]: Wrong TestInformation section format:[{group}] in setting.ini")
                return

            location = group_parts[1]
            laboratory = group_parts[2]
            tester_location = self.comboBox_TesterLocation.currentText().replace(" ", "")

            if (laboratory in tester_location) and (location in tester_location):
                self.test_information = group
                break

        if not self.test_information:
            self.checker_table.set_error(
                "Can't find matched TestInformation section in setting.ini")
            self.statusBar_BatteryAnalysis.showMessage(
                "[Error]: Can't find matched TestInformation section in setting.ini")
            return

        def set_item(item_data, row: int, col: int) -> None:
            item_text = ", ".join(item_data) if item_data else ""
            qt_item = QW.QTableWidgetItem(item_text)
            self.tableWidget_TestInformation.setItem(row, col, qt_item)

        set_item(self.get_config(
            f"{self.test_information}/TestEquipment"), 0, 2)
        set_item(self.get_config(
            f"{self.test_information}/SoftwareVersions.BTSServerVersion"), 1, 2)
        set_item(self.get_config(
            f"{self.test_information}/SoftwareVersions.BTSClientVersion"), 2, 2)
        set_item(self.get_config(
            f"{self.test_information}/SoftwareVersions.BTSDAVersion"), 3, 2)
        set_item(self.get_config(
            f"{self.test_information}/MiddleMachines.Model"), 4, 2)
        set_item(self.get_config(
            f"{self.test_information}/MiddleMachines.HardwareVersion"), 5, 2)
        set_item(self.get_config(
            f"{self.test_information}/MiddleMachines.SerialNumber"), 6, 2)
        set_item(self.get_config(
            f"{self.test_information}/MiddleMachines.FirmwareVersion"), 7, 2)
        set_item(self.get_config(
            f"{self.test_information}/MiddleMachines.DeviceType"), 8, 2)
        set_item(self.get_config(
            f"{self.test_information}/TestUnits.Model"), 9, 2)
        set_item(self.get_config(
            f"{self.test_information}/TestUnits.HardwareVersion"), 10, 2)
        set_item(self.get_config(
            f"{self.test_information}/TestUnits.FirmwareVersion"), 11, 2)

        # 移除根据TesterLocation自动设置ReportedBy的逻辑
        # 现在ReportedBy直接使用comboBox_ReportedBy的值

    def on_temperature_type_changed(self, index):
        """处理温度类型变化事件，控制spinBox_Temperature的启用状态"""
        # 获取当前选中的温度类型
        temperature_type = self.comboBox_Temperature.currentText()
        
        # 根据温度类型决定是否启用spinBox_Temperature
        if temperature_type == "Freezer Temperature":
            self.spinBox_Temperature.setEnabled(True)
        else:  # Room Temperature
            self.spinBox_Temperature.setEnabled(False)
        
        # 移除对lineEdit_Temperature的引用，不再更新它
    
    def _detect_temperature_type_from_xml(self, xml_path: str) -> None:
        """
        根据XML文件名自动检测温度类型
        
        规则：
        - 文件名中包含"Freezer"（不区分大小写），表示冷冻温度
        - 否则表示常温
        
        Args:
            xml_path: XML文件的完整路径
        """
        try:
            # 使用temperature_utils模块检测温度类型
            temperature_type = temperature_utils.detect_temperature_type_from_xml(xml_path)
            
            # 获取文件名用于日志
            file_name = os.path.basename(xml_path)
            
            # 设置温度类型和UI状态
            self.comboBox_Temperature.setCurrentText(temperature_type)
            self.spinBox_Temperature.setEnabled(temperature_type == "Freezer Temperature")
            
            if temperature_type == "Freezer Temperature":
                self.logger.info("检测到冷冻温度测试配置文件: %s", file_name)
            else:
                self.logger.info("检测到常温测试配置文件: %s", file_name)
                
        except (AttributeError, ValueError) as e:
            self.logger.warning("检测温度类型时发生错误: %s", e)
    
    def get_xlsxinfo(self) -> None:
        '''
        获取Excel文件信息，委托给优化的DataProcessor处理
        '''
        # 调用优化版的data_processor获取Excel信息
        self.data_processor.get_xlsxinfo()
    def get_version(self) -> None:
        """计算并设置电池分析的版本号，委托给VersionManager"""
        from battery_analysis.main.business_logic.version_manager import VersionManager
        version_manager = VersionManager(self)
        version_manager.get_version()
        return
        strInPutDir = self.lineEdit_InputPath.text()
        strOutoutDir = self.lineEdit_OutputPath.text()
        if os.path.exists(strInPutDir) and os.path.exists(strOutoutDir):
            listAllInXlsx = [strInPutDir + f"/{f}" for f in os.listdir(
                strInPutDir) if f[:2] != "~$" and f[-5:] == ".xlsx"]
            if not listAllInXlsx:
                self.lineEdit_Version.setText("")
                return
            strCsvMd5Path = strOutoutDir + "/MD5.csv"
            # 使用FileUtils.calc_md5checksum替换calc_md5checksum
            from battery_analysis.main.utils.file_utils import FileUtils
            self.md5_checksum = FileUtils.calc_md5checksum(listAllInXlsx)
            if os.path.exists(strCsvMd5Path) and os.path.getsize(strCsvMd5Path) != 0:
                listMD5Reader = []
                f = open(strCsvMd5Path, mode='r', encoding='utf-8')
                csvMD5Reader = csv.reader(f)
                for row in csvMD5Reader:
                    listMD5Reader.append(row)
                f.close()
                # 确保列表长度足够，正确访问CSV行数据
                if len(listMD5Reader) >= 4:
                    listChecksum = listMD5Reader[1] if len(listMD5Reader) > 1 else []
                    listTimes = listMD5Reader[3] if len(listMD5Reader) > 3 else []
                else:
                    listChecksum = []
                    listTimes = []

                os.remove(strCsvMd5Path)
                f = open(strCsvMd5Path, mode='w', newline='', encoding='utf-8')
                csvMD5Writer = csv.writer(f)

                if not listChecksum:
                    csvMD5Writer.writerow(["Checksums:"])
                    csvMD5Writer.writerow([self.md5_checksum])
                    csvMD5Writer.writerow(["Times:"])
                    csvMD5Writer.writerow(["0"])
                    self.lineEdit_Version.setText("1.0")
                else:
                    intVersionMajor = 1
                    intVersionMinor = 0
                    for c in range(len(listChecksum)):
                        if self.md5_checksum == listChecksum[c]:
                            intVersionMajor = c + 1
                            intVersionMinor = int(listTimes[c])
                            # increase it after executing the whole program
                            break
                        if c == len(listChecksum) - 1:
                            intVersionMajor = c + 2
                            listChecksum.append(self.md5_checksum)
                            listTimes.append("0")
                    csvMD5Writer.writerow(["Checksums:"])
                    csvMD5Writer.writerow(listChecksum)
                    csvMD5Writer.writerow(["Times:"])
                    csvMD5Writer.writerow(listTimes)
                    self.lineEdit_Version.setText(
                        f"{intVersionMajor}.{intVersionMinor}")
                f.close()
            else:
                f = open(strCsvMd5Path, mode='w', newline='', encoding='utf-8')
                csvMD5Writer = csv.writer(f)
                csvMD5Writer.writerow(["Checksums:"])
                csvMD5Writer.writerow([self.md5_checksum])
                csvMD5Writer.writerow(["Times:"])
                csvMD5Writer.writerow(["0"])
                f.close()
                self.lineEdit_Version.setText("1.0")
            # 使用文件服务设置文件隐藏属性
            file_service = self._get_service("file")
            if file_service:
                file_service.hide_file(strCsvMd5Path)
            else:
                # 降级到直接调用
                try:
                    import win32api
                    import win32con
                    win32api.SetFileAttributes(strCsvMd5Path, win32con.FILE_ATTRIBUTE_HIDDEN)
                except ImportError:
                    self.logger.warning("文件服务不可用，无法设置文件隐藏属性")
        else:
            self.lineEdit_Version.setText("")

    def select_testprofile(self) -> None:
        selected_file, _ = QW.QFileDialog.getOpenFileName(
            self, "Select Test Profile", self.current_directory, "XML Files(*.xml)")
        
        if selected_file and selected_file.strip():
            try:
                # 验证文件是否存在
                if not os.path.exists(selected_file):
                    QW.QMessageBox.warning(
                        self,
                        "文件错误",
                        f"选择的文件不存在:\n{selected_file}",
                        QW.QMessageBox.StandardButton.Ok
                    )
                    return
                
                # 验证文件扩展名
                if not selected_file.lower().endswith('.xml'):
                    QW.QMessageBox.warning(
                        self,
                        "文件格式错误",
                        "请选择XML格式的Test Profile文件",
                        QW.QMessageBox.StandardButton.Ok
                    )
                    return
                
                # 显示选中的文件路径
                self.lineEdit_TestProfile.setText(selected_file)
                
                # 获取Test Profile的目录
                test_profile_dir = os.path.dirname(selected_file)
                
                # 验证目录是否有效
                if not test_profile_dir or not os.path.exists(test_profile_dir):
                    self.logger.error("无效的Test Profile目录: %s", test_profile_dir)
                    return
                
                # 获取父目录（项目根目录）
                parent_dir = os.path.dirname(test_profile_dir)
                
                # 验证父目录是否存在
                if not parent_dir or not os.path.exists(parent_dir):
                    self.logger.error("无效的父目录: %s", parent_dir)
                    return
                
                # 自动设置input path为同级的2_xlsx文件夹
                input_path = os.path.join(parent_dir, "2_xlsx")
                if os.path.exists(input_path) and os.path.isdir(input_path):
                    self.lineEdit_InputPath.setText(input_path)
                    self.sigSetVersion.emit()
                    self.logger.info("自动设置输入路径: %s", input_path)
                else:
                    self.logger.info("未找到输入目录: %s", input_path)
                
                # 自动设置output path为同级的3_analysis results文件夹
                output_path = os.path.join(parent_dir, "3_analysis results")
                if os.path.exists(output_path) and os.path.isdir(output_path):
                    self.lineEdit_OutputPath.setText(output_path)
                else:
                    # 如果输出目录不存在，询问用户是否创建
                    reply = QW.QMessageBox.question(
                        self,
                        "创建输出目录",
                        f"输出目录不存在，是否创建？\n\n路径: {output_path}",
                        QW.QMessageBox.StandardButton.Yes | QW.QMessageBox.StandardButton.No,
                        QW.QMessageBox.StandardButton.Yes
                    )
                    
                    if reply == QW.QMessageBox.StandardButton.Yes:
                        try:
                            os.makedirs(output_path, exist_ok=True)
                            self.lineEdit_OutputPath.setText(output_path)
                            self.logger.info("创建并设置输出目录: %s", output_path)
                        except (OSError, PermissionError, FileNotFoundError) as e:
                            self.logger.error("创建输出目录失败: %s", e)
                            QW.QMessageBox.critical(
                                self,
                                "创建失败",
                                f"无法创建输出目录:\n{str(e)}",
                                QW.QMessageBox.StandardButton.Ok
                            )
                            return
                    else:
                        # 用户选择不创建，手动设置路径但不创建目录
                        self.lineEdit_OutputPath.setText(output_path)
                        self.logger.info("手动设置输出目录（未创建）: %s", output_path)
                
                self.sigSetVersion.emit()
                
                # 更新current_directory为项目根目录
                self.current_directory = parent_dir
                self.logger.info("设置当前目录为项目根目录: %s", parent_dir)
                
                # 根据XML文件名自动检测温度类型
                self._detect_temperature_type_from_xml(selected_file)
                
            except (OSError, ValueError, TypeError, RuntimeError, FileNotFoundError, PermissionError) as e:
                self.logger.error("选择Test Profilewhen发生错误: %s", e)
                QW.QMessageBox.critical(
                    self,
                    "错误",
                    f"处理Test Profilewhen发生错误:\n{str(e)}",
                    QW.QMessageBox.StandardButton.Ok
                )

    def select_inputpath(self) -> None:
        self.current_directory = QW.QFileDialog.getExistingDirectory(
            self, "Select Input Path", self.current_directory)
        if self.current_directory != "":
            self.lineEdit_InputPath.setText(self.current_directory)
            self.sigSetVersion.emit()
            self.current_directory = self.current_directory + "/../../"

    def select_outputpath(self) -> None:
        self.current_directory = QW.QFileDialog.getExistingDirectory(
            self, "Select Output Path", self.current_directory)
        if self.current_directory != "":
            self.lineEdit_OutputPath.setText(self.current_directory)
            self.sigSetVersion.emit()
            self.current_directory = self.current_directory + "/../"

    def run(self) -> None:
        # 保存表格数据
        self.save_table()
        self.init_widgetcolor()
        # 线程管理已转移到控制器，此方法保留以保持向后兼容性
        # 不再需要init_thread()
        
        # 检查输入是否完整，包括reportedby
        if not self.checkinput():
            # 检查失败，获取警告信息
            warning_info = []
            if not self.comboBox_ReportedBy.currentText():
                warning_info.append("Reported By")
            
            # 构建警告信息
            if warning_info:
                warning_str = "请完成以下必填项：" + ", ".join(warning_info)
                QW.QMessageBox.warning(self, "输入验证失败", warning_str)
            else:
                QW.QMessageBox.warning(self, "输入验证失败", "请检查所有必填项")
            
            self.pushButton_Run.setEnabled(True)
            return

        # 准备测试信息
        """ test_info
        index 0: Battery Type
        index 1: Construction Method
        index 2: Specification_Type
        index 3: Specification_Method
        index 4: Manufacturer
        index 5: Batch/Date Code
        index 6: Sample Qty
        index 7: Temperature
        index 8: Datasheet Nominal Capacity
        index 9: Calculation Nominal Capacity
        index 10: Accelerated Aging
        index 11: Tester Location
        index 12: Test By
        index 13: Test Profile
        index 14: Pulse Current List
        index 15: Cut-off Voltage List
        index 16: Report word version
        index 17: Required Useable Capacity
        """
        # 构建温度值字符串，根据选择的类型包含spinBox值和℃单位
        temperature_type = self.comboBox_Temperature.currentText()
        if temperature_type == "Freezer Temperature":
            temperature_value = f"{temperature_type}:{self.spinBox_Temperature.value()}"
        else:
            temperature_value = temperature_type
        
        test_info = [
            self.comboBox_BatteryType.currentText(),
            self.comboBox_ConstructionMethod.currentText(),
            self.comboBox_Specification_Type.currentText(),
            self.comboBox_Specification_Method.currentText(),
            self.comboBox_Manufacturer.currentText(),
            self.lineEdit_BatchDateCode.text(),
            self.lineEdit_SamplesQty.text(),
            temperature_value,  # 使用构建的温度值
            self.lineEdit_DatasheetNominalCapacity.text(),
            self.lineEdit_CalculationNominalCapacity.text(),
            str(self.spinBox_AcceleratedAging.value()),
            self.comboBox_TesterLocation.currentText(),
            self.comboBox_TestedBy.currentText(),
            self.lineEdit_TestProfile.text(),
            self.listCurrentLevel,
            self.listVoltageLevel,
            self.lineEdit_Version.text(),
            self.lineEdit_RequiredUseableCapacity.text(),
            # 直接使用comboBox_ReportedBy的值，不再从表格获取
            self.comboBox_ReportedBy.currentText()
        ]
        # 简化验证，只验证必要的路径
        if not self.lineEdit_InputPath.text():
            QW.QMessageBox.critical(self, _("validation_failed", "输入验证失败"), _("input_path_empty", "输入数据路径不能为空"))
            self.pushButton_Run.setEnabled(True)
            return

        if not self.lineEdit_OutputPath.text():
            QW.QMessageBox.critical(self, _("validation_failed", "输入验证失败"), _("output_path_empty", "输出路径不能为空"))
            self.pushButton_Run.setEnabled(True)
            return

        # 检查冷冻温度是否设置为0，如果是则提示用户
        temperature_type = self.comboBox_Temperature.currentText()
        if temperature_type == "Freezer Temperature" and self.spinBox_Temperature.value() == 0:
            reply = QW.QMessageBox.question(
                self,
                "温度确认",
                "当前冷冻温度设置为0°C，是否继续运行？",
                QW.QMessageBox.StandardButton.Yes | QW.QMessageBox.StandardButton.No,
                QW.QMessageBox.StandardButton.No
            )
            if reply == QW.QMessageBox.StandardButton.No:
                self.pushButton_Run.setEnabled(True)
                return
        
        # 更新控制器的上下文和测试信息
        success = False
        main_controller = self._get_controller("main_controller")
        if main_controller:
            main_controller.set_project_context(
                project_path=self.path,
                input_path=self.lineEdit_InputPath.text(),
                output_path=self.lineEdit_OutputPath.text()
            )
            main_controller.set_test_info(test_info)

            # 更新配置
            self.update_config(test_info)
            self.md5_checksum_run = self.md5_checksum
            self.statusBar_BatteryAnalysis.showMessage("status:ok")

            # 启动分析
            success = main_controller.start_analysis()
        if not success:
            self.pushButton_Run.setEnabled(True)
            QW.QMessageBox.warning(self, _("start_failed", "启动失败"), _("cannot_start_analysis", "无法启动分析任务"))

    def save_table(self) -> None:
        # set focus on pushButton_Run for saving the input text
        self.pushButton_Run.setFocus()

        def set_item(config_key: str, row: int, col: int):
            item = self.tableWidget_TestInformation.item(row, col)
            if item is None:
                self.config.setValue(f"{config_key}", "")
                return
            list_item_text = item.text().split(",")
            for i in range(len(list_item_text)):
                list_item_text[i] = list_item_text[i].strip()
            if len(list_item_text) == 1:
                self.config.setValue(f"{config_key}", list_item_text[0])
            else:
                self.config.setValue(f"{config_key}", list_item_text)

        if self.test_information != "":
            set_item(f"{self.test_information}/TestEquipment", 0, 2)
            set_item(
                f"{self.test_information}/SoftwareVersions.BTSServerVersion", 1, 2)
            set_item(
                f"{self.test_information}/SoftwareVersions.BTSClientVersion", 2, 2)
            set_item(
                f"{self.test_information}/SoftwareVersions.BTSDAVersion", 3, 2)
            set_item(f"{self.test_information}/middleMachines.Model", 4, 2)
            set_item(
                f"{self.test_information}/middleMachines.HardwareVersion", 5, 2)
            set_item(
                f"{self.test_information}/middleMachines.SerialNumber", 6, 2)
            set_item(
                f"{self.test_information}/middleMachines.FirmwareVersion", 7, 2)
            set_item(f"{self.test_information}/middleMachines.DeviceType", 8, 2)
            set_item(f"{self.test_information}/TestUnits.Model", 9, 2)
            set_item(
                f"{self.test_information}/TestUnits.HardwareVersion", 10, 2)
            set_item(
                f"{self.test_information}/TestUnits.FirmwareVersion", 11, 2)

        set_item("TestInformation/TestEquipment", 0, 2)
        set_item("TestInformation/SoftwareVersions.BTSServerVersion", 1, 2)
        set_item("TestInformation/SoftwareVersions.BTSClientVersion", 2, 2)
        set_item("TestInformation/SoftwareVersions.BTSDAVersion", 3, 2)
        set_item("TestInformation/middleMachines.Model", 4, 2)
        set_item("TestInformation/middleMachines.HardwareVersion", 5, 2)
        set_item("TestInformation/middleMachines.SerialNumber", 6, 2)
        set_item("TestInformation/middleMachines.FirmwareVersion", 7, 2)
        set_item("TestInformation/middleMachines.DeviceType", 8, 2)
        set_item("TestInformation/TestUnits.Model", 9, 2)
        set_item("TestInformation/TestUnits.HardwareVersion", 10, 2)
        set_item("TestInformation/TestUnits.FirmwareVersion", 11, 2)

    def init_widgetcolor(self) -> None:
        # 清除所有标签的背景样式
        # 具体样式由checkinput方法根据验证结果设置
        self.label_BatteryType.setStyleSheet("")
        self.label_ConstructionMethod.setStyleSheet("")
        self.label_Specification.setStyleSheet("")
        self.label_Manufacturer.setStyleSheet("")
        self.label_BatchDateCode.setStyleSheet("")
        self.label_SamplesQty.setStyleSheet("")
        self.label_Temperature.setStyleSheet("")
        self.label_DatasheetNominalCapacity.setStyleSheet("")
        self.label_CalculationNominalCapacity.setStyleSheet("")
        self.label_AcceleratedAging.setStyleSheet("")
        self.label_RequiredUseableCapacity.setStyleSheet("")
        self.label_TesterLocation.setStyleSheet("")
        self.label_TestedBy.setStyleSheet("")
        self.label_TestProfile.setStyleSheet("")
        self.label_InputPath.setStyleSheet("")
        self.label_OutputPath.setStyleSheet("")
        self.label_Version.setStyleSheet("")
        self.pushButton_Run.setStyleSheet("")

    def checkinput(self) -> bool:
        """检查所有输入是否完整有效，委托给ValidationManager"""
        from battery_analysis.main.business_logic.validation_manager import ValidationManager
        validation_manager = ValidationManager(self)
        return validation_manager.checkinput()
        check_pass_flag = True
        warning_info = ["Unknown: "]
        if not self.comboBox_BatteryType.currentText():
            check_pass_flag = False
            warning_info.append("Battery Type")
            self.label_BatteryType.setStyleSheet("background-color:red")
        if self.comboBox_BatteryType.currentText() == "Pouch Cell":
            if not self.comboBox_ConstructionMethod.currentText():
                check_pass_flag = False
                warning_info.append("Construction Method")
                self.label_ConstructionMethod.setStyleSheet(
                    "background-color:red")
        if (not self.comboBox_Specification_Type.currentText()
                or not self.comboBox_Specification_Method.currentText()):
            check_pass_flag = False
            warning_info.append("Specification")
            self.label_Specification.setStyleSheet("background-color:red")
        if not self.comboBox_Manufacturer.currentText():
            check_pass_flag = False
            warning_info.append("Manufacturer")
            self.label_Manufacturer.setStyleSheet("background-color:red")
        if not self.lineEdit_BatchDateCode.text():
            check_pass_flag = False
            warning_info.append("Batch/Date Code")
            self.label_BatchDateCode.setStyleSheet("background-color:red")
        if not self.lineEdit_SamplesQty.text():
            check_pass_flag = False
            warning_info.append("SamplesQty")
            self.label_SamplesQty.setStyleSheet("background-color:red")
        if not self.comboBox_Temperature.currentText():
            check_pass_flag = False
            warning_info.append("Temperature")
            self.label_Temperature.setStyleSheet("background-color:red")
        if not self.lineEdit_DatasheetNominalCapacity.text():
            check_pass_flag = False
            warning_info.append("Datasheet Nominal Capacity")
            self.label_DatasheetNominalCapacity.setStyleSheet(
                "background-color:red")
        if not self.lineEdit_CalculationNominalCapacity.text():
            check_pass_flag = False
            warning_info.append("Calculation Nominal Capacity")
            self.label_CalculationNominalCapacity.setStyleSheet(
                "background-color:red")
        # QSpinBox总是有一个值（0-10），所以不需要检查是否empty
        # 但我们仍然可以检查值是否在有效范围内（虽然控件已经限制了）
        aging_value = self.spinBox_AcceleratedAging.value()
        if aging_value < 0 or aging_value > 10:
            check_pass_flag = False
            warning_info.append("Accelerated Aging")
            self.label_AcceleratedAging.setStyleSheet("background-color:red")
        if not self.lineEdit_RequiredUseableCapacity.text():
            check_pass_flag = False
            warning_info.append("Required Useable Capacity")
            self.label_RequiredUseableCapacity.setStyleSheet(
                "background-color:red")
        if not self.comboBox_TesterLocation.currentText():
            check_pass_flag = False
            warning_info.append("Test Location")
            self.label_TesterLocation.setStyleSheet("background-color:red")
        if not self.comboBox_TestedBy.currentText():
            check_pass_flag = False
            warning_info.append("Test By")
            self.label_TestedBy.setStyleSheet("background-color:red")
        if not self.comboBox_ReportedBy.currentText():
            check_pass_flag = False
            warning_info.append("Reported By")
            # 注意：Reported By没有对应的label，所以不需要设置样式
        if not self.lineEdit_TestProfile.text():
            check_pass_flag = False
            warning_info.append("Test Profile")
            self.label_TestProfile.setStyleSheet("background-color:red")
        if not self.lineEdit_InputPath.text():
            check_pass_flag = False
            warning_info.append("Input Path")
            self.label_InputPath.setStyleSheet("background-color:red")
        if not self.lineEdit_OutputPath.text():
            check_pass_flag = False
            warning_info.append("Output Path")
            self.label_OutputPath.setStyleSheet("background-color:red")
        if not self.lineEdit_Version.text():
            check_pass_flag = False
            warning_info.append("Version")
            self.label_Version.setStyleSheet("background-color:red")
        # check_pass_flag = True
        if check_pass_flag:
            self.pushButton_Run.setEnabled(False)
            self.pushButton_Run.setFocus()
        else:
            warning_info_str = warning_info[0]
            for i in range(1, len(warning_info) - 1):
                warning_info_str = warning_info_str + warning_info[i] + ", "
            warning_info_str += warning_info[-1]
            # print(warning_info_str)
            self.statusBar_BatteryAnalysis.showMessage(warning_info_str)
            self.pushButton_Run.setText("Rerun")
            self.pushButton_Run.setFocus()
        return check_pass_flag

    def _open_report(self):
        """打开生成的docx格式报告"""
        output_path_str = self.lineEdit_OutputPath.text()
        version = self.lineEdit_Version.text()
        
        try:
            from pathlib import Path
            output_path = Path(output_path_str)
            
            if not output_path.exists() or not output_path.is_dir():
                QW.QMessageBox.warning(self, "警告", f"无效的输出路径: {output_path}")
                return
            
            # 搜索docx文件
            docx_files = list(output_path.rglob("*.docx"))
            
            if not docx_files:
                QW.QMessageBox.information(self, "信息", f"未找到docx报告文件\n搜索路径: {output_path}")
                return
            
            # 找到与当前版本匹配的报告
            target_docx = None
            for docx_file in docx_files:
                if f"_V{version}" in docx_file.name:
                    target_docx = docx_file
                    break
            
            # 如果没有匹配版本，使用最新的报告
            if not target_docx and docx_files:
                target_docx = sorted(docx_files, key=lambda f: f.stat().st_mtime, reverse=True)[0]
            
            # 打开报告
            if target_docx:
                target_path = str(target_docx)
                try:
                    os.startfile(target_path)
                except Exception as popen_error:
                    logging.error("打开报告失败: %s", popen_error)
                    QW.QMessageBox.critical(self, "错误", f"打开报告失败: {str(popen_error)}")
        except Exception as e:
            QW.QMessageBox.critical(self, "错误", f"打开报告失败: {str(e)}")
            self.logger.error("打开报告失败: %s", e)
            
    def _open_report_path(self):
        """打开报告所在的文件夹"""
        output_path_str = self.lineEdit_OutputPath.text()
        
        try:
            from pathlib import Path
            output_path = Path(output_path_str)
            
            if not output_path.exists() or not output_path.is_dir():
                QW.QMessageBox.warning(self, "警告", f"无效的输出路径: {output_path}")
                return
            
            # 直接打开输出路径，因为报告已经存储在这里
            try:
                os.startfile(str(output_path))
            except Exception as popen_error:
                logging.error("打开报告文件夹失败: %s", popen_error)
                QW.QMessageBox.critical(self, "错误", f"打开文件夹失败: {str(popen_error)}")
        except Exception as e:
            QW.QMessageBox.critical(self, "错误", f"打开文件夹失败: {str(e)}")
            self.logger.error("打开报告文件夹失败: %s", e)

    def set_version(self) -> None:
        """更新版本号，增加次要版本号，委托给VersionManager"""
        from battery_analysis.main.business_logic.version_manager import VersionManager
        version_manager = VersionManager(self)
        version_manager.set_version()
        return
        # 初始化必要的属性如果不存在
        if not hasattr(self, 'md5_checksum_run'):
            self.md5_checksum_run = self.md5_checksum if hasattr(
                self, 'md5_checksum') else ''

        list_md5_reader = []
        output_path_str = self.lineEdit_OutputPath.text()

        try:
            # 使用Path对象进行路径处理
            output_path = Path(output_path_str)
            md5_file = output_path / "MD5.csv"

            # 检查路径是否有效
            if not output_path_str or not output_path.is_dir():
                self.statusBar_BatteryAnalysis.showMessage(
                    f"[Warning]: Invalid output path: {output_path_str}")
                return

            # 读取MD5文件
            if md5_file.exists():
                try:
                    with md5_file.open(mode='r', encoding='utf-8') as f:
                        csv_md5_reader = csv.reader(f)
                        for row in csv_md5_reader:
                            list_md5_reader.append(row)
                except PermissionError:
                    self.statusBar_BatteryAnalysis.showMessage(
                        f"[Warning]: Permission denied reading {md5_file}")
                    return
                except (IOError, UnicodeDecodeError, csv.Error, OSError) as read_error:
                    self.statusBar_BatteryAnalysis.showMessage(
                        f"[Warning]: Failed to read MD5 file: {str(read_error)}")
                    return

            # 处理文件内容
            if len(list_md5_reader) >= 4:
                try:
                    # 正确处理CSV数据：每一行是一个列表，我们需要访问特定行的数据
                    list_checksum = list_md5_reader[1] if len(list_md5_reader) > 1 else []
                    list_times = list_md5_reader[3] if len(list_md5_reader) > 3 else []

                    # 创建临when文件避免权限问题
                    temp_file = output_path / "MD5_temp.csv"
                    with temp_file.open(mode='w', newline='', encoding='utf-8') as f:
                        csv_md5_writer = csv.writer(f)
                        for c, checksum in enumerate(list_checksum):
                            if self.md5_checksum_run == checksum:
                                version_major = c + 1
                                version_minor = int(list_times[c]) + 1
                                list_times[c] = str(version_minor)
                                if self.md5_checksum_run == getattr(self, 'md5_checksum', ''):
                                    self.lineEdit_Version.setText(
                                        f"{version_major}.{version_minor}")
                                break

                        csv_md5_writer.writerow(["Checksums:"])
                        csv_md5_writer.writerow(list_checksum)
                        csv_md5_writer.writerow(["Times:"])
                        csv_md5_writer.writerow(list_times)

                    # 替换原文件
                    if md5_file.exists():
                        try:
                            md5_file.unlink()  # 删除原文件
                        except PermissionError:
                            self.statusBar_BatteryAnalysis.showMessage(
                                "[Warning]: Cannot remove existing MD5 file, using new location")
                            md5_file = temp_file  # 使用临when文件作为新的MD5文件
                            temp_file = None

                    if temp_file:
                        temp_file.replace(md5_file)  # 替换文件

                    # 尝试设置隐藏属性，但不抛出异常
                    file_service = self._get_service("file")
                    if file_service:
                        success, error_msg = file_service.hide_file(str(md5_file))
                        if not success:
                            self.logger.warning("无法设置MD5文件隐藏属性: %s", error_msg)
                    else:
                        # 降级到直接调用
                        try:
                            import win32api
                            import win32con
                            win32api.SetFileAttributes(str(md5_file), win32con.FILE_ATTRIBUTE_HIDDEN)
                        except (ImportError, AttributeError, OSError) as e:
                            # 忽略设置隐藏属性失败的错误
                            self.logger.debug("无法设置MD5文件隐藏属性（直接调用）: %s", e)
                except PermissionError:
                    self.statusBar_BatteryAnalysis.showMessage(
                        f"[Warning]: Permission denied writing to {output_path}")
                except (IOError, UnicodeEncodeError, csv.Error, OSError, PermissionError) as write_error:
                    self.statusBar_BatteryAnalysis.showMessage(
                        f"[Warning]: Failed to write MD5 file: {str(write_error)}")
            else:
                # 如果文件不存在or格式不correct，创建新文件
                try:
                    with md5_file.open(mode='w', newline='', encoding='utf-8') as f:
                        csv_md5_writer = csv.writer(f)
                        csv_md5_writer.writerow(["Checksums:"])
                        csv_md5_writer.writerow(
                            [self.md5_checksum_run if self.md5_checksum_run else ""])
                        csv_md5_writer.writerow(["Times:"])
                        csv_md5_writer.writerow(["1"])

                    try:
                        win32api.SetFileAttributes(
                            str(md5_file), win32con.FILE_ATTRIBUTE_HIDDEN)
                    except (AttributeError, OSError, ImportError) as e:
                        self.logger.debug("无法设置MD5文件隐藏属性: %s", e)
                except PermissionError:
                    self.statusBar_BatteryAnalysis.showMessage(
                        f"[Warning]: Cannot create MD5 file in {output_path}")
                except (IOError, UnicodeEncodeError, csv.Error, OSError, PermissionError) as create_error:
                    self.statusBar_BatteryAnalysis.showMessage(
                        f"[Warning]: Failed to create MD5 file: {str(create_error)}")

        except (IOError, UnicodeError, csv.Error, OSError, PermissionError, TypeError, ValueError) as e:
            # 捕获所有其他异常但不中断程序
            self.statusBar_BatteryAnalysis.showMessage(
                f"[Info]: Version tracking skipped: {str(e)}")

    def _show_analysis_complete_dialog(self):
        """
        显示分析完成对话框，包含"打开报告"、"打开路径"和"确定"按钮
        """
        dialog = QW.QDialog(self)
        dialog.setWindowTitle("分析完成")
        dialog.setFixedSize(450, 150)
        dialog.setWindowFlags(QC.Qt.WindowType.Window | QC.Qt.WindowType.WindowTitleHint |
                             QC.Qt.WindowType.WindowCloseButtonHint)
        
        layout = QW.QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 添加状态文本标签
        status_label = QW.QLabel("电池分析已完成！")
        status_label.setAlignment(QC.Qt.AlignmentFlag.AlignCenter)
        status_label.setWordWrap(True)
        layout.addWidget(status_label)
        
        # 添加底部按钮布局
        button_layout = QW.QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setAlignment(QC.Qt.AlignmentFlag.AlignCenter)
        
        # 添加打开报告按钮
        open_report_button = QW.QPushButton("打开报告")
        open_report_button.setMinimumHeight(32)
        open_report_button.setMinimumWidth(120)
        open_report_button.clicked.connect(lambda: self._open_report(dialog))
        button_layout.addWidget(open_report_button)
        
        # 添加打开路径按钮
        open_path_button = QW.QPushButton("打开路径")
        open_path_button.setMinimumHeight(32)
        open_path_button.setMinimumWidth(120)
        open_path_button.clicked.connect(lambda: self._open_report_path(dialog))
        button_layout.addWidget(open_path_button)
        
        # 添加确定按钮
        ok_button = QW.QPushButton("确定")
        ok_button.setMinimumHeight(32)
        ok_button.setMinimumWidth(120)
        ok_button.clicked.connect(dialog.accept)
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        dialog.exec()
        
    def rename_pltPath(self, strTestDate):
        self.config.setValue(
            "PltConfig/Path", f"{self.lineEdit_OutputPath.text()}/"
            f"{strTestDate}_V{self.lineEdit_Version.text()}")

    def update_config(self, test_info) -> None:
        # 初始化checker_update_config如果不存在
        if not hasattr(self, 'checker_update_config'):
            self.checker_update_config = Checker()
        self.checker_update_config.clear()
        self.config.setValue(
            "PltConfig/Path", f"{self.lineEdit_OutputPath.text()}/V{test_info[16]}")

        bSetTitle = False
        rules = self.get_config("BatteryConfig/Rules")
        specification_type = self.comboBox_Specification_Type.currentText()
        strPulseCurrent = "".join(
            [f"{current_level}mA/" for current_level in self.listCurrentLevel])
        for rule in rules:
            rule_parts = rule.split("/")
            if not self.cc_current:
                self.cc_current = rule_parts[5]
            if rule_parts[0] == specification_type:
                self.config.setValue(
                    "PltConfig/Title",
                    f"{test_info[4]} {test_info[2]} {test_info[3]}({test_info[5]}), "
                    f"-{test_info[8]}mAh@{self.cc_current}mA, "
                    f"{strPulseCurrent[:-1]}, {test_info[7]}")
                bSetTitle = True
                break
            if rule_parts[0] in specification_type:
                self.config.setValue(
                    "PltConfig/Title",
                    f"{test_info[4]} {test_info[2]} {test_info[3]}({test_info[5]}), "
                    f"-{test_info[8]}mAh@{self.cc_current}mA, "
                    f"{strPulseCurrent[:-1]}, {test_info[7]}")
                bSetTitle = True
        if not bSetTitle:
            self.checker_update_config.set_error("PltTitle")
            self.statusBar_BatteryAnalysis.showMessage(
                f"[Error]: No rules for {specification_type}")

    def resizeEvent(self, event):
        """窗口大小改变时的事件处理函数"""
        super().resizeEvent(event)
        if hasattr(self, 'tableWidget_TestInformation'):
            self.tableWidget_TestInformation.resizeColumnsToContents()


def main() -> None:
    # 解决PyInstaller打包后multiprocessing导致的递归启动问题
    multiprocessing.freeze_support()
    # 优化PyQt6的警告处理
    warnings.filterwarnings("ignore", message=".*sipPyTypeDict.*")

    # 优化matplotlib配置，避免font cache构建警告
    # 使用QtAgg后端，自动检测Qt绑定（兼容PyQt6）
    matplotlib.use('QtAgg')
    matplotlib.rcParams['font.family'] = 'sans-serif'
    matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial',
                                              'DejaVu Sans', 'Liberation Sans', 'Times New Roman']
    matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

    app = QW.QApplication(sys.argv)
    # 设置应用程序样式为Fusion，确保在不同Windows版本上表现一致
    app.setStyle(QW.QStyleFactory.create("Fusion"))
    window = Main()
    # 设置窗口最小尺寸为更小的值，确保在小分辨率屏幕上也能显示标题栏
    window.setMinimumSize(800, 600)  # 设置一个合理的最小尺寸
    window.show()

    # 获取屏幕可用区域
    screen_rect = app.primaryScreen().availableGeometry()

    # 确保窗口不会超出屏幕边界
    window_handle = window.windowHandle()
    if window_handle:
        # 如果窗口太大，调整为适合屏幕
        if window.width() > screen_rect.width() or window.height() > screen_rect.height():
            new_width = min(window.width(), int(screen_rect.width() * 0.9))
            new_height = min(window.height(), int(screen_rect.height() * 0.9))
            window.resize(new_width, new_height)

    sys.exit(app.exec())


if __name__ == '__main__':
    # 这确保在multiprocessing子进程中不会执行UI初始化代码
    # 防止在Windows和PyInstaller环境下的递归启动问题
    main()



