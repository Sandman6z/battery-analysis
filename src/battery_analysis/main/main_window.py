"""
电池分析主窗口模块

这个模块实现了电池分析应用的主窗口界面和核心功能，包括：
- 窗口初始化和布局设置
- 配置文件管理
- 控制器连接和信号处理
- 用户交互界面
"""

# 标准库导入
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
from battery_analysis.main.managers.initialization_manager import InitializationManager
from battery_analysis.main.utils import FileUtils
from battery_analysis.resources import resources_rc
from battery_analysis.ui import ui_main_window
from battery_analysis.utils.config_parser import safe_int_convert, safe_float_convert

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class Main(QW.QMainWindow, ui_main_window.Ui_MainWindow):
    sigSetVersion = QC.pyqtSignal()

    def __init__(self) -> None:
        super().__init__()

        # 使用初始化管理器处理所有初始化逻辑
        init_manager = InitializationManager(self)
        init_manager.initialize()

        # 初始化窗口和部件
        self.init_window()
        self.init_widget()

    # ------------------------------
    # 初始化相关方法
    # ------------------------------
    def _initialize_current_and_voltage_levels(self):
        """
        初始化电流和电压级别配置
        """
        listPulseCurrent = self.get_config("BatteryConfig/PulseCurrent")
        listCutoffVoltage = self.get_config("BatteryConfig/CutoffVoltage")

        # 处理可能包含浮点数的电流值
        try:
            self.listCurrentLevel = [safe_int_convert(listPulseCurrent[c].strip())
                                     for c in range(len(listPulseCurrent))]
        except (ValueError, TypeError):
            # 如果转换失败，使用默认值
            self.listCurrentLevel = [0] * len(listPulseCurrent)

        self.listVoltageLevel = [
            safe_float_convert(listCutoffVoltage[c].strip()) for c in range(len(listCutoffVoltage))]

    # ------------------------------
    # 服务和控制器获取方法
    # ------------------------------
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
                self._services[service_name] = self._service_container.get(
                    service_name)
                self.logger.debug("Successfully retrieved service: %s", service_name)
            except TypeError as e:
                self.logger.warning(
                    "Failed to get service %s due to type error: %s", service_name, e)
                self.logger.debug("TypeError details: %s", str(e))
                self._services[service_name] = None
            except AttributeError as e:
                self.logger.warning(
                    "Failed to get service %s due to attribute error: %s", service_name, e)
                self.logger.debug("AttributeError details: %s", str(e))
                self._services[service_name] = None
            except OSError as e:
                self.logger.warning(
                    "Failed to get service %s due to OS error: %s", service_name, e)
                self.logger.debug("OSError details: %s", str(e))
                self._services[service_name] = None
            except ValueError as e:
                self.logger.warning(
                    "Failed to get service %s due to value error: %s", service_name, e)
                self.logger.debug("ValueError details: %s", str(e))
                self._services[service_name] = None
            except ImportError as e:
                self.logger.warning(
                    "Failed to get service %s due to import error: %s", service_name, e)
                self.logger.debug("ImportError details: %s", str(e))
                self._services[service_name] = None
            except Exception as e:
                # 捕获其他未预期的异常
                self.logger.warning(
                    "Failed to get service %s due to unexpected error: %s", service_name, e)
                self.logger.debug("Unexpected error details: %s", str(e))
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
                self._controllers[controller_name] = self._service_container.get(
                    controller_name)
                self.logger.debug("Successfully retrieved controller: %s", controller_name)
            except TypeError as e:
                self.logger.warning(
                    "Failed to get controller %s due to type error: %s", controller_name, e)
                self.logger.debug("TypeError details: %s", str(e))
                self._controllers[controller_name] = None
            except AttributeError as e:
                self.logger.warning(
                    "Failed to get controller %s due to attribute error: %s", controller_name, e)
                self.logger.debug("AttributeError details: %s", str(e))
                self._controllers[controller_name] = None
            except OSError as e:
                self.logger.warning(
                    "Failed to get controller %s due to OS error: %s", controller_name, e)
                self.logger.debug("OSError details: %s", str(e))
                self._controllers[controller_name] = None
            except ValueError as e:
                self.logger.warning(
                    "Failed to get controller %s due to value error: %s", controller_name, e)
                self.logger.debug("ValueError details: %s", str(e))
                self._controllers[controller_name] = None
            except ImportError as e:
                self.logger.warning(
                    "Failed to get controller %s due to import error: %s", controller_name, e)
                self.logger.debug("ImportError details: %s", str(e))
                self._controllers[controller_name] = None
            except Exception as e:
                # 捕获其他未预期的异常
                self.logger.warning(
                    "Failed to get controller %s due to unexpected error: %s", controller_name, e)
                self.logger.debug("Unexpected error details: %s", str(e))
                self._controllers[controller_name] = None
        return self._controllers[controller_name]

    # ------------------------------
    # 配置相关方法
    # ------------------------------
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

    # ------------------------------
    # 窗口和UI管理方法
    # ------------------------------
    def _load_application_icon(self) -> QG.QIcon:
        """
        加载应用程序图标，使用环境检测器来找到正确的路径

        Returns:
            QIcon: 应用程序图标
        """
        try:
            # 使用FileUtils获取所有可能的图标路径
            icon_paths = FileUtils.get_icon_paths(
                self.env_detector, self.current_directory)

            # 遍历所有可能的路径，找到第一个存在的
            for icon_path in icon_paths:
                if icon_path.exists():
                    self.logger.debug(_("found_app_icon", "找到应用图标: %s"), icon_path)
                    return QG.QIcon(str(icon_path))

            # 如果都找不到，使用默认图标
            self.logger.warning(_("app_icon_not_found", "未找到应用图标文件，使用默认图标"))
            return QG.QIcon()

        except (OSError, TypeError, ValueError, RuntimeError, ImportError) as e:
            # 捕获所有可能的异常，确保应用能正常启动
            self.logger.error(_("app_icon_load_failed", "加载应用图标失败: %s"), e)
            return QG.QIcon()

    # ------------------------------
    # 语言相关方法
    # ------------------------------
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
            self.signal_connector.progress_dialog.setWindowTitle(
                _("progress_title", "Battery Analysis Progress"))
            self.signal_connector.progress_dialog.status_label.setText(
                _("progress_ready", "Ready to start analysis..."))

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

    # ------------------------------
    # 用户交互方法
    # ------------------------------
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
        """显示用户手册，委托给help_manager"""
        self.help_manager.show_user_manual()

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

    # ------------------------------
    # 电池分析功能方法
    # ------------------------------
    def calculate_battery(self) -> None:
        """执行电池计算，使用命令模式"""
        self.calculate_battery_command.execute()

    def analyze_data(self) -> None:
        """分析数据，使用命令模式"""
        self.analyze_data_command.execute()

    def generate_report(self) -> None:
        """生成报告，使用命令模式"""
        self.generate_report_command.execute()

    # ------------------------------
    # 环境和信息管理方法
    # ------------------------------
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

    # ------------------------------
    # 可视化相关方法
    # ------------------------------
    def run_visualizer(self, xml_path=None) -> None:
        """运行可视化工具，使用工厂模式解耦依赖"""
        # 委托给可视化管理器
        self.visualization_manager.run_visualizer(xml_path)

    def show_visualizer_error(self, error_msg: str):
        """在主线程中显示可视化工具错误消息"""
        self.visualization_manager.show_visualizer_error(error_msg)

    def batch_processing(self) -> None:
        """批量处理，使用命令模式"""
        self.batch_processing_command.execute()

    def save_settings(self) -> None:
        """保存当前设置到用户配置文件，委托给config_manager"""
        self.config_manager.save_user_settings()

    # ------------------------------
    # 报告相关方法
    # ------------------------------
    def export_report(self) -> None:
        """导出报告，使用命令模式"""
        self.export_report_command.execute()

    def set_theme(self, theme_name) -> None:
        """设置应用程序主题，委托给theme_manager处理"""
        self.theme_manager.set_theme(theme_name)

    def toggle_statusbar(self) -> None:
        """切换状态栏的显示/隐藏状态，委托给menu_manager处理"""
        self.menu_manager.toggle_statusbar()

    # ------------------------------
    # 验证相关方法
    # ------------------------------
    def validate_version(self) -> None:
        """验证版本号格式并提供实时反馈，委托给ValidationManager"""
        self.validation_manager.validate_version()

    def validate_input_path(self) -> None:
        """验证输入路径是否存在，委托给ValidationManager"""
        self.validation_manager.validate_input_path()

    def validate_required_fields(self) -> None:
        """验证必填字段是否为空，委托给ValidationManager"""
        self.validation_manager.validate_required_fields()

    def check_batterytype(self) -> None:
        """检查电池类型并更新相关UI组件，委托给ValidationManager"""
        self.validation_manager.check_batterytype()

    def check_specification(self) -> None:
        """检查规格并更新相关UI组件，委托给ValidationManager"""
        self.validation_manager.check_specification()
    # ------------------------------
    # 表格相关方法
    # ------------------------------

    def set_table(self) -> None:
        """
        根据配置文件设置测试信息表格，委托给table_manager
        """
        self.table_manager.set_table()

    # ------------------------------
    # 温度相关方法
    # ------------------------------
    def on_temperature_type_changed(self, index):
        """处理温度类型变化事件，控制spinBox_Temperature的启用状态"""
        # 委托给温度处理器
        self.temperature_handler.on_temperature_type_changed()

    def get_xlsxinfo(self) -> None:
        '''
        获取Excel文件信息，委托给优化的DataProcessor处理
        '''
        # 调用优化版的data_processor获取Excel信息
        self.data_processor.get_xlsxinfo()

    def get_version(self) -> None:
        """计算并设置电池分析的版本号，委托给已初始化的version_manager"""
        self.version_manager.get_version()

    # ------------------------------
    # 路径选择方法
    # ------------------------------
    def select_testprofile(self) -> None:
        """
        选择测试配置文件，委托给test_profile_manager
        """
        self.test_profile_manager.select_testprofile()

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
        """
        运行电池分析，使用命令模式
        """
        self.run_analysis_command.execute()

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
        return self.validation_manager.checkinput()

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
