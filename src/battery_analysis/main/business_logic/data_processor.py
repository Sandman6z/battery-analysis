"""
数据处理器模块

负责处理数据相关的业务逻辑，包括Excel文件信息获取、数据验证等
"""

import logging
import os

from PyQt6 import QtCore as QC
from PyQt6 import QtWidgets as QW

from battery_analysis.i18n.language_manager import _
from battery_analysis.main.business_logic import excel_validator, filename_parser
from battery_analysis.main.business_logic.cache import LRUCache
from battery_analysis.main.workers.task_runner import TaskManager, TaskRunner
from battery_analysis.utils.pulse_currents import (
    capacity_from_rules,
    is_freezer_context,
    lookup_pulse_currents,
    normalize_current_levels,
)


class DataProcessor:
    """
    数据处理器类，负责处理数据相关的业务逻辑
    """

    MAX_EXCEL_CACHE_SIZE = 50
    MAX_DIRECTORY_CACHE_SIZE = 20
    MAX_VALIDATION_CACHE_SIZE = 100

    # 文件名未识别到规格方法时的默认值（用户确认提示，5 秒自动关闭）
    SPEC_METHOD_DEFAULT = "1S1P"
    SPEC_METHOD_NOTICE_TIMEOUT_MS = 5000

    def __init__(self, main_window=None):
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        self._cache = {
            "excel_files": LRUCache(self.MAX_EXCEL_CACHE_SIZE),
            "directory_files": LRUCache(self.MAX_DIRECTORY_CACHE_SIZE),
            "file_validation": LRUCache(self.MAX_VALIDATION_CACHE_SIZE),
        }
        self._scan_generation = 0
        self._task_manager = TaskManager()
        self._spec_method_defaulted = False

    def _invalidate_cache(self, path=None):
        if path:
            path_str = str(path)
            self._cache["excel_files"].remove(path_str)
            self._cache["file_validation"].remove(path_str)
            self._cache["directory_files"].remove(path_str)
        else:
            for c in self._cache.values():
                c.clear()

    def clear_cache(self):
        self._invalidate_cache()
        self.logger.info("DataProcessor cache cleared")

    def _run_async(self, task_func, on_finished, on_error, *args, **kwargs):
        """TaskRunner 派发：回调经 TaskSignals 自动回主线程（AutoConnection Queued）。"""
        runner = TaskRunner(task_func, *args, **kwargs)
        if on_finished:
            runner.signals.finished.connect(on_finished)
        if on_error:
            runner.signals.error.connect(on_error)
        self._task_manager.submit(runner)
        return runner

    def get_cache_stats(self):
        return {
            "excel_files": len(self._cache["excel_files"]),
            "directory_files": len(self._cache["directory_files"]),
            "file_validation": len(self._cache["file_validation"]),
            "max_excel": self.MAX_EXCEL_CACHE_SIZE,
            "max_directory": self.MAX_DIRECTORY_CACHE_SIZE,
            "max_validation": self.MAX_VALIDATION_CACHE_SIZE,
        }

    def _scan_excel_files_task(self, input_dir, **kwargs):
        return [f for f in os.listdir(input_dir) if f[:2] != "~$" and f[-5:] == ".xlsx"]

    def _on_scan_finished(self, excel_files):
        input_dir = self.main_window.lineEdit_InputPath.text()
        self._cache["directory_files"].put(input_dir, excel_files)
        # generation 已在 get_xlsxinfo 请求时推进（唯一入口）；此处仅捕获当前值
        # 传给后续 process dispatch 的 closures，守卫判定在 _on_excel_files_processed。
        generation = self._scan_generation

        if not excel_files:
            self._handle_no_excel_files(input_dir)
            return

        # 逐文件 pd.read_excel 校验是重活，放后台线程执行；回调经
        # TaskSignals 自动回主线程弹窗/更新 UI（roadmap #9）。
        self._run_async(
            self._process_excel_files_task,
            lambda result, g=generation: self._on_excel_files_processed(result, g),
            lambda error, g=generation: self._on_excel_files_process_error(error, g),
            input_dir,
            excel_files,
        )

    def _on_scan_error(self, error_msg):
        self.logger.error("Failed to scan Excel files: %s", error_msg)
        if hasattr(self.main_window, "checker_input_xlsx"):
            self.main_window.checker_input_xlsx.set_error(f"Failed to scan files: {error_msg}")
        if hasattr(self.main_window, "statusBar_BatteryAnalysis"):
            self.main_window.statusBar_BatteryAnalysis.showMessage("[Error]: Failed to scan files")

    def get_xlsxinfo(self) -> None:
        self.logger.info("Retrieving Excel file info")
        if hasattr(self.main_window, "checker_input_xlsx"):
            self.main_window.checker_input_xlsx.clear()
        self._disconnect_specification_signals()

        input_dir = self.main_window.lineEdit_InputPath.text()
        from battery_analysis.utils.file_validator import FileValidator

        validator = FileValidator()
        is_valid, error_msg = validator.validate_input_directory(input_dir)
        if not is_valid:
            self.logger.error(error_msg)
            # 对齐 version_manager else 分支：无效路径也推进代次并取消在途任务，
            # 防在途旧 process 结果（generation 匹配旧值）误接受覆盖当前无效路径 UI。
            self._scan_generation += 1
            self._task_manager.cancel_all()
            if hasattr(self.main_window, "checker_input_xlsx"):
                self.main_window.checker_input_xlsx.set_error(error_msg)
            if hasattr(self.main_window, "statusBar_BatteryAnalysis"):
                self.main_window.statusBar_BatteryAnalysis.showMessage(
                    f"[Error]: {error_msg.split(':')[0]}"
                )
            # 信号在 get_xlsxinfo 入口已断开，提前返回也需重连，
            # 否则后续手动选择规格不会触发规则填充。
            self._reconnect_specification_signals()
            return

        # 新扫描请求会切换 UI 目标：请求时即推进 generation，使任何在途/已入队的旧
        # process 结果（generation 低于新值）被守卫丢弃（对齐 version_manager 派发时
        # 推进语义）；同时取消在途 process/scan 任务（协作式，逐文件 progress_callback
        # 检查点抛 TaskCancelled），中断仍在执行的路径。双保险。
        self._task_manager.cancel_all()
        self._scan_generation += 1

        cached = self._cache["directory_files"].get(input_dir)
        if cached is None:
            if hasattr(self.main_window, "statusBar_BatteryAnalysis"):
                self.main_window.statusBar_BatteryAnalysis.showMessage("Scanning Excel files...")
            self._run_async(
                self._scan_excel_files_task, self._on_scan_finished, self._on_scan_error, input_dir
            )
        else:
            self._on_scan_finished(cached)

    def _disconnect_specification_signals(self):
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
        self.logger.warning("No Excel files found: %s", input_dir)
        self.main_window.comboBox_BatteryType.setCurrentIndex(-1)
        self.main_window.comboBox_Specification_Type.clear()
        self.main_window.comboBox_Specification_Type.addItems(
            self.main_window.config_manager.get_config("BatteryConfig/SpecificationTypeCoinCell")
        )
        self.main_window.comboBox_Specification_Type.addItems(
            self.main_window.config_manager.get_config("BatteryConfig/SpecificationTypePouchCell")
        )
        self.main_window.comboBox_Specification_Type.setCurrentIndex(-1)
        self.main_window.comboBox_Specification_Method.clear()
        self.main_window.comboBox_Specification_Method.addItems(
            self.main_window.config_manager.get_config("BatteryConfig/SpecificationMethod")
        )
        self.main_window.comboBox_Specification_Method.setCurrentIndex(-1)
        self.main_window.comboBox_Manufacturer.setCurrentIndex(-1)
        self.main_window.lineEdit_BatchDateCode.setText("")
        self.main_window.lineEdit_SamplesQty.setText("")
        self.main_window.lineEdit_DatasheetNominalCapacity.setText("")
        self.main_window.lineEdit_CalculationNominalCapacity.setText("")
        if hasattr(self.main_window, "checker_input_xlsx"):
            self.main_window.checker_input_xlsx.set_error("Input path has no data")
        if hasattr(self.main_window, "statusBar_BatteryAnalysis"):
            self.main_window.statusBar_BatteryAnalysis.showMessage(
                _("[Error]: Input path has no data")
            )
        # 无文件路径同样重连规格信号（修复：此前仅成功/异常路径重连）
        self._reconnect_specification_signals()

    def _process_excel_files_task(self, input_dir, excel_files, progress_callback=None, **kwargs):
        """后台线程：逐文件验证并提取 Excel 元信息（不触碰任何 UI）。

        progress_callback 由 TaskRunner 注入，每次调用即协作式取消检查点。
        返回 (excel_files, excel_data, error_files)。
        """
        excel_data = []
        error_files = []
        for index, filename in enumerate(excel_files):
            if progress_callback:
                progress_callback(
                    int((index + 1) / len(excel_files) * 100), f"Validating {filename}..."
                )
            file_path = os.path.join(input_dir, filename)
            is_valid, error_msg, df = excel_validator.validate_excel_file(
                file_path, filename, self._cache["file_validation"]
            )
            if not is_valid:
                self.logger.error(error_msg)
                error_files.append((filename, error_msg))
                continue
            file_info = {
                "filename": filename,
                "sheet_name": df.columns.tolist(),
                "row_count": len(df),
                "column_count": len(df.columns),
                "first_five_rows": df.head().to_dict("records"),
            }
            excel_data.append(file_info)
        return excel_files, excel_data, error_files

    def _on_excel_files_processed(self, result, generation):
        """主线程：_process_excel_files_task 完成后的 UI 更新"""
        # 过期结果守卫（generation 精确匹配）：用户已切换输入路径时丢弃旧代次结果。
        if generation != self._scan_generation:
            self.logger.info("Discarding stale Excel parse result for changed input path")
            return

        excel_files, excel_data, error_files = result

        if error_files:
            error_message = "The following files have issues:\n" + "\n".join(
                f"- {f}: {m}" for f, m in error_files
            )
            if hasattr(self.main_window, "statusBar_BatteryAnalysis"):
                self.main_window.statusBar_BatteryAnalysis.showMessage(
                    f"[Error]: Found {len(error_files)} problematic files"
                )
            if hasattr(self.main_window, "checker_input_xlsx"):
                self.main_window.checker_input_xlsx.set_error(error_message)
            try:
                # 只在状态栏和 checker 显示错误，不弹框
                pass
            except Exception as e:  # pylint: disable=broad-exception-caught
                self.logger.warning("Error showing error dialog: %s", e)

        if not excel_data:
            self.logger.error("No Excel files were processed successfully")
            if hasattr(self.main_window, "checker_input_xlsx"):
                self.main_window.checker_input_xlsx.set_error(
                    "No Excel files were processed successfully. Please check the file format."
                )
            if hasattr(self.main_window, "statusBar_BatteryAnalysis"):
                self.main_window.statusBar_BatteryAnalysis.showMessage(
                    "[Error]: No Excel files were processed successfully"
                )
            return

        self._update_ui_with_excel_info(excel_files, excel_data)
        if excel_data:
            self._process_first_excel_file(excel_data[0]["filename"])
        self._reconnect_specification_signals()
        if self._spec_method_defaulted:
            self._spec_method_defaulted = False
            self._show_spec_method_default_notice()

    def _on_excel_files_process_error(self, error_msg, generation):
        """主线程：后台任务异常兜底"""
        # 过期结果守卫（generation 精确匹配）：用户已切换输入路径时丢弃旧代次错误。
        if generation != self._scan_generation:
            self.logger.info("Discarding stale Excel parse result for changed input path")
            return
        self.logger.error("Failed to process Excel files: %s", error_msg)
        if hasattr(self.main_window, "checker_input_xlsx"):
            self.main_window.checker_input_xlsx.set_error(f"Failed to process files: {error_msg}")
        if hasattr(self.main_window, "statusBar_BatteryAnalysis"):
            self.main_window.statusBar_BatteryAnalysis.showMessage(
                "[Error]: Failed to process files"
            )
        self._reconnect_specification_signals()

    def _update_ui_with_excel_info(self, excel_files, excel_data):
        self.main_window.lineEdit_SamplesQty.setText(str(len(excel_files)))
        if hasattr(self.main_window, "checker_input_xlsx"):
            self.main_window.checker_input_xlsx.clear()
        if hasattr(self.main_window, "statusBar_BatteryAnalysis"):
            self.main_window.statusBar_BatteryAnalysis.showMessage(_("Ready"))

    def _process_first_excel_file(self, filename):
        mw = self.main_window
        mw.construction_method = ""
        for c in range(mw.comboBox_ConstructionMethod.count()):
            if mw.comboBox_ConstructionMethod.itemText(c) in filename:
                mw.construction_method = mw.comboBox_ConstructionMethod.itemText(c)
                break

        all_spec_types = mw.config_manager.get_config("BatteryConfig/SpecificationTypeCoinCell") + mw.config_manager.get_config(
            "BatteryConfig/SpecificationTypePouchCell"
        )
        all_spec_methods = mw.config_manager.get_config("BatteryConfig/SpecificationMethod")

        filename_parser.set_specification_type(
            filename, all_spec_types, mw.comboBox_Specification_Type
        )
        method_matched = filename_parser.set_specification_method(
            filename, all_spec_methods, mw.comboBox_Specification_Method
        )
        # 文件名未提到规格方法（如 1S1P）→ 默认选 1S1P，识别带出后弹框请用户确认
        self._spec_method_defaulted = False
        if not method_matched and self.SPEC_METHOD_DEFAULT in (all_spec_methods or []):
            mw.comboBox_Specification_Method.setCurrentIndex(
                all_spec_methods.index(self.SPEC_METHOD_DEFAULT)
            )
            self._spec_method_defaulted = True
            self.logger.info(
                "Specification method not found in filename %s; defaulting to %s",
                filename,
                self.SPEC_METHOD_DEFAULT,
            )
        filename_parser.set_manufacturer(filename, mw.comboBox_Manufacturer)
        filename_parser.extract_batch_date_code(filename, mw.lineEdit_BatchDateCode)

        # 脉冲电流档位：文件名解析优先，容量档位查表兜底（BatteryQualityRequirements_v2.3 §7.1.1）
        pulse_values = filename_parser.extract_pulse_current(filename)
        table_values = self._lookup_pulse_currents_from_table(filename)
        if pulse_values and table_values:
            # 双重验证：文件名档位 vs 型号/容量查表档位，不一致则告警（以文件名为准）
            self._verify_pulse_currents(filename, pulse_values, table_values)
        if not pulse_values:
            pulse_values = table_values
        if pulse_values:
            pulse_values = normalize_current_levels(pulse_values)
            mw.listCurrentLevel = pulse_values
            cs = mw._get_service("config")
            if cs:
                cs.set_config_value("battery.pulseCurrents", pulse_values)
                cs.save_config()

        mw.cc_current = filename_parser.extract_cc_current(filename)

    def _lookup_pulse_currents_from_table(self, filename) -> list:
        """文件名未携带脉冲电流时，按型号/容量查表兜底获取脉冲电流档位

        Args:
            filename: Excel 文件名（用于识别冷冻型）

        Returns:
            脉冲电流档位列表，无法确定时返回空列表
        """
        mw = self.main_window
        try:
            spec_name = mw.comboBox_Specification_Type.currentText().strip()
            spec_method = mw.comboBox_Specification_Method.currentText().strip()
            rules = mw.config_manager.get_config("BatteryConfig/Rules")
            capacity = capacity_from_rules(rules, spec_name)
            # 冷冻型识别：统一入口 is_freezer_context（文件名/规则/required OR 语义，
            # 与 quality_requirements 报告侧、temperature_handler 口径同步）
            is_freezer = is_freezer_context(filename=filename, rules=rules, spec_name=spec_name)
            return lookup_pulse_currents(spec_name, capacity, spec_method, is_freezer)
        except Exception as e:
            self.logger.warning("Failed to lookup pulse currents from table: %s", e)
            return []

    def _verify_pulse_currents(self, filename, pulse_values, table_values) -> None:
        """双重验证：文件名解析的脉冲档位与容量查表档位不一致时告警（BatteryQualityRequirements_v2.3 §7.1.1）

        不一致时仍以文件名解析值为准，仅提示用户核对文件名或规则容量。
        """
        try:
            file_levels = normalize_current_levels(pulse_values)
            std_levels = normalize_current_levels(table_values)
            if file_levels == std_levels:
                return
            msg = _(
                "Pulse currents mismatch: filename {filename} gives {file_levels}, "
                "but capacity table gives {std_levels}. Using filename values."
            ).format(filename=filename, file_levels=file_levels, std_levels=std_levels)
            self.logger.warning(msg)
            if hasattr(self.main_window, "statusBar_BatteryAnalysis"):
                self.main_window.statusBar_BatteryAnalysis.showMessage(f"[Warning]: {msg}")
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.logger.warning("Failed to verify pulse currents: %s", e)

    def _reconnect_specification_signals(self):
        try:
            self.main_window.comboBox_Specification_Type.currentIndexChanged.connect(
                self.main_window.check_specification
            )
            self.main_window.comboBox_Specification_Method.currentIndexChanged.connect(
                self.main_window.check_specification
            )
            self.main_window.check_specification()
        except (TypeError, AttributeError):
            pass

    def _show_spec_method_default_notice(self) -> None:
        """文件名未识别到规格方法、已默认 1S1P 时的确认提示

        仅一个 OK 按钮，居中于主窗口，5 秒未点击自动关闭。
        """
        box = QW.QMessageBox(self.main_window)
        box.setWindowTitle(_("Default Specification Method"))
        box.setText(
            _(
                "The specification method was not found for this battery. "
                "{method} has been selected by default. Please confirm."
            ).format(method=self.SPEC_METHOD_DEFAULT)
        )
        box.setStandardButtons(QW.QMessageBox.StandardButton.Ok)
        box.setDefaultButton(QW.QMessageBox.StandardButton.Ok)

        def _center() -> None:
            if self.main_window is None:
                return
            frame = box.frameGeometry()
            frame.moveCenter(self.main_window.geometry().center())
            box.move(frame.topLeft())

        # QMessageBox 无 aboutToShow 信号（PyQt6 中该信号属于 QMenu）；
        # 在 exec() 前用 adjustSize() 让布局确定尺寸，随后直接居中。
        box.adjustSize()
        _center()
        QC.QTimer.singleShot(self.SPEC_METHOD_NOTICE_TIMEOUT_MS, box.accept)
        box.exec()
