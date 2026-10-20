"""
分析运行管理器

负责处理电池分析的运行逻辑，包括：
- 输入验证
- 测试信息准备
- 控制器上下文更新
- 分析启动
"""

# 标准库导入
import csv
import logging
from pathlib import Path

# 第三方库导入
import PyQt6.QtWidgets as QW
from PyQt6 import QtCore as QC

# 本地应用/库导入
from battery_analysis.domain.entities.test_info import TestInfo
from battery_analysis.i18n.language_manager import _
from battery_analysis.main.business_logic.version_manager import delivered_versions, parse_version


class AnalysisRunner:
    """
    分析运行管理器
    负责处理电池分析的运行逻辑
    """

    def __init__(self, main_window=None):
        """
        初始化分析运行管理器

        Args:
            main_window: 主窗口实例（旧接口）
        """
        self.main_window = main_window
        self.logger = logging.getLogger("battery_analysis.analysis_runner")

    def run_analysis(self):
        """
        执行分析运行逻辑
        """
        # 保存表格数据
        self.main_window.table_manager.save_table()
        self.main_window.ui_manager.init_widgetcolor()

        # 检查输入是否完整，包括reportedby
        if not self._check_inputs():
            return

        # Run-before-read recipe validation on the GUI thread; NDA time series stays in worker.
        try:
            files, profile_decision = self._preflight_recipe()
        except (OSError, ValueError, KeyError) as e:
            self.logger.warning("NDAX preflight rejected: %s", e)
            QW.QMessageBox.critical(self.main_window, "NDAX recipe validation", str(e))
            self.main_window.pushButton_Run.setEnabled(True)
            return
        if files is None:
            self.logger.info("NDAX preflight aborted by user: %s", profile_decision)
            self.main_window.pushButton_Run.setEnabled(True)
            return

        # 准备测试信息
        test_info = self._prepare_test_info()
        if not test_info:
            return

        # 更新控制器的上下文和测试信息
        self._update_controller_context(test_info, files, profile_decision)

    def _preflight_recipe(self):
        from battery_analysis.ndax.reader import profile_levels, recipe_levels, recipe_temperature

        input_dir = Path(self.main_window.lineEdit_InputPath.text())
        from battery_analysis.utils.file_finder import scan_sorted_ndax

        files = scan_sorted_ndax(str(input_dir))
        if not files:
            raise ValueError(f"No .ndax files in {input_dir}")
        levels = recipe_levels(files[0])
        temperature = recipe_temperature(files[0])
        for path in files[1:]:
            if recipe_temperature(path) != temperature:
                raise ValueError(f"Different TestInfo.xml recipe temperatures: {Path(files[0]).name}; {Path(path).name}")
            other = recipe_levels(path)
            if other != levels:
                raise ValueError(f"Different Step.xml pulse levels: {Path(files[0]).name}: {levels}; {Path(path).name}: {other}")
        from battery_analysis.main.utils.file_utils import FileUtils

        checksum = FileUtils.calc_checksum([str(path) for path in files])
        if not checksum or checksum != getattr(self.main_window, "sha256_checksum", None):
            raise ValueError("NDAX checksum is not ready or inputs changed; refresh the version before analysis")
        csv_path = Path(self.main_window.lineEdit_OutputPath.text()) / "SHA256.csv"
        with csv_path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.reader(handle))
        checksums = rows[1] if len(rows) > 1 else []
        times = rows[3] if len(rows) > 3 else []
        if checksum not in checksums:
            raise ValueError("Current NDAX checksum is absent from SHA256.csv; refresh the version")
        index = checksums.index(checksum)
        if index >= len(times) or not times[index].isdigit():
            raise ValueError(f"Invalid SHA256.csv success count: {csv_path}")
        expected_version = f"{index + 1}.{times[index]}"
        requested_version = self.main_window.lineEdit_Version.text().strip()
        requested = parse_version(requested_version)
        used = delivered_versions(csv_path.parent)
        highest = max({parse_version(expected_version), *used})
        if requested < highest:
            raise ValueError(f"Version {requested_version} is below the highest version {'.'.join(map(str, highest[:2]))}; choose a version not lower than it")
        if requested in used:
            raise ValueError(f"Version {requested_version} already has a report; choose an unused version")
        self.logger.info("NDAX preflight passed: files=%d levels=%s version=%s", len(files), levels, requested_version)
        self.main_window.listCurrentLevel = levels
        from battery_analysis.main.handlers.temperature_handler import TemperatureType

        self.main_window.temperature_handler.update_temperature_ui(TemperatureType(temperature))
        decision = {"result": "no_profile", "mismatch_type": None, "decision": "continue", "policy_version": "2026.10"}
        profile_path = self.main_window.lineEdit_TestProfile.text().strip()
        if profile_path:
            profile = profile_levels(profile_path)
            mismatch = "count" if len(profile) != len(levels) else "value" if profile != levels else None
            decision.update(result="match" if mismatch is None else "mismatch", mismatch_type=mismatch)
            if mismatch:
                answer = QW.QMessageBox.question(
                    self.main_window, "Profile differs from Step.xml",
                    f"Step.xml: {levels}\nProfile: {profile}\nContinue using Step.xml?",
                    QW.QMessageBox.StandardButton.Yes | QW.QMessageBox.StandardButton.No,
                    QW.QMessageBox.StandardButton.No,
                )
                decision["decision"] = "continue_ndax" if answer == QW.QMessageBox.StandardButton.Yes else "abort"
                if answer != QW.QMessageBox.StandardButton.Yes:
                    return None, decision
        else:
            settings = QC.QSettings()
            if settings.value("validation/profile_disclaimer_version") != "2026.10":
                answer = QW.QMessageBox.question(
                    self.main_window, "No test profile",
                    "No profile was selected. Analysis will use Step.xml recipe levels. Continue?",
                    QW.QMessageBox.StandardButton.Yes | QW.QMessageBox.StandardButton.No,
                    QW.QMessageBox.StandardButton.No,
                )
                if answer != QW.QMessageBox.StandardButton.Yes:
                    return None, decision
                settings.setValue("validation/profile_disclaimer_version", "2026.10")
        return [str(path) for path in files], decision

    def _check_inputs(self):
        """
        检查输入是否完整

        Returns:
            bool: 输入是否完整
        """
        if not self.main_window.checkinput():
            # 检查失败：从验证管理器获取具体失败字段，便于用户定位
            failed_messages = []
            try:
                result = self.main_window.validation_manager.validate_fields()
                if result.field_errors:
                    failed_messages = list(result.field_errors.values())
            except (AttributeError, TypeError, RuntimeError):
                failed_messages = []

            if failed_messages:
                warning_str = "The following fields failed validation:\n- " + "\n- ".join(
                    failed_messages
                )
            else:
                # 兜底：至少指出 Reported By
                warning_info = []
                if not self.main_window.comboBox_ReportedBy.currentText():
                    warning_info.append("Reported By")
                warning_str = (
                    "Please complete the following required fields: " + ", ".join(warning_info)
                    if warning_info
                    else "Please check all required fields"
                )

            QW.QMessageBox.warning(self.main_window, "Input Validation Failed", warning_str)

            self.main_window.pushButton_Run.setEnabled(True)
            return False

        # 简化验证，只验证必要的路径
        if not self.main_window.lineEdit_InputPath.text():
            QW.QMessageBox.critical(
                self.main_window, _("Input Validation Failed"), _("Input data path cannot be empty")
            )
            self.main_window.pushButton_Run.setEnabled(True)
            return False

        if not self.main_window.lineEdit_OutputPath.text():
            QW.QMessageBox.critical(
                self.main_window, _("Input Validation Failed"), _("Output path cannot be empty")
            )
            self.main_window.pushButton_Run.setEnabled(True)
            return False

        # 检查冷冻温度是否设置为0，如果是则提示用户
        temperature_type = self.main_window.comboBox_Temperature.currentText()
        if (
            temperature_type == "Freezer Temperature"
            and self.main_window.spinBox_Temperature.value() == 0
        ):
            reply = QW.QMessageBox.question(
                self.main_window,
                "Temperature Confirmation",
                "The current freezer temperature is set to 0°C. Continue running?",
                QW.QMessageBox.StandardButton.Yes | QW.QMessageBox.StandardButton.No,
                QW.QMessageBox.StandardButton.No,
            )
            if reply == QW.QMessageBox.StandardButton.No:
                self.main_window.pushButton_Run.setEnabled(True)
                return False

        return True

    def _prepare_test_info(self):
        """
        准备测试信息

        Returns:
            TestInfo: 具名的测试信息数据类
        """
        # 使用温度处理器构建温度值字符串
        temperature_value = self.main_window.temperature_handler.get_temperature_value()

        return TestInfo(
            battery_type=self.main_window.comboBox_BatteryType.currentText(),
            construction_method=self.main_window.comboBox_ConstructionMethod.currentText(),
            specification_type=self.main_window.comboBox_Specification_Type.currentText(),
            specification_method=self.main_window.comboBox_Specification_Method.currentText(),
            manufacturer=self.main_window.comboBox_Manufacturer.currentText(),
            batch_date_code=self.main_window.lineEdit_BatchDateCode.text(),
            samples_qty=self.main_window.lineEdit_SamplesQty.text(),
            temperature_value=temperature_value,
            datasheet_nominal_capacity=self.main_window.lineEdit_DatasheetNominalCapacity.text(),
            calculation_nominal_capacity=self.main_window.lineEdit_CalculationNominalCapacity.text(),
            accelerated_aging=str(self.main_window.spinBox_AcceleratedAging.value()),
            tester_location=self.main_window.comboBox_TesterLocation.currentText(),
            tested_by=self.main_window.comboBox_TestedBy.currentText(),
            test_profile=self.main_window.lineEdit_TestProfile.text(),
            current_levels=self.main_window.listCurrentLevel,
            voltage_levels=self.main_window.listVoltageLevel,
            version=self.main_window.lineEdit_Version.text(),
            required_usable_capacity=self.main_window.lineEdit_RequiredUseableCapacity.text(),
            reported_by=self.main_window.comboBox_ReportedBy.currentText(),
        )

    def _update_controller_context(self, test_info, files=None, profile_decision=None):
        """
        更新控制器的上下文和测试信息

        Args:
            test_info: 测试信息列表
        """
        # 更新控制器的上下文和测试信息
        success = False
        main_controller = self.main_window._get_controller("main_controller")
        if main_controller:
            main_controller.set_project_context(
                project_path=self.main_window.path,
                input_path=self.main_window.lineEdit_InputPath.text(),
                output_path=self.main_window.lineEdit_OutputPath.text(),
            )
            main_controller.set_test_info(test_info)
            main_controller.input_files = files
            main_controller.profile_validation = profile_decision

            # 更新配置
            self.main_window.config_manager.update_config(test_info)
            self.main_window.sha256_checksum_run = self.main_window.sha256_checksum
            self.main_window.version_run = test_info.version
            self.main_window.statusBar_BatteryAnalysis.showMessage("status:ok")

            # 启动分析
            success = main_controller.start_analysis()

        if not success:
            # 如果分析已在运行，不显示错误（可能是重复点击）
            if main_controller and main_controller.is_analysis_running:
                self.logger.info("Analysis already running, ignoring duplicate start request")
            else:
                self.main_window.pushButton_Run.setEnabled(True)
                QW.QMessageBox.warning(
                    self.main_window, _("Start Failed"), _("Cannot start the analysis task")
                )
