"""
数据处理器模块

负责处理数据相关的业务逻辑，包括Excel文件信息获取、数据验证等
"""

import logging
import os
import re
from concurrent.futures import ProcessPoolExecutor, as_completed
import pandas as pd
from PyQt6 import QtWidgets as QW
from PyQt6 import QtCore as QC

from battery_analysis.i18n.language_manager import _
from battery_analysis.main.business_logic.cache import LRUCache
from battery_analysis.main.business_logic.background_worker import BackgroundWorker
from battery_analysis.main.business_logic import excel_validator
from battery_analysis.main.business_logic import filename_parser


class DataProcessor:
    """
    数据处理器类，负责处理数据相关的业务逻辑
    """

    MAX_EXCEL_CACHE_SIZE = 50
    MAX_DIRECTORY_CACHE_SIZE = 20
    MAX_VALIDATION_CACHE_SIZE = 100

    def __init__(self, main_window):
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        self._cache = {
            'excel_files': LRUCache(self.MAX_EXCEL_CACHE_SIZE),
            'directory_files': LRUCache(self.MAX_DIRECTORY_CACHE_SIZE),
            'file_validation': LRUCache(self.MAX_VALIDATION_CACHE_SIZE),
        }
        self._background_thread = None
        self._background_worker = None

    def _invalidate_cache(self, path=None):
        if path:
            path_str = str(path)
            self._cache['excel_files'].remove(path_str)
            self._cache['file_validation'].remove(path_str)
            self._cache['directory_files'].remove(path_str)
        else:
            for c in self._cache.values():
                c.clear()

    def clear_cache(self):
        self._invalidate_cache()
        self.logger.info("DataProcessor cache cleared")

    def _cleanup_background_thread(self):
        if self._background_thread and self._background_thread.isRunning():
            self._background_thread.quit()
            self._background_thread.wait(1000)
            if self._background_thread.isRunning():
                self._background_thread.terminate()
        self._background_thread = None
        self._background_worker = None

    def run_in_background(self, task_func, on_finished, on_error, *args, **kwargs):
        self._cleanup_background_thread()
        self._background_thread = QC.QThread()
        self._background_worker = BackgroundWorker(task_func, *args, **kwargs)
        self._background_worker.moveToThread(self._background_thread)

        self._background_thread.started.connect(self._background_worker.run)
        self._background_worker.finished.connect(self._background_thread.quit)
        self._background_worker.finished.connect(self._background_worker.deleteLater)
        self._background_thread.finished.connect(self._background_thread.deleteLater)
        if on_finished:
            self._background_worker.finished.connect(on_finished)
        if on_error:
            self._background_worker.error.connect(on_error)
        self._background_thread.start()

    def get_cache_stats(self):
        return {
            'excel_files': len(self._cache['excel_files']),
            'directory_files': len(self._cache['directory_files']),
            'file_validation': len(self._cache['file_validation']),
            'max_excel': self.MAX_EXCEL_CACHE_SIZE,
            'max_directory': self.MAX_DIRECTORY_CACHE_SIZE,
            'max_validation': self.MAX_VALIDATION_CACHE_SIZE,
        }

    @staticmethod
    def optimize_dataframe_memory(df: pd.DataFrame) -> pd.DataFrame:
        for col in df.select_dtypes(include=['int64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='integer')
        for col in df.select_dtypes(include=['float64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='float')
        for col in df.select_dtypes(include=['object']).columns:
            if len(df[col].unique()) / len(df[col]) < 0.5:
                df[col] = df[col].astype('category')
        return df

    def process_excel_with_pandas(self, file_path: str) -> dict:
        try:
            cached = self._cache['excel_files'].get(file_path)
            if cached is not None:
                return cached

            df = pd.read_excel(file_path, sheet_name=0, engine='openpyxl', header=0)
            df = self.optimize_dataframe_memory(df)

            file_info = {
                'filename': os.path.basename(file_path),
                'sheet_name': df.columns.tolist(),
                'row_count': len(df),
                'column_count': len(df.columns),
                'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
                'non_numeric_columns': df.select_dtypes(exclude=['number']).columns.tolist(),
                'missing_values': df.isnull().sum().to_dict(),
                'basic_stats': df.describe().to_dict(),
            }
            self._cache['excel_files'].put(file_path, file_info)
            return file_info
        except Exception as e:
            self.logger.error("处理Excel文件失败 %s: %s", file_path, str(e))
            return {}

    def process_all_excel_files(self, directory: str) -> list:
        try:
            cached = self._cache['directory_files'].get(directory)
            if cached is None:
                listAllInXlsx = [f for f in os.listdir(directory) if f[:2] != "~$" and f[-5:] == ".xlsx"]
                self._cache['directory_files'].put(directory, listAllInXlsx)
            else:
                listAllInXlsx = cached

            if not listAllInXlsx:
                return []

            from battery_analysis.utils.resource_manager import ResourceManager
            excel_data = []
            optimal_count = ResourceManager.get_optimal_process_count()
            actual_count = min(optimal_count, len(listAllInXlsx))

            with ProcessPoolExecutor(max_workers=actual_count) as executor:
                futures = {executor.submit(self.process_excel_with_pandas, os.path.join(directory, f)): f
                           for f in listAllInXlsx}
                for future in as_completed(futures):
                    info = future.result()
                    if info:
                        excel_data.append(info)
            return excel_data
        except Exception:
            excel_data = []
            for f in os.listdir(directory):
                if f[:2] != "~$" and f[-5:] == ".xlsx":
                    info = self.process_excel_with_pandas(os.path.join(directory, f))
                    if info:
                        excel_data.append(info)
            return excel_data

    def _scan_excel_files_task(self, input_dir):
        return [f for f in os.listdir(input_dir) if f[:2] != "~$" and f[-5:] == ".xlsx"]

    def _on_scan_finished(self, excel_files):
        input_dir = self.main_window.lineEdit_InputPath.text()
        self._cache['directory_files'].put(input_dir, excel_files)

        if not excel_files:
            self._handle_no_excel_files(input_dir)
            return

        excel_data = self._process_excel_files(input_dir, excel_files)
        if not excel_data:
            self.logger.error("没有成功处理的Excel文件")
            if hasattr(self.main_window, 'checker_input_xlsx'):
                self.main_window.checker_input_xlsx.set_error("没有成功处理的Excel文件，请检查文件格式")
            if hasattr(self.main_window, 'statusBar_BatteryAnalysis'):
                self.main_window.statusBar_BatteryAnalysis.showMessage("[错误]: 没有成功处理的Excel文件")
            return

        self._update_ui_with_excel_info(excel_files, excel_data)
        if excel_files:
            self._process_first_excel_file(excel_files[0])
        self._reconnect_specification_signals()

    def _on_scan_error(self, error_msg):
        self.logger.error("扫描Excel文件失败: %s", error_msg)
        if hasattr(self.main_window, 'checker_input_xlsx'):
            self.main_window.checker_input_xlsx.set_error(f"扫描文件失败: {error_msg}")
        if hasattr(self.main_window, 'statusBar_BatteryAnalysis'):
            self.main_window.statusBar_BatteryAnalysis.showMessage("[错误]: 扫描文件失败")

    def get_xlsxinfo(self) -> None:
        self.logger.info("获取Excel文件信息")
        if hasattr(self.main_window, 'checker_input_xlsx'):
            self.main_window.checker_input_xlsx.clear()
        self._disconnect_specification_signals()

        input_dir = self.main_window.lineEdit_InputPath.text()
        from battery_analysis.utils.file_validator import FileValidator
        validator = FileValidator()
        is_valid, error_msg = validator.validate_input_directory(input_dir)
        if not is_valid:
            self.logger.error(error_msg)
            if hasattr(self.main_window, 'checker_input_xlsx'):
                self.main_window.checker_input_xlsx.set_error(error_msg)
            if hasattr(self.main_window, 'statusBar_BatteryAnalysis'):
                self.main_window.statusBar_BatteryAnalysis.showMessage(f"[错误]: {error_msg.split(':')[0]}")
            return

        cached = self._cache['directory_files'].get(input_dir)
        if cached is None:
            if hasattr(self.main_window, 'statusBar_BatteryAnalysis'):
                self.main_window.statusBar_BatteryAnalysis.showMessage("正在扫描Excel文件...")
            self.run_in_background(self._scan_excel_files_task, self._on_scan_finished,
                                   self._on_scan_error, input_dir)
        else:
            self._on_scan_finished(cached)

    def _disconnect_specification_signals(self):
        try:
            self.main_window.comboBox_Specification_Type.currentIndexChanged.disconnect(
                self.main_window.check_specification)
            self.main_window.comboBox_Specification_Method.currentIndexChanged.disconnect(
                self.main_window.check_specification)
        except (TypeError, AttributeError):
            pass

    def _handle_no_excel_files(self, input_dir):
        self.logger.warning("没有找到Excel文件: %s", input_dir)
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
        if hasattr(self.main_window, 'checker_input_xlsx'):
            self.main_window.checker_input_xlsx.set_error("Input path has no data")
        if hasattr(self.main_window, 'statusBar_BatteryAnalysis'):
            self.main_window.statusBar_BatteryAnalysis.showMessage(
                _("input_path_no_data", "[Error]: Input path has no data"))

    def _process_excel_files(self, input_dir, excel_files):
        excel_data = []
        error_files = []
        for filename in excel_files:
            file_path = os.path.join(input_dir, filename)
            is_valid, error_msg, df = excel_validator.validate_excel_file(
                file_path, filename, self._cache['file_validation'], self.optimize_dataframe_memory)
            if not is_valid:
                self.logger.error(error_msg)
                error_files.append((filename, error_msg))
                continue
            file_info = {
                'filename': filename,
                'sheet_name': df.columns.tolist(),
                'row_count': len(df),
                'column_count': len(df.columns),
                'first_five_rows': df.head().to_dict('records'),
            }
            excel_data.append(file_info)

        if error_files:
            error_message = "以下文件存在问题:\n" + "\n".join(f"- {f}: {m}" for f, m in error_files)
            if hasattr(self.main_window, 'statusBar_BatteryAnalysis'):
                self.main_window.statusBar_BatteryAnalysis.showMessage(
                    f"[错误]: 发现{len(error_files)}个问题文件")
            if hasattr(self.main_window, 'checker_input_xlsx'):
                self.main_window.checker_input_xlsx.set_error(error_message)
            try:
                msg = QW.QMessageBox(self.main_window)
                msg.setIcon(QW.QMessageBox.Icon.Warning)
                msg.setWindowTitle("文件验证错误")
                msg.setText(f"发现 {len(error_files)} 个问题文件，无法分析")
                msg.setInformativeText("请检查文件格式和内容后重试")
                msg.setDetailedText(error_message)
                msg.setStandardButtons(QW.QMessageBox.StandardButton.Ok)
                msg.exec()
            except Exception as e:
                self.logger.warning("显示错误对话框时出错: %s", e)

        return excel_data

    def _update_ui_with_excel_info(self, excel_files, excel_data):
        self.main_window.lineEdit_SamplesQty.setText(str(len(excel_files)))
        if hasattr(self.main_window, 'checker_input_xlsx'):
            self.main_window.checker_input_xlsx.clear()
        if hasattr(self.main_window, 'statusBar_BatteryAnalysis'):
            self.main_window.statusBar_BatteryAnalysis.showMessage(_("status_ready", "状态:就绪"))

    def _process_first_excel_file(self, filename):
        mw = self.main_window
        mw.construction_method = ""
        for c in range(mw.comboBox_ConstructionMethod.count()):
            if mw.comboBox_ConstructionMethod.itemText(c) in filename:
                mw.construction_method = mw.comboBox_ConstructionMethod.itemText(c)
                break

        all_spec_types = mw.get_config("BatteryConfig/SpecificationTypeCoinCell") + \
                         mw.get_config("BatteryConfig/SpecificationTypePouchCell")
        all_spec_methods = mw.get_config("BatteryConfig/SpecificationMethod")

        filename_parser.set_specification_type(filename, all_spec_types, mw.comboBox_Specification_Type)
        filename_parser.set_specification_method(filename, all_spec_methods, mw.comboBox_Specification_Method)
        filename_parser.set_manufacturer(filename, mw.comboBox_Manufacturer)
        filename_parser.extract_batch_date_code(filename, mw.lineEdit_BatchDateCode)

        pulse_values = filename_parser.extract_pulse_current(filename)
        if pulse_values:
            mw.listCurrentLevel = pulse_values
            mw.config.setValue("BatteryConfig/PulseCurrent", pulse_values)

        mw.cc_current = filename_parser.extract_cc_current(filename)

    def _reconnect_specification_signals(self):
        try:
            self.main_window.comboBox_Specification_Type.currentIndexChanged.connect(
                self.main_window.check_specification)
            self.main_window.comboBox_Specification_Method.currentIndexChanged.connect(
                self.main_window.check_specification)
            self.main_window.check_specification()
        except (TypeError, AttributeError):
            pass

    def save_table(self) -> None:
        self.logger.info("保存表格数据")
        self.main_window.pushButton_Run.setFocus()

        def set_item(config_key, row, col):
            item = self.main_window.tableWidget_TestInformation.item(row, col)
            if item and hasattr(self.main_window, 'config'):
                self.main_window.config.setValue(config_key, item.text())

        mappings = [
            ("TestInformation/TestEquipment", 0, 2),
            ("TestInformation/BTS_Server_Version", 1, 2),
            ("TestInformation/BTS_Client_Version", 2, 2),
            ("TestInformation/Data_Analysis_Version", 3, 2),
            ("TestInformation/Software_Version", 4, 2),
            ("TestInformation/Testing_Company", 5, 1),
            ("TestInformation/Testing_Department", 5, 2),
            ("TestInformation/Testing_Location", 6, 1),
            ("TestInformation/Testing_Room", 6, 2),
            ("TestInformation/Testing_Standard", 7, 1),
            ("TestInformation/Test_Method", 7, 2),
            ("TestInformation/Battery_Manufacturer", 8, 1),
            ("TestInformation/Battery_Model", 8, 2),
            ("TestInformation/Battery_Type", 9, 1),
            ("TestInformation/Battery_Chemistry", 9, 2),
            ("TestInformation/Battery_Capacity", 10, 1),
            ("TestInformation/Battery_Voltage", 10, 2),
            ("TestInformation/Battery_Series", 11, 1),
            ("TestInformation/Battery_Parallel", 11, 2),
            ("TestInformation/Test_Date", 12, 1),
            ("TestInformation/Test_Time", 12, 2),
            ("TestInformation/Test_Operator", 13, 1),
            ("TestInformation/Test_Assistant", 13, 2),
            ("TestInformation/Test_Temperature", 14, 1),
            ("TestInformation/Test_Humidity", 14, 2),
            ("TestInformation/Test_Comments", 15, 1),
            ("TestInformation/Test_Results", 15, 2),
        ]
        for key, row, col in mappings:
            set_item(key, row, col)

    def update_config(self, test_info) -> None:
        self.logger.info("更新配置")
        if not hasattr(self.main_window, 'checker_update_config'):
            from battery_analysis.main.main_window import Checker
            self.main_window.checker_update_config = Checker()
        self.main_window.checker_update_config.clear()

        if hasattr(self.main_window, 'config'):
            for key in ("TestDate", "TestTime", "BatteryModel", "TestEquipment", "Software_Version"):
                self.main_window.config.setValue(f"UserConfig/{key}", test_info[key])

    def analyze_data(self) -> None:
        self.logger.info("开始数据分析")
        input_path = self.main_window.lineEdit_InputPath.text()
        if not input_path:
            QW.QMessageBox.warning(self.main_window, _("warning_title", "警告"),
                                   _("input_path_not_set", "请先设置输入路径。"))
            return

        self.main_window.statusBar_BatteryAnalysis.showMessage(_("analyzing_data", "分析数据..."))

        try:
            cached = self._cache['directory_files'].get(input_path)
            if cached is None:
                excel_files = [f for f in os.listdir(input_path) if f[:2] != "~$" and f[-5:] == ".xlsx"]
                self._cache['directory_files'].put(input_path, excel_files)
            else:
                excel_files = cached

            if not excel_files:
                QW.QMessageBox.information(self.main_window, _("analysis_result", "分析结果"),
                                           _("no_excel_files_found", "没有找到Excel文件。"))
                return

            def analyze_single_file(file_info):
                filename, path = file_info
                try:
                    df = pd.read_excel(os.path.join(path, filename), sheet_name=0, engine='openpyxl', header=0)

                    def optimize_df_memory(df):
                        for col in df.select_dtypes(include=['int64']).columns:
                            df[col] = pd.to_numeric(df[col], downcast='integer')
                        for col in df.select_dtypes(include=['float64']).columns:
                            df[col] = pd.to_numeric(df[col], downcast='float')
                        for col in df.select_dtypes(include=['object']).columns:
                            if len(df[col].unique()) / len(df[col]) < 0.5:
                                df[col] = df[col].astype('category')
                        return df

                    df = optimize_df_memory(df)
                    return {
                        'filename': filename,
                        'total_records': len(df),
                        'columns': df.columns.tolist(),
                        'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
                        'non_numeric_columns': df.select_dtypes(exclude=['number']).columns.tolist(),
                        'missing_values': df.isnull().sum().to_dict(),
                        'basic_stats': df.describe().to_dict(),
                    }
                except Exception as e:
                    return {'filename': filename, 'error': str(e)}

            from battery_analysis.utils.resource_manager import ResourceManager
            all_data = []
            optimal_count = ResourceManager.get_optimal_process_count()
            actual_count = min(optimal_count, len(excel_files))

            with ProcessPoolExecutor(max_workers=actual_count) as executor:
                futures = {executor.submit(analyze_single_file, (f, input_path)): f for f in excel_files}
                for future in as_completed(futures):
                    result = future.result()
                    if 'error' in result:
                        self.logger.error("分析失败 %s: %s", result['filename'], result['error'])
                    else:
                        all_data.append(result)

            summary = {
                'total_files': len(excel_files),
                'successful_files': len(all_data),
                'failed_files': len(excel_files) - len(all_data),
                'total_records': sum(r['total_records'] for r in all_data),
            }

            msg = (f"数据分析已完成！\n\n总文件数: {summary['total_files']}\n"
                   f"成功分析: {summary['successful_files']}\n"
                   f"失败文件: {summary['failed_files']}\n"
                   f"总记录数: {summary['total_records']}\n\n详细结果已记录到日志。")
            QW.QMessageBox.information(self.main_window, _("analysis_result", "分析结果"), msg)
            self.logger.info("数据分析汇总: %s", summary)

        except Exception as e:
            self.logger.error("数据分析失败: %s", str(e))
            QW.QMessageBox.error(self.main_window, _("error_title", "错误"),
                                 _("data_analysis_failed", "数据分析失败: {}").format(str(e)))
        finally:
            self.main_window.statusBar_BatteryAnalysis.showMessage(_("status_ready", "状态:就绪"))
