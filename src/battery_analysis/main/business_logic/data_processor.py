"""
数据处理器模块

负责处理数据相关的业务逻辑，包括Excel文件信息获取、数据验证等
"""

import logging
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from PyQt6 import QtWidgets as QW
from PyQt6 import QtCore as QC

from battery_analysis.i18n.language_manager import _
from battery_analysis.main.business_logic.cache import LRUCache
from battery_analysis.main.business_logic.background_worker import BackgroundWorker
from battery_analysis.main.business_logic import excel_validator
from battery_analysis.main.business_logic import filename_parser
from battery_analysis.utils.processors.excel_processor import optimize_dataframe_memory, read_excel_file, analyze_single_excel


class _MainThreadCallback(QC.QObject):
    """确保回调在 Qt 主线程执行的信号中继器

    用法: 包装回调后连接到后台线程的信号，自动通过 QueuedConnection
    将执行切换到主线程。
    """
    _signal = QC.pyqtSignal(object)

    def __init__(self, callback):
        super().__init__()
        self._callback = callback
        self._signal.connect(self._invoke, QC.Qt.ConnectionType.QueuedConnection)

    def __call__(self, result):
        self._signal.emit(result)

    def _invoke(self, result):
        self._callback(result)


class DataProcessor:
    """
    数据处理器类，负责处理数据相关的业务逻辑
    """

    MAX_EXCEL_CACHE_SIZE = 50
    MAX_DIRECTORY_CACHE_SIZE = 20
    MAX_VALIDATION_CACHE_SIZE = 100

    def __init__(self, main_window=None, ctx=None):
        self.main_window = main_window
        self._ctx = ctx
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
            self._background_worker.finished.connect(_MainThreadCallback(on_finished))
        if on_error:
            self._background_worker.error.connect(_MainThreadCallback(on_error))
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

    def process_excel_with_pandas(self, file_path: str) -> dict:
        cached = self._cache['excel_files'].get(file_path)
        if cached is not None:
            return cached

        file_info = read_excel_file(file_path)
        if file_info:
            self._cache['excel_files'].put(file_path, file_info)
        return file_info

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

    def _scan_excel_files_task(self, input_dir, **kwargs):
        return [f for f in os.listdir(input_dir) if f[:2] != "~$" and f[-5:] == ".xlsx"]

    def _on_scan_finished(self, excel_files):
        input_dir = self.main_window.lineEdit_InputPath.text()
        self._cache['directory_files'].put(input_dir, excel_files)

        if not excel_files:
            self._handle_no_excel_files(input_dir)
            return

        excel_data = self._process_excel_files(input_dir, excel_files)
        if not excel_data:
            self.logger.error("No Excel files were processed successfully")
            if hasattr(self.main_window, 'checker_input_xlsx'):
                self.main_window.checker_input_xlsx.set_error("No Excel files were processed successfully. Please check the file format.")
            if hasattr(self.main_window, 'statusBar_BatteryAnalysis'):
                self.main_window.statusBar_BatteryAnalysis.showMessage("[Error]: No Excel files were processed successfully")
            return

        self._update_ui_with_excel_info(excel_files, excel_data)
        if excel_files:
            self._process_first_excel_file(excel_files[0])
        self._reconnect_specification_signals()

    def _on_scan_error(self, error_msg):
        self.logger.error("Failed to scan Excel files: %s", error_msg)
        if hasattr(self.main_window, 'checker_input_xlsx'):
            self.main_window.checker_input_xlsx.set_error(f"Failed to scan files: {error_msg}")
        if hasattr(self.main_window, 'statusBar_BatteryAnalysis'):
            self.main_window.statusBar_BatteryAnalysis.showMessage("[Error]: Failed to scan files")

    def get_xlsxinfo(self) -> None:
        self.logger.info("Retrieving Excel file info")
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
                self.main_window.statusBar_BatteryAnalysis.showMessage(f"[Error]: {error_msg.split(':')[0]}")
            return

        cached = self._cache['directory_files'].get(input_dir)
        if cached is None:
            if hasattr(self.main_window, 'statusBar_BatteryAnalysis'):
                self.main_window.statusBar_BatteryAnalysis.showMessage("Scanning Excel files...")
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
        self.logger.warning("No Excel files found: %s", input_dir)
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
                _("[Error]: Input path has no data"))

    def _process_excel_files(self, input_dir, excel_files):
        excel_data = []
        error_files = []
        for filename in excel_files:
            file_path = os.path.join(input_dir, filename)
            is_valid, error_msg, df = excel_validator.validate_excel_file(
                file_path, filename, self._cache['file_validation'], optimize_dataframe_memory)
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
            error_message = "The following files have issues:\n" + "\n".join(f"- {f}: {m}" for f, m in error_files)
            if hasattr(self.main_window, 'statusBar_BatteryAnalysis'):
                self.main_window.statusBar_BatteryAnalysis.showMessage(
                    f"[Error]: Found {len(error_files)} problematic files")
            if hasattr(self.main_window, 'checker_input_xlsx'):
                self.main_window.checker_input_xlsx.set_error(error_message)
            try:
                msg = QW.QMessageBox(self.main_window)
                msg.setIcon(QW.QMessageBox.Icon.Warning)
                msg.setWindowTitle("File Validation Error")
                msg.setText(f"Found {len(error_files)} problematic files that cannot be analyzed")
                msg.setInformativeText("Please check the file format and content, then retry")
                msg.setDetailedText(error_message)
                msg.setStandardButtons(QW.QMessageBox.StandardButton.Ok)
                msg.exec()
            except Exception as e:
                self.logger.warning("Error showing error dialog: %s", e)

        return excel_data

    def _update_ui_with_excel_info(self, excel_files, excel_data):
        self.main_window.lineEdit_SamplesQty.setText(str(len(excel_files)))
        if hasattr(self.main_window, 'checker_input_xlsx'):
            self.main_window.checker_input_xlsx.clear()
        if hasattr(self.main_window, 'statusBar_BatteryAnalysis'):
            self.main_window.statusBar_BatteryAnalysis.showMessage(_("Ready"))

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
            cs = mw._get_service("config")
            if cs:
                cs.set_config_value("BatteryConfig/PulseCurrent", ", ".join(map(str, pulse_values)))
                cs.save_config()

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
        self.logger.info("Saving table data")
        self.main_window.pushButton_Run.setFocus()

        def set_item(config_key, row, col):
            item = self.main_window.tableWidget_TestInformation.item(row, col)
            if item:
                cs = self.main_window._get_service("config")
                if cs:
                    cs.set_config_value(config_key, item.text())
                    cs.save_config()

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
        self.logger.info("Updating configuration")
        if not hasattr(self.main_window, 'checker_update_config'):
            from battery_analysis.main.main_window import Checker
            self.main_window.checker_update_config = Checker()
        self.main_window.checker_update_config.clear()

    def analyze_data(self) -> None:
        self.logger.info("Starting data analysis")
        input_path = self.main_window.lineEdit_InputPath.text()
        if not input_path:
            QW.QMessageBox.warning(self.main_window, _("Warning"),
                                   _("Please set the input path first."))
            return

        self.main_window.statusBar_BatteryAnalysis.showMessage(_("Analyzing data..."))

        try:
            cached = self._cache['directory_files'].get(input_path)
            if cached is None:
                excel_files = [f for f in os.listdir(input_path) if f[:2] != "~$" and f[-5:] == ".xlsx"]
                self._cache['directory_files'].put(input_path, excel_files)
            else:
                excel_files = cached

            if not excel_files:
                QW.QMessageBox.information(self.main_window, _("Analysis Result"),
                                           _("No Excel files found."))
                return

            from battery_analysis.utils.resource_manager import ResourceManager
            all_data = []
            optimal_count = ResourceManager.get_optimal_process_count()
            actual_count = min(optimal_count, len(excel_files))

            with ProcessPoolExecutor(max_workers=actual_count) as executor:
                futures = {
                    executor.submit(analyze_single_excel, os.path.join(input_path, f), f): f
                    for f in excel_files
                }
                for future in as_completed(futures):
                    result = future.result()
                    if 'error' in result:
                        self.logger.error("Analysis failed %s: %s", result['filename'], result['error'])
                    else:
                        all_data.append(result)

            summary = {
                'total_files': len(excel_files),
                'successful_files': len(all_data),
                'failed_files': len(excel_files) - len(all_data),
                'total_records': sum(r['total_records'] for r in all_data),
            }

            msg = (f"Data analysis completed!\n\nTotal files: {summary['total_files']}\n"
                   f"Successful: {summary['successful_files']}\n"
                   f"Failed: {summary['failed_files']}\n"
                   f"Total records: {summary['total_records']}\n\nDetailed results have been logged.")
            QW.QMessageBox.information(self.main_window, _("Analysis Result"), msg)
            self.logger.info("Data analysis summary: %s", summary)

        except Exception as e:
            self.logger.error("Data analysis failed: %s", str(e))
            QW.QMessageBox.critical(self.main_window, _("Error"),
                                    _("Data analysis failed: {}").format(str(e)))
        finally:
            self.main_window.statusBar_BatteryAnalysis.showMessage(_("Ready"))
