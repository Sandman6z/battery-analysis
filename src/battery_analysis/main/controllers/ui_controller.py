# -*- coding: utf-8 -*-
"""
UI控制器模块
负责处理UI状态管理和界面更新
"""

from PyQt6 import QtCore as QC
from PyQt6 import QtWidgets as QW
from PyQt6 import QtGui as QG

import logging
from pathlib import Path


class UiController(QC.QObject):
    """
    UI控制器类
    负责处理UI状态管理和界面更新
    """
    # 定义信号
    ui_state_changed = QC.pyqtSignal(str, object)  # UI状态变化信号
    
    def __init__(self, main_window):
        """
        初始化UI控制器
        
        Args:
            main_window: 主窗口实例
        """
        super().__init__()
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        self._ui_state = {}
    
    def init_ui_elements(self):
        """
        初始化UI元素
        """
        self._init_lineedit()
        self._init_combobox()
        self._init_table()
        self._connect_ui_signals()
    
    def _init_lineedit(self):
        """
        初始化行编辑器
        """
        # 数字输入验证
        reg = QC.QRegularExpression(r"^\d*$")
        validator = QG.QRegularExpressionValidator(self.main_window)
        validator.setRegularExpression(reg)
        
        self.main_window.lineEdit_SamplesQty.setValidator(validator)
        self.main_window.lineEdit_DatasheetNominalCapacity.setValidator(validator)
        self.main_window.lineEdit_CalculationNominalCapacity.setValidator(validator)
        self.main_window.lineEdit_RequiredUseableCapacity.setValidator(validator)
        
        # 版本号验证（支持x.y.z格式）
        reg = QC.QRegularExpression(r"^\d+(\.\d+){0,2}$")
        validator = QG.QRegularExpressionValidator(self.main_window)
        validator.setRegularExpression(reg)
        self.main_window.lineEdit_Version.setValidator(validator)
        
        # 设置默认值
        self.main_window.lineEdit_TestProfile.setText("Not provided")
        self.main_window.lineEdit_Temperature.setText("Room Temperature")
    
    def _init_combobox(self):
        """
        初始化下拉框
        """
        main_window = self.main_window
        
        # 从配置中加载下拉框选项
        main_window.comboBox_BatteryType.addItems(main_window.get_config("BatteryConfig/BatteryType"))
        main_window.comboBox_ConstructionMethod.addItems(main_window.get_config("BatteryConfig/ConstructionMethod"))
        main_window.comboBox_Specification_Type.addItems(main_window.get_config("BatteryConfig/SpecificationTypeCoinCell"))
        main_window.comboBox_Specification_Type.addItems(main_window.get_config("BatteryConfig/SpecificationTypePouchCell"))
        main_window.comboBox_Specification_Method.addItems(main_window.get_config("BatteryConfig/SpecificationMethod"))
        main_window.comboBox_Manufacturer.addItems(main_window.get_config("BatteryConfig/Manufacturer"))
        main_window.comboBox_TesterLocation.addItems(main_window.get_config("TestConfig/TesterLocation"))
        main_window.comboBox_TestedBy.addItems(main_window.get_config("TestConfig/TestedBy"))
        
        # 初始化默认选择
        for combo_box in [
            main_window.comboBox_BatteryType,
            main_window.comboBox_ConstructionMethod,
            main_window.comboBox_Specification_Type,
            main_window.comboBox_Specification_Method,
            main_window.comboBox_Manufacturer,
            main_window.comboBox_TesterLocation,
            main_window.comboBox_TestedBy
        ]:
            combo_box.setCurrentIndex(-1)
        
        # 禁用部分控件
        main_window.comboBox_ConstructionMethod.setEnabled(False)
    
    def _init_table(self):
        """
        初始化表格
        """
        table = self.main_window.tableWidget_TestInformation
        
        # 设置表格属性
        table.horizontalHeader().setStretchLastSection(True)
        
        def set_span_item(item_text: str, row: int, col: int, 
                          row_span: int = 1, col_span: int = 1, 
                          editable: bool = False) -> None:
            """设置表格单元格内容和属性"""
            if row_span > 1 or col_span > 1:
                table.setSpan(row, col, row_span, col_span)
            
            item = QW.QTableWidgetItem(item_text)
            if not editable:
                item.setFlags(QC.Qt.ItemFlag.ItemIsEnabled)
                item.setBackground(QG.QBrush(QG.QColor(242, 242, 242)))
            
            table.setItem(row, col, item)
        
        # 设置表格内容
        set_span_item("Test Equipment", 0, 0, 1, 2)
        set_span_item("", 0, 2, editable=True)

        set_span_item("Software Versions", 1, 0, 3, 1)
        set_span_item("BTS Server Version", 1, 1)
        set_span_item("BTS Client Version", 2, 1)
        set_span_item("TSDA (Data Analysis) Version", 3, 1)
        set_span_item("", 1, 2, editable=True)
        set_span_item("", 2, 2, editable=True)
        set_span_item("", 3, 2, editable=True)

        set_span_item("Middle Machines", 4, 0, 5, 1)
        set_span_item("Model", 4, 1)
        set_span_item("Hardware Version", 5, 1)
        set_span_item("Serial Number", 6, 1)
        set_span_item("Firmware Version", 7, 1)
        set_span_item("Device Type", 8, 1)
        set_span_item("", 4, 2, editable=True)
        set_span_item("", 5, 2, editable=True)
    
    def _connect_ui_signals(self):
        """
        连接UI信号
        """
        main_window = self.main_window
        
        # 验证相关信号
        main_window.lineEdit_Version.textChanged.connect(self._validate_version)
        main_window.lineEdit_InputPath.textChanged.connect(self._validate_input_path)
        
        # 必填字段验证
        required_fields = [
            main_window.lineEdit_SamplesQty,
            main_window.lineEdit_DatasheetNominalCapacity,
            main_window.lineEdit_CalculationNominalCapacity,
            main_window.lineEdit_RequiredUseableCapacity
        ]
        for field in required_fields:
            field.textChanged.connect(self._validate_required_fields)
    
    def _validate_version(self, text):
        """
        验证版本号
        
        Args:
            text: 版本号文本
        """
        # 版本号验证逻辑已通过正则表达式实现
        pass
    
    def _validate_input_path(self, text):
        """
        验证输入路径
        
        Args:
            text: 输入路径文本
        """
        if text and not Path(text).exists():
            self.logger.warning(f"输入路径不存在: {text}")
    
    def _validate_required_fields(self):
        """
        验证必填字段
        """
        main_window = self.main_window
        
        # 检查所有必填字段是否已填写
        required_fields = [
            main_window.lineEdit_SamplesQty,
            main_window.lineEdit_DatasheetNominalCapacity,
            main_window.lineEdit_CalculationNominalCapacity,
            main_window.lineEdit_RequiredUseableCapacity
        ]
        
        all_fields_filled = all(field.text().strip() for field in required_fields)
        
        # 更新UI状态
        self._ui_state["all_fields_filled"] = all_fields_filled
        self.ui_state_changed.emit("all_fields_filled", all_fields_filled)
    
    def update_status_bar(self, message):
        """
        更新状态栏
        
        Args:
            message: 状态消息
        """
        if hasattr(self.main_window, 'statusBar_BatteryAnalysis'):
            self.main_window.statusBar_BatteryAnalysis.showMessage(message)
    
    def update_progress(self, progress, status_text):
        """
        更新进度条
        
        Args:
            progress: 进度值(0-100)
            status_text: 状态文本
        """
        # 更新嵌入式进度条
        if hasattr(self.main_window, 'progressBar'):
            self.main_window.progressBar.setValue(progress)
        
        # 更新状态栏信息
        self.update_status_bar(f"状态: {status_text}")
    
    def get_ui_state(self, key=None):
        """
        获取UI状态
        
        Args:
            key: 状态键
            
        Returns:
            object: UI状态值
        """
        if key is None:
            return self._ui_state.copy()
        return self._ui_state.get(key)
    
    def set_ui_state(self, key, value):
        """
        设置UI状态
        
        Args:
            key: 状态键
            value: 状态值
        """
        self._ui_state[key] = value
        self.ui_state_changed.emit(key, value)
    
    def load_user_settings(self):
        """
        加载用户设置
        """
        try:
            main_window = self.main_window
            if not main_window.b_has_config:
                return
            
            user_config_path = Path(main_window.config_path).parent / "user_settings.ini"
            
            if user_config_path.exists():
                # 创建用户配置QSettings实例
                user_settings = QC.QSettings(
                    str(user_config_path), 
                    QC.QSettings.Format.IniFormat
                )
                
                # 加载电池类型相关设置
                battery_type = user_settings.value("UserConfig/BatteryType")
                if battery_type:
                    index = main_window.comboBox_BatteryType.findText(battery_type)
                    if index >= 0:
                        main_window.comboBox_BatteryType.setCurrentIndex(index)
                
                construction_method = user_settings.value("UserConfig/ConstructionMethod")
                if construction_method:
                    index = main_window.comboBox_ConstructionMethod.findText(construction_method)
                    if index >= 0:
                        main_window.comboBox_ConstructionMethod.setCurrentIndex(index)
                
                specification_type = user_settings.value("UserConfig/SpecificationType")
                if specification_type:
                    index = main_window.comboBox_Specification_Type.findText(specification_type)
                    if index >= 0:
                        main_window.comboBox_Specification_Type.setCurrentIndex(index)
                
                specification_method = user_settings.value("UserConfig/SpecificationMethod")
                if specification_method:
                    index = main_window.comboBox_Specification_Method.findText(specification_method)
                    if index >= 0:
                        main_window.comboBox_Specification_Method.setCurrentIndex(index)
                
                manufacturer = user_settings.value("UserConfig/Manufacturer")
                if manufacturer:
                    index = main_window.comboBox_Manufacturer.findText(manufacturer)
                    if index >= 0:
                        main_window.comboBox_Manufacturer.setCurrentIndex(index)
                
                tester_location = user_settings.value("UserConfig/TesterLocation")
                if tester_location:
                    index = main_window.comboBox_TesterLocation.findText(tester_location)
                    if index >= 0:
                        main_window.comboBox_TesterLocation.setCurrentIndex(index)
                
                tested_by = user_settings.value("UserConfig/TestedBy")
                if tested_by:
                    index = main_window.comboBox_TestedBy.findText(tested_by)
                    if index >= 0:
                        main_window.comboBox_TestedBy.setCurrentIndex(index)
                
                # 加载温度设置
                temperature = user_settings.value("UserConfig/Temperature")
                if temperature:
                    main_window.lineEdit_Temperature.setText(temperature)
                
                # 加载输出路径设置
                output_path = user_settings.value("UserConfig/OutputPath")
                if output_path:
                    main_window.lineEdit_OutputPath.setText(output_path)
                    
        except Exception as e:
            self.logger.error(f"加载用户设置失败: {e}")
