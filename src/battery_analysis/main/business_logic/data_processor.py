"""
数据处理器模块

负责处理数据相关的业务逻辑，包括Excel文件信息获取、数据验证等
"""

import logging
import os
import csv
import re
from pathlib import Path
import pandas as pd


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
    
    def process_excel_with_pandas(self, file_path: str) -> dict:
        """
        使用pandas处理单个Excel文件，提取关键信息
        
        Args:
            file_path: Excel文件路径
            
        Returns:
            dict: 包含文件信息的字典
        """
        try:
            self.logger.info("使用pandas处理Excel文件: %s", file_path)
            
            # 使用pandas读取Excel文件
            df = pd.read_excel(file_path, sheet_name=0, engine='openpyxl', header=0)
            
            # 提取文件信息
            file_info = {
                'filename': os.path.basename(file_path),
                'sheet_name': df.columns.tolist(),
                'row_count': len(df),
                'column_count': len(df.columns),
                'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
                'non_numeric_columns': df.select_dtypes(exclude=['number']).columns.tolist(),
                'missing_values': df.isnull().sum().to_dict(),
                'basic_stats': df.describe().to_dict()
            }
            
            return file_info
            
        except Exception as e:
            self.logger.error("处理Excel文件失败 %s: %s", file_path, str(e))
            return {}
    
    def process_all_excel_files(self, directory: str) -> list:
        """
        使用pandas批量处理目录中的所有Excel文件
        
        Args:
            directory: 包含Excel文件的目录
            
        Returns:
            list: 包含所有文件信息的列表
        """
        try:
            self.logger.info("使用pandas批量处理目录中的Excel文件: %s", directory)
            
            # 查找所有Excel文件
            listAllInXlsx = [f for f in os.listdir(directory) if f[:2] != "~$" and f[-5:] == ".xlsx"]
            
            if not listAllInXlsx:
                self.logger.warning("目录中没有找到Excel文件: %s", directory)
                return []
            
            # 批量处理Excel文件
            excel_data = []
            for filename in listAllInXlsx:
                file_path = os.path.join(directory, filename)
                file_info = self.process_excel_with_pandas(file_path)
                if file_info:
                    excel_data.append(file_info)
            
            self.logger.info("成功处理 %d 个Excel文件", len(excel_data))
            return excel_data
            
        except Exception as e:
            self.logger.error("批量处理Excel文件失败: %s", str(e))
            return []
    
    def get_xlsxinfo(self) -> None:
        """
        获取Excel文件信息，使用pandas优化处理
        """
        self.logger.info("获取Excel文件信息")
        
        # 清除检查器状态
        if hasattr(self.main_window, 'checker_input_xlsx'):
            self.main_window.checker_input_xlsx.clear()
        
        # 断开信号连接
        self._disconnect_specification_signals()
        
        # 获取输入路径
        input_dir = self.main_window.lineEdit_InputPath.text()
        
        # 检查输入路径是否存在
        if not os.path.exists(input_dir):
            self.logger.error("输入路径不存在: %s", input_dir)
            return
        
        # 查找所有Excel文件
        excel_files = [f for f in os.listdir(input_dir) if f[:2] != "~$" and f[-5:] == ".xlsx"]
        
        # 如果没有找到Excel文件，清除相关控件
        if not excel_files:
            self._handle_no_excel_files(input_dir)
            return
        
        # 使用pandas处理Excel文件
        excel_data = self._process_excel_files(input_dir, excel_files)
        
        # 更新UI控件
        self._update_ui_with_excel_info(excel_files, excel_data)
        
        # 如果有Excel文件，处理第一个文件的信息
        if excel_files:
            self._process_first_excel_file(excel_files[0])
        
        # 重新连接信号
        self._reconnect_specification_signals()
        
        self.logger.info("Excel文件信息获取完成")
    
    def _disconnect_specification_signals(self):
        """断开规格相关信号连接"""
        try:
            self.main_window.comboBox_Specification_Type.currentIndexChanged.disconnect(
                self.main_window.check_specification
            )
            self.main_window.comboBox_Specification_Method.currentIndexChanged.disconnect(
                self.main_window.check_specification
            )
        except (TypeError, AttributeError):
            pass
    
    def _handle_no_excel_files(self, input_dir):
        """处理没有找到Excel文件的情况"""
        self.logger.warning("没有找到Excel文件: %s", input_dir)
        
        # 清除相关控件
        self.main_window.comboBox_BatteryType.setCurrentIndex(-1)
        self.main_window.comboBox_Specification_Type.clear()
        self.main_window.comboBox_Specification_Type.addItems(
            self.main_window.get_config("BatteryConfig/SpecificationTypeCoinCell"))
        self.main_window.comboBox_Specification_Type.addItems(
            self.main_window.get_config("BatteryConfig/SpecificationTypePouchCell"))
        self.main_window.comboBox_Specification_Type.setCurrentIndex(-1)
        self.main_window.comboBox_Specification_Method.clear()
        self.main_window.comboBox_Specification_Method.addItems(
            self.main_window.get_config("BatteryConfig/SpecificationMethod"))
        self.main_window.comboBox_Specification_Method.setCurrentIndex(-1)
        self.main_window.comboBox_Manufacturer.setCurrentIndex(-1)
        self.main_window.lineEdit_BatchDateCode.setText("")
        self.main_window.lineEdit_SamplesQty.setText("")
        self.main_window.lineEdit_DatasheetNominalCapacity.setText("")
        self.main_window.lineEdit_CalculationNominalCapacity.setText("")
        
        # 设置错误信息
        if hasattr(self.main_window, 'checker_input_xlsx'):
            self.main_window.checker_input_xlsx.set_error("Input path has no data")
        if hasattr(self.main_window, 'statusBar_BatteryAnalysis'):
            self.main_window.statusBar_BatteryAnalysis.showMessage("[Error]: Input path has no data")
    
    def _process_excel_files(self, input_dir, excel_files):
        """处理Excel文件并提取信息"""
        excel_data = []
        for filename in excel_files:
            try:
                file_path = os.path.join(input_dir, filename)
                self.logger.info("使用pandas处理Excel文件: %s", filename)
                
                # 使用pandas读取Excel文件
                df = pd.read_excel(file_path, sheet_name=0, engine='openpyxl', header=0)
                
                # 提取文件信息
                file_info = {
                    'filename': filename,
                    'sheet_name': df.columns.tolist(),
                    'row_count': len(df),
                    'column_count': len(df.columns),
                    'first_five_rows': df.head().to_dict('records')
                }
                
                excel_data.append(file_info)
                
            except Exception as e:
                self.logger.error("处理Excel文件失败 %s: %s", filename, str(e))
                continue
        return excel_data
    
    def _update_ui_with_excel_info(self, excel_files, excel_data):
        """使用Excel信息更新UI控件"""
        self.logger.info("成功处理 %d 个Excel文件，开始更新UI控件", len(excel_data))
        
        # 设置样本数量
        self.main_window.lineEdit_SamplesQty.setText(str(len(excel_files)))
        
        # 重置检查器状态为正常
        if hasattr(self.main_window, 'checker_input_xlsx'):
            self.main_window.checker_input_xlsx.clear()
        if hasattr(self.main_window, 'statusBar_BatteryAnalysis'):
            self.main_window.statusBar_BatteryAnalysis.showMessage("状态:就绪")
    
    def _process_first_excel_file(self, filename):
        """处理第一个Excel文件的详细信息"""
        self.main_window.construction_method = ""
        
        # 查找构造方法
        for c in range(self.main_window.comboBox_ConstructionMethod.count()):
            if self.main_window.comboBox_ConstructionMethod.itemText(c) in filename:
                self.main_window.construction_method = self.main_window.comboBox_ConstructionMethod.itemText(c)
                break
        
        # 获取规格类型和方法
        all_spec_types = self.main_window.get_config("BatteryConfig/SpecificationTypeCoinCell") + \
                        self.main_window.get_config("BatteryConfig/SpecificationTypePouchCell")
        all_spec_methods = self.main_window.get_config("BatteryConfig/SpecificationMethod")
        
        # 优先匹配最长的规格类型，避免短匹配优先
        self._set_specification_type(filename, all_spec_types)
        
        # 匹配规格方法
        self._set_specification_method(filename, all_spec_methods)
        
        # 匹配制造商
        self._set_manufacturer(filename)
        
        # 提取批次日期代码
        self._extract_batch_date_code(filename)
        
        # 提取脉冲电流
        self._extract_pulse_current(filename)
        
        # 提取恒流电流
        self._extract_cc_current(filename)
    
    def _set_specification_type(self, filename, all_spec_types):
        """设置规格类型"""
        type_index = -1
        max_match_length = 0
        for t, spec_type in enumerate(all_spec_types):
            if spec_type in filename and len(spec_type) > max_match_length:
                type_index = t
                max_match_length = len(spec_type)
        
        if type_index != -1:
            self.main_window.comboBox_Specification_Type.setCurrentIndex(type_index)
    
    def _set_specification_method(self, filename, all_spec_methods):
        """设置规格方法"""
        method_index = -1
        max_match_length = 0
        for m, method in enumerate(all_spec_methods):
            if method in filename and len(method) > max_match_length:
                method_index = m
                max_match_length = len(method)
        
        if method_index != -1:
            self.main_window.comboBox_Specification_Method.setCurrentIndex(method_index)
    
    def _set_manufacturer(self, filename):
        """设置制造商"""
        for m in range(self.main_window.comboBox_Manufacturer.count()):
            if self.main_window.comboBox_Manufacturer.itemText(m) in filename:
                self.main_window.comboBox_Manufacturer.setCurrentIndex(m)
                break
    
    def _extract_batch_date_code(self, filename):
        """提取批次日期代码"""
        batch_date_codes = re.findall("DC(.*?),", filename)
        if len(batch_date_codes) == 1:
            self.main_window.lineEdit_BatchDateCode.setText(batch_date_codes[0].strip())
    
    def _extract_pulse_current(self, filename):
        """提取脉冲电流"""
        pulse_current_matches = re.findall(r"\(([\d.]+[-\d.]+)mA", filename)
        if len(pulse_current_matches) == 1:
            pulse_current_values = pulse_current_matches[0].split("-")
            try:
                # 将字符串转换为浮点数，保留小数精度
                self.main_window.listCurrentLevel = [float(c.strip()) for c in pulse_current_values]
            except ValueError:
                # 处理转换失败的情况
                self.main_window.listCurrentLevel = [int(float(c.strip())) for c in pulse_current_values]
            self.main_window.config.setValue("BatteryConfig/PulseCurrent", pulse_current_values)
    
    def _extract_cc_current(self, filename):
        """提取恒流电流"""
        self.main_window.cc_current = ""
        cc_current_matches = re.findall(r"mA,(.*?)\)", filename)
        if len(cc_current_matches) == 1:
            cc_current_str = cc_current_matches[0].replace("mAh", "")
            cc_current_values = re.findall(r"([\d.]+)mA", cc_current_str)
            if len(cc_current_values) >= 1:
                self.main_window.cc_current = cc_current_values[-1]
    
    def _reconnect_specification_signals(self):
        """重新连接规格相关信号"""
        try:
            self.main_window.comboBox_Specification_Type.currentIndexChanged.connect(
                self.main_window.check_specification
            )
            self.main_window.comboBox_Specification_Method.currentIndexChanged.connect(
                self.main_window.check_specification
            )
            
            # 调用check_specification方法，更新电池容量等信息
            self.main_window.check_specification()
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
        分析数据，使用pandas优化分析逻辑
        """
        self.logger.info("开始数据分析")
        
        # 检查输入路径是否设置
        input_path = self.main_window.lineEdit_InputPath.text()
        if not input_path:
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
        
        try:
            # 查找所有Excel文件
            excel_files = [f for f in os.listdir(input_path) if f[:2] != "~$" and f[-5:] == ".xlsx"]
            
            if not excel_files:
                self.logger.warning("没有找到Excel文件")
                from PyQt6 import QtWidgets as QW
                from battery_analysis.i18n.language_manager import _
                QW.QMessageBox.information(
                    self.main_window,
                    _("analysis_result", "分析结果"),
                    _("no_excel_files_found", "没有找到Excel文件。")
                )
                return
            
            # 使用pandas批量处理Excel文件
            all_data = []
            for filename in excel_files:
                try:
                    file_path = os.path.join(input_path, filename)
                    self.logger.info("分析Excel文件: %s", filename)
                    
                    # 使用pandas读取Excel文件
                    df = pd.read_excel(file_path, sheet_name=0, engine='openpyxl', header=0)
                    
                    # 基本数据分析
                    analysis_result = {
                        'filename': filename,
                        'total_records': len(df),
                        'columns': df.columns.tolist(),
                        'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
                        'non_numeric_columns': df.select_dtypes(exclude=['number']).columns.tolist(),
                        'missing_values': df.isnull().sum().to_dict(),
                        'basic_stats': df.describe().to_dict()
                    }
                    
                    all_data.append(analysis_result)
                    
                except Exception as e:
                    self.logger.error("分析Excel文件失败 %s: %s", filename, str(e))
                    continue
            
            # 汇总分析结果
            summary = {
                'total_files': len(excel_files),
                'successful_files': len(all_data),
                'failed_files': len(excel_files) - len(all_data),
                'total_records': sum(item['total_records'] for item in all_data),
                'analysis_details': all_data
            }
            
            # 显示分析结果
            from PyQt6 import QtWidgets as QW
            from battery_analysis.i18n.language_manager import _
            message = f"数据分析已完成！\n\n"\
                     f"总文件数: {summary['total_files']}\n"\
                     f"成功分析: {summary['successful_files']}\n"\
                     f"失败文件: {summary['failed_files']}\n"\
                     f"总记录数: {summary['total_records']}\n\n"\
                     f"详细结果已记录到日志。"
            
            QW.QMessageBox.information(
                self.main_window,
                _("analysis_result", "分析结果"),
                message
            )
            
            # 记录详细分析结果到日志
            self.logger.info("数据分析汇总: %s", summary)
            
        except Exception as e:
            self.logger.error("数据分析失败: %s", str(e))
            from PyQt6 import QtWidgets as QW
            from battery_analysis.i18n.language_manager import _
            QW.QMessageBox.error(
                self.main_window,
                _("error_title", "错误"),
                _("data_analysis_failed", "数据分析失败: {}").format(str(e))
            )
        finally:
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
