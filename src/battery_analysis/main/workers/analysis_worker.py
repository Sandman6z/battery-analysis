"""
电池分析工作线程模块（AnalysisWorker 继承 TaskRunner，信号并入 TaskSignals）
"""

import logging
import os
import shutil
import threading

from battery_analysis.main.workers.task_runner import TaskCancelled, TaskRunner


class AnalysisWorker(TaskRunner):
    """
    电池分析工作线程类，继承自 TaskRunner
    负责执行后台分析任务
    """

    def __init__(self, signals=None):
        """
        初始化工作线程

        Args:
            signals: 可选的 TaskSignals 实例，由调用方（QObject controller）持有
                     生命周期；不传则内部创建（无 parent，依赖引用链）。
        """
        super().__init__(self._run_placeholder, signals=signals)
        self.str_path = ""
        self.str_input_path = ""
        self.str_output_path = ""
        self.list_test_info = []
        self.b_thread_run = False
        self.b_cancel_requested = False  # 取消标志
        self.progress_value = 0  # 当前进度值
        self.str_error_battery = ""
        self.str_error_xlsx = ""
        self.str_test_date = ""
        self.profile_validation = {}
        self._decision_event = threading.Event()
        self._decision = False

    def confirm_anomalies(self, allowed):
        self._decision = allowed
        self._decision_event.set()

    def _ask_anomalies(self, anomalies):
        self._decision_event.clear()
        self._decision = False
        self.signals.anomalies_request.emit(anomalies)
        while not self._decision_event.wait(0.1):
            if self.b_cancel_requested or self._cancelled:
                return False
        return self._decision and not (self.b_cancel_requested or self._cancelled)

    def _run_placeholder(self):
        """占位 task_func：run() 被重写，不使用 task_func 机制。"""
        return None

    def request_cancel(self):
        """
        请求取消任务（协作式：下次进度检查点生效）
        """
        self.b_cancel_requested = True
        self.cancel()  # TaskRunner.cancel()：设 _cancelled + 发 cancelled 信号
        self.signals.progress.emit(self.progress_value, "Canceling task...")

    def set_info(self, str_path, str_input_path, str_output_path, test_info):
        """
        设置分析所需的信息

        Args:
            str_path: 项目路径
            str_input_path: 输入数据路径
            str_output_path: 输出结果路径
            test_info: TestInfo 实例（或向后兼容的 list）
        """
        self.str_path = str_path
        self.str_input_path = str_input_path
        self.str_output_path = str_output_path
        self.list_test_info = test_info

    def _emit_progress(self, value, status):
        """
        更新进度值并检查取消请求

        将「设置进度→发射信号→检查取消」三步合并为一行，
        检测到取消时抛出 TaskCancelled，由 run() 顶层的 except 统一捕获退出。
        每个进度点只需一行 self._emit_progress(...)，无需逐行 if-return。
        """
        self.progress_value = value
        try:
            self.signals.progress.emit(value, status)
        except RuntimeError:
            raise TaskCancelled from None
        if self.b_cancel_requested or self._cancelled:
            raise TaskCancelled

    def run(self):
        """
        执行分析任务的主方法
        """
        self.b_thread_run = True
        self.b_cancel_requested = False
        self.progress_value = 0
        self.str_error_battery = ""
        self.str_error_xlsx = ""
        owned_dir = None
        owned_docx = None
        succeeded = False

        # 发送初始运行状态
        try:
            status_text = "status:run"
            self.signals.info.emit(True, 0, status_text)
            self.signals.info.emit(True, 1, status_text)
            self.signals.info.emit(True, 2, status_text)
            self.signals.info.emit(True, 3, status_text)
        except RuntimeError as e:
            logging.warning("Failed to send initial running status: %s", str(e))

        try:
            self._emit_progress(0, "Preparing analysis...")

            # 后向兼容：若传入 TestInfo，转为 list 供旧版引擎使用
            from battery_analysis.domain.entities.test_info import TestInfo

            if isinstance(self.list_test_info, TestInfo):
                self.list_test_info = self.list_test_info.to_list()

            # 确保输出根目录存在（3_analysis results）
            os.makedirs(self.str_output_path, exist_ok=True)

            # 检查并创建版本目录
            version_dir = f"{self.str_output_path}/v{self.list_test_info[16]}"
            if self.b_cancel_requested or self._cancelled:
                raise TaskCancelled
            # mkdir is exclusive: never remove a pre-existing report or crash remnant.
            os.mkdir(version_dir)
            owned_dir = version_dir
            self._emit_progress(3, "Initializing analysis environment...")

            # 电池分析
            # 延迟导入以避免循环引用
            from battery_analysis.utils.processors import battery_analysis

            self._emit_progress(5, "Loading battery analysis module...")

            self._emit_progress(8, "Initializing battery analysis engine...")

            info_battery = battery_analysis.BatteryAnalysis(
                strInDataXlsxDir=self.str_input_path,
                strResultPath=self.str_output_path,
                listTestInfo=self.list_test_info,
                progress_callback=lambda v, s: self._emit_progress(v, s),
                decision_callback=self._ask_anomalies,
                profile_validation=self.profile_validation,
                input_files=getattr(self, "input_files", None),
            )

            # BatteryAnalysis.__init__ 内部已报告进度至约55%，继续后续步骤
            self._emit_progress(self.progress_value, "Processing battery information...")

            self.str_error_battery = info_battery.UBA_GetErrorLog()
            if self.str_error_battery == "":
                list_battery_info = info_battery.UBA_GetBatteryInfo()

                if self.b_cancel_requested or self._cancelled:
                    raise TaskCancelled

                # 获取Test Date和原始周期日期进行验证
                # 从修改后的UBA_GetBatteryInfo返回值中获取Test Date
                test_date = list_battery_info[3]
                # 从修改后的UBA_GetBatteryInfo返回值中获取原始周期日期
                original_cycle_date = list_battery_info[4]

                logging.info(
                    "Retrieved Test Date: %s, original cycle date: %s",
                    test_date,
                    original_cycle_date,
                )

                from datetime import datetime

                # Only measured sampling time may name a delivered report.
                timestamp = list_battery_info[2][0] if list_battery_info[2] else ""
                self.str_test_date = datetime.fromisoformat(str(timestamp)).strftime("%Y%m%d")
                list_battery_info[3] = self.str_test_date
                logging.info("Final test date determined: %s", self.str_test_date)

                self._emit_progress(self.progress_value, "Processing output directory...")

                # 重命名目录
                try:
                    final_dir = (
                        f"{self.str_output_path}/{self.str_test_date}_v{self.list_test_info[16]}"
                    )
                    report_name = (
                        f"{self.list_test_info[4]}_{self.list_test_info[2]}"
                        f"_DC{self.list_test_info[5]}_TD{self.str_test_date}"
                        f"_v{self.list_test_info[16]}.docx"
                    )
                    docx_path = os.path.join(self.str_output_path, report_name)
                    if os.path.exists(final_dir) or os.path.exists(docx_path):
                        raise FileExistsError(f"Report already exists: {final_dir if os.path.exists(final_dir) else docx_path}")
                    # Word writes outside the report directory; reserve it exclusively too.
                    with open(docx_path, "x"):
                        pass
                    owned_docx = docx_path
                    os.rename(version_dir, final_dir)
                    owned_dir = final_dir
                except (OSError, PermissionError, FileNotFoundError):
                    raise

                self._emit_progress(self.progress_value, "Preparing to generate report...")

                self._emit_progress(60, "Initializing report generation module...")

                # 文件写入
                try:
                    from battery_analysis.main.services.service_container import (
                        get_service_container,
                    )
                    from battery_analysis.utils import file_writer

                    _equipment = {}
                    try:
                        _container = get_service_container()
                        _config = _container.get("config")
                        if _config:
                            _eq = _config.get_config_value("test.equipment", {})
                            if _eq:
                                _equipment = next(iter(_eq.values()))
                    except (KeyError, TypeError, AttributeError, StopIteration):
                        pass

                    info_file = file_writer.FileWriter(
                        strResultPath=self.str_output_path,
                        listTestInfo=self.list_test_info,
                        listBatteryInfo=list_battery_info,
                        equipment_info=_equipment,
                        result_dir=final_dir,
                        test_date=self.str_test_date,
                    )

                    self._emit_progress(63, "Organizing analysis data...")

                    self._emit_progress(65, "Writing analysis results...")

                    self._emit_progress(70, "Generating charts...")

                    self._emit_progress(74, "Optimizing chart layout...")

                    self._emit_progress(78, "Validating analysis result data...")

                    self._emit_progress(82, "Packaging final data...")

                    self.str_error_xlsx = info_file.UFW_GetErrorLog()
                    if self.str_error_xlsx != "":
                        logging.error(self.str_error_xlsx)
                    else:
                        self._emit_progress(85, "Completing final processing...")

                        self._emit_progress(90, "Validating output results...")

                        self._emit_progress(95, "Validating generated reports...")
                        from pathlib import Path

                        delivered = [p for p in Path(final_dir).iterdir() if p.is_file() and p.stat().st_size]
                        for suffix in (".xlsx", ".csv", ".json", ".png", ".svg"):
                            if not any(p.suffix == suffix for p in delivered):
                                raise RuntimeError(f"Missing report output {suffix} in {final_dir}")
                        for name in ("Info_Image.csv", "Info_Plot.json"):
                            if not any(p.name == name for p in delivered):
                                raise RuntimeError(f"Missing report output {name} in {final_dir}")
                        if sum(p.suffix == ".xlsx" for p in delivered) < 2:
                            raise RuntimeError(f"Result and Sample Excel reports are required in {final_dir}")
                        for image in ("Image_FilteredLoadVoltageOverCharge", "Image_UnfilteredLoadVoltageOverCharge"):
                            for ext in (".png", ".svg"):
                                if not any(p.name == image + ext for p in delivered):
                                    raise RuntimeError(f"Missing image: {image + ext}")
                        if not os.path.getsize(owned_docx):
                            raise RuntimeError(f"Word report was not generated: {owned_docx}")
                        self._emit_progress(100, "Analysis complete!")
                        succeeded = True

                    # 优化ImageMaker启动逻辑：仅查找与 analyzer 同版本的 visualizer
                    try:
                        self._start_visualizer()
                    except (ImportError, OSError, PermissionError, ValueError) as e:
                        logging.error("Failed to start visualizer: %s", e)
                except (ImportError, OSError, PermissionError, ValueError) as e:
                    logging.error("An error occurred during file writing: %s", e)
                    self.str_error_xlsx = f"File writing error: {e!s}"

        except TaskCancelled:
            return
        except Exception as e:
            # 捕获所有异常，包括自定义的 BatteryAnalysisException
            logging.error("An error occurred during thread execution: %s", e)
            # 将未捕获的异常信息传递给UI层
            self.str_error_xlsx = f"Thread execution error: {e!s}"
        finally:
            succeeded = succeeded and not (self.b_cancel_requested or self._cancelled)
            if not succeeded:
                if owned_docx:
                    try:
                        os.remove(owned_docx)
                    except OSError as e:
                        logging.error("Could not remove this run's Word file %s: %s", owned_docx, e)
                if owned_dir:
                    try:
                        shutil.rmtree(owned_dir)
                    except OSError as e:
                        logging.error("Could not remove this run's directory %s: %s", owned_dir, e)
            self.b_thread_run = False
            # 发送完成状态（取消的任务发 cancelled 信号，其他正常上报）
            try:
                if self.b_cancel_requested or self._cancelled:
                    self.signals.info.emit(False, 0, "status:cancelled")
                elif self.str_error_battery != "":
                    self.signals.info.emit(False, 1, self.str_error_battery)
                elif self.str_error_xlsx != "":
                    self.signals.info.emit(False, 2, self.str_error_xlsx)
                elif succeeded:
                    self.signals.info.emit(False, 0, "status:success")
                    self.signals.rename_path.emit(self.str_test_date)
                    self.signals.analysis_succeeded.emit()
                else:
                    self.signals.info.emit(False, 2, "Analysis did not produce all reports")
            except RuntimeError as e:
                logging.warning(
                    "Signal object already deleted, cannot emit completion status: %s", e
                )
            # thread_end 必须无条件发射：_on_analysis_completed 依赖它来重置
            # is_analysis_running，否则 UI 永远卡在 "Running" 状态
            try:
                self.signals.thread_end.emit()
            except RuntimeError:
                pass

    def _start_visualizer(self):
        """
        启动可视化工具的内部方法
        发送信号通知主线程启动可视化工具，确保环境一致
        """
        try:
            if hasattr(self, "signals"):
                self.signals.start_visualizer.emit()
        except RuntimeError as e:
            logging.warning(
                "Signal object already deleted, cannot emit start visualizer signal: %s", e
            )
