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


class UIManager:
    """
    UI管理器类，负责UI初始化和设置
    """
    
    def __init__(self, main_window=None, ctx=None):
        """
        初始化UI管理器

        Args:
            main_window: 主窗口实例（旧接口）
            ctx: AppContext（新接口）
        """
        self.main_window = main_window
        self._ctx = ctx
        self.logger = logging.getLogger(__name__)
    
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
        self.setup_tooltips()
        self.connect_widget()
    
    def setup_accessibility(self):
        """
        设置UI控件的可访问性属性
        """
        try:
            # 设置控件的可访问名称和描述
            # 测试配置组
            self.main_window.groupBox_TestConfig.setAccessibleName(_("Test Config"))
            self.main_window.groupBox_TestConfig.setAccessibleDescription(_("Settings related to the test configuration"))

            # 电池配置组
            self.main_window.groupBox_BatteryConfig.setAccessibleName(_("Battery Config"))
            self.main_window.groupBox_BatteryConfig.setAccessibleDescription(_("Settings related to the battery configuration"))

            # 运行按钮
            self.main_window.pushButton_Run.setAccessibleName(_("Run Analysis"))
            self.main_window.pushButton_Run.setAccessibleDescription(_("Start battery analysis"))

            # 文件选择按钮
            self.main_window.pushButton_TestProfile.setAccessibleName(_("Select Test Profile"))
            self.main_window.pushButton_TestProfile.setAccessibleDescription(_("Select battery test profile file"))
            self.main_window.pushButton_InputPath.setAccessibleName(_("Select Input Path"))
            self.main_window.pushButton_InputPath.setAccessibleDescription(_("Select input data file path"))
            self.main_window.pushButton_OutputPath.setAccessibleName(_("Select Output Path"))
            self.main_window.pushButton_OutputPath.setAccessibleDescription(_("Select analysis output path"))
            
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
                self.main_window.tableWidget_TestInformation.setAccessibleName(_("Test Information Table"))
                self.main_window.tableWidget_TestInformation.setAccessibleDescription(_("Table containing test equipment and software version information"))
                self.main_window.tableWidget_TestInformation.setFocusPolicy(QC.Qt.FocusPolicy.ClickFocus | QC.Qt.FocusPolicy.TabFocus)
            
            self.logger.info("可访问性设置已完成")
        except (AttributeError, TypeError, RuntimeError) as e:
            self.logger.warning("设置可访问性属性失败: %s", e)
    
    def setup_tooltips(self):
        """
        为所有UI控件设置悬停工具提示
        """
        try:
            # 测试配置组
            self.main_window.groupBox_TestConfig.setToolTip(_("Test config group - settings related to the test configuration"))

            # 电池配置组
            self.main_window.groupBox_BatteryConfig.setToolTip(_("Battery config group - settings related to the battery configuration"))

            # 电池类型
            self.main_window.comboBox_BatteryType.setToolTip(_("Select battery type"))

            # 构造方法
            self.main_window.comboBox_ConstructionMethod.setToolTip(_("Select battery construction method"))

            # 规格类型
            self.main_window.comboBox_Specification_Type.setToolTip(_("Select battery specification type"))

            # 规格方法
            self.main_window.comboBox_Specification_Method.setToolTip(_("Select battery specification method"))

            # 制造商
            self.main_window.comboBox_Manufacturer.setToolTip(_("Select battery manufacturer"))

            # 批次日期代码
            self.main_window.lineEdit_BatchDateCode.setToolTip(_("Enter battery batch date code"))

            # 样品数量
            self.main_window.lineEdit_SamplesQty.setToolTip(_("Enter number of samples"))

            # 温度类型
            self.main_window.comboBox_Temperature.setToolTip(_("Select temperature type"))

            # 温度值
            self.main_window.spinBox_Temperature.setToolTip(_("Enter freezing temperature value"))

            # 标称容量（数据手册）
            self.main_window.lineEdit_DatasheetNominalCapacity.setToolTip(_("Enter datasheet nominal capacity"))

            # 标称容量（计算值）
            self.main_window.lineEdit_CalculationNominalCapacity.setToolTip(_("Enter calculated nominal capacity"))

            # 加速老化天数
            self.main_window.spinBox_AcceleratedAging.setToolTip(_("Enter accelerated aging days"))

            # 所需可用容量
            self.main_window.lineEdit_RequiredUseableCapacity.setToolTip(_("Enter required usable capacity"))

            # 测试地点
            self.main_window.comboBox_TesterLocation.setToolTip(_("Select tester location"))

            # 测试人员
            self.main_window.comboBox_TestedBy.setToolTip(_("Select tested-by"))

            # 报告人员
            self.main_window.comboBox_ReportedBy.setToolTip(_("Select reported-by"))

            # 测试文件
            self.main_window.lineEdit_TestProfile.setToolTip(_("Test profile file path"))
            self.main_window.pushButton_TestProfile.setToolTip(_("Select test profile file"))

            # 输入路径
            self.main_window.lineEdit_InputPath.setToolTip(_("Input data file path"))
            self.main_window.pushButton_InputPath.setToolTip(_("Select input data file path"))

            # 输出路径
            self.main_window.lineEdit_OutputPath.setToolTip(_("Output result file path"))
            self.main_window.pushButton_OutputPath.setToolTip(_("Select output result file path"))

            # 运行按钮
            self.main_window.pushButton_Run.setToolTip(_("Start battery analysis"))

            # 版本号
            self.main_window.lineEdit_Version.setToolTip(_("Enter version number"))

            # 测试信息表格
            if hasattr(self.main_window, 'tableWidget_TestInformation'):
                self.main_window.tableWidget_TestInformation.setToolTip(_("Test information table - contains test equipment and software version information"))
            
            self.logger.info("控件工具提示设置已完成")
        except (AttributeError, TypeError, RuntimeError) as e:
            self.logger.warning("设置控件工具提示失败: %s", e)
    
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
    
    def _add_items_with_fallback(self, combobox, items, fallback=None):
        """添加项到下拉框，配置为空时使用内置兜底值"""
        if items:
            combobox.addItems(items)
        elif fallback:
            combobox.addItems(fallback)

    def init_combobox(self):
        """
        初始化组合框设置
        """
        # 屏蔽信号，防止 clear/addItems/setCurrentIndex 触发已连接的
        # currentIndexChanged 导致级联回调（见 check_batterytype / check_specification）
        all_combos = [
            self.main_window.comboBox_BatteryType,
            self.main_window.comboBox_ConstructionMethod,
            self.main_window.comboBox_Specification_Type,
            self.main_window.comboBox_Specification_Method,
            self.main_window.comboBox_Manufacturer,
            self.main_window.comboBox_TesterLocation,
            self.main_window.comboBox_TestedBy,
            self.main_window.comboBox_ReportedBy,
        ]
        for combo in all_combos:
            combo.blockSignals(True)

        # 清除现有项目
        for combo in all_combos:
            combo.clear()

        # 添加新项目（配置缺失时使用内置兜底值）
        self._add_items_with_fallback(
            self.main_window.comboBox_BatteryType,
            self.main_window.get_config("BatteryConfig/BatteryType"),
            ["Coin Cell", "Pouch Cell"])
        self._add_items_with_fallback(
            self.main_window.comboBox_ConstructionMethod,
            self.main_window.get_config("BatteryConfig/ConstructionMethod"),
            ["Spiral Type", "Laminate Type"])
        self.main_window.comboBox_Specification_Type.addItems(
            self.main_window.get_config("BatteryConfig/SpecificationTypeCoinCell"))
        self.main_window.comboBox_Specification_Type.addItems(
            self.main_window.get_config("BatteryConfig/SpecificationTypePouchCell"))
        if self.main_window.comboBox_Specification_Type.count() == 0:
            self.main_window.comboBox_Specification_Type.addItems(
                ["CR2032", "CR2450", "LP503048", "LP603040"])
        self._add_items_with_fallback(
            self.main_window.comboBox_Specification_Method,
            self.main_window.get_config("BatteryConfig/SpecificationMethod"),
            ["Standard", "High Rate"])
        self._add_items_with_fallback(
            self.main_window.comboBox_Manufacturer,
            self.main_window.get_config("BatteryConfig/Manufacturer"),
            ["Unknown"])
        self._add_items_with_fallback(
            self.main_window.comboBox_TesterLocation,
            self.main_window.get_config("TestConfig/TesterLocation"),
            ["Lab 1", "Lab 2"])

        # 获取TestedBy列表并同时用于comboBox_TestedBy和comboBox_ReportedBy
        tested_by_list = self.main_window.get_config("TestConfig/TestedBy")
        if tested_by_list:
            self.main_window.comboBox_TestedBy.addItems(tested_by_list)
            self.main_window.comboBox_ReportedBy.addItems(tested_by_list)
        else:
            self.main_window.comboBox_TestedBy.addItems(["Tester"])
            self.main_window.comboBox_ReportedBy.addItems(["Tester"])
        
        # 为comboBox_Temperature添加选项（只添加一次，不需要清除）
        if self.main_window.comboBox_Temperature.count() == 0:
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
        self.main_window.comboBox_Specification_Type.setEnabled(False)
        self.main_window.comboBox_Specification_Method.setEnabled(False)

        # 恢复信号
        for combo in all_combos:
            combo.blockSignals(False)

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
            self.main_window.progress_dialog.setWindowTitle(_("Battery Analysis Progress"))
            self.main_window.progress_dialog.status_label.setText(_("Ready to start analysis..."))
    
    def update_statusbar_messages(self):
        """
        更新状态栏消息为当前语言
        """
        # 保存当前消息，以便切换语言后恢复
        current_message = self.main_window.statusBar_BatteryAnalysis.currentMessage()
        
        # 获取翻译后的状态消息
        status_ready = _("Ready")
        
        # 更新状态栏
        if current_message in ("状态:就绪", "Ready"):
            self.main_window.statusBar_BatteryAnalysis.showMessage(status_ready)

    def load_user_settings(self):
        """已废弃 —— 用户偏好不再以外部 INI 形式持久化"""
        pass
    
    def init_widgetcolor(self) -> None:
        """
        清除所有标签的背景样式
        具体样式由checkinput方法根据验证结果设置
        """
        try:
            # 清除所有标签的背景样式
            labels_to_clear = [
                self.main_window.label_BatteryType,
                self.main_window.label_ConstructionMethod,
                self.main_window.label_Specification,
                self.main_window.label_Manufacturer,
                self.main_window.label_BatchDateCode,
                self.main_window.label_SamplesQty,
                self.main_window.label_Temperature,
                self.main_window.label_DatasheetNominalCapacity,
                self.main_window.label_CalculationNominalCapacity,
                self.main_window.label_AcceleratedAging,
                self.main_window.label_RequiredUseableCapacity,
                self.main_window.label_TesterLocation,
                self.main_window.label_TestedBy,
                self.main_window.label_TestProfile,
                self.main_window.label_InputPath,
                self.main_window.label_OutputPath,
                self.main_window.label_Version,
                self.main_window.pushButton_Run
            ]
            
            for label in labels_to_clear:
                label.setStyleSheet("")
        except (AttributeError, TypeError, RuntimeError) as e:
            self.logger.warning("初始化部件颜色失败: %s", e)
