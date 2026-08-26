# -*- coding: utf-8 -*-
"""
电池分析工作线程模块（AnalysisWorker 继承 TaskRunner，信号并入 TaskSignals）
"""
import os
import shutil
import logging
from battery_analysis.main.workers.task_runner import TaskRunner, TaskCancelled


class AnalysisWorker(TaskRunner):
    """
    电池分析工作线程类，继承自 TaskRunner
    负责执行后台分析任务
    """

    def __init__(self):
        """
        初始化工作线程
        """
        super().__init__(self._run_placeholder)
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
            if os.path.exists(version_dir):
                shutil.rmtree(version_dir)
            if self.b_cancel_requested:
                return

            os.mkdir(version_dir)
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
                progress_callback=lambda v, s: self._emit_progress(v, s)
            )

            # BatteryAnalysis.__init__ 内部已报告进度至约55%，继续后续步骤
            self._emit_progress(self.progress_value, "Processing battery information...")

            self.str_error_battery = info_battery.UBA_GetErrorLog()
            if self.str_error_battery == "":
                list_battery_info = info_battery.UBA_GetBatteryInfo()

                if self.b_cancel_requested:
                    return

                # 获取Test Date和原始周期日期进行验证
                # 从修改后的UBA_GetBatteryInfo返回值中获取Test Date
                test_date = list_battery_info[3]
                # 从修改后的UBA_GetBatteryInfo返回值中获取原始周期日期
                original_cycle_date = list_battery_info[4]

                logging.info(
                    "Retrieved Test Date: %s, original cycle date: %s", test_date, original_cycle_date)

                from battery_analysis.utils.readers.date_parser import parse_test_date

                fallback = (
                    list_battery_info[2][0]
                    if len(list_battery_info) > 2 and list_battery_info[2]
                    else ""
                )
                self.str_test_date = parse_test_date(
                    test_date, original_cycle_date, fallback
                )
                logging.info("Final test date determined: %s", self.str_test_date)

                self._emit_progress(self.progress_value, "Processing output directory...")

                # 重命名目录
                try:
                    final_dir = f"{self.str_output_path}/" \
                        f"{self.str_test_date}_v{self.list_test_info[16]}"
                    if os.path.exists(final_dir):
                        shutil.rmtree(final_dir)

                    # 发送重命名路径信号
                    try:
                        self.signals.rename_path.emit(self.str_test_date)
                    except RuntimeError:
                        logging.warning("Signal object already deleted, cannot emit rename path signal")

                    os.rename(version_dir, final_dir)
                except (OSError, PermissionError, FileNotFoundError) as e:
                    logging.error("Failed to rename directory: %s", e)
                    # 重命名失败时，使用默认目录名继续执行
                    final_dir = version_dir

                self._emit_progress(self.progress_value, "Preparing to generate report...")

                self._emit_progress(60, "Initializing report generation module...")

                # 文件写入
                try:
                    from battery_analysis.utils import file_writer
                    from battery_analysis.main.services.service_container import get_service_container

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

                        self._emit_progress(95, "Cleaning up temporary files...")

                        self._emit_progress(100, "Analysis complete!")

                    # 优化ImageMaker启动逻辑：仅查找与 analyzer 同版本的 visualizer
                    try:
                        self._start_visualizer()
                    except (ImportError, OSError, PermissionError, ValueError) as e:
                        logging.error("Failed to start visualizer: %s", e)
                except (ImportError, OSError, PermissionError, IOError, ValueError) as e:
                    logging.error("An error occurred during file writing: %s", e)
                    self.str_error_xlsx = f"File writing error: {str(e)}"

        except TaskCancelled:
            return
        except Exception as e:
            # 捕获所有异常，包括自定义的 BatteryAnalysisException
            logging.error("An error occurred during thread execution: %s", e)
            # 将未捕获的异常信息传递给UI层
            self.str_error_xlsx = f"Thread execution error: {str(e)}"
        finally:
            self.b_thread_run = False
            # 发送完成状态（取消的任务发 cancelled 信号，其他正常上报）
            try:
                if self.b_cancel_requested or self._cancelled:
                    self.signals.info.emit(False, 0, "status:cancelled")
                elif self.str_error_battery != "":
                    self.signals.info.emit(False, 1, self.str_error_battery)
                elif self.str_error_xlsx != "":
                    self.signals.info.emit(False, 2, self.str_error_xlsx)
                else:
                    self.signals.info.emit(False, 0, "status:success")
                    self.signals.thread_end.emit()
            except RuntimeError as e:
                logging.warning("Signal object already deleted, cannot emit completion status: %s", e)

    def _start_visualizer(self):
        """
        启动可视化工具的内部方法
        发送信号通知主线程启动可视化工具，确保环境一致
        """
        try:
            if hasattr(self, 'signals'):
                self.signals.start_visualizer.emit()
        except RuntimeError as e:
            logging.warning("Signal object already deleted, cannot emit start visualizer signal: %s", e)
