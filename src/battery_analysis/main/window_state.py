"""主窗口由 UIBuilder 和初始化流水线填充的属性契约。

仅声明类型，不创建控件或提前初始化服务，避免改变现有启动时序。
"""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

import PyQt6.QtCore as QC
import PyQt6.QtGui as QG
import PyQt6.QtWidgets as QW

if TYPE_CHECKING:
    from battery_analysis.main.business_logic.validation_manager import ValidationManager
    from battery_analysis.main.handlers.temperature_handler import TemperatureHandler
    from battery_analysis.main.ndax_converter_window import NdaxConverterWindow
    from battery_analysis.main.ui_components.config_manager import ConfigManager
    from battery_analysis.main.ui_components.menu_manager import MenuManager
    from battery_analysis.main.ui_components.table_manager import TableManager
    from battery_analysis.main.ui_components.theme_manager import ThemeManager
    from battery_analysis.main.ui_components.ui_manager import UIManager
    from battery_analysis.main.utils.signal_connector import SignalConnector
    from battery_analysis.main.utils.validator_utils import Checker


class MainWindowState:
    """供窗口 Mixin 和 UI 构建器共用的已知属性。"""

    centralwidget: QW.QWidget
    chart_area_widget: QW.QWidget
    chart_container: QW.QWidget
    chart_control_panel: QW.QWidget
    frame_RunButton: QW.QFrame
    scrollArea: QW.QScrollArea
    progressBar: QW.QProgressBar
    statusBar_BatteryAnalysis: QW.QStatusBar
    tableWidget_TestInformation: QW.QTableWidget
    groupBox_BatteryConfig: QW.QGroupBox
    groupBox_Path: QW.QGroupBox
    groupBox_TestConfig: QW.QGroupBox
    groupBox_TestInformation: QW.QGroupBox
    comboBox_BatteryType: QW.QComboBox
    comboBox_ConstructionMethod: QW.QComboBox
    comboBox_Manufacturer: QW.QComboBox
    comboBox_ReportedBy: QW.QComboBox
    comboBox_Specification_Method: QW.QComboBox
    comboBox_Specification_Type: QW.QComboBox
    comboBox_Temperature: QW.QComboBox
    comboBox_TestedBy: QW.QComboBox
    comboBox_TesterLocation: QW.QComboBox
    label_AcceleratedAging: QW.QLabel
    label_BatchDateCode: QW.QLabel
    label_BatteryType: QW.QLabel
    label_CalculationNominalCapacity: QW.QLabel
    label_ConstructionMethod: QW.QLabel
    label_DatasheetNominalCapacity: QW.QLabel
    label_InputPath: QW.QLabel
    label_Manufacturer: QW.QLabel
    label_OutputPath: QW.QLabel
    label_ReportedBy: QW.QLabel
    label_RequiredUseableCapacity: QW.QLabel
    label_SamplesQty: QW.QLabel
    label_Specification: QW.QLabel
    label_Temperature: QW.QLabel
    label_TemperatureType: QW.QLabel
    label_TestProfile: QW.QLabel
    label_TestedBy: QW.QLabel
    label_TesterLocation: QW.QLabel
    label_Version: QW.QLabel
    lineEdit_BatchDateCode: QW.QLineEdit
    lineEdit_CalculationNominalCapacity: QW.QLineEdit
    lineEdit_DatasheetNominalCapacity: QW.QLineEdit
    lineEdit_InputPath: QW.QLineEdit
    lineEdit_OutputPath: QW.QLineEdit
    lineEdit_RequiredUseableCapacity: QW.QLineEdit
    lineEdit_SamplesQty: QW.QLineEdit
    lineEdit_TestProfile: QW.QLineEdit
    lineEdit_Version: QW.QLineEdit
    pushButton_InputPath: QW.QPushButton
    pushButton_Run: QW.QPushButton
    pushButton_TestProfile: QW.QPushButton
    spinBox_AcceleratedAging: QW.QSpinBox
    spinBox_Temperature: QW.QSpinBox
    actionAbout: QG.QAction
    actionAnalyze_Data: QG.QAction
    actionBatteryChartViewer: QG.QAction
    actionConfiguration: QG.QAction
    actionCopy: QG.QAction
    actionCut: QG.QAction
    actionDark_Theme: QG.QAction
    actionExit: QG.QAction
    actionLight_Theme: QG.QAction
    actionNdaxConverter: QG.QAction
    actionOnline_Help: QG.QAction
    actionPaste: QG.QAction
    actionPreferences: QG.QAction
    actionReset_Zoom: QG.QAction
    actionShow_Statusbar: QG.QAction
    actionUser_Mannual: QG.QAction
    actionZoom_In: QG.QAction
    actionZoom_Out: QG.QAction
    config_manager: ConfigManager
    menu_manager: MenuManager
    signal_connector: SignalConnector
    table_manager: TableManager
    theme_manager: ThemeManager
    ui_manager: UIManager
    validation_manager: ValidationManager
    temperature_handler: TemperatureHandler
    checker_battery_type: Checker
    specification_type: str
    construction_method: str
    _ndax_converter_window: NdaxConverterWindow | None
    # 服务注册表按名称返回不同实现；具体服务在消费者处验证。
    _get_service: Callable[[str], Any]
    focusWidget: Callable[[], QW.QWidget | None]
    _resize_timer: QC.QTimer | None
