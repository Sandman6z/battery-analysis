# -*- coding: utf-8 -*-
"""
电池分析工作线程模块
"""
import os
import sys
import re
import shutil
import subprocess
import logging
from PyQt6 import QtCore as QC


class _TaskCancelled(Exception):
    """检测到取消请求时抛出，优雅退出 run()，避免逐行 if-return"""
    pass


class AnalysisWorker(QC.QRunnable):
    """
    电池分析工作线程类，继承自QRunnable
    负责执行后台分析任务
    """
    # 定义信号
    class Signals(QC.QObject):
        """
        信号定义类
        """
        info = QC.pyqtSignal(bool, int, str)
        thread_end = QC.pyqtSignal()
        rename_path = QC.pyqtSignal(str)
        progress_update = QC.pyqtSignal(int, str)  # 进度更新信号：进度值(0-100)，状态文本
        start_visualizer = QC.pyqtSignal()  # 通知主线程启动可视化工具的信号

    def __init__(self):
        """
        初始化工作线程
        """
        super().__init__()
        self.signals = self.Signals()
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

    def request_cancel(self):
        """
        请求取消任务
        """
        self.b_cancel_requested = True
        self.signals.progress_update.emit(self.progress_value, "正在取消任务...")

    def set_info(self, str_path, str_input_path, str_output_path, list_test_info):
        """
        设置分析所需的信息

        Args:
            str_path: 项目路径
            str_input_path: 输入数据路径
            str_output_path: 输出结果路径
            list_test_info: 测试信息列表
        """
        self.str_path = str_path
        self.str_input_path = str_input_path
        self.str_output_path = str_output_path
        self.list_test_info = list_test_info

    def _emit_progress(self, value, status):
        """
        更新进度值并检查取消请求

        将「设置进度→发射信号→检查取消」三步合并为一行，
        检测到取消时抛出 _TaskCancelled，由 run() 顶层的 except 统一捕获退出。
        每个进度点只需一行 self._emit_progress(...)，无需逐行 if-return。
        """
        self.progress_value = value
        try:
            self.signals.progress_update.emit(value, status)
        except RuntimeError:
            raise _TaskCancelled from None
        if self.b_cancel_requested:
            raise _TaskCancelled

    def _emit_info_safe(self, is_running, state_index, message):
        """安全发射 info 信号，忽略信号对象已删除的异常"""
        try:
            self.signals.info.emit(is_running, state_index, message)
        except RuntimeError:
            pass

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
            logging.warning("发送初始运行状态失败: %s", str(e))

        try:
            self._emit_progress(0, "准备分析...")

            # 确保输出根目录存在（3_analysis results）
            os.makedirs(self.str_output_path, exist_ok=True)

            # 检查并创建版本目录
            version_dir = f"{self.str_output_path}/v{self.list_test_info[16]}"
            if os.path.exists(version_dir):
                shutil.rmtree(version_dir)
            if self.b_cancel_requested:
                return

            os.mkdir(version_dir)
            self._emit_progress(3, "正在初始化分析环境...")

            # 电池分析
            # 延迟导入以避免循环引用
            from battery_analysis.utils.processors import battery_analysis

            self._emit_progress(5, "正在加载电池分析模块...")

            self._emit_progress(8, "正在初始化电池分析引擎...")

            info_battery = battery_analysis.BatteryAnalysis(
                strInDataXlsxDir=self.str_input_path,
                strResultPath=self.str_output_path,
                listTestInfo=self.list_test_info,
                progress_callback=lambda v, s: self._emit_progress(v, s)
            )

            # BatteryAnalysis.__init__ 内部已报告进度至约55%，继续后续步骤
            self._emit_progress(self.progress_value, "正在处理电池信息...")

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
                    "获取到的Test Date: %s, 原始周期日期: %s", test_date, original_cycle_date)

                from battery_analysis.utils.readers.date_parser import parse_test_date

                fallback = (
                    list_battery_info[2][0]
                    if len(list_battery_info) > 2 and list_battery_info[2]
                    else ""
                )
                self.str_test_date = parse_test_date(
                    test_date, original_cycle_date, fallback
                )
                logging.info("最终确定的测试日期: %s", self.str_test_date)

                self._emit_progress(self.progress_value, "正在处理输出目录...")

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
                        logging.warning("信号对象已被删除，无法发送重命名路径信号")

                    os.rename(version_dir, final_dir)
                except (OSError, PermissionError, FileNotFoundError) as e:
                    logging.error("目录重命名失败: %s", e)
                    # 重命名失败时，使用默认目录名继续执行
                    final_dir = version_dir

                self._emit_progress(self.progress_value, "正在准备生成报告...")

                self._emit_progress(60, "正在初始化报告生成模块...")

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
                    except Exception:
                        pass

                    info_file = file_writer.FileWriter(
                        strResultPath=self.str_output_path,
                        listTestInfo=self.list_test_info,
                        listBatteryInfo=list_battery_info,
                        equipment_info=_equipment,
                    )

                    self._emit_progress(63, "正在整理分析数据...")

                    self._emit_progress(65, "正在写入分析结果...")

                    self._emit_progress(70, "正在生成图表...")

                    self._emit_progress(74, "正在优化图表布局...")

                    self._emit_progress(78, "正在验证分析结果数据...")

                    self._emit_progress(82, "正在封装最终数据包...")

                    self.str_error_xlsx = info_file.UFW_GetErrorLog()
                    if self.str_error_xlsx != "":
                        logging.error(self.str_error_xlsx)
                    else:
                        self._emit_progress(85, "正在完成最终处理...")

                        self._emit_progress(90, "正在验证输出结果...")

                        self._emit_progress(95, "正在清理临时文件...")

                        self._emit_progress(100, "分析完成！")

                    # 优化ImageMaker启动逻辑：仅查找与 analyzer 同版本的 visualizer
                    try:
                        self._start_visualizer()
                    except (ImportError, OSError, PermissionError, ValueError) as e:
                        logging.error("启动可视化工具失败: %s", e)
                except (ImportError, OSError, PermissionError, IOError, ValueError) as e:
                    logging.error("文件写入过程中发生错误: %s", e)
                    self.str_error_xlsx = f"文件写入错误: {str(e)}"

        except _TaskCancelled:
            return
        except Exception as e:
            # 捕获所有异常，包括自定义的 BatteryAnalysisException
            logging.error("线程运行过程中发生错误: %s", e)
            # 将未捕获的异常信息传递给UI层
            self.str_error_xlsx = f"线程运行错误: {str(e)}"
        finally:
            self.b_thread_run = False
            # 发送完成状态（取消的任务发 cancelled 信号，其他正常上报）
            try:
                if self.b_cancel_requested:
                    self.signals.info.emit(False, 0, "status:cancelled")
                elif self.str_error_battery != "":
                    self.signals.info.emit(False, 1, self.str_error_battery)
                elif self.str_error_xlsx != "":
                    self.signals.info.emit(False, 2, self.str_error_xlsx)
                else:
                    self.signals.info.emit(False, 0, "status:success")
                    self.signals.thread_end.emit()
            except RuntimeError as e:
                logging.warning("信号对象已被删除，无法发送完成状态: %s", e)

    def _start_visualizer(self):
        """
        启动可视化工具的内部方法
        发送信号通知主线程启动可视化工具，确保环境一致
        """
        try:
            if hasattr(self, 'signals'):
                self.signals.start_visualizer.emit()
        except RuntimeError as e:
            logging.warning("信号对象已被删除，无法发送启动可视化工具信号: %s", e)
        except RuntimeError as e:
            logging.error("发送启动可视化工具信号时发生错误: %s", e)
