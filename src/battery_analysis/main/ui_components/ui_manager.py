"""
UI管理器模块

这个模块实现了电池分析应用的UI管理功能，包括：
- 窗口初始化和布局设置
- 部件初始化和配置
- 可访问性设置
- 信号连接管理
"""

# 标准库导入
import logging
import os
import re

# 第三方库导入
import PyQt6.QtCore as QC
import PyQt6.QtGui as QG
import PyQt6.QtWidgets as QW

# 本地应用/库导入
from battery_analysis.i18n.language_manager import _
from battery_analysis.main.user_settings_manager import UserSettingsManager


class UIManager:
    """
    UI管理器类，负责UI初始化和设置
    """
    
    def __init__(self, main_window):
        """
        初始化UI管理器
        
        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        # 初始化用户设置管理器
        self.user_settings_manager = UserSettingsManager(self.main_window.config_path)
    
    def init_window(self):
        """
        初始化窗口设置
        """
        # 使用WindowSetup组件进行窗口初始化
        from battery_analysis.main.ui_components.window_setup import WindowSetup
        window_setup = WindowSetup(self.main_window)
        window_setup.init_window()
    
    def _load_application_icon(self):
        """
        加载应用程序图标
        """
        # 使用WindowSetup组件加载应用图标
        from battery_analysis.main.ui_components.window_setup import WindowSetup
        window_setup = WindowSetup(self.main_window)
        window_setup._load_application_icon()
    
    def init_widget(self):
        """
        初始化部件设置
        """
        if self.main_window.b_has_config:
            self.main_window.statusBar_BatteryAnalysis.showMessage("status:ok")

        self.init_lineedit()
        self.init_combobox()
        self.init_table()
        self.setup_accessibility()
        self.connect_widget()
    
    def setup_accessibility(self):
        """
        设置UI控件的可访问性属性
        """
        try:
            # 设置控件的可访问名称和描述
            # 测试配置组
            self.main_window.groupBox_TestConfig.setAccessibleName(_("access_test_config", "测试配置"))
            self.main_window.groupBox_TestConfig.setAccessibleDescription(_("access_test_config_desc", "包含测试相关配置的设置"))
            
            # 电池配置组
            self.main_window.groupBox_BatteryConfig.setAccessibleName(_("access_battery_config", "电池配置"))
            self.main_window.groupBox_BatteryConfig.setAccessibleDescription(_("access_battery_config_desc", "包含电池相关配置的设置"))
            
            # 运行按钮
            self.main_window.pushButton_Run.setAccessibleName(_("access_run_button", "运行分析"))
            self.main_window.pushButton_Run.setAccessibleDescription(_("access_run_button_desc", "开始电池分析任务"))
            
            # 文件选择按钮
            self.main_window.pushButton_TestProfile.setAccessibleName(_("access_test_profile_button", "选择测试文件"))
            self.main_window.pushButton_TestProfile.setAccessibleDescription(_("access_test_profile_desc", "选择电池测试配置文件"))
            self.main_window.pushButton_InputPath.setAccessibleName(_("access_input_path_button", "选择输入路径"))
            self.main_window.pushButton_InputPath.setAccessibleDescription(_("access_input_path_desc", "选择输入数据文件路径"))
            self.main_window.pushButton_OutputPath.setAccessibleName(_("access_output_path_button", "选择输出路径"))
            self.main_window.pushButton_OutputPath.setAccessibleDescription(_("access_output_path_desc", "选择分析结果输出路径"))
            
            # 设置焦点策略
            # 确保所有交互控件都支持键盘焦点
            interactive_widgets = [
                self.main_window.comboBox_BatteryType,
                self.main_window.comboBox_ConstructionMethod,
                self.main_window.comboBox_Specification_Type,
                self.main_window.comboBox_Specification_Method,
                self.main_window.comboBox_Manufacturer,
                self.main_window.lineEdit_BatchDateCode,
                self.main_window.lineEdit_SamplesQty,
                self.main_window.comboBox_Temperature,
                self.main_window.spinBox_Temperature,
                self.main_window.lineEdit_DatasheetNominalCapacity,
                self.main_window.lineEdit_CalculationNominalCapacity,
                self.main_window.spinBox_AcceleratedAging,
                self.main_window.lineEdit_RequiredUseableCapacity,
                self.main_window.comboBox_TesterLocation,
                self.main_window.comboBox_TestedBy,
                self.main_window.comboBox_ReportedBy,
                self.main_window.lineEdit_TestProfile,
                self.main_window.pushButton_TestProfile,
                self.main_window.lineEdit_InputPath,
                self.main_window.pushButton_InputPath,
                self.main_window.lineEdit_OutputPath,
                self.main_window.pushButton_OutputPath,
                self.main_window.pushButton_Run
            ]
            
            for widget in interactive_widgets:
                widget.setFocusPolicy(QC.Qt.FocusPolicy.ClickFocus | QC.Qt.FocusPolicy.TabFocus)
            
            # 设置合理的键盘焦点顺序
            # 测试配置部分
            QW.QWidget.setTabOrder(self.main_window.comboBox_TesterLocation, self.main_window.comboBox_TestedBy)
            QW.QWidget.setTabOrder(self.main_window.comboBox_TestedBy, self.main_window.lineEdit_TestProfile)
            QW.QWidget.setTabOrder(self.main_window.lineEdit_TestProfile, self.main_window.pushButton_TestProfile)
            
            # 电池配置部分
            QW.QWidget.setTabOrder(self.main_window.pushButton_TestProfile, self.main_window.comboBox_BatteryType)
            QW.QWidget.setTabOrder(self.main_window.comboBox_BatteryType, self.main_window.comboBox_ConstructionMethod)
            QW.QWidget.setTabOrder(self.main_window.comboBox_ConstructionMethod, self.main_window.comboBox_Specification_Type)
            QW.QWidget.setTabOrder(self.main_window.comboBox_Specification_Type, self.main_window.comboBox_Specification_Method)
            QW.QWidget.setTabOrder(self.main_window.comboBox_Specification_Method, self.main_window.comboBox_Manufacturer)
            QW.QWidget.setTabOrder(self.main_window.comboBox_Manufacturer, self.main_window.lineEdit_BatchDateCode)
            QW.QWidget.setTabOrder(self.main_window.lineEdit_BatchDateCode, self.main_window.lineEdit_SamplesQty)
            QW.QWidget.setTabOrder(self.main_window.lineEdit_SamplesQty, self.main_window.comboBox_Temperature)
            QW.QWidget.setTabOrder(self.main_window.comboBox_Temperature, self.main_window.spinBox_Temperature)
            QW.QWidget.setTabOrder(self.main_window.spinBox_Temperature, self.main_window.lineEdit_DatasheetNominalCapacity)
            QW.QWidget.setTabOrder(self.main_window.lineEdit_DatasheetNominalCapacity, self.main_window.lineEdit_CalculationNominalCapacity)
            QW.QWidget.setTabOrder(self.main_window.lineEdit_CalculationNominalCapacity, self.main_window.spinBox_AcceleratedAging)
            QW.QWidget.setTabOrder(self.main_window.spinBox_AcceleratedAging, self.main_window.lineEdit_RequiredUseableCapacity)
            
            # 路径配置部分
            QW.QWidget.setTabOrder(self.main_window.lineEdit_RequiredUseableCapacity, self.main_window.lineEdit_InputPath)
            QW.QWidget.setTabOrder(self.main_window.lineEdit_InputPath, self.main_window.pushButton_InputPath)
            QW.QWidget.setTabOrder(self.main_window.pushButton_InputPath, self.main_window.lineEdit_OutputPath)
            QW.QWidget.setTabOrder(self.main_window.lineEdit_OutputPath, self.main_window.pushButton_OutputPath)
            
            # 最终运行按钮
            QW.QWidget.setTabOrder(self.main_window.pushButton_OutputPath, self.main_window.pushButton_Run)
            
            # 确保表格支持键盘导航
            if hasattr(self.main_window, 'tableWidget_TestInformation'):
                self.main_window.tableWidget_TestInformation.setAccessibleName(_("access_test_info_table", "测试信息表格"))
                self.main_window.tableWidget_TestInformation.setAccessibleDescription(_("access_test_info_table_desc", "包含测试设备和软件版本信息的表格"))
                self.main_window.tableWidget_TestInformation.setFocusPolicy(QC.Qt.FocusPolicy.ClickFocus | QC.Qt.FocusPolicy.TabFocus)
            
            self.logger.info("可访问性设置已完成")
        except (AttributeError, TypeError, RuntimeError) as e:
            self.logger.warning("设置可访问性属性失败: %s", e)
    
    def init_lineedit(self):
        """
        初始化输入框设置
        """
        # 数字输入限制
        reg = QC.QRegularExpression(r"^\d*$")
        validator = QG.QRegularExpressionValidator(self.main_window)
        validator.setRegularExpression(reg)
        
        self.main_window.lineEdit_SamplesQty.setValidator(validator)
        self.main_window.lineEdit_DatasheetNominalCapacity.setValidator(validator)
        self.main_window.lineEdit_CalculationNominalCapacity.setValidator(validator)
        self.main_window.lineEdit_RequiredUseableCapacity.setValidator(validator)
        
        # 增强版本号验证，支持x.y.z格式
        reg = QC.QRegularExpression(r"^\d+(\.\d+){0,2}$")
        validator = QG.QRegularExpressionValidator(self.main_window)
        validator.setRegularExpression(reg)
        self.main_window.lineEdit_Version.setValidator(validator)
        
        # 添加版本号实时验证
        self.main_window.lineEdit_Version.textChanged.connect(self.main_window.validate_version)

        # 为输入路径添加存在性验证
        self.main_window.lineEdit_InputPath.textChanged.connect(self.main_window.validate_input_path)

        # 为必填字段添加非空验证
        required_fields = [
            self.main_window.lineEdit_SamplesQty,
            self.main_window.lineEdit_DatasheetNominalCapacity,
            self.main_window.lineEdit_CalculationNominalCapacity,
            self.main_window.lineEdit_RequiredUseableCapacity
        ]
        for field in required_fields:
            field.textChanged.connect(self.main_window.validate_required_fields)

        self.main_window.lineEdit_TestProfile.setText("Not provided")
    
    def init_combobox(self):
        """
        初始化组合框设置
        """
        self.main_window.comboBox_BatteryType.addItems(
            self.main_window.get_config("BatteryConfig/BatteryType"))
        self.main_window.comboBox_ConstructionMethod.addItems(
            self.main_window.get_config("BatteryConfig/ConstructionMethod"))
        self.main_window.comboBox_Specification_Type.addItems(
            self.main_window.get_config("BatteryConfig/SpecificationTypeCoinCell"))
        self.main_window.comboBox_Specification_Type.addItems(
            self.main_window.get_config("BatteryConfig/SpecificationTypePouchCell"))
        self.main_window.comboBox_Specification_Method.addItems(
            self.main_window.get_config("BatteryConfig/SpecificationMethod"))
        self.main_window.comboBox_Manufacturer.addItems(
            self.main_window.get_config("BatteryConfig/Manufacturer"))
        self.main_window.comboBox_TesterLocation.addItems(
            self.main_window.get_config("TestConfig/TesterLocation"))
        
        # 获取TestedBy列表并同时用于comboBox_TestedBy和comboBox_ReportedBy
        tested_by_list = self.main_window.get_config("TestConfig/TestedBy")
        self.main_window.comboBox_TestedBy.addItems(tested_by_list)
        self.main_window.comboBox_ReportedBy.addItems(tested_by_list)
        
        # 为comboBox_Temperature添加选项
        self.main_window.comboBox_Temperature.addItems(["Room Temperature", "Freezer Temperature"])
        # 设置默认值为Room Temperature
        self.main_window.comboBox_Temperature.setCurrentText("Room Temperature")
        # 默认禁用spinBox_Temperature
        self.main_window.spinBox_Temperature.setEnabled(False)

        self.main_window.comboBox_BatteryType.setCurrentIndex(-1)
        self.main_window.comboBox_ConstructionMethod.setCurrentIndex(-1)
        self.main_window.comboBox_Specification_Type.setCurrentIndex(-1)
        self.main_window.comboBox_Specification_Method.setCurrentIndex(-1)
        self.main_window.comboBox_Manufacturer.setCurrentIndex(-1)
        self.main_window.comboBox_TesterLocation.setCurrentIndex(-1)
        self.main_window.comboBox_TestedBy.setCurrentIndex(-1)
        self.main_window.comboBox_ReportedBy.setCurrentIndex(-1)

        self.main_window.comboBox_ConstructionMethod.setEnabled(False)

        # 加载用户配置的设置
        self.load_user_settings()
    
    def init_table(self):
        """
        初始化表格设置
        """
        # 不再硬编码DataProcessingPlatforms的值，而是从配置文件中读取
        # 确保表格的最后一列自动拉伸
        self.main_window.tableWidget_TestInformation.horizontalHeader().setStretchLastSection(True)
        # 设置表格行高自动适应内容
        self.main_window.tableWidget_TestInformation.verticalHeader().setSectionResizeMode(
            QW.QHeaderView.ResizeMode.ResizeToContents)

        # 暂时断开cellChanged信号的连接，避免在初始化时触发保存操作
        try:
            self.main_window.tableWidget_TestInformation.cellChanged.disconnect()
        except TypeError:
            # 忽略TypeError异常，因为信号可能还没有被连接
            pass

        def set_span_item(item_text: str, row: int, col: int,
                          row_span: int = 1, col_span: int = 1,
                          editable: bool = False) -> None:
            # 只有当跨度大于1时才调用setSpan，避免单个单元格跨度的警告
            if row_span > 1 or col_span > 1:
                self.main_window.tableWidget_TestInformation.setSpan(
                    row, col, row_span, col_span)

            item = QW.QTableWidgetItem(item_text)
            if not editable:
                item.setFlags(QC.Qt.ItemFlag.ItemIsEnabled)
                item.setBackground(QG.QBrush(QG.QColor(242, 242, 242)))

            self.main_window.tableWidget_TestInformation.setItem(row, col, item)

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
    
    def connect_widget(self):
        """
        连接部件信号
        """
        self.main_window.comboBox_BatteryType.currentIndexChanged.connect(
            self.main_window.check_batterytype)
        self.main_window.comboBox_Specification_Type.currentIndexChanged.connect(
            self.main_window.check_specification)
        self.main_window.comboBox_Specification_Method.currentIndexChanged.connect(
            self.main_window.check_specification)
        self.main_window.comboBox_TesterLocation.currentIndexChanged.connect(
            self.main_window.set_table)
        
        # 添加温度类型变化的信号连接
        self.main_window.comboBox_Temperature.currentIndexChanged.connect(
            self.main_window.on_temperature_type_changed)
        
        self.main_window.lineEdit_InputPath.textChanged.connect(self.main_window.get_xlsxinfo)
        self.main_window.pushButton_TestProfile.clicked.connect(self.main_window.select_testprofile)
        self.main_window.pushButton_InputPath.clicked.connect(self.main_window.select_inputpath)
        self.main_window.pushButton_OutputPath.clicked.connect(self.main_window.select_outputpath)
        self.main_window.pushButton_Run.clicked.connect(self.main_window.run)
        self.main_window.sigSetVersion.connect(self.main_window.get_version)
    
    def update_ui_texts(self):
        """
        更新UI文本为当前语言
        """
        window_title = f"Battery Analyzer v{self.main_window.version}"
        self.main_window.setWindowTitle(window_title)
        
        # 更新进度对话框标题
        if hasattr(self.main_window, 'progress_dialog') and self.main_window.progress_dialog:
            self.main_window.progress_dialog.setWindowTitle(_("progress_title", "Battery Analysis Progress"))
            self.main_window.progress_dialog.status_label.setText(_("progress_ready", "Ready to start analysis..."))
    
    def update_statusbar_messages(self):
        """
        更新状态栏消息为当前语言
        """
        # 保存当前消息，以便切换语言后恢复
        current_message = self.main_window.statusBar_BatteryAnalysis.currentMessage()
        
        # 获取翻译后的状态消息
        status_ready = _("status_ready", "状态:就绪")
        
        # 更新状态栏
        if current_message in ("状态:就绪", "Ready"):
            self.main_window.statusBar_BatteryAnalysis.showMessage(status_ready)

    def load_user_settings(self):
        """
        加载用户配置文件中的设置
        """
        try:
            # 使用用户设置管理器加载配置
            user_config = self.user_settings_manager.load_user_settings()
            
            # 更新UI控件
            # 电池类型相关设置
            if user_config.get("BatteryType"):
                index = self.main_window.comboBox_BatteryType.findText(user_config["BatteryType"])
                if index >= 0:
                    self.main_window.comboBox_BatteryType.setCurrentIndex(index)

            if user_config.get("ConstructionMethod"):
                index = self.main_window.comboBox_ConstructionMethod.findText(
                    user_config["ConstructionMethod"])
                if index >= 0:
                    self.main_window.comboBox_ConstructionMethod.setCurrentIndex(index)

            if user_config.get("SpecificationType"):
                index = self.main_window.comboBox_Specification_Type.findText(
                    user_config["SpecificationType"])
                if index >= 0:
                    self.main_window.comboBox_Specification_Type.setCurrentIndex(index)

            if user_config.get("SpecificationMethod"):
                index = self.main_window.comboBox_Specification_Method.findText(
                    user_config["SpecificationMethod"])
                if index >= 0:
                    self.main_window.comboBox_Specification_Method.setCurrentIndex(
                        index)

            if user_config.get("Manufacturer"):
                index = self.main_window.comboBox_Manufacturer.findText(user_config["Manufacturer"])
                if index >= 0:
                    self.main_window.comboBox_Manufacturer.setCurrentIndex(index)

            if user_config.get("TesterLocation"):
                index = self.main_window.comboBox_TesterLocation.findText(
                    user_config["TesterLocation"])
                if index >= 0:
                    self.main_window.comboBox_TesterLocation.setCurrentIndex(index)

            if user_config.get("TestedBy"):
                index = self.main_window.comboBox_TestedBy.findText(user_config["TestedBy"])
                if index >= 0:
                    self.main_window.comboBox_TestedBy.setCurrentIndex(index)
                else:
                    # 如果找不到匹配项，直接设置文本（用于自定义输入的情况）
                    self.main_window.comboBox_TestedBy.setCurrentText(user_config["TestedBy"])

            if user_config.get("ReportedBy"):
                index = self.main_window.comboBox_ReportedBy.findText(user_config["ReportedBy"])
                if index >= 0:
                    self.main_window.comboBox_ReportedBy.setCurrentIndex(index)
                else:
                    # 如果找不到匹配项，直接设置文本（用于自定义输入的情况）
                    self.main_window.comboBox_ReportedBy.setCurrentText(user_config["ReportedBy"])

            # 加载温度设置
            if user_config.get("TemperatureType"):
                self.main_window.comboBox_Temperature.setCurrentText(user_config["TemperatureType"])
                # 同时更新spinBox的启用状态
                if user_config["TemperatureType"] == "Freezer Temperature":
                    self.main_window.spinBox_Temperature.setEnabled(True)
                else:
                    self.main_window.spinBox_Temperature.setEnabled(False)
            
            # 加载冷冻温度数值设置
            if user_config.get("FreezerTemperature"):
                try:
                    self.main_window.spinBox_Temperature.setValue(int(user_config["FreezerTemperature"]))
                except (ValueError, TypeError):
                    pass

            # 加载输出路径设置
            if user_config.get("OutputPath"):
                self.main_window.lineEdit_OutputPath.setText(user_config["OutputPath"])
                # 更新控制器的输出路径
                main_controller = self.main_window._get_controller("main_controller")
                if main_controller:
                    main_controller.set_project_context(
                        output_path=user_config["OutputPath"])
        except (AttributeError, TypeError, KeyError, OSError) as e:
            self.logger.error("加载用户设置失败: %s", e)
