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
from battery_analysis.main.handlers.temperature_handler import TemperatureHandler
from battery_analysis.main.interfaces.ivisualizer import IVisualizer
from battery_analysis.main.managers.environment_manager import EnvironmentManager
from battery_analysis.main.managers.path_manager import PathManager
from battery_analysis.main.managers.report_manager import ReportManager
from battery_analysis.main.managers.visualization_manager import VisualizationManager
from battery_analysis.main.services.service_container import get_service_container
from battery_analysis.main.ui_components import ConfigManager, DialogManager, MenuManager, ProgressDialog, TableManager, UIManager
from battery_analysis.main.utils import Checker, EnvironmentAdapter, FileUtils, SignalConnector
from battery_analysis.main.business_logic.validation_manager import ValidationManager
from battery_analysis.resources import resources_rc
from battery_analysis.ui import ui_main_window
from battery_analysis.utils import temperature_utils

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')




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
        
        # 初始化自定义管理器和处理器
        self.temperature_handler = TemperatureHandler(self)
        self.report_manager = ReportManager(self)
        self.path_manager = PathManager(self)
        self.environment_manager = EnvironmentManager(self)
        self.visualization_manager = VisualizationManager(self)
        
        # 现在初始化环境信息，因为environment_manager已经创建
        self._initialize_environment_info()
        # 确保环境信息包含必要的键
        self._ensure_env_info_keys()
        
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
        
        # 初始化表格管理器
        self.table_manager = TableManager(self)
        
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
            # 使用FileUtils获取所有可能的图标路径
            icon_paths = FileUtils.get_icon_paths(self.env_detector, self.current_directory)
            
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
            # 使用FileUtils获取所有可能的手册路径
            manual_paths = FileUtils.get_manual_paths(self.current_directory)
            
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
                f"{_("cannot_open_user_manual", "无法打开用户手册")}: {str(e)}",
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
        初始化环境信息，委托给EnvironmentManager
        """
        self.environment_manager.initialize_environment_info()
    
    def _ensure_env_info_keys(self):
        """
        确保环境信息包含必要的键，委托给EnvironmentManager
        """
        self.environment_manager.ensure_env_info_keys()
    
    def run_visualizer(self, xml_path=None) -> None:
        """运行可视化工具，使用工厂模式解耦依赖"""
        # 委托给可视化管理器
        self.visualization_manager.run_visualizer(xml_path)
    
    def show_visualizer_error(self, error_msg: str):
        """在主线程中显示可视化工具错误消息"""
        self.visualization_manager.show_visualizer_error(error_msg)

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
        validation_manager = ValidationManager(self)
        validation_manager.validate_version()

    def validate_input_path(self) -> None:
        """验证输入路径是否存在，委托给ValidationManager"""
        validation_manager = ValidationManager(self)
        validation_manager.validate_input_path()

    def validate_required_fields(self) -> None:
        """验证必填字段是否为空，委托给ValidationManager"""
        validation_manager = ValidationManager(self)
        validation_manager.validate_required_fields()

    def check_batterytype(self) -> None:
        """检查电池类型并更新相关UI组件，委托给ValidationManager"""
        validation_manager = ValidationManager(self)
        validation_manager.check_batterytype()
    def check_specification(self) -> None:
        """检查规格并更新相关UI组件，委托给ValidationManager"""
        validation_manager = ValidationManager(self)
        validation_manager.check_specification()
    def set_table(self) -> None:
        """
        根据配置文件设置测试信息表格，委托给table_manager
        """
        self.table_manager.set_table()

    def on_temperature_type_changed(self, index):
        """处理温度类型变化事件，控制spinBox_Temperature的启用状态"""
        # 委托给温度处理器
        self.temperature_handler.on_temperature_type_changed()
    
    def _detect_temperature_type_from_xml(self, xml_path: str) -> None:
        """
        根据XML文件名自动检测温度类型
        
        Args:
            xml_path: XML文件的完整路径
        """
        try:
            # 使用温度处理器检测温度类型
            temperature_type = self.temperature_handler.detect_temperature_type_from_xml(xml_path)
            
            # 获取文件名用于日志
            file_name = os.path.basename(xml_path)
            
            # 使用温度处理器更新UI
            self.temperature_handler.update_temperature_ui(temperature_type)
            
            # 记录日志
            if temperature_type.value == "Freezer Temperature":
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
    def select_testprofile(self) -> None:
        """选择测试配置文件"""
        try:
            # 1. 选择测试配置文件
            selected_file = self.path_manager.select_test_profile()
            
            if not selected_file:
                return
            
            # 2. 验证测试配置文件
            if not self.path_manager.validate_test_profile(selected_file):
                return
            
            # 3. 显示选中的文件路径
            self.lineEdit_TestProfile.setText(selected_file)
            
            # 4. 获取父目录
            parent_dir = self.path_manager.get_parent_directory(selected_file)
            if not parent_dir:
                return
            
            # 5. 设置输入路径
            self.path_manager.set_input_path(parent_dir)
            
            # 6. 设置输出路径
            if not self.path_manager.set_output_path(parent_dir):
                return
            
            # 7. 发出版本设置信号
            self.sigSetVersion.emit()
            
            # 8. 更新当前目录
            self.current_directory = parent_dir
            self.logger.info("设置当前目录为项目根目录: %s", parent_dir)
            
            # 9. 根据XML文件名自动检测温度类型
            self._detect_temperature_type_from_xml(selected_file)
            
        except (OSError, ValueError, TypeError, RuntimeError, FileNotFoundError, PermissionError) as e:
            self.logger.error("选择Test Profile时发生错误: %s", e)
            QW.QMessageBox.critical(
                self,
                "错误",
                f"处理Test Profile时发生错误:\n{str(e)}",
                QW.QMessageBox.StandardButton.Ok
            )

    def select_inputpath(self) -> None:
        """
        选择输入路径，委托给path_manager
        """
        self.path_manager.select_inputpath()

    def select_outputpath(self) -> None:
        """
        选择输出路径，委托给path_manager
        """
        self.path_manager.select_outputpath()

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
        # 使用温度处理器构建温度值字符串
        temperature_value = self.temperature_handler.get_temperature_value()
        
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
        """
        保存表格数据到配置文件，委托给table_manager
        """
        self.table_manager.save_table()

    def init_widgetcolor(self) -> None:
        """
        清除所有标签的背景样式，委托给ui_manager
        具体样式由checkinput方法根据验证结果设置
        """
        self.ui_manager.init_widgetcolor()

    def checkinput(self) -> bool:
        """检查所有输入是否完整有效，委托给ValidationManager"""
        validation_manager = ValidationManager(self)
        return validation_manager.checkinput()
    def _open_report(self, dialog=None):
        """打开生成的docx格式报告"""
        self.report_manager.open_report(dialog)
        
    def _open_report_path(self, dialog=None):
        """打开报告所在的文件夹"""
        self.report_manager.open_report_path(dialog)
        
    def _show_analysis_complete_dialog(self):
        """
        显示分析完成对话框，包含"打开报告"、"打开路径"和"确定"按钮
        """
        self.report_manager.show_analysis_complete_dialog()
        
    def rename_pltPath(self, strTestDate):
        """
        根据测试日期重命名图表保存路径，委托给config_manager
        
        Args:
            strTestDate: 测试日期字符串
        """
        self.config_manager.rename_pltPath(strTestDate)

    def update_config(self, test_info) -> None:
        """
        更新配置文件中的图表相关设置，委托给config_manager
        
        Args:
            test_info: 测试信息列表
        """
        self.config_manager.update_config(test_info)

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


