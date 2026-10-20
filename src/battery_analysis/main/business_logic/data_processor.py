"""
数据处理器模块

负责处理数据相关的业务逻辑，包括Excel文件信息获取、数据验证等
"""

import logging
import os
import zipfile

from battery_analysis.i18n.language_manager import _
from battery_analysis.main.business_logic import filename_parser
from battery_analysis.main.business_logic.cache import LRUCache
from battery_analysis.main.ui_components.countdown_message_box import show_countdown_notice
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
    SPEC_METHOD_NOTICE_TIMEOUT_SECONDS = 5
    # 型号未配置时提示的默认秒数（battery.missingRulesNotice.timeoutSeconds 可配）
    MISSING_RULES_NOTICE_DEFAULT_TIMEOUT_SECONDS = 3

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
        self._spec_missing_rules = False

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
        from battery_analysis.utils.file_finder import scan_sorted_ndax

        return [os.path.basename(f) for f in scan_sorted_ndax(input_dir)]

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
            from battery_analysis.ndax.reader import recipe_levels

            try:
                levels = recipe_levels(file_path)
            except (OSError, ValueError, KeyError, zipfile.BadZipFile) as e:
                error_files.append((filename, str(e)))
                continue
            file_info = {"filename": filename, "current_levels": levels}
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
        if self._spec_missing_rules or self._spec_method_defaulted:
            missing_rules = self._spec_missing_rules
            method_defaulted = self._spec_method_defaulted
            self._spec_missing_rules = False
            self._spec_method_defaulted = False
            self._show_spec_notices(missing_rules, method_defaulted, excel_data[0]["filename"])

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

        matched_type = filename_parser.set_specification_type(
            filename, all_spec_types, mw.comboBox_Specification_Type
        )
        # 未匹配到已配置的规格型号（NDAX 转换 / 导入 XML 两条链路均汇合于此）→ 置标志，由统一弹框提示补充配置
        self._spec_missing_rules = matched_type is None
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

        # 配方是唯一的分析档位权威；文件名与配置表仅用于非档位 UI 信息。
        from battery_analysis.ndax.reader import recipe_levels

        mw.listCurrentLevel = recipe_levels(os.path.join(mw.lineEdit_InputPath.text(), filename))

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

    def _show_spec_notices(
        self, missing_rules: bool, method_defaulted: bool, filename: str
    ) -> None:
        """识别结果提示的统一入口（型号未配置 / 规格方法默认）

        两者同时发生时合并为一个弹框（型号未配置提示为主，附带默认方法说明）。
        """
        if missing_rules:
            self._show_missing_rules_notice(filename, method_defaulted)
        elif method_defaulted:
            self._show_spec_method_default_notice()

    def _missing_rules_notice_settings(self) -> tuple[bool, int]:
        """读取 battery.missingRulesNotice 配置（enabled / timeoutSeconds），失败回退默认值"""
        enabled, timeout = True, self.MISSING_RULES_NOTICE_DEFAULT_TIMEOUT_SECONDS
        try:
            cs = self.main_window._get_service("config")
            cfg = cs.get_config_value("battery.missingRulesNotice") if cs else None
            if isinstance(cfg, dict):
                enabled = bool(cfg.get("enabled", True))
                timeout = int(cfg.get("timeoutSeconds", self.MISSING_RULES_NOTICE_DEFAULT_TIMEOUT_SECONDS))
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.logger.warning("Failed to read missingRulesNotice config: %s", e)
        return enabled, timeout

    def _show_missing_rules_notice(
        self, filename: str, method_defaulted: bool = False
    ) -> None:
        """识别到的规格型号不在系统 rules 配置中时的提示

        倒计时自动关闭（默认 3 秒，可在 battery.missingRulesNotice.timeoutSeconds 配置），
        OK 按钮旁显示剩余秒数；"前往配置"按钮跳转到配置对话框的 Battery 页补充规则。
        """
        enabled, timeout_seconds = self._missing_rules_notice_settings()
        if not enabled:
            self.logger.info("missingRulesNotice disabled; skipping for %s", filename)
            return
        text = _(
            "The system has no configuration for the battery model "
            "(file: {filename}). Please add it via Tools → Configuration → Battery → Rules."
        ).format(filename=filename)
        if method_defaulted:
            text += "\n\n" + _(
                "The specification method was not found for this battery. "
                "{method} has been selected by default. Please confirm."
            ).format(method=self.SPEC_METHOD_DEFAULT)
        show_countdown_notice(
            self.main_window,
            title=_("Missing Battery Configuration"),
            text=text,
            timeout_seconds=timeout_seconds,
            extra_button=(_("Go to Configuration"), self._open_config_dialog),
        )

    def _open_config_dialog(self) -> None:
        """跳转到配置对话框（Battery 页可编辑 Rules）"""
        try:
            self.main_window.show_config_dialog()
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.logger.warning("Failed to open configuration dialog: %s", e)

    def _show_spec_method_default_notice(self) -> None:
        """文件名未识别到规格方法、已默认 1S1P 时的确认提示

        仅一个 OK 按钮（旁显剩余秒数），居中于主窗口，5 秒未点击自动关闭。
        """
        show_countdown_notice(
            self.main_window,
            title=_("Default Specification Method"),
            text=_(
                "The specification method was not found for this battery. "
                "{method} has been selected by default. Please confirm."
            ).format(method=self.SPEC_METHOD_DEFAULT),
            timeout_seconds=self.SPEC_METHOD_NOTICE_TIMEOUT_SECONDS,
        )
