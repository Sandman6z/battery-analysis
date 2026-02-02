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
from PyQt6 import QtWidgets as QW
from PyQt6 import QtCore as QC
from PyQt6 import QtGui as QG
from battery_analysis.i18n.language_manager import _


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
        # 初始化缓存
        self._cache = {
            'excel_files': {},  # 缓存Excel文件内容
            'directory_files': {},  # 缓存目录文件列表
            'file_validation': {}  # 缓存文件验证结果
        }
    
    def _invalidate_cache(self, path=None):
        """
        使缓存失效
        
        Args:
            path: 可选的路径，用于更精确地失效缓存
        """
        if path:
            # 失效与特定路径相关的缓存
            path_str = str(path)
            # 失效Excel文件缓存
            if path_str in self._cache['excel_files']:
                del self._cache['excel_files'][path_str]
            # 失效文件验证缓存
            if path_str in self._cache['file_validation']:
                del self._cache['file_validation'][path_str]
            # 失效目录文件列表缓存
            for dir_path in list(self._cache['directory_files'].keys()):
                if path_str.startswith(dir_path):
                    del self._cache['directory_files'][dir_path]
        else:
            # 完全清空缓存
            self._cache = {
                'excel_files': {},
                'directory_files': {},
                'file_validation': {}
            }
    
    def clear_cache(self):
        """
        清空所有缓存
        """
        self._invalidate_cache()
        self.logger.info("DataProcessor cache cleared")
    
    def optimize_dataframe_memory(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        优化DataFrame内存使用
        
        Args:
            df: 原始DataFrame
            
        Returns:
            pd.DataFrame: 优化内存后的DataFrame
        """
        # 优化数值列
        for col in df.select_dtypes(include=['int64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='integer')
        
        for col in df.select_dtypes(include=['float64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='float')
        
        # 优化对象列
        for col in df.select_dtypes(include=['object']).columns:
            # 检查唯一值比例
            unique_ratio = len(df[col].unique()) / len(df[col])
            if unique_ratio < 0.5:
                df[col] = df[col].astype('category')
        
        return df
    
    def process_excel_with_pandas(self, file_path: str) -> dict:
        """
        使用pandas处理单个Excel文件，提取关键信息
        
        Args:
            file_path: Excel文件路径
            
        Returns:
            dict: 包含文件信息的字典
        """
        try:
            # 检查缓存
            if file_path in self._cache['excel_files']:
                self.logger.info("从缓存读取Excel文件信息: %s", file_path)
                return self._cache['excel_files'][file_path]
            
            self.logger.info("使用pandas处理Excel文件: %s", file_path)
            
            # 使用pandas读取Excel文件，指定引擎和优化参数
            df = pd.read_excel(file_path, sheet_name=0, engine='openpyxl', header=0)
            
            # 优化DataFrame内存使用
            df = self.optimize_dataframe_memory(df)
            
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
            
            # 缓存结果
            self._cache['excel_files'][file_path] = file_info
            
            return file_info
            
        except Exception as e:
            self.logger.error("处理Excel文件失败 %s: %s", file_path, str(e))
            return {}
    
    def process_all_excel_files(self, directory: str) -> list:
        """
        使用pandas并行处理目录中的所有Excel文件
        
        Args:
            directory: 包含Excel文件的目录
            
        Returns:
            list: 包含所有文件信息的列表
        """
        try:
            self.logger.info("使用pandas批量处理目录中的Excel文件: %s", directory)
            
            # 查找所有Excel文件（使用缓存）
            if directory not in self._cache['directory_files']:
                self.logger.info("扫描目录查找Excel文件: %s", directory)
                self._cache['directory_files'][directory] = [f for f in os.listdir(directory) if f[:2] != "~$" and f[-5:] == ".xlsx"]
            
            listAllInXlsx = self._cache['directory_files'][directory]
            
            if not listAllInXlsx:
                self.logger.warning("目录中没有找到Excel文件: %s", directory)
                return []
            
            # 使用并行处理Excel文件
            from concurrent.futures import ProcessPoolExecutor, as_completed
            from battery_analysis.utils.resource_manager import ResourceManager
            excel_data = []
            
            def process_file(filename):
                file_path = os.path.join(directory, filename)
                return self.process_excel_with_pandas(file_path)
            
            # 获取最优进程数
            optimal_process_count = ResourceManager.get_optimal_process_count()
            actual_process_count = min(optimal_process_count, len(listAllInXlsx))
            
            # 使用进程池并行处理
            with ProcessPoolExecutor(max_workers=actual_process_count) as executor:
                # 提交所有任务
                future_to_file = {executor.submit(process_file, filename): filename for filename in listAllInXlsx}
                
                # 收集结果
                for future in as_completed(future_to_file):
                    file_info = future.result()
                    if file_info:
                        excel_data.append(file_info)
            
            self.logger.info("成功处理 %d 个Excel文件", len(excel_data))
            return excel_data
            
        except Exception as e:
            self.logger.error("批量处理Excel文件失败: %s", str(e))
            # 失败时回退到串行处理
            excel_data = []
            for filename in [f for f in os.listdir(directory) if f[:2] != "~$" and f[-5:] == ".xlsx"]:
                file_path = os.path.join(directory, filename)
                file_info = self.process_excel_with_pandas(file_path)
                if file_info:
                    excel_data.append(file_info)
            return excel_data
    
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
        
        # 使用FileValidator验证输入目录
        from battery_analysis.utils.file_validator import FileValidator
        validator = FileValidator()
        
        # 验证输入目录
        is_valid, error_msg = validator.validate_input_directory(input_dir)
        if not is_valid:
            self.logger.error(error_msg)
            if hasattr(self.main_window, 'checker_input_xlsx'):
                self.main_window.checker_input_xlsx.set_error(error_msg)
            if hasattr(self.main_window, 'statusBar_BatteryAnalysis'):
                self.main_window.statusBar_BatteryAnalysis.showMessage(f"[错误]: {error_msg.split(':')[0]}")
            return
        
        # 查找所有Excel文件（使用缓存）
        if input_dir not in self._cache['directory_files']:
            self.logger.info("扫描目录查找Excel文件: %s", input_dir)
            self._cache['directory_files'][input_dir] = [f for f in os.listdir(input_dir) if f[:2] != "~$" and f[-5:] == ".xlsx"]
        
        excel_files = self._cache['directory_files'][input_dir]
        
        # 如果没有找到Excel文件，清除相关控件
        if not excel_files:
            self._handle_no_excel_files(input_dir)
            return
        
        # 使用pandas处理Excel文件
        excel_data = self._process_excel_files(input_dir, excel_files)
        
        # 如果没有成功处理的文件，显示错误
        if not excel_data:
            self.logger.error("没有成功处理的Excel文件")
            if hasattr(self.main_window, 'checker_input_xlsx'):
                self.main_window.checker_input_xlsx.set_error("没有成功处理的Excel文件，请检查文件格式")
            if hasattr(self.main_window, 'statusBar_BatteryAnalysis'):
                self.main_window.statusBar_BatteryAnalysis.showMessage("[错误]: 没有成功处理的Excel文件")
            return
        
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
            self.main_window.statusBar_BatteryAnalysis.showMessage(_("input_path_no_data", "[Error]: Input path has no data"))
    
    def _validate_excel_filename(self, filename):
        """验证Excel文件名的有效性
        
        Args:
            filename: 文件名
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        from battery_analysis.utils.file_validator import FileValidator
        
        validator = FileValidator()
        return validator.validate_excel_filename(filename)
    
    def _validate_excel_file_content(self, df, filename):
        """
        验证Excel文件内容的有效性
        
        Args:
            df: 数据框
            filename: 文件名
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        # 验证sheet页是否为空
        if df.empty:
            return False, f"Sheet页为空: {filename}"
        
        # 验证是否有列数据
        if len(df.columns) == 0:
            return False, f"Sheet页无列数据: {filename}"
        
        # 验证是否有行数据
        if len(df) == 0:
            return False, f"Sheet页无行数据: {filename}"
        
        # 尝试转换列数据类型，看是否能得到数值列
        numeric_columns = df.select_dtypes(include=['number']).columns
        
        # 如果没有数值列，尝试将可能的数值列转换为数值类型
        if len(numeric_columns) == 0:
            has_potential_numeric = False
            for col in df.columns:
                try:
                    # 尝试转换为数值类型
                    pd.to_numeric(df[col], errors='coerce')
                    has_potential_numeric = True
                    break
                except:
                    pass
            
            # 如果有潜在的数值列，只警告不报错
            if has_potential_numeric:
                self.logger.warning(f"Sheet页可能包含数值数据但未被识别: {filename}")
            else:
                # 只有当完全没有潜在数值列时才报错
                self.logger.warning(f"Sheet页无数值列数据: {filename}")
                # 这里改为警告，不返回错误，因为某些测试文件可能确实不需要数值列
        
        # 验证数据是否包含必要的信息
        # 检查是否有常见的电池测试列名
        common_columns = ['Capacity', '容量', 'Voltage', '电压', 'Current', '电流', 'Cycle', '循环', 'Temperature', '温度', 'Time', '时间']
        has_common_column = False
        for col in df.columns:
            if col in common_columns:
                has_common_column = True
                break
        
        if not has_common_column:
            self.logger.warning(f"Sheet页可能缺少必要的列: {filename}, 找到列: {list(df.columns)}")
            # 这里只警告，不返回错误，因为不同的测试可能有不同的列名
        
        return True, ""
    
    def _validate_excel_file(self, file_path, filename):
        """
        验证Excel文件的有效性
        
        Args:
            file_path: Excel文件路径
            filename: 文件名
            
        Returns:
            tuple: (是否有效, 错误消息, 数据框)
        """
        # 检查缓存
        cache_key = f"{file_path}:{filename}"
        if cache_key in self._cache['file_validation']:
            self.logger.info("从缓存读取文件验证结果: %s", file_path)
            return self._cache['file_validation'][cache_key]
        
        from battery_analysis.utils.file_validator import FileValidator
        validator = FileValidator()
        
        # 验证文件名
        is_valid, error_msg = self._validate_excel_filename(filename)
        if not is_valid:
            result = (False, error_msg, None)
            self._cache['file_validation'][cache_key] = result
            return result
        
        # 验证文件是否为空
        is_valid, error_msg = validator.validate_file_not_empty(file_path)
        if not is_valid:
            result = (False, error_msg, None)
            self._cache['file_validation'][cache_key] = result
            return result
        
        try:
            # 尝试读取Excel文件
            df = pd.read_excel(file_path, sheet_name=0, engine='openpyxl', header=0)
            
            # 优化DataFrame内存使用
            df = self.optimize_dataframe_memory(df)
            
            # 验证文件内容
            is_valid, error_msg = self._validate_excel_file_content(df, filename)
            if not is_valid:
                result = (False, error_msg, None)
                self._cache['file_validation'][cache_key] = result
                return result
            
            result = (True, "", df)
            self._cache['file_validation'][cache_key] = result
            return result
            
        except Exception as e:
            result = (False, f"Excel文件读取失败: {filename} - {str(e)}", None)
            self._cache['file_validation'][cache_key] = result
            return result
    
    def _process_excel_files(self, input_dir, excel_files):
        """处理Excel文件并提取信息"""
        excel_data = []
        error_files = []
        
        for filename in excel_files:
            file_path = os.path.join(input_dir, filename)
            self.logger.info("验证Excel文件: %s", filename)
            
            # 验证Excel文件
            is_valid, error_msg, df = self._validate_excel_file(file_path, filename)
            
            if not is_valid:
                self.logger.error(error_msg)
                error_files.append((filename, error_msg))
                continue
            
            try:
                self.logger.info("使用pandas处理Excel文件: %s", filename)
                
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
                error_msg = f"处理Excel文件失败: {filename} - {str(e)}"
                self.logger.error(error_msg)
                error_files.append((filename, error_msg))
                continue
        
        # 显示错误文件信息
        if error_files:
            error_message = "以下文件存在问题:\n"
            for filename, msg in error_files:
                error_message += f"- {filename}: {msg}\n"
            
            # 显示状态栏错误信息
            if hasattr(self.main_window, 'statusBar_BatteryAnalysis'):
                self.main_window.statusBar_BatteryAnalysis.showMessage(f"[错误]: 发现{len(error_files)}个问题文件")
            
            # 显示检查器错误信息
            if hasattr(self.main_window, 'checker_input_xlsx'):
                self.main_window.checker_input_xlsx.set_error(error_message)
            
            # 显示详细的错误对话框
            try:
                from PyQt6.QtWidgets import QMessageBox
                msg_box = QMessageBox(self.main_window)
                msg_box.setIcon(QMessageBox.Icon.Warning)
                msg_box.setWindowTitle("文件验证错误")
                msg_box.setText(f"发现 {len(error_files)} 个问题文件，无法分析")
                msg_box.setInformativeText("请检查文件格式和内容后重试")
                msg_box.setDetailedText(error_message)
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg_box.exec()
            except Exception as msg_error:
                self.logger.warning("显示错误对话框时出错: %s", msg_error)
        
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
            self.main_window.statusBar_BatteryAnalysis.showMessage(_("status_ready", "状态:就绪"))
    
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
        sorted_spec_types = sorted(enumerate(all_spec_types), key=lambda x: len(x[1]), reverse=True)
        for t, spec_type in sorted_spec_types:
            if spec_type in filename:
                self.main_window.comboBox_Specification_Type.setCurrentIndex(t)
                break
        
        # 匹配规格方法
        sorted_spec_methods = sorted(enumerate(all_spec_methods), key=lambda x: len(x[1]), reverse=True)
        for m, method in sorted_spec_methods:
            if method in filename:
                self.main_window.comboBox_Specification_Method.setCurrentIndex(m)
                break
        
        # 匹配制造商
        for m in range(self.main_window.comboBox_Manufacturer.count()):
            if self.main_window.comboBox_Manufacturer.itemText(m) in filename:
                self.main_window.comboBox_Manufacturer.setCurrentIndex(m)
                break
        
        # 提取批次日期代码
        batch_date_codes = re.findall("DC(.*?),", filename)
        if batch_date_codes:
            self.main_window.lineEdit_BatchDateCode.setText(batch_date_codes[0].strip())
        
        # 提取脉冲电流
        pulse_current_match = re.search(r"\(([\d.]+[-\d.]+)mA", filename)
        if pulse_current_match:
            pulse_current_values = pulse_current_match.group(1).split("-")
            try:
                self.main_window.listCurrentLevel = [float(c.strip()) for c in pulse_current_values]
            except ValueError:
                self.main_window.listCurrentLevel = [int(float(c.strip())) for c in pulse_current_values]
            self.main_window.config.setValue("BatteryConfig/PulseCurrent", pulse_current_values)
        
        # 提取恒流电流
        self.main_window.cc_current = ""
        cc_current_match = re.search(r"mA,(.*?)\)", filename)
        if cc_current_match:
            cc_current_str = cc_current_match.group(1).replace("mAh", "")
            cc_current_value = re.search(r"([\d.]+)mA", cc_current_str)
            if cc_current_value:
                self.main_window.cc_current = cc_current_value.group(1)
    
    def _set_specification_type(self, filename, all_spec_types):
        """设置规格类型，使用预处理和高效匹配"""
        # 预处理：按长度降序排序，优先匹配最长的规格类型
        sorted_spec_types = sorted(enumerate(all_spec_types), key=lambda x: len(x[1]), reverse=True)
        
        # 遍历匹配
        for t, spec_type in sorted_spec_types:
            if spec_type in filename:
                self.main_window.comboBox_Specification_Type.setCurrentIndex(t)
                return  # 找到最长匹配后直接返回，避免不必要的计算
    
    def _set_specification_method(self, filename, all_spec_methods):
        """设置规格方法，使用预处理和高效匹配"""
        # 预处理：按长度降序排序，优先匹配最长的规格方法
        sorted_spec_methods = sorted(enumerate(all_spec_methods), key=lambda x: len(x[1]), reverse=True)
        
        # 遍历匹配
        for m, method in sorted_spec_methods:
            if method in filename:
                self.main_window.comboBox_Specification_Method.setCurrentIndex(m)
                return  # 找到最长匹配后直接返回，避免不必要的计算
    
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
        分析数据，使用pandas优化分析逻辑，并行处理多个Excel文件
        """
        self.logger.info("开始数据分析")
        
        # 检查输入路径是否设置
        input_path = self.main_window.lineEdit_InputPath.text()
        if not input_path:
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
            # 查找所有Excel文件（使用缓存）
            if input_path not in self._cache['directory_files']:
                self.logger.info("扫描目录查找Excel文件: %s", input_path)
                self._cache['directory_files'][input_path] = [f for f in os.listdir(input_path) if f[:2] != "~$" and f[-5:] == ".xlsx"]
            
            excel_files = self._cache['directory_files'][input_path]
            
            if not excel_files:
                self.logger.warning("没有找到Excel文件")
                QW.QMessageBox.information(
                    self.main_window,
                    _("analysis_result", "分析结果"),
                    _("no_excel_files_found", "没有找到Excel文件。")
                )
                return
            
            # 使用并行处理Excel文件
            from concurrent.futures import ProcessPoolExecutor, as_completed
            
            def analyze_single_file(file_info):
                """分析单个Excel文件"""
                filename, input_path = file_info
                try:
                    file_path = os.path.join(input_path, filename)
                    # 使用pandas读取Excel文件
                    df = pd.read_excel(file_path, sheet_name=0, engine='openpyxl', header=0)
                    
                    # 优化DataFrame内存使用
                    # 复制内存优化函数的逻辑，因为在子进程中无法访问实例方法
                    def optimize_df_memory(df):
                        # 优化数值列
                        for col in df.select_dtypes(include=['int64']).columns:
                            df[col] = pd.to_numeric(df[col], downcast='integer')
                        
                        for col in df.select_dtypes(include=['float64']).columns:
                            df[col] = pd.to_numeric(df[col], downcast='float')
                        
                        # 优化对象列
                        for col in df.select_dtypes(include=['object']).columns:
                            # 检查唯一值比例
                            unique_ratio = len(df[col].unique()) / len(df[col])
                            if unique_ratio < 0.5:
                                df[col] = df[col].astype('category')
                        return df
                    
                    df = optimize_df_memory(df)
                    
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
                    
                    return analysis_result
                except Exception as e:
                    return {
                        'filename': filename,
                        'error': str(e)
                    }
            
            # 使用进程池并行处理
            from battery_analysis.utils.resource_manager import ResourceManager
            all_data = []
            failed_files = []
            
            # 获取最优进程数
            optimal_process_count = ResourceManager.get_optimal_process_count()
            actual_process_count = min(optimal_process_count, len(excel_files))
            
            with ProcessPoolExecutor(max_workers=actual_process_count) as executor:
                # 提交所有任务
                file_infos = [(filename, input_path) for filename in excel_files]
                future_to_file = {executor.submit(analyze_single_file, file_info): file_info[0] for file_info in file_infos}
                
                # 收集结果
                for future in as_completed(future_to_file):
                    filename = future_to_file[future]
                    result = future.result()
                    
                    if 'error' in result:
                        self.logger.error("分析Excel文件失败 %s: %s", filename, result['error'])
                        failed_files.append(filename)
                    else:
                        all_data.append(result)
            
            # 汇总分析结果
            summary = {
                'total_files': len(excel_files),
                'successful_files': len(all_data),
                'failed_files': len(excel_files) - len(all_data),
                'total_records': sum(item['total_records'] for item in all_data),
                'analysis_details': all_data
            }
            
            # 显示分析结果
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
