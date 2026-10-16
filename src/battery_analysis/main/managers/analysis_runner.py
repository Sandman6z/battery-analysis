"""
分析运行管理器

负责处理电池分析的运行逻辑，包括：
- 输入验证
- 测试信息准备
- 控制器上下文更新
- 分析启动
"""

# 标准库导入
import logging
import os

# 第三方库导入
import PyQt6.QtWidgets as QW

from battery_analysis.domain.entities.test_info import TestInfo

# 本地应用/库导入
from battery_analysis.i18n.language_manager import _
from battery_analysis.utils.ndax_meta import read_sidecar
from battery_analysis.utils.profile_validation import (
    DECISION_BLOCK,
    DECISION_OFFER_OVERRIDE,
    DECISION_PROCEED,
    check_batch_consistency,
    decide_profile_validation,
    extract_profile_levels,
)


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
        self.logger = logging.getLogger(__name__)

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

        # profile 与 ndax 档位校验闸门（会议裁决①③④）
        if not self._run_profile_validation():
            return

        # 准备测试信息
        test_info = self._prepare_test_info()
        if not test_info:
            return

        # 更新控制器的上下文和测试信息
        self._update_controller_context(test_info)

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

    def _run_profile_validation(self):
        """profile 与 ndax 档位校验闸门（会议裁决①③④）。

        扫描输入目录 xlsx 的 sidecar，先做批内一致性（裁决③，硬阻断），
        再与 profile 声明档位走决策树。放行时留痕记录存
        main_window.profile_validation，后续随分析写入
        Info_Plot.json.profile_validation（裁决⑤）。

        Returns:
            bool: True 放行；False 阻断（已弹框并恢复 Run 按钮）。
        """
        mw = self.main_window
        # 每次运行重置，防止上次放行记录泄漏进本次
        mw.profile_validation = None

        input_dir = mw.lineEdit_InputPath.text()
        if not input_dir or not os.path.isdir(str(input_dir)):
            return True

        # 收集全批次 sidecar 档位
        sidecars: list[dict] = []
        levels_by_file: dict[str, list[float]] = {}
        try:
            names = sorted(os.listdir(input_dir))
        except OSError:
            return True
        for name in names:
            if not name.lower().endswith(".xlsx") or name.startswith("~$"):
                continue
            meta = read_sidecar(os.path.join(input_dir, name))
            if meta and meta.get("pulse_currents"):
                levels_by_file[name] = meta["pulse_currents"]
                sidecars.append(meta)

        # 裁决③：批内多 ndax 档位不一致 → 硬阻断，无放行选项
        batch_record = check_batch_consistency(levels_by_file)
        if batch_record is not None:
            self._show_validation_block(
                _("ndax data inconsistent"),
                _(
                    "Pulse current levels differ between ndax files in this batch. "
                    "Please check the test data."
                ),
            )
            return False

        if not sidecars:
            # 旧链路（无 sidecar）：不校验，维持文件名解析行为
            return True

        # profile 侧：无 profile / 解析不出脉冲 → 放行
        # （无 profile 的声明弹框属后续 "profile 验证接线" 步）
        profile_path = mw.lineEdit_TestProfile.text()
        if not profile_path:
            return True
        profile_levels = extract_profile_levels(profile_path)
        if not profile_levels:
            return True

        first = sidecars[0]
        record = decide_profile_validation(
            profile_levels,
            first.get("pulse_currents"),
            first.get("observed_pulse_currents"),
            first.get("observed_pulse_medians"),
        )
        decision = record.get("decision")

        # 裁决②：实测层漂移超阈值 → 黄警放行（阻断/弹窗路径另有交互）
        if record.get("measured_drift") and decision == DECISION_PROCEED:
            drift_str = ", ".join(
                f"{level} mA (+/-{deviation:.3f})"
                for level, deviation in record["measured_drift"].items()
            )
            QW.QMessageBox.warning(
                self.main_window,
                _("Measured Current Drift"),
                _(
                    "Measured pulse current medians exceed the tolerance "
                    "(max 1%%, 0.5mA): %s. The analysis will continue."
                )
                % drift_str,
            )

        if decision == DECISION_BLOCK:
            if record.get("mismatch_type") == "level_count_mismatch_truncated":
                title = _("Test may be incomplete")
                body = _(
                    "Some pulse current levels declared in the profile were not "
                    "executed in the test data. The test may not have finished. "
                    "Please check the test data."
                )
            else:  # level_count_missing_evidence
                title = _("Missing completion evidence")
                body = _(
                    "No completion evidence for the declared pulse levels "
                    "(sidecar has no observed levels). Please re-convert the "
                    "ndax files."
                )
            self._show_validation_block(title, body)
            return False

        if decision == DECISION_OFFER_OVERRIDE:
            if not self._ask_override(profile_levels, first.get("pulse_currents"), record):
                return False  # 用户选中止：不写留痕，不启动分析
            record["decision"] = "override_accepted"

        # match / 无档值差异 / 放行：留痕
        mw.profile_validation = record
        self.logger.info("Profile validation: %s", record)
        return True

    def _show_validation_block(self, title, body):
        """硬阻断弹框（无放行按钮），并恢复 Run 按钮可点击。"""
        QW.QMessageBox.critical(self.main_window, title, body)
        self.main_window.pushButton_Run.setEnabled(True)

    def _ask_override(self, profile_levels, ndax_levels, record) -> bool:
        """裁决① 两按钮弹窗：[中止]（默认焦点）+[以 ndax 档位为准继续]。

        Returns:
            bool: 用户点继续 → True；中止/Esc → False。
        """
        box = QW.QMessageBox(self.main_window)
        box.setIcon(QW.QMessageBox.Icon.Warning)
        box.setWindowTitle(_("Profile Mismatch"))

        profile_text = ", ".join(str(x) for x in profile_levels)
        ndax_text = ", ".join(str(x) for x in (ndax_levels or []))
        if record.get("result") == "value_mismatch":
            summary = _("Pulse current levels do not match the profile.")
        else:
            summary = _("The number of pulse current levels does not match the profile.")
        box.setText(summary)
        box.setInformativeText(_("Continue the analysis with the ndax levels?"))
        details = "Profile: [%s] mA\nndax:   [%s] mA" % (profile_text, ndax_text)
        if record.get("measured_drift"):
            drift_text = ", ".join(
                "%s (+/-%.3f)" % (level, deviation)
                for level, deviation in record["measured_drift"].items()
            )
            details += "\nMeasured drift: %s mA" % drift_text
        box.setDetailedText(details)

        # Qt6 ButtonRole 无 DefaultRole：中止用 RejectRole，
        # 默认焦点由 setDefaultButton 控制
        btn_abort = box.addButton(_("Abort"), QW.QMessageBox.ButtonRole.RejectRole)
        box.addButton(_("Continue with ndax levels"), QW.QMessageBox.ButtonRole.AcceptRole)
        box.setDefaultButton(btn_abort)
        box.exec()
        return box.clickedButton() is not None and box.clickedButton() is not btn_abort

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

    def _update_controller_context(self, test_info):
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
            main_controller.profile_validation = getattr(
                self.main_window, "profile_validation", None
            )

            # 更新配置
            self.main_window.config_manager.update_config(test_info)
            self.main_window.sha256_checksum_run = self.main_window.sha256_checksum
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
