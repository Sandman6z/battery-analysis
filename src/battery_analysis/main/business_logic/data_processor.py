"""
数据处理器模块

负责处理数据相关的业务逻辑，包括Excel文件信息获取、数据验证等
"""

import logging
import os
import csv
from pathlib import Path


class DataProcessor:
    """
    数据处理器类，负责处理数据相关的业务逻辑
    """
    
    def __init__(self, main_window):
        """
        初始化数据处理器
        
        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
    
    def get_xlsxinfo(self) -> None:
        """
        获取Excel文件信息
        """
        self.logger.info("获取Excel文件信息")
        
        # 清除检查器状态
        if hasattr(self.main_window, 'checker_input_xlsx'):
            self.main_window.checker_input_xlsx.clear()
        
        # 断开信号连接，避免在处理过程中触发不必要的事件
        try:
            self.main_window.comboBox_Specification_Type.currentIndexChanged.disconnect(
                self.main_window.check_specification
            )
            self.main_window.comboBox_Specification_Method.currentIndexChanged.disconnect(
                self.main_window.check_specification
            )
        except (TypeError, AttributeError):
            pass
        
        # 获取输入路径
        strInPutDir = self.main_window.lineEdit_InputPath.text()
        
        # 检查输入路径是否存在
        if not os.path.exists(strInPutDir):
            self.logger.error("输入路径不存在: %s", strInPutDir)
            return
        
        # 查找所有Excel文件
        listAllInXlsx = [f for f in os.listdir(strInPutDir) if f[:2] != "~$" and f[-5:] == ".xlsx"]
        
        # 如果没有找到Excel文件，清除相关控件
        if not listAllInXlsx:
            self.logger.warning("没有找到Excel文件")
            # 这里可以添加清除相关控件的逻辑
            return
        
        # 这里可以添加处理Excel文件的逻辑
        # 例如：读取Excel文件内容，提取相关信息，更新UI控件
        
        # 重新连接信号
        try:
            self.main_window.comboBox_Specification_Type.currentIndexChanged.connect(
                self.main_window.check_specification
            )
            self.main_window.comboBox_Specification_Method.currentIndexChanged.connect(
                self.main_window.check_specification
            )
        except (TypeError, AttributeError):
            pass
    
    def save_table(self) -> None:
        """
        保存表格数据
        """
        self.logger.info("保存表格数据")
        
        # 设置焦点到Run按钮，以便保存输入文本
        self.main_window.pushButton_Run.setFocus()
        
        def set_item(config_key: str, row: int, col: int):
            """设置表格项到配置"""
            item = self.main_window.tableWidget_TestInformation.item(row, col)
            if item and hasattr(self.main_window, 'config'):
                self.main_window.config.setValue(config_key, item.text())
        
        # 保存表格数据到配置
        set_item("TestInformation/TestEquipment", 0, 2)
        set_item("TestInformation/BTS_Server_Version", 1, 2)
        set_item("TestInformation/BTS_Client_Version", 2, 2)
        set_item("TestInformation/Data_Analysis_Version", 3, 2)
        set_item("TestInformation/Software_Version", 4, 2)
        set_item("TestInformation/Testing_Company", 5, 1)
        set_item("TestInformation/Testing_Department", 5, 2)
        set_item("TestInformation/Testing_Location", 6, 1)
        set_item("TestInformation/Testing_Room", 6, 2)
        set_item("TestInformation/Testing_Standard", 7, 1)
        set_item("TestInformation/Test_Method", 7, 2)
        set_item("TestInformation/Battery_Manufacturer", 8, 1)
        set_item("TestInformation/Battery_Model", 8, 2)
        set_item("TestInformation/Battery_Type", 9, 1)
        set_item("TestInformation/Battery_Chemistry", 9, 2)
        set_item("TestInformation/Battery_Capacity", 10, 1)
        set_item("TestInformation/Battery_Voltage", 10, 2)
        set_item("TestInformation/Battery_Series", 11, 1)
        set_item("TestInformation/Battery_Parallel", 11, 2)
        set_item("TestInformation/Test_Date", 12, 1)
        set_item("TestInformation/Test_Time", 12, 2)
        set_item("TestInformation/Test_Operator", 13, 1)
        set_item("TestInformation/Test_Assistant", 13, 2)
        set_item("TestInformation/Test_Temperature", 14, 1)
        set_item("TestInformation/Test_Humidity", 14, 2)
        set_item("TestInformation/Test_Comments", 15, 1)
        set_item("TestInformation/Test_Results", 15, 2)
    
    def update_config(self, test_info) -> None:
        """
        更新配置
        
        Args:
            test_info: 测试信息
        """
        self.logger.info("更新配置")
        
        # 初始化检查器如果不存在
        if not hasattr(self.main_window, 'checker_update_config'):
            from battery_analysis.main.main_window import Checker
            self.main_window.checker_update_config = Checker()
        
        # 清除检查器状态
        self.main_window.checker_update_config.clear()
        
        # 更新配置
        if hasattr(self.main_window, 'config'):
            self.main_window.config.setValue(
                "UserConfig/TestDate", test_info["TestDate"]
            )
            self.main_window.config.setValue(
                "UserConfig/TestTime", test_info["TestTime"]
            )
            self.main_window.config.setValue(
                "UserConfig/BatteryModel", test_info["BatteryModel"]
            )
            self.main_window.config.setValue(
                "UserConfig/TestEquipment", test_info["TestEquipment"]
            )
            self.main_window.config.setValue(
                "UserConfig/Software_Version", test_info["Software_Version"]
            )
    
    def analyze_data(self) -> None:
        """
        分析数据
        """
        self.logger.info("开始数据分析")
        
        # 检查输入路径是否设置
        if not self.main_window.lineEdit_InputPath.text():
            from PyQt6 import QtWidgets as QW
            from battery_analysis.i18n.language_manager import _
            QW.QMessageBox.warning(
                self.main_window,
                _("warning_title", "警告"),
                _("input_path_not_set", "请先设置输入路径。")
            )
            return
        
        # 更新状态栏
        self.main_window.statusBar_BatteryAnalysis.showMessage(
            _("analyzing_data", "分析数据...")
        )
        
        # 这里可以实现数据分析的逻辑
        # 目前暂时使用消息框提示
        from PyQt6 import QtWidgets as QW
        from battery_analysis.i18n.language_manager import _
        QW.QMessageBox.information(
            self.main_window,
            _("analysis_result", "分析结果"),
            _("data_analysis_complete", "数据分析已完成。\n\n目前此功能处于开发阶段。")
        )
        
        # 更新状态栏为就绪状态
        self.main_window.statusBar_BatteryAnalysis.showMessage(
            _("status_ready", "状态:就绪")
        )
    
    def handle_data_error_recovery(self, error_msg: str):
        """
        处理数据相关错误的恢复选项
        
        Args:
            error_msg: 错误信息
        """
        self.logger.error("处理数据错误恢复: %s", error_msg)
        
        # 创建自定义对话框
        from PyQt6 import QtWidgets as QW
        from PyQt6 import QtCore as QC
        from PyQt6 import QtGui as QG
        
        dialog = QW.QDialog(self.main_window)
        dialog.setWindowTitle("数据加载错误 - 恢复选项")
        dialog.setModal(True)
        dialog.resize(500, 300)
        dialog.setWindowModality(QC.Qt.WindowModality.ApplicationModal)
        
        layout = QW.QVBoxLayout(dialog)
        
        # 错误标题
        title_label = QW.QLabel("无法加载电池数据，请选择如何继续:")
        title_font = QG.QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        layout.addSpacing(10)
        
        # 错误信息
        error_label = QW.QLabel(f"错误详情: {error_msg}")
        error_label.setWordWrap(True)
        error_label.setStyleSheet("background-color: #f0f0f0; padding: 10px; border: 1px solid #ccc;")
        layout.addWidget(error_label)
        layout.addSpacing(15)
        
        # 建议解决方案
        details_label = QW.QLabel("请选择以下恢复选项之一:")
        details_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(details_label)
        
        # 按钮布局
        button_layout = QW.QHBoxLayout()
        button_layout.addStretch()
        
        # 选项1: 重新选择数据目录
        retry_button = QW.QPushButton("重新选择数据目录")
        retry_button.clicked.connect(lambda: self._handle_error_option(dialog, "retry"))
        button_layout.addWidget(retry_button)
        
        # 选项2: 使用默认配置
        default_button = QW.QPushButton("使用默认配置")
        default_button.clicked.connect(lambda: self._handle_error_option(dialog, "default"))
        button_layout.addWidget(default_button)
        
        # 选项3: 取消操作
        cancel_button = QW.QPushButton("取消")
        cancel_button.clicked.connect(lambda: self._handle_error_option(dialog, "cancel"))
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        # 存储用户选择
        self._error_option = None
        
        # 显示对话框
        dialog.exec()
        
        # 处理用户选择
        if self._error_option == "retry":
            # 重新选择数据目录
            self._open_data_directory_dialog()
        elif self._error_option == "default":
            # 使用默认配置，继续分析
            pass
        else:
            # 取消操作
            pass
    
    def _handle_error_option(self, dialog, option):
        """
        处理错误选项
        
        Args:
            dialog: 对话框实例
            option: 用户选择的选项
        """
        self._error_option = option
        dialog.accept()
    
    def _open_data_directory_dialog(self):
        """
        打开数据目录选择对话框
        """
        from PyQt6 import QtWidgets as QW
        from battery_analysis.i18n.language_manager import _
        
        self.main_window.statusBar_BatteryAnalysis.showMessage(
            _("selecting_data_directory", "选择数据目录...")
        )
        
        # 打开目录选择对话框
        directory = QW.QFileDialog.getExistingDirectory(
            self.main_window,
            _("select_data_directory", "选择数据目录"),
            self.main_window.lineEdit_InputPath.text()
        )
        
        if directory:
            self.main_window.lineEdit_InputPath.setText(directory)
            # 重新分析数据
            self.analyze_data()
        
        self.main_window.statusBar_BatteryAnalysis.showMessage(
            _("status_ready", "状态:就绪")
        )
