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
from battery_analysis.i18n.preferences_dialog import PreferencesDialog
from battery_analysis.main.factories.visualizer_factory import VisualizerFactory
from battery_analysis.main.interfaces.ivisualizer import IVisualizer
from battery_analysis.main.services.service_container import get_service_container
from battery_analysis.resources import resources_rc
from battery_analysis.ui import ui_main_window

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def calc_md5checksum(file_paths):
    md5_hash = hashlib.md5()
    for file_path in file_paths:
        with open(file_path, "rb") as file:
            data = file.read()
            md5_hash.update(data)
    return md5_hash.hexdigest()


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


class ProgressDialog(QW.QDialog):
    """
    弹出式进度条对话框类

    用于显示详细的进度信息，适合长when间运行的任务
    """
    
    # 信号定义
    canceled = QC.pyqtSignal()  # 取消信号

    def __init__(self, parent=None):
        """
        初始化弹出式进度条

        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        self.setWindowTitle(_("progress_title", "Battery Analysis Progress"))
        self.setModal(False)  # Non-modal window, allows user to operate main interface
        self.setFixedSize(450, 150)
        self.setWindowFlags(QC.Qt.WindowType.Window | QC.Qt.WindowType.WindowTitleHint |
                            QC.Qt.WindowType.WindowCloseButtonHint |
                            QC.Qt.WindowType.WindowStaysOnTopHint |
                            QC.Qt.WindowType.WindowMinimizeButtonHint)
        
        # 设置窗口样式
        self.setObjectName("progress_dialog")

        # 创建布局
        layout = QW.QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 添加状态文本标签
        self.status_label = QW.QLabel(_("progress_ready", "Ready to start analysis..."))
        self.status_label.setAlignment(QC.Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setObjectName("progress_status_label")
        layout.addWidget(self.status_label)

        # 添加进度条
        self.progress_bar = QW.QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setAlignment(QC.Qt.AlignmentFlag.AlignCenter)
        self.progress_bar.setObjectName("progress_bar")
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)
        
        # 添加底部按钮布局
        button_layout = QW.QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setAlignment(QC.Qt.AlignmentFlag.AlignCenter)
        
        # 添加取消按钮
        self.cancel_button = QW.QPushButton(_("cancel", "Cancel"))
        self.cancel_button.setObjectName("cancel_button")
        self.cancel_button.setMinimumHeight(32)
        self.cancel_button.setMinimumWidth(100)
        self.cancel_button.clicked.connect(self._on_cancel)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)

        # 设置布局
        self.setLayout(layout)
        
        # 取消标志
        self.is_canceled = False

    def update_progress(self, progress, status_text):
        """
        更新进度信息

        Args:
            progress: 进度值
            status_text: 状态文本
        """
        self.progress_bar.setValue(progress)
        self.status_label.setText(status_text)
        
        # 更新窗口标题，显示百分比
        self.setWindowTitle(f"{_('progress_title', 'Battery Analysis Progress')} - {progress}%")

        # 确保界面实when更新
        QW.QApplication.processEvents()

    def _on_cancel(self):
        """
        处理取消按钮点击事件
        """
        self.is_canceled = True
        self.canceled.emit()
        self.status_label.setText(_("progress_canceled", "Task canceled..."))
        QW.QApplication.processEvents()

    def closeEvent(self, event):
        """
        关闭事件处理

        Args:
            event: 关闭事件
        """
        # 这里可以添加关闭when的处理逻辑
        event.accept()


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
        
        # 初始化环境检测器
        self.env_detector = self._initialize_environment_detector()
        
        # 初始化语言管理器
        self.language_manager = None

        # 初始化可视化器工厂
        self.visualizer_factory = VisualizerFactory()
        self.current_visualizer = None

        # 进度条相关属性
        self.progress_dialog = None
        self.progress_start_time = None
        self.show_popup_progress = False
        self.task_duration_threshold = 30  # 任务when长阈值（秒），超过这个when间显示弹出式进度条

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
        try:
            environment_service = self._get_service("environment")
            if environment_service:
                if hasattr(environment_service, 'env_info'):
                    self.env_info = environment_service.env_info
                elif hasattr(environment_service, 'initialize'):
                    if environment_service.initialize():
                        if hasattr(environment_service, 'env_info'):
                            self.env_info = environment_service.env_info
        except (AttributeError, TypeError, ImportError, OSError) as e:
            self.logger.warning("Failed to initialize environment service: %s", e)
        
        # 确保环境信息包含必要的键
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
        
        # 环境适配处理
        self._handle_environment_adaptation()

        if sys.platform == "win32":
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("bt")

        # 改进的配置文件路径查找逻辑（使用配置服务）
        try:
            config_service = self._get_service("config")
            if config_service:
                config_path_result = config_service.find_config_file()
                self.config_path = str(config_path_result) if config_path_result else None
            else:
                # 降级到直接导入
                from battery_analysis.utils.config_utils import find_config_file
                self.config_path = find_config_file()
        except (AttributeError, TypeError, ImportError, OSError) as e:
            self.logger.warning("Failed to get config service: %s", e)
            # 降级到直接导入
            from battery_analysis.utils.config_utils import find_config_file
            self.config_path = find_config_file()

        project_root = Path(__file__).resolve().parent.parent.parent

        # 添加对None值的检查，避免TypeError
        if self.config_path is None or not Path(self.config_path).exists():
            self.b_has_config = False
            # 创建默认配置设置
            self.config = QC.QSettings()
        else:
            self.b_has_config = True
            self.config = QC.QSettings(
                self.config_path,
                QC.QSettings.Format.IniFormat
            )

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

        # 连接控制器信号
        self._connect_controllers()

        self.setupUi(self)
        
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
    
    def _initialize_environment_detector(self):
        """
        初始化环境检测器
        
        Returns:
            环境检测器实例或None
        """
        try:
            env_service = self._get_service("environment")
            if env_service:
                if hasattr(env_service, 'initialize'):
                    env_service.initialize()
                if hasattr(env_service, 'get_environment_detector'):
                    return env_service.get_environment_detector()
        except (AttributeError, TypeError, ImportError, OSError) as e:
            self.logger.warning("Failed to initialize environment service: %s", e)
        return None
    
    def _handle_environment_adaptation(self):
        """
        处理环境适配逻辑
        """
        env_type = self.env_info['environment_type']
        
        # 通过环境服务获取 EnvironmentType
        try:
            env_service = self._get_service("environment")
            if env_service and hasattr(env_service, 'EnvironmentType'):
                EnvironmentType = env_service.EnvironmentType
            else:
                # 降级到直接导入
                from battery_analysis.utils.environment_utils import EnvironmentType
        except (AttributeError, TypeError, ImportError) as e:
            self.logger.warning("Failed to get EnvironmentType: %s", e)
            from battery_analysis.utils.environment_utils import EnvironmentType
        
        # 根据环境类型进行适配
        if env_type == EnvironmentType.IDE:
            self.logger.debug("IDE环境：调整UI行为以适应开发环境")
            self._adapt_for_ide_environment()
        elif env_type == EnvironmentType.CONTAINER:
            self.logger.debug("容器环境：调整UI行为以适应容器环境")
            self._adapt_for_container_environment()
        elif env_type == EnvironmentType.PRODUCTION:
            self.logger.debug("生产环境：优化UI性能")
            self._adapt_for_production_environment()
        
        # GUI可用性检查
        if not self.env_info['gui_available']:
            self.logger.warning("GUI环境不可用，应用可能无法正常显示")
            self._handle_gui_unavailable()

    def _adapt_for_ide_environment(self):
        """
        IDE环境适配
        """
        # 在IDE中可能没有显示，添加调试信息
        self.logger.debug("在IDE环境中运行，某些功能可能受限")
        
        # 调整任务阈值，在IDE中通常任务较快
        self.task_duration_threshold = 15

    def _adapt_for_container_environment(self):
        """
        容器环境适配
        """
        self.logger.debug("在容器环境中运行，调整路径和资源管理")
        
        # 容器环境中的资源路径可能不同
        # 禁用某些容器中可能不支持的功能
        self.task_duration_threshold = 45

    def _adapt_for_production_environment(self):
        """
        生产环境适配
        """
        self.logger.debug("在生产环境中运行，优化性能和稳定性")
        
        # 生产环境中启用更多优化
        self.task_duration_threshold = 30

    def _handle_gui_unavailable(self):
        """
        处理GUI不可用的情况
        """
        self.logger.error("GUI环境不可用，尝试使用无头模式")
        # 在GUI不可用时，可以考虑切换到命令行模式
        # 或者显示错误信息并退出

    def get_config(self, config_key):
        # 获取配置值并处理为列表格式，移除所有DEBUG打印以避免UI卡死
        # 如果没有配置文件，直接返回空列表
        if not self.b_has_config:
            return []

        try:
            value = self.config.value(config_key)
            if isinstance(value, list):
                list_value = []
                for item in value:
                    if item != "":
                        list_value.append(item)
            elif isinstance(value, str):
                list_value = [value]
            else:
                list_value = []
            return list_value
        except (AttributeError, TypeError, ValueError, KeyError, OSError) as e:
            logging.error("读取配置 %s 失败: %s", config_key, e)
            return []

    def init_window(self) -> None:
        # 在窗口标题中显示应用程序名称和版本号（支持国际化）
        window_title_template = _("window_title")
        try:
            # 如果翻译包含{version}占位符，则进行格式化
            if "{version}" in window_title_template:
                window_title = window_title_template.format(version=self.version)
            else:
                window_title = window_title_template
        except (KeyError, ValueError):
            # 如果格式化失败，使用备用标题
            window_title = f"Battery Analyzer v{self.version}"
        self.setWindowTitle(window_title)
        
        # 使用环境检测器获取正确的图标路径
        icon = self._load_application_icon()

        self.setWindowIcon(icon)

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

    def _connect_controllers(self):
        """
        连接控制器信号和槽函数
        """
        # 连接主控制器信号到事件总线
        main_controller = self._get_controller("main_controller")
        if main_controller:
            if hasattr(main_controller, 'progress_updated'):
                main_controller.progress_updated.connect(self._on_progress_updated)
            if hasattr(main_controller, 'status_changed'):
                main_controller.status_changed.connect(self.get_threadinfo)
            if hasattr(main_controller, 'analysis_completed'):
                main_controller.analysis_completed.connect(self.set_version)
            if hasattr(main_controller, 'path_renamed'):
                main_controller.path_renamed.connect(self.rename_pltPath)
            if hasattr(main_controller, 'start_visualizer'):
                main_controller.start_visualizer.connect(self.run_visualizer)

        # 连接文件控制器信号
        file_controller = self._get_controller("file_controller")
        if file_controller:
            if hasattr(file_controller, 'config_loaded'):
                file_controller.config_loaded.connect(self._on_config_loaded)
            if hasattr(file_controller, 'error_occurred'):
                file_controller.error_occurred.connect(self._on_controller_error)

        # 连接验证控制器信号
        validation_controller = self._get_controller("validation_controller")
        if validation_controller:
            if hasattr(validation_controller, 'validation_error'):
                validation_controller.validation_error.connect(self._on_controller_error)

        # 连接事件总线事件
        event_bus = self._get_service("event_bus")
        if event_bus:
            # 订阅进度更新事件
            event_bus.subscribe("progress_updated", self._on_event_progress_updated)
            # 订阅状态变化事件
            event_bus.subscribe("status_changed", self._on_event_status_changed)
            # 订阅文件选择事件
            event_bus.subscribe("file_selected", self._on_file_selected)
            # 订阅配置变更事件
            event_bus.subscribe("config_changed", self._on_config_changed)

    def _on_progress_updated(self, progress, status_text):
        """
        进度更新处理

        Args:
            progress: 进度值
            status_text: 状态文本
        """
        # 更新嵌入式进度条
        if hasattr(self, 'progressBar'):
            self.progressBar.setValue(progress)
        # 更新状态栏信息
        if hasattr(self, 'statusBar_BatteryAnalysis'):
            self.statusBar_BatteryAnalysis.showMessage(f"状态: {status_text}")

        # 检查是否需要显示弹出式进度条
        if self.progress_start_time is not None:
            elapsed_time = time.time() - self.progress_start_time

            # 如果任务已经运行超过阈值且弹出式进度条尚未显示，则显示它
            if elapsed_time > self.task_duration_threshold and not self.show_popup_progress:
                self._show_progress_dialog()

        # 更新弹出式进度条（如果已显示）
        if self.show_popup_progress and self.progress_dialog:
            self.progress_dialog.update_progress(progress, status_text)

        # 如果任务完成，关闭弹出式进度条
        if progress >= 100:
            self._close_progress_dialog()

    def _on_event_progress_updated(self, progress: int, status: str):
        """
        事件总线进度更新处理

        Args:
            progress: 进度值
            status: 状态文本
        """
        # 使用进度服务更新进度
        progress_service = self._get_service("progress")
        if progress_service:
            progress_service.update_progress(progress, status)
        
        # 继续使用原有的进度更新处理
        self._on_progress_updated(progress, status)

    def _on_event_status_changed(self, status: bool, code: int, message: str):
        """
        事件总线状态变化处理

        Args:
            status: 状态布尔值
            code: 状态码
            message: 状态消息
        """
        self.logger.info("Status changed: %s, Code: %s, Message: %s", status, code, message)

    def _on_file_selected(self, file_path: str):
        """
        事件总线文件选择处理

        Args:
            file_path: 文件路径
        """
        self.logger.info("File selected via event bus: %s", file_path)

    def _on_config_changed(self, key: str, value: Any):
        """
        事件总线配置变更处理

        Args:
            key: 配置键
            value: 配置值
        """
        self.logger.debug("Config changed: %s = %s", key, value)
        config_service = self._get_service("config")
        if config_service:
            config_service.set(key, value)

    def _on_config_loaded(self, config_dict):
        """
        配置加载完成处理

        Args:
            config_dict: 配置字典
        """
        pass

    def _show_progress_dialog(self):
        """
        显示弹出式进度条对话框
        """
        if not self.progress_dialog:
            self.progress_dialog = ProgressDialog(self)
        self.progress_dialog.show()
        self.progress_dialog.raise_()
        self.progress_dialog.activateWindow()
        self.show_popup_progress = True

    def _close_progress_dialog(self):
        """
        关闭弹出式进度条对话框
        """
        if self.progress_dialog and self.show_popup_progress:
            self.progress_dialog.close()
            self.progress_dialog = None
            self.show_popup_progress = False
        self.progress_start_time = None

    def _on_controller_error(self, error_msg):
        """
        控制器错误处理
        
        Args:
            error_msg: 错误消息
        """
        # 关闭进度条
        self._close_progress_dialog()
        QW.QMessageBox.critical(self, _("error_title", "错误"), error_msg)

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
        # 更新窗口标题
        window_title_template = _("window_title")
        try:
            # 如果翻译包含{version}占位符，则进行格式化
            if "{version}" in window_title_template:
                window_title = window_title_template.format(version=self.version)
            else:
                window_title = window_title_template
        except (KeyError, ValueError):
            # 如果格式化失败，使用备用标题
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
        # 更新进度对话框标题
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.setWindowTitle(_("progress_title", "Battery Analysis Progress"))
            self.progress_dialog.status_label.setText(_("progress_ready", "Ready to start analysis..."))
    
    def _update_statusbar_messages(self):
        """更新状态栏消息为当前语言"""
        # 保存当前消息，以便切换语言后恢复
        current_message = self.statusBar_BatteryAnalysis.currentMessage()
        
        # 获取翻译后的状态消息
        status_ready = _("status_ready", "状态:就绪")
        
        # 更新状态栏
        if current_message in ("状态:就绪", "Ready"):
            self.statusBar_BatteryAnalysis.showMessage(status_ready)
        
        # 更新其他可能需要翻译的消息
        # 添加更多状态栏消息的翻译
    
    def _refresh_dialogs(self):
        """刷新所有对话框以应用新语言"""
        # 关闭并重新创建首选项对话框（如果正在显示）
        # 如果需要刷新其他对话框，也在这里处理
        pass

    def init_widget(self) -> None:
        if self.b_has_config:
            self.statusBar_BatteryAnalysis.showMessage("status:ok")

            self.init_lineedit()
            self.init_combobox()
            self.init_table()
            self.connect_widget()
            self._setup_accessibility()

            self.pushButton_Run.setFocus()
        else:
            # @todo: Add error popup windows here
            pass
    
    def _setup_accessibility(self) -> None:
        """
        设置UI控件的可访问性属性，确保符合无障碍标准
        """
        try:
            # 设置控件的可访问名称和描述
            # 测试配置组
            self.groupBox_TestConfig.setAccessibleName(_("access_test_config", "测试配置"))
            self.groupBox_TestConfig.setAccessibleDescription(_("access_test_config_desc", "包含测试相关配置的设置"))
            
            # 电池配置组
            self.groupBox_BatteryConfig.setAccessibleName(_("access_battery_config", "电池配置"))
            self.groupBox_BatteryConfig.setAccessibleDescription(_("access_battery_config_desc", "包含电池相关配置的设置"))
            
            # 运行按钮
            self.pushButton_Run.setAccessibleName(_("access_run_button", "运行分析"))
            self.pushButton_Run.setAccessibleDescription(_("access_run_button_desc", "开始电池分析任务"))
            
            # 文件选择按钮
            self.pushButton_TestProfile.setAccessibleName(_("access_test_profile_button", "选择测试文件"))
            self.pushButton_TestProfile.setAccessibleDescription(_("access_test_profile_desc", "选择电池测试配置文件"))
            self.pushButton_InputPath.setAccessibleName(_("access_input_path_button", "选择输入路径"))
            self.pushButton_InputPath.setAccessibleDescription(_("access_input_path_desc", "选择输入数据文件路径"))
            self.pushButton_OutputPath.setAccessibleName(_("access_output_path_button", "选择输出路径"))
            self.pushButton_OutputPath.setAccessibleDescription(_("access_output_path_desc", "选择分析结果输出路径"))
            
            # 设置焦点策略
            # 确保所有交互控件都支持键盘焦点
            interactive_widgets = [
                self.comboBox_BatteryType,
                self.comboBox_ConstructionMethod,
                self.comboBox_Specification_Type,
                self.comboBox_Specification_Method,
                self.comboBox_Manufacturer,
                self.lineEdit_BatchDateCode,
                self.lineEdit_SamplesQty,
                self.lineEdit_Temperature,
                self.lineEdit_DatasheetNominalCapacity,
                self.lineEdit_CalculationNominalCapacity,
                self.spinBox_AcceleratedAging,
                self.lineEdit_RequiredUseableCapacity,
                self.comboBox_TesterLocation,
                self.comboBox_TestedBy,
                self.lineEdit_TestProfile,
                self.pushButton_TestProfile,
                self.lineEdit_InputPath,
                self.pushButton_InputPath,
                self.lineEdit_OutputPath,
                self.pushButton_OutputPath,
                self.pushButton_Run
            ]
            
            for widget in interactive_widgets:
                widget.setFocusPolicy(QC.Qt.FocusPolicy.ClickFocus | QC.Qt.FocusPolicy.TabFocus)
            
            # 设置合理的键盘焦点顺序
            # 测试配置部分
            QW.QWidget.setTabOrder(self.comboBox_TesterLocation, self.comboBox_TestedBy)
            QW.QWidget.setTabOrder(self.comboBox_TestedBy, self.lineEdit_TestProfile)
            QW.QWidget.setTabOrder(self.lineEdit_TestProfile, self.pushButton_TestProfile)
            
            # 电池配置部分
            QW.QWidget.setTabOrder(self.pushButton_TestProfile, self.comboBox_BatteryType)
            QW.QWidget.setTabOrder(self.comboBox_BatteryType, self.comboBox_ConstructionMethod)
            QW.QWidget.setTabOrder(self.comboBox_ConstructionMethod, self.comboBox_Specification_Type)
            QW.QWidget.setTabOrder(self.comboBox_Specification_Type, self.comboBox_Specification_Method)
            QW.QWidget.setTabOrder(self.comboBox_Specification_Method, self.comboBox_Manufacturer)
            QW.QWidget.setTabOrder(self.comboBox_Manufacturer, self.lineEdit_BatchDateCode)
            QW.QWidget.setTabOrder(self.lineEdit_BatchDateCode, self.lineEdit_SamplesQty)
            QW.QWidget.setTabOrder(self.lineEdit_SamplesQty, self.lineEdit_Temperature)
            QW.QWidget.setTabOrder(self.lineEdit_Temperature, self.lineEdit_DatasheetNominalCapacity)
            QW.QWidget.setTabOrder(self.lineEdit_DatasheetNominalCapacity, self.lineEdit_CalculationNominalCapacity)
            QW.QWidget.setTabOrder(self.lineEdit_CalculationNominalCapacity, self.spinBox_AcceleratedAging)
            QW.QWidget.setTabOrder(self.spinBox_AcceleratedAging, self.lineEdit_RequiredUseableCapacity)
            
            # 路径配置部分
            QW.QWidget.setTabOrder(self.lineEdit_RequiredUseableCapacity, self.lineEdit_InputPath)
            QW.QWidget.setTabOrder(self.lineEdit_InputPath, self.pushButton_InputPath)
            QW.QWidget.setTabOrder(self.pushButton_InputPath, self.lineEdit_OutputPath)
            QW.QWidget.setTabOrder(self.lineEdit_OutputPath, self.pushButton_OutputPath)
            
            # 最终运行按钮
            QW.QWidget.setTabOrder(self.pushButton_OutputPath, self.pushButton_Run)
            
            # 确保表格支持键盘导航
            if hasattr(self, 'tableWidget_TestInformation'):
                self.tableWidget_TestInformation.setAccessibleName(_("access_test_info_table", "测试信息表格"))
                self.tableWidget_TestInformation.setAccessibleDescription(_("access_test_info_table_desc", "包含测试设备和软件版本信息的表格"))
                self.tableWidget_TestInformation.setFocusPolicy(QC.Qt.FocusPolicy.ClickFocus | QC.Qt.FocusPolicy.TabFocus)
            
            self.logger.info("可访问性设置已完成")
        except (AttributeError, TypeError, RuntimeError) as e:
            self.logger.warning("设置可访问性属性失败: %s", e)

    def init_lineedit(self) -> None:
        # input limit, only numbers allowed
        reg = QC.QRegularExpression(r"^\d*$")
        validator = QG.QRegularExpressionValidator(self)
        validator.setRegularExpression(reg)
        # self.lineEdit_BatchDateCode.setValidator(validator)
        self.lineEdit_SamplesQty.setValidator(validator)
        # self.lineEdit_Temperature.setValidator(validator)
        self.lineEdit_DatasheetNominalCapacity.setValidator(validator)
        self.lineEdit_CalculationNominalCapacity.setValidator(validator)
        self.lineEdit_RequiredUseableCapacity.setValidator(validator)
        # QSpinBox不需要设置文本验证器，因为它有内置的范围限制

        # 增强版本号验证，支持x.y.z格式
        reg = QC.QRegularExpression(r"^\d+(\.\d+){0,2}$")
        validator = QG.QRegularExpressionValidator(self)
        validator.setRegularExpression(reg)
        self.lineEdit_Version.setValidator(validator)
        # 添加版本号实when验证
        self.lineEdit_Version.textChanged.connect(self.validate_version)

        # 为输入路径添加存在性验证
        self.lineEdit_InputPath.textChanged.connect(self.validate_input_path)

        # 为必填字段添加非空验证
        required_fields = [
            self.lineEdit_SamplesQty,
            self.lineEdit_DatasheetNominalCapacity,
            self.lineEdit_CalculationNominalCapacity,
            self.lineEdit_RequiredUseableCapacity
        ]
        for field in required_fields:
            field.textChanged.connect(self.validate_required_fields)

        self.lineEdit_TestProfile.setText("Not provided")
        self.lineEdit_Temperature.setText("Room Temperature")

    def _load_user_settings(self) -> None:
        """加载用户配置文件中的设置"""
        try:
            user_config_path = os.path.join(os.path.dirname(
                self.config_path), "user_settings.ini") if self.b_has_config else None

            if user_config_path and os.path.exists(user_config_path):
                # 创建用户配置QSettings实例
                user_settings = QC.QSettings(
                    user_config_path, QC.QSettings.Format.IniFormat)

                # 加载电池类型相关设置
                battery_type = user_settings.value("UserConfig/BatteryType")
                if battery_type:
                    index = self.comboBox_BatteryType.findText(battery_type)
                    if index >= 0:
                        self.comboBox_BatteryType.setCurrentIndex(index)

                construction_method = user_settings.value(
                    "UserConfig/ConstructionMethod")
                if construction_method:
                    index = self.comboBox_ConstructionMethod.findText(
                        construction_method)
                    if index >= 0:
                        self.comboBox_ConstructionMethod.setCurrentIndex(index)

                specification_type = user_settings.value(
                    "UserConfig/SpecificationType")
                if specification_type:
                    index = self.comboBox_Specification_Type.findText(
                        specification_type)
                    if index >= 0:
                        self.comboBox_Specification_Type.setCurrentIndex(index)

                specification_method = user_settings.value(
                    "UserConfig/SpecificationMethod")
                if specification_method:
                    index = self.comboBox_Specification_Method.findText(
                        specification_method)
                    if index >= 0:
                        self.comboBox_Specification_Method.setCurrentIndex(
                            index)

                manufacturer = user_settings.value("UserConfig/Manufacturer")
                if manufacturer:
                    index = self.comboBox_Manufacturer.findText(manufacturer)
                    if index >= 0:
                        self.comboBox_Manufacturer.setCurrentIndex(index)

                tester_location = user_settings.value(
                    "UserConfig/TesterLocation")
                if tester_location:
                    index = self.comboBox_TesterLocation.findText(
                        tester_location)
                    if index >= 0:
                        self.comboBox_TesterLocation.setCurrentIndex(index)

                tested_by = user_settings.value("UserConfig/TestedBy")
                if tested_by:
                    index = self.comboBox_TestedBy.findText(tested_by)
                    if index >= 0:
                        self.comboBox_TestedBy.setCurrentIndex(index)
                    else:
                        # 如果找不到匹配项，直接设置文本（用于自定义输入的情况）
                        self.comboBox_TestedBy.setCurrentText(tested_by)

                # 加载温度设置
                temperature = user_settings.value("UserConfig/Temperature")
                if temperature:
                    self.lineEdit_Temperature.setText(temperature)

                # 加载输出路径设置
                output_path = user_settings.value("UserConfig/OutputPath")
                if output_path:
                    self.lineEdit_OutputPath.setText(output_path)
                    # 更新控制器的输出路径
                    main_controller = self._get_controller("main_controller")
                    if main_controller:
                        main_controller.set_project_context(
                            output_path=output_path)
        except (AttributeError, TypeError, KeyError, OSError) as e:
            logging.error("加载用户设置失败: %s", e)

    def init_combobox(self) -> None:
        self.comboBox_BatteryType.addItems(
            self.get_config("BatteryConfig/BatteryType"))
        self.comboBox_ConstructionMethod.addItems(
            self.get_config("BatteryConfig/ConstructionMethod"))
        self.comboBox_Specification_Type.addItems(
            self.get_config("BatteryConfig/SpecificationTypeCoinCell"))
        self.comboBox_Specification_Type.addItems(
            self.get_config("BatteryConfig/SpecificationTypePouchCell"))
        self.comboBox_Specification_Method.addItems(
            self.get_config("BatteryConfig/SpecificationMethod"))
        self.comboBox_Manufacturer.addItems(
            self.get_config("BatteryConfig/Manufacturer"))
        self.comboBox_TesterLocation.addItems(
            self.get_config("TestConfig/TesterLocation"))
        self.comboBox_TestedBy.addItems(self.get_config("TestConfig/TestedBy"))

        self.comboBox_BatteryType.setCurrentIndex(-1)
        self.comboBox_ConstructionMethod.setCurrentIndex(-1)
        self.comboBox_Specification_Type.setCurrentIndex(-1)
        self.comboBox_Specification_Method.setCurrentIndex(-1)
        self.comboBox_Manufacturer.setCurrentIndex(-1)
        self.comboBox_TesterLocation.setCurrentIndex(-1)
        self.comboBox_TestedBy.setCurrentIndex(-1)

        self.comboBox_ConstructionMethod.setEnabled(False)

        # 加载用户配置的设置
        self._load_user_settings()

    def init_table(self) -> None:
        # 不再硬编码DataProcessingPlatforms的值，而是从配置文件中读取
        # 这样用户的手动修改才能持久化
        # 移除固定列宽设置，改为在resizeEvent中按比例分配
        # 确保表格的最后一列自动拉伸
        self.tableWidget_TestInformation.horizontalHeader().setStretchLastSection(True)
        # 设置表格行高自动适应内容
        self.tableWidget_TestInformation.verticalHeader().setSectionResizeMode(
            QW.QHeaderView.ResizeMode.ResizeToContents)

        # 暂when断开cellChanged信号的连接，避免在初始化when触发保存操作
        try:
            self.tableWidget_TestInformation.cellChanged.disconnect()
        except TypeError:
            # 忽略TypeError异常，因为信号可能还没有被连接
            pass

        def set_span_item(item_text: str, row: int, col: int,
                          row_span: int = 1, col_span: int = 1,
                          editable: bool = False) -> None:
            # 只有当跨度大于1when才调用setSpan，避免单个单元格跨度的警告
            if row_span > 1 or col_span > 1:
                self.tableWidget_TestInformation.setSpan(
                    row, col, row_span, col_span)

            item = QW.QTableWidgetItem(item_text)
            if not editable:
                item.setFlags(QC.Qt.ItemFlag.ItemIsEnabled)
                item.setBackground(QG.QBrush(QG.QColor(242, 242, 242)))

            self.tableWidget_TestInformation.setItem(row, col, item)

        set_span_item("Test Equipment", 0, 0, 1, 2)
        set_span_item("", 0, 2, editable=True)

        set_span_item("Software Versions", 1, 0, 3, 1)
        set_span_item("BTS Server Version", 1, 1)
        set_span_item("BTS Client Version", 2, 1)
        set_span_item("TSDA (Data Analysis) Version", 3, 1)
        set_span_item("", 1, 2, editable=True)
        set_span_item("", 2, 2, editable=True)
        set_span_item("", 3, 2, editable=True)

        set_span_item("middle Machines", 4, 0, 5, 1)
        set_span_item("Model", 4, 1)
        set_span_item("Hardware Version", 5, 1)
        set_span_item("Serial Number", 6, 1)
        set_span_item("Firmware Version", 7, 1)
        set_span_item("Device Type", 8, 1)
        set_span_item("", 4, 2, editable=True)
        set_span_item("", 5, 2, editable=True)
        set_span_item("", 6, 2, editable=True)
        set_span_item("", 7, 2, editable=True)
        set_span_item("", 8, 2, editable=True)

        set_span_item("Test Units", 9, 0, 3, 1)
        set_span_item("Model", 9, 1)
        set_span_item("Hardware Version", 10, 1)
        set_span_item("Firmware Version", 11, 1)
        set_span_item("", 9, 2, editable=True)
        set_span_item("", 9, 3, editable=True)
        set_span_item("", 10, 2, editable=True)
        set_span_item("", 11, 2, editable=True)

        # Data Processing Platforms 不写入setting.ini，默认跟随软件版本
        from battery_analysis import __version__
        set_span_item("Data Processing Platforms", 12, 0, 1, 2)
        set_span_item(
            f"Battery Analyzer-v{__version__}",
            12, 2,
            editable=False
        )
        set_span_item("Reported By", 13, 0, 1, 2)
        set_span_item(
            "",
            13, 2,
            editable=True
        )

    def connect_widget(self) -> None:
        self.comboBox_BatteryType.currentIndexChanged.connect(
            self.check_batterytype)
        self.comboBox_Specification_Type.currentIndexChanged.connect(
            self.check_specification)
        self.comboBox_Specification_Method.currentIndexChanged.connect(
            self.check_specification)
        self.comboBox_TesterLocation.currentIndexChanged.connect(
            self.set_table)
        self.lineEdit_InputPath.textChanged.connect(self.get_xlsxinfo)
        self.pushButton_TestProfile.clicked.connect(self.select_testprofile)
        self.pushButton_InputPath.clicked.connect(self.select_inputpath)
        self.pushButton_OutputPath.clicked.connect(self.select_outputpath)
        self.pushButton_Run.clicked.connect(self.run)
        self.sigSetVersion.connect(self.get_version)

        # 设置菜单快捷键
        self.setup_menu_shortcuts()

        # 菜单动作连接
        self.actionExit.triggered.connect(self.handle_exit)
        self.actionAbout.triggered.connect(self.handle_about)
        self.actionUser_Mannual.triggered.connect(self.show_user_manual)
        self.actionOnline_Help.triggered.connect(self.show_online_help)

        # 常用编辑功能连接
        self.actionCopy.triggered.connect(self.copy_selected_text)
        self.actionPaste.triggered.connect(self.paste_text)
        self.actionCut.triggered.connect(self.cut_selected_text)

        # 首选项对话框连接
        self.actionPreferences.triggered.connect(self.show_preferences)

        # 工具栏和状态栏显示/隐藏功能连接
        if hasattr(self, 'actionShow_Toolbar'):
            self.actionShow_Toolbar.triggered.connect(self.toggle_toolbar_safe)
        if hasattr(self, 'actionShow_Statusbar'):
            self.actionShow_Statusbar.triggered.connect(
                self.toggle_statusbar_safe)

        # 工具菜单功能连接
        self.actionCalculate_Battery.triggered.connect(self.calculate_battery)
        self.actionAnalyze_Data.triggered.connect(self.analyze_data)
        self.actionBatteryChartViewer.triggered.connect(self.run_visualizer)
        self.actionGenerate_Report.triggered.connect(self.generate_report)
        self.actionBatch_Processing.triggered.connect(self.batch_processing)

        # 缩放功能连接
        self.actionZoom_In.triggered.connect(self.zoom_in)
        self.actionZoom_Out.triggered.connect(self.zoom_out)
        self.actionReset_Zoom.triggered.connect(self.reset_zoom)

        # 主题菜单功能连接
        if hasattr(self, 'actionSystem_Default'):
            self.actionSystem_Default.triggered.connect(
                lambda: self.set_theme("System Default"))
        if hasattr(self, 'actionWindows_11'):
            self.actionWindows_11.triggered.connect(
                lambda: self.set_theme("Windows 11"))
        if hasattr(self, 'actionWindows_Vista'):
            self.actionWindows_Vista.triggered.connect(
                lambda: self.set_theme("Windows Vista"))
        if hasattr(self, 'actionFusion'):
            self.actionFusion.triggered.connect(
                lambda: self.set_theme("Fusion"))
        if hasattr(self, 'actionDark_Theme'):
            self.actionDark_Theme.triggered.connect(
                lambda: self.set_theme("Dark Theme"))

        # 文件操作连接
        self.actionSave.triggered.connect(self.save_settings)
        self.actionExport_Report.triggered.connect(self.export_report)

    def handle_exit(self) -> None:
        """处理退出操作，显示确认对话框"""
        reply = QW.QMessageBox.question(
            self,
            '确认退出',
            '确定要退出应用程序吗？',
            QW.QMessageBox.StandardButton.Yes | QW.QMessageBox.StandardButton.No,
            QW.QMessageBox.StandardButton.No
        )

        if reply == QW.QMessageBox.StandardButton.Yes:
            self.close()

    def handle_about(self) -> None:
        """显示关于对话框"""
        about_text = f"""
        <h3>Battery Analyzer</h3>
        <p>版本: v{self.version}</p>
        <p>电池分析工具，用于电池性能测试和数据分析。</p>
        <p>© {time.localtime().tm_year} Battery Testing System</p>
        """

        QW.QMessageBox.about(
            self,
            '关于 Battery Analyzer',
            about_text
        )

    def show_preferences(self) -> None:
        """显示首选项对话框"""
        try:
            preferences_dialog = PreferencesDialog(self)
            
            # 连接首选项应用信号
            preferences_dialog.preferences_applied.connect(self.on_preferences_applied)
            
            # 显示对话框
            preferences_dialog.exec()
            
        except (OSError, ValueError, ImportError) as e:
            self.logger.error("显示首选项对话框时发生错误: %s", e)
            QW.QMessageBox.critical(
                self,
                _("error", "错误"),
                f"{_('show_preferences_failed', '显示首选项对话框失败')}: {str(e)}"
            )

    def on_preferences_applied(self) -> None:
        """首选项应用后的处理"""
        try:
            # 这里可以添加首选项应用后的特殊处理
            # 比如重新加载某些设置、更新界面等
            self.logger.info("首选项已应用")
            
        except (OSError, ValueError, ImportError) as e:
            self.logger.error("应用首选项后处理时发生错误: %s", e)

    def toggle_toolbar_safe(self) -> None:
        """安全地切换工具栏的显示/隐藏状态"""
        if hasattr(self, 'actionShow_Toolbar') and hasattr(self, 'toolBar'):
            self.toolBar.setVisible(self.actionShow_Toolbar.isChecked())
        elif hasattr(self, 'toolBar'):
            # 如果没有actionShow_Toolbar，只是切换显示状态
            self.toolBar.setVisible(not self.toolBar.isVisible())

    def toggle_statusbar_safe(self) -> None:
        """安全地切换状态栏的显示/隐藏状态"""
        if hasattr(self, 'actionShow_Statusbar') and hasattr(self, 'statusBar_BatteryAnalysis'):
            self.statusBar_BatteryAnalysis.setVisible(
                self.actionShow_Statusbar.isChecked())
        elif hasattr(self, 'statusBar_BatteryAnalysis'):
            # 如果没有actionShow_Statusbar，只是切换显示状态
            self.statusBar_BatteryAnalysis.setVisible(
                not self.statusBar_BatteryAnalysis.isVisible())

    def setup_menu_shortcuts(self) -> None:
        """安全地设置所有菜单的快捷键"""
        try:
            # 文件菜单快捷键
            if hasattr(self, 'actionNew'):
                self.actionNew.setShortcut(QG.QKeySequence.StandardKey.New)
            if hasattr(self, 'actionOpen'):
                self.actionOpen.setShortcut(QG.QKeySequence.StandardKey.Open)
            if hasattr(self, 'actionSave'):
                self.actionSave.setShortcut(QG.QKeySequence.StandardKey.Save)
            if hasattr(self, 'actionSave_As'):
                self.actionSave_As.setShortcut(
                    QG.QKeySequence.StandardKey.SaveAs)
            if hasattr(self, 'actionExit'):
                self.actionExit.setShortcut(QG.QKeySequence.StandardKey.Quit)

            # 编辑菜单快捷键
            if hasattr(self, 'actionUndo'):
                self.actionUndo.setShortcut(QG.QKeySequence.StandardKey.Undo)
            if hasattr(self, 'actionRedo'):
                self.actionRedo.setShortcut(QG.QKeySequence.StandardKey.Redo)
            if hasattr(self, 'actionCut'):
                self.actionCut.setShortcut(QG.QKeySequence.StandardKey.Cut)
            if hasattr(self, 'actionCopy'):
                self.actionCopy.setShortcut(QG.QKeySequence.StandardKey.Copy)
            if hasattr(self, 'actionPaste'):
                self.actionPaste.setShortcut(QG.QKeySequence.StandardKey.Paste)

            # 视图菜单快捷键
            if hasattr(self, 'actionZoom_In'):
                self.actionZoom_In.setShortcut(
                    QG.QKeySequence.StandardKey.ZoomIn)
            if hasattr(self, 'actionZoom_Out'):
                self.actionZoom_Out.setShortcut(
                    QG.QKeySequence.StandardKey.ZoomOut)

            # 工具菜单快捷键
            if hasattr(self, 'actionCalculate_Battery'):
                self.actionCalculate_Battery.setShortcut(
                    QG.QKeySequence("Ctrl+B"))
            if hasattr(self, 'actionAnalyze_Data'):
                self.actionAnalyze_Data.setShortcut(QG.QKeySequence("Ctrl+D"))
            if hasattr(self, 'actionGenerate_Report'):
                self.actionGenerate_Report.setShortcut(
                    QG.QKeySequence("Ctrl+R"))

            # 帮助菜单快捷键
            if hasattr(self, 'actionUser_Mannual'):
                self.actionUser_Mannual.setShortcut(
                    QG.QKeySequence.StandardKey.HelpContents)
            if hasattr(self, 'actionOnline_Help'):
                self.actionOnline_Help.setShortcut(QG.QKeySequence("F1"))
            if hasattr(self, 'actionAbout'):
                self.actionAbout.setShortcut(QG.QKeySequence("Ctrl+Alt+A"))

            # 为菜单项添加视觉提示
            if hasattr(self, 'actionShow_Toolbar'):
                self.actionShow_Toolbar.setCheckable(True)
                self.actionShow_Toolbar.setChecked(False)
                # 确保toolbar的可见性与action状态一致
                if hasattr(self, 'toolBar'):
                    self.toolBar.setVisible(False)
            if hasattr(self, 'actionShow_Statusbar'):
                self.actionShow_Statusbar.setCheckable(True)
                self.actionShow_Statusbar.setChecked(True)
        except (AttributeError, TypeError, RuntimeError) as e:
            logging.error("设置菜单快捷键失败: %s", e)

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
        """显示在线帮助"""
        try:
            # 打开在线帮助网页
            help_url = "https://example.com/battery-analyzer-help"
            QG.QDesktopServices.openUrl(QC.QUrl(help_url))
        except (OSError, ValueError, RuntimeError, TypeError) as e:
            logging.error("打开在线帮助失败: %s", e)
            QW.QMessageBox.information(
                self,
                "在线帮助",
                "无法打开在线帮助。请检查网络连接or联系技术支持。\n\n帮助中心网址: https://example.com/battery-analyzer-help",
                QW.QMessageBox.StandardButton.Ok
            )

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
        """执行电池计算"""
        # 这里可以实现电池计算的逻辑，or连接到现有的计算功能
        self.statusBar_BatteryAnalysis.showMessage(_("calculating_battery", "执行电池计算..."))
        # 模拟计算过程
        QW.QMessageBox.information(
            self,
            "电池计算",
            "电池计算功能将根据输入的参数进行计算。\n\n点击'运行'按钮开始完整的电池分析流程。",
            QW.QMessageBox.StandardButton.Ok
        )
        self.statusBar_BatteryAnalysis.showMessage(_("status_ready", "状态:就绪"))

    def analyze_data(self) -> None:
        """分析数据"""
        # 检查输入路径是否设置
        if not self.lineEdit_InputPath.text():
            QW.QMessageBox.warning(
                self,
                _("warning", "警告"),
                "请先设置输入路径后再分析数据。",
                QW.QMessageBox.StandardButton.Ok
            )
            return

        self.statusBar_BatteryAnalysis.showMessage(_("analyzing_data", "分析数据中..."))
        # 这里可以连接到现有的数据分析功能
        QW.QMessageBox.information(
            self,
            "数据分析",
            "数据分析功能将处理输入路径中的数据文件。\n\n点击'运行'按钮开始完整的电池分析流程。",
            QW.QMessageBox.StandardButton.Ok
        )
        self.statusBar_BatteryAnalysis.showMessage(_("status_ready", "状态:就绪"))

    def generate_report(self) -> None:
        """生成报告"""
        # 检查输出路径是否设置
        if not self.lineEdit_OutputPath.text():
            QW.QMessageBox.warning(
                self,
                _("warning", "警告"),
                "请先设置输出路径后再生成报告。",
                QW.QMessageBox.StandardButton.Ok
            )
            return

        self.statusBar_BatteryAnalysis.showMessage(_("generating_report", "生成报告中..."))
        # 这里可以连接到现有的报告生成功能
        QW.QMessageBox.information(
            self,
            "生成报告",
            "报告将被生成到指定的输出路径。\n\n点击'运行'按钮开始完整的电池分析流程。",
            QW.QMessageBox.StandardButton.Ok
        )
        self.statusBar_BatteryAnalysis.showMessage(_("status_ready", "状态:就绪"))

    def run_visualizer(self, xml_path=None) -> None:
        """运行可视化工具，使用工厂模式解耦依赖"""
        logging.info("进入main_window.run_visualizer方法")
        
        # 检查xml_path是否为布尔值，如果是，则忽略（可能来自QAction的triggered信号）
        if isinstance(xml_path, bool):
            logging.info("检测到布尔类型的xml_path参数，忽略它")
            xml_path = None
        
        # 如果没有传入xml_path参数，则从界面获取
        if xml_path is None:
            logging.info("没有传入xml_path，尝试从界面获取")
            xml_path = self.lineEdit_TestProfile.text() if hasattr(self, 'lineEdit_TestProfile') else None
            logging.info("从界面获取的xml_path: %s", xml_path)
        else:
            logging.info("传入的xml_path: %s", xml_path)
        
        self.statusBar_BatteryAnalysis.showMessage(_("starting_visualizer", "启动可视化工具..."))

        try:
            # 使用工厂模式创建可视化器
            logging.info("使用工厂模式创建可视化器")
            self.current_visualizer = self.visualizer_factory.create_visualizer("battery_chart")
            
            if self.current_visualizer is None:
                raise RuntimeError("无法创建可视化器实例")

            # 检查是否有有效的数据路径
            if xml_path and os.path.exists(xml_path):
                # 如果有有效的数据路径，先加载数据
                logging.info("加载数据: %s", xml_path)
                success = self.current_visualizer.load_data(xml_path)
                if not success:
                    logging.warning("数据加载失败，将显示空图表")
            else:
                logging.info("没有有效的数据路径，将显示提示信息")
                # 清除任何可能已加载的数据
                self.current_visualizer.clear_data()

            # 显示可视化
            logging.info("显示可视化")
            show_success = self.current_visualizer.show_figure(xml_path)
            
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
        """批量处理"""
        self.statusBar_BatteryAnalysis.showMessage(_("preparing_batch_processing", "准备批量处理..."))
        QW.QMessageBox.information(
            self,
            "批量处理",
            "批量处理功能允许您同when分析多个电池数据集。\n\n此功能正在开发中，敬请期待。",
            QW.QMessageBox.StandardButton.Ok
        )
        self.statusBar_BatteryAnalysis.showMessage(_("status_ready", "状态:就绪"))

    def zoom_in(self) -> None:
        """放大界面元素"""
        # 实现界面元素放大功能
        font = self.font()
        current_size = font.pointSize()
        if current_size < 20:  # 设置最大字体大小限制
            font.setPointSize(current_size + 1)
            self.setFont(font)

    def zoom_out(self) -> None:
        """缩小界面元素"""
        # 实现界面元素缩小功能
        font = self.font()
        current_size = font.pointSize()
        if current_size > 8:  # 设置最小字体大小限制
            font.setPointSize(current_size - 1)
            self.setFont(font)

    def reset_zoom(self) -> None:
        """重置界面缩放"""
        # 重置界面元素大小到默认值
        font = self.font()
        font.setPointSize(9)  # 假设默认字体大小为9
        self.setFont(font)

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

                # 温度设置
                temperature = self.lineEdit_Temperature.text()
                if temperature:
                    user_settings.setValue(
                        "UserConfig/Temperature", temperature)

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
        """导出报告"""
        # 检查输出路径是否设置
        if not self.lineEdit_OutputPath.text():
            QW.QMessageBox.warning(
                self,
                _("warning", "警告"),
                "请先设置输出路径后再导出报告。",
                QW.QMessageBox.StandardButton.Ok
            )
            return

        self.statusBar_BatteryAnalysis.showMessage(_("exporting_report", "导出报告中..."))
        # 这里可以连接到现有的报告导出功能
        QW.QMessageBox.information(
            self,
            "导出报告",
            "报告将被导出到指定的输出路径。\n\n点击'运行'按钮开始完整的电池分析流程。",
            QW.QMessageBox.StandardButton.Ok
        )
        self.statusBar_BatteryAnalysis.showMessage(_("status_ready", "状态:就绪"))

    def set_theme(self, theme_name) -> None:
        """设置应用程序主题"""
        app = QW.QApplication.instance()

        # 清除现有的样式表
        app.setStyleSheet("")

        # 主题动作映射字典
        theme_actions = {
            "System Default": self.actionSystem_Default,
            "Windows 11": self.actionWindows_11,
            "Windows Vista": self.actionWindows_Vista,
            "Fusion": self.actionFusion,
            "Dark Theme": self.actionDark_Theme
        }

        # 确保所有主题动作都是可检查的
        for action in theme_actions.values():
            action.setCheckable(True)

        # 清除所有主题动作的选中状态
        for action in theme_actions.values():
            action.setChecked(False)

        try:
            if theme_name == "System Default":
                # 使用系统默认样式
                app.setStyle(QW.QStyleFactory.create(
                    "windowsvista" if sys.platform == "win32" else "fusion"))
                self.statusBar_BatteryAnalysis.showMessage(_("theme_switched_default", f"已切换到系统默认主题"))
            elif theme_name == "Windows 11":
                # 尝试使用Windows 11样式（如果可用）
                if sys.platform == "win32":
                    app.setStyle(QW.QStyleFactory.create("windowsvista"))
                    self.statusBar_BatteryAnalysis.showMessage(
                        f"已切换到Windows 11主题")
                else:
                    # 非Windows平台回退到Fusion
                    app.setStyle(QW.QStyleFactory.create("fusion"))
                    self.statusBar_BatteryAnalysis.showMessage(
                        f"已切换到Fusion主题（Windows 11样式在当前平台不可用）")
            elif theme_name == "Windows Vista":
                # 使用Windows Vista样式
                if sys.platform == "win32":
                    app.setStyle(QW.QStyleFactory.create("windowsvista"))
                    self.statusBar_BatteryAnalysis.showMessage(
                        f"已切换到Windows Vista主题")
                else:
                    # 非Windows平台回退到Fusion
                    app.setStyle(QW.QStyleFactory.create("fusion"))
                    self.statusBar_BatteryAnalysis.showMessage(
                        f"已切换到Fusion主题（Windows Vista样式在当前平台不可用）")
            elif theme_name == "Fusion":
                # 使用Fusion样式（跨平台）
                app.setStyle(QW.QStyleFactory.create("fusion"))
                self.statusBar_BatteryAnalysis.showMessage(_("theme_switched_fusion", f"已切换到Fusion主题"))
            elif theme_name == "Dark Theme":
                # 使用深色主题
                try:
                    # 尝试使用我们的QSS主题系统
                    from battery_analysis.ui.styles import style_manager
                    style_manager.apply_global_style(app, "dark")
                    self.statusBar_BatteryAnalysis.showMessage(_("theme_switched_dark", f"已切换到深色主题"))
                except (ImportError, AttributeError, TypeError, RuntimeError) as e:
                    # 如果主题系统加载失败，使用简单的深色主题样式表
                    dark_stylesheet = """.QWidget {
                        background-color: #2b2b2b;
                        color: #cccccc;
                    }
                    QMenuBar {
                        background-color: #2b2b2b;
                        color: #cccccc;
                    }
                    QMenu {
                        background-color: #3a3a3a;
                        color: #cccccc;
                    }
                    QMenu::item:selected {
                        background-color: #555555;
                    }
                    QPushButton {
                        background-color: #4a4a4a;
                        border: 1px solid #6a6a6a;
                        color: #cccccc;
                    }
                    QPushButton:hover {
                        background-color: #555555;
                    }
                    QLineEdit, QComboBox, QTextEdit, QSpinBox {
                        background-color: #3a3a3a;
                        border: 1px solid #6a6a6a;
                        color: #cccccc;
                    }
                    QTableWidget {
                        background-color: #3a3a3a;
                        color: #cccccc;
                        alternate-background-color: #4a4a4a;
                    }
                    QHeaderView::section {
                        background-color: #4a4a4a;
                        color: #cccccc;
                    }
                    """
                    app.setStyleSheet(dark_stylesheet)
                    self.statusBar_BatteryAnalysis.showMessage(_("theme_switched_simple_dark", f"已切换到简单深色主题"))
        except (ImportError, AttributeError, TypeError, RuntimeError) as e:
            logging.error("切换主题失败: %s", e)
            self.statusBar_BatteryAnalysis.showMessage(_("theme_switch_failed", f"切换主题失败: {str(e)}"))

        # 设置当前主题动作的选中状态
        if theme_name in theme_actions:
            theme_actions[theme_name].setChecked(True)

        # 确保界面立即更新
        QW.QApplication.processEvents()

    def toggle_statusbar(self) -> None:
        """切换状态栏的显示/隐藏状态"""
        self.statusBar_BatteryAnalysis.setVisible(
            self.actionShow_Statusbar.isChecked())

    def validate_version(self) -> None:
        """验证版本号格式并提供实when反馈"""
        version_text = self.lineEdit_Version.text()
        regex = QC.QRegularExpression(r"^\d+(\.\d+){0,2}$")
        if version_text and not regex.match(version_text).hasMatch():
            self.statusBar_BatteryAnalysis.showMessage(
                f"{_('warning', '警告')}: {_('version_format_invalid', '版本号格式不correct，应为 x.y.z 格式')}")
            # 设置错误样式
            self.lineEdit_Version.setStyleSheet(
                "background-color: #FFDDDD; border: 1px solid #FF6666;")
        else:
            # 重置样式
            self.lineEdit_Version.setStyleSheet("")
            # 如果所有验证都通过，显示正常状态
            if self.checker_battery_type.b_check_pass:
                self.statusBar_BatteryAnalysis.showMessage("status:ok")

    def validate_input_path(self) -> None:
        """验证输入路径是否存在"""
        path = self.lineEdit_InputPath.text()
        if path and not os.path.exists(path):
            self.statusBar_BatteryAnalysis.showMessage(f"{_('warning', '警告')}: {_('input_path_not_exists', '输入路径不存在')}")
            self.lineEdit_InputPath.setStyleSheet(
                "background-color: #FFDDDD; border: 1px solid #FF6666;")
        else:
            self.lineEdit_InputPath.setStyleSheet("")
            # 如果所有验证都通过，显示正常状态
            if self.checker_battery_type.b_check_pass:
                self.statusBar_BatteryAnalysis.showMessage("status:ok")

    def validate_required_fields(self) -> None:
        """验证必填字段是否empty"""
        empty_fields = []

        if not self.lineEdit_SamplesQty.text():
            empty_fields.append("样品数量")
            self.lineEdit_SamplesQty.setStyleSheet(
                "background-color: #FFDDDD; border: 1px solid #FF6666;")
        else:
            self.lineEdit_SamplesQty.setStyleSheet("")

        if not self.lineEdit_DatasheetNominalCapacity.text():
            empty_fields.append("标称容量")
            self.lineEdit_DatasheetNominalCapacity.setStyleSheet(
                "background-color: #FFDDDD; border: 1px solid #FF6666;")
        else:
            self.lineEdit_DatasheetNominalCapacity.setStyleSheet("")

        if not self.lineEdit_CalculationNominalCapacity.text():
            empty_fields.append("计算容量")
            self.lineEdit_CalculationNominalCapacity.setStyleSheet(
                "background-color: #FFDDDD; border: 1px solid #FF6666;")
        else:
            self.lineEdit_CalculationNominalCapacity.setStyleSheet("")

        if not self.lineEdit_RequiredUseableCapacity.text():
            empty_fields.append("可用容量")
            self.lineEdit_RequiredUseableCapacity.setStyleSheet(
                "background-color: #FFDDDD; border: 1px solid #FF6666;")
        else:
            self.lineEdit_RequiredUseableCapacity.setStyleSheet("")

        if empty_fields:
            self.statusBar_BatteryAnalysis.showMessage(
                f"{_('warning', '警告')}: {_('required_fields_empty', '以下必填字段empty')}: {', '.join(empty_fields)}")
        else:
            # 如果所有验证都通过，显示正常状态
            if self.checker_battery_type.b_check_pass:
                self.statusBar_BatteryAnalysis.showMessage("status:ok")

    def check_batterytype(self) -> None:
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
                if self.strSpecificationType == self.comboBox_Specification_Type.itemText(t):
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
            f"{self.test_information}/middleMachines.Model"), 4, 2)
        set_item(self.get_config(
            f"{self.test_information}/middleMachines.HardwareVersion"), 5, 2)
        set_item(self.get_config(
            f"{self.test_information}/middleMachines.SerialNumber"), 6, 2)
        set_item(self.get_config(
            f"{self.test_information}/middleMachines.FirmwareVersion"), 7, 2)
        set_item(self.get_config(
            f"{self.test_information}/middleMachines.DeviceType"), 8, 2)
        set_item(self.get_config(
            f"{self.test_information}/TestUnits.Model"), 9, 2)
        set_item(self.get_config(
            f"{self.test_information}/TestUnits.HardwareVersion"), 10, 2)
        set_item(self.get_config(
            f"{self.test_information}/TestUnits.FirmwareVersion"), 11, 2)

        # 根据TesterLocation自动设置ReportedBy
        current_tester_location = self.comboBox_TesterLocation.currentIndex()
        # 根据用户要求，前两个选项都是BOEDT，后面的依次为PDI, BOECQ, Jabil VN和VG Fernitz
        if current_tester_location in (0, 1):
            reported_by = "BOEDT"
        elif current_tester_location == 2:
            reported_by = "PDI"
        elif current_tester_location == 3:
            reported_by = "BOECQ"
        elif current_tester_location == 4:
            reported_by = "Jabil VN"
        elif current_tester_location == 5:
            reported_by = "VG Fernitz"
        else:
            reported_by = ""

        # 更新ReportedBy到表格
        qt_item = QW.QTableWidgetItem(reported_by)
        self.tableWidget_TestInformation.setItem(13, 2, qt_item)

    def get_xlsxinfo(self) -> None:
        self.checker_input_xlsx.clear()
        self.comboBox_Specification_Type.currentIndexChanged.disconnect(
            self.check_specification)
        self.comboBox_Specification_Method.currentIndexChanged.disconnect(
            self.check_specification)
        self.comboBox_BatteryType.setCurrentIndex(-1)
        self.comboBox_Specification_Type.clear()
        self.comboBox_Specification_Type.addItems(
            self.get_config("BatteryConfig/SpecificationTypeCoinCell"))
        self.comboBox_Specification_Type.addItems(
            self.get_config("BatteryConfig/SpecificationTypePouchCell"))
        self.comboBox_Specification_Type.setCurrentIndex(-1)
        self.comboBox_Specification_Method.clear()
        self.comboBox_Specification_Method.addItems(
            self.get_config("BatteryConfig/SpecificationMethod"))
        self.comboBox_Specification_Method.setCurrentIndex(-1)
        self.comboBox_Manufacturer.setCurrentIndex(-1)
        self.lineEdit_BatchDateCode.setText("")
        self.lineEdit_SamplesQty.setText("")
        self.lineEdit_DatasheetNominalCapacity.setText("")
        self.lineEdit_CalculationNominalCapacity.setText("")
        self.comboBox_Specification_Type.currentIndexChanged.connect(
            self.check_specification)
        self.comboBox_Specification_Method.currentIndexChanged.connect(
            self.check_specification)
        strInDataXlsxDir = self.lineEdit_InputPath.text()
        if strInDataXlsxDir != "":
            listAllInXlsx = [f for f in os.listdir(
                strInDataXlsxDir) if f[:2] != "~$" and f[-5:] == ".xlsx"]
            if listAllInXlsx:
                intIndexType = -1
                intIndexMethod = -1
                strSampleInputXlsxTitle = listAllInXlsx[0]
                self.construction_method = ""
                for c in range(self.comboBox_ConstructionMethod.count()):
                    if self.comboBox_ConstructionMethod.itemText(c) in strSampleInputXlsxTitle:
                        self.construction_method = self.comboBox_ConstructionMethod.itemText(
                            c)
                        break
                listAllSpecificationType = \
                    self.get_config("BatteryConfig/SpecificationTypeCoinCell") \
                    + self.get_config("BatteryConfig/SpecificationTypePouchCell")
                listAllSpecificationMethod = self.get_config(
                    "BatteryConfig/SpecificationMethod")
                for t in range(len(listAllSpecificationType)):
                    if f"{listAllSpecificationType[t]}" in strSampleInputXlsxTitle:
                        intIndexType = t
                        break
                for m in range(len(listAllSpecificationMethod)):
                    if f"{listAllSpecificationMethod[m]}" in strSampleInputXlsxTitle:
                        intIndexMethod = m
                        break
                self.comboBox_Specification_Type.setCurrentIndex(intIndexType)
                self.comboBox_Specification_Method.setCurrentIndex(
                    intIndexMethod)
                for m in range(self.comboBox_Manufacturer.count()):
                    if self.comboBox_Manufacturer.itemText(m) in strSampleInputXlsxTitle:
                        self.comboBox_Manufacturer.setCurrentIndex(m)
                listBatchDateCode = re.findall(
                    "DC(.*?),", strSampleInputXlsxTitle)
                if len(listBatchDateCode) == 1:
                    self.lineEdit_BatchDateCode.setText(
                        listBatchDateCode[0].strip())
                listPulseCurrentToSplit = re.findall(
                    r"\(([\d.]+[-\d.]+)mA", strSampleInputXlsxTitle)
                if len(listPulseCurrentToSplit) == 1:
                    listPulseCurrent = listPulseCurrentToSplit[0].split("-")
                    try:
                        # 将字符串转换为浮点数，保留小数精度
                        self.listCurrentLevel = [
                            float(c.strip()) for c in listPulseCurrent]
                    except ValueError:
                        # 处理转换失败的情况
                        self.listCurrentLevel = [
                            int(float(c.strip())) for c in listPulseCurrent]
                    self.config.setValue(
                        "BatteryConfig/PulseCurrent", listPulseCurrent)
                    # self.listCurrentLevel = [int(listPulseCurrent[c].strip()) \
                    #                          for c in range(len(listPulseCurrent))]
                    # self.config.setValue("BatteryConfig/PulseCurrent", listPulseCurrent)

                self.cc_current = ""
                list_cc_current_to_split = re.findall(
                    r"mA,(.*?)\)", strSampleInputXlsxTitle)
                if len(list_cc_current_to_split) == 1:
                    str_cc_current_to_split = list_cc_current_to_split[0].replace(
                        "mAh", "")
                    list_cc_current_to_split = re.findall(
                        r"([\d.]+)mA", str_cc_current_to_split)
                    if len(list_cc_current_to_split) >= 1:
                        self.cc_current = list_cc_current_to_split[-1]
                self.lineEdit_SamplesQty.setText(str(len(listAllInXlsx)))
            else:
                self.checker_input_xlsx.set_error("Input path has no data")
            self.statusBar_BatteryAnalysis.showMessage(
                "[Error]: Input path has no data")

    def get_version(self) -> None:
        """
        计算并设置电池分析的版本号

        此方法通过分析输入目录中的XLSX文件，计算其MD5校验和，
        然后根据MD5.csv文件中的历史记录确定当前版本号。如果输入文件内容变更，
        版本号会自动增加。

        工作流程：
        1. 从UI获取输入和输出目录路径
        2. 检查目录是否存在
        3. 收集输入目录中所有有效的.xlsx文件（排除临when文件）
        4. 计算这些文件的MD5校验和
        5. 读取MD5.csv文件（如果存在）来获取历史记录
        6. 根据MD5校验和匹配确定版本号
        7. 如果找到匹配的MD5，使用对应的版本号；否则创建新版本
        8. 更新MD5.csv文件并设置为隐藏属性
        9. 将版本号显示在UI中

        版本号格式：
        - 主版本号：当输入文件内容发生变化when增加
        - 次版本号：同一内容的重复运行计数

        错误处理：
        - 如果输入or输出目录不存在，清空版本号显示
        - 如果输入目录中没有XLSX文件，清空版本号显示

        返回值：
            None
        """
        strInPutDir = self.lineEdit_InputPath.text()
        strOutoutDir = self.lineEdit_OutputPath.text()
        if os.path.exists(strInPutDir) and os.path.exists(strOutoutDir):
            listAllInXlsx = [strInPutDir + f"/{f}" for f in os.listdir(
                strInPutDir) if f[:2] != "~$" and f[-5:] == ".xlsx"]
            if not listAllInXlsx:
                self.lineEdit_Version.setText("")
                return
            strCsvMd5Path = strOutoutDir + "/MD5.csv"
            self.md5_checksum = calc_md5checksum(listAllInXlsx)
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
        # 初始化线程（方法保留以保持向后兼容性）
        self.init_thread()

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
        test_info = [
            self.comboBox_BatteryType.currentText(),
            self.comboBox_ConstructionMethod.currentText(),
            self.comboBox_Specification_Type.currentText(),
            self.comboBox_Specification_Method.currentText(),
            self.comboBox_Manufacturer.currentText(),
            self.lineEdit_BatchDateCode.text(),
            self.lineEdit_SamplesQty.text(),
            self.lineEdit_Temperature.text(),
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
            self.tableWidget_TestInformation.item(13, 2).text(
            ) if self.tableWidget_TestInformation.item(13, 2) else ""
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
        self.label_BatteryType.setStyleSheet("background-color:")
        self.label_ConstructionMethod.setStyleSheet("background-color:")
        self.label_Specification.setStyleSheet("background-color:")
        self.label_Manufacturer.setStyleSheet("background-color:")
        self.label_BatchDateCode.setStyleSheet("background-color:")
        self.label_SamplesQty.setStyleSheet("background-color:")
        self.label_Temperature.setStyleSheet("background-color:")
        self.label_DatasheetNominalCapacity.setStyleSheet("background-color:")
        self.label_CalculationNominalCapacity.setStyleSheet(
            "background-color:")
        self.label_AcceleratedAging.setStyleSheet("background-color:")
        self.label_RequiredUseableCapacity.setStyleSheet("background-color:")
        self.label_TesterLocation.setStyleSheet("background-color:")
        self.label_TestedBy.setStyleSheet("background-color:")
        self.label_TestProfile.setStyleSheet("background-color:")
        self.label_InputPath.setStyleSheet("background-color:")
        self.label_OutputPath.setStyleSheet("background-color:")
        self.label_Version.setStyleSheet("background-color:")
        self.pushButton_Run.setStyleSheet("background-color:")

    def checkinput(self) -> bool:
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
        if not self.lineEdit_Temperature.text():
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

    def init_thread(self) -> None:
        """
        初始化线程（现在由控制器管理）
        """
        # 线程管理已转移到控制器
        # 此方法保留以保持向后兼容性
        pass

    def get_threadinfo(self, threadstate, stateindex, threadinfo) -> None:
        # 正常运行状态处理
        if threadstate:
            # 处理取消状态
            if "canceling" in threadinfo:
                self.statusBar_BatteryAnalysis.showMessage("正在取消任务...")
                self.pushButton_Run.setText("取消中...")
                self.pushButton_Run.setEnabled(False)
            else:
                # 正常运行状态显示
                self.statusBar_BatteryAnalysis.showMessage("正在分析电池数据...")
                if stateindex == 0:
                    self.pushButton_Run.setText("Running.")
                if stateindex == 1:
                    self.pushButton_Run.setText("Running..")
                if stateindex == 2:
                    self.pushButton_Run.setText("Running...")
                if stateindex == 3:
                    self.pushButton_Run.setText("Running....")
        else:
            # 不再需要手动删除线程，由控制器管理线程生命周期

            # 任务完成处理
            if stateindex == 0 and "success" in threadinfo:
                # 关闭进度条
                self._close_progress_dialog()

                self.pushButton_Run.setText("Run")
                self.pushButton_Run.setStyleSheet("background-color:#00FF00")
                self.pushButton_Run.setEnabled(True)
                self.statusBar_BatteryAnalysis.showMessage("电池分析完成！")

                # 显示成功提示
                QW.QMessageBox.information(
                    self,
                    "分析完成",
                    "电池分析已成功完成！\n\n报告已生成到指定输出路径。",
                    QW.QMessageBox.StandardButton.Ok
                )

            # 日期不一致错误处理 (stateindex == 3)
            elif stateindex == 3:
                # 关闭进度条
                self._close_progress_dialog()

                self.pushButton_Run.setText("Rerun")
                self.pushButton_Run.setStyleSheet("background-color:red")
                self.pushButton_Run.setEnabled(True)

                # 日期不一致错误消息处理
                error_title = "日期不一致错误"
                error_details = threadinfo

                # 构建日期不一致错误的具体建议
                suggestions = [
                    "请检查Excel文件中的Test Date字段是否correct",
                    "确保Test Date与实际测试日期一致",
                    "修正日期后重新运行分析"
                ]

                # 构建完整的错误消息
                full_error_msg = f"{error_title}:\n\n{error_details}\n\n建议解决步骤:\n"
                full_error_msg += "\n".join([f"- {s}" for s in suggestions])

                # 显示专门的日期不一致错误对话框
                QW.QMessageBox.critical(
                    self,
                    error_title,
                    full_error_msg,
                    QW.QMessageBox.StandardButton.Ok
                )

                self.statusBar_BatteryAnalysis.showMessage(
                    f"[错误]: {error_title}")

            # 电池分析错误处理 (stateindex == 1)
            elif stateindex == 1:
                # 关闭进度条
                self._close_progress_dialog()

                self.pushButton_Run.setText("Rerun")
                self.pushButton_Run.setStyleSheet("background-color:red")
                self.pushButton_Run.setEnabled(True)

                # 增强的错误消息处理
                error_title = "电池分析错误"
                error_msg = "分析电池数据when出现错误。"
                error_details = threadinfo

                # 根据错误内容提供更具体的建议
                suggestions = []
                if "input path" in error_details.lower() or "找不到文件" in error_details:
                    suggestions.append("请检查输入路径是否correct")
                    suggestions.append("确保包含必要的数据文件")
                if "格式" in error_details or "format" in error_details.lower():
                    suggestions.append("检查数据文件格式是否符合要求")
                if "权限" in error_details or "permission" in error_details.lower():
                    suggestions.append("确保您有足够的文件操作权限")

                # 如果没有具体建议，提供通用建议
                if not suggestions:
                    suggestions.append("检查输入数据的完整性")
                    suggestions.append("确保文件路径不包含特殊字符")
                    suggestions.append("重新选择有效的输入和输出目录")

                # 构建完整的错误消息
                full_error_msg = f"{error_msg}\n\n错误详情:\n{error_details}\n\n建议解决步骤:\n"
                full_error_msg += "\n".join([f"- {s}" for s in suggestions])

                # 显示详细的错误对话框
                QW.QMessageBox.critical(
                    self,
                    error_title,
                    full_error_msg,
                    QW.QMessageBox.StandardButton.Ok
                )

                self.statusBar_BatteryAnalysis.showMessage(
                    f"[错误]: {error_title}")

            # 文件写入错误处理 (stateindex == 2)
            elif stateindex == 2:
                # 关闭进度条
                self._close_progress_dialog()

                self.pushButton_Run.setText("Rerun")
                self.pushButton_Run.setStyleSheet("background-color:red")
                self.pushButton_Run.setEnabled(True)

                error_title = "报告生成错误"
                error_msg = "生成分析报告when出现错误。"
                error_details = threadinfo

                suggestions = [
                    "检查输出路径是否存在且可写",
                    "确保有足够的磁盘空间",
                    "关闭可能正在使用输出文件的其他程序",
                    "尝试选择不同的输出目录"
                ]

                full_error_msg = f"{error_msg}\n\n错误详情:\n{error_details}\n\n建议解决步骤:\n"
                full_error_msg += "\n".join([f"- {s}" for s in suggestions])

                QW.QMessageBox.critical(
                    self,
                    error_title,
                    full_error_msg,
                    QW.QMessageBox.StandardButton.Ok
                )

                self.statusBar_BatteryAnalysis.showMessage(
                    f"[错误]: {error_title}")

            # 其他错误情况
            else:
                self.pushButton_Run.setText("Rerun")
                self.pushButton_Run.setStyleSheet("background-color:red")
                self.pushButton_Run.setEnabled(True)
                self.statusBar_BatteryAnalysis.showMessage(
                    f"[错误]: {threadinfo}")

    def set_version(self) -> None:
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
        """窗口大小改变when的事件处理函数"""
        # 调用父类的resizeEvent以确保正常的事件处理
        super().resizeEvent(event)

        # 调整表格列宽以适应窗口大小
        if hasattr(self, 'tableWidget_TestInformation'):
            # 计算可用宽度（减去边距和滚动条）
            available_width = self.tableWidget_TestInformation.width() - 20

            # 设置列宽比例
            # 第0列（15%）
            self.tableWidget_TestInformation.horizontalHeader(
            ).resizeSection(0, int(available_width * 0.15))
            # 第1列（25%）
            self.tableWidget_TestInformation.horizontalHeader(
            ).resizeSection(1, int(available_width * 0.25))
            # 第2列（剩余空间）
            self.tableWidget_TestInformation.horizontalHeader(
            ).resizeSection(2, int(available_width * 0.6))


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
