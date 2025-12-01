# -*- coding: utf-8 -*-
"""
电池分析工作线程模块
"""
import os
import sys
import re
import time
import shutil
import threading
import subprocess
import logging
from PyQt6 import QtCore as QC


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
    
    def run(self):
        """
        执行分析任务的主方法
        """
        self.b_thread_run = True
        self.b_cancel_requested = False
        self.progress_value = 0
        
        # 启动状态信号线程
        status_thread = threading.Thread(target=self._signal_running, daemon=True)
        status_thread.start()
        
        try:
            # 发送初始进度
            self.signals.progress_update.emit(0, "准备分析...")
            
            # 检查并创建目录
            version_dir = f"{self.str_output_path}/V{self.list_test_info[16]}"
            if os.path.exists(version_dir):
                shutil.rmtree(version_dir)
            if self.b_cancel_requested:
                return
            
            os.mkdir(version_dir)
            self.progress_value = 10
            self.signals.progress_update.emit(self.progress_value, "初始化分析...")
            
            # 电池分析
            # 延迟导入以避免循环引用
            from src.battery_analysis.utils import battery_analysis
            
            info_battery = battery_analysis.BatteryAnalysis(
                strInDataXlsxDir=self.str_input_path,
                strResultPath=self.str_output_path,
                listTestInfo=self.list_test_info
            )
            
            self.progress_value = 20
            self.signals.progress_update.emit(self.progress_value, "进行电池分析...")
            if self.b_cancel_requested:
                return
            
            self.str_error_battery = info_battery.UBA_GetErrorLog()
            if self.str_error_battery == "":
                self.progress_value = 40
                self.signals.progress_update.emit(self.progress_value, "获取电池信息...")
                list_battery_info = info_battery.UBA_GetBatteryInfo()
                
                if self.b_cancel_requested:
                    return
                
                try:
                    [sy, sm, sd] = list_battery_info[2][0].split(" ")[0].split("-")
                    self.str_test_date = f"{sy}{sm}{sd}"
                except ValueError:
                    self.str_test_date = "00000000"
                except Exception as e:
                    logging.error(f"解析测试日期失败: {e}")
                    self.str_test_date = "00000000"
                
                # 重命名目录
                final_dir = f"{self.str_output_path}/{self.str_test_date}_V{self.list_test_info[16]}"
                if os.path.exists(final_dir):
                    shutil.rmtree(final_dir)
                
                self.signals.rename_path.emit(self.str_test_date)
                os.rename(version_dir, final_dir)
                
                self.progress_value = 60
                self.signals.progress_update.emit(self.progress_value, "准备生成报告...")
                if self.b_cancel_requested:
                    return
                
                # 文件写入
                from src.battery_analysis.utils import file_writer
                
                info_file = file_writer.FileWriter(
                    strResultPath=self.str_output_path,
                    listTestInfo=self.list_test_info,
                    listBatteryInfo=list_battery_info
                )
                
                self.progress_value = 80
                self.signals.progress_update.emit(self.progress_value, "生成报告中...")
                if self.b_cancel_requested:
                    return
                
                self.str_error_xlsx = info_file.UFW_GetErrorLog()
                if self.str_error_xlsx != "":
                    logging.error(self.str_error_xlsx)
                else:
                    self.progress_value = 100
                    self.signals.progress_update.emit(self.progress_value, "分析完成！")
                    
                # 优化ImageMaker启动逻辑：仅查找与 analyzer 同版本的 visualizer
                self._start_visualizer()
                
        except Exception as e:
            logging.error(f"线程运行过程中发生错误: {e}")
        finally:
            self.b_thread_run = False
            # 等待状态线程结束，设置超时避免死锁
            try:
                status_thread.join(timeout=1.0)
            except Exception as e:
                logging.error(f"等待状态线程结束时出错: {e}")
    
    def _signal_running(self):
        """
        发送运行状态信号的内部方法
        """
        try:
            while self.b_thread_run:
                status_text = "status:run"
                if self.b_cancel_requested:
                    status_text = "status:canceling"
                
                try:
                    self.signals.info.emit(True, 0, status_text)
                    time.sleep(0.4)
                    self.signals.info.emit(True, 1, status_text)
                    time.sleep(0.4)
                    self.signals.info.emit(True, 2, status_text)
                    time.sleep(0.4)
                    self.signals.info.emit(True, 3, status_text)
                    time.sleep(0.4)
                except RuntimeError:
                    # 处理信号对象已被删除的情况
                    break
        except Exception as e:
            logging.error(f"状态线程运行出错: {e}")
        
        # 发送完成状态
        try:
            if self.str_error_battery != "":
                self.signals.info.emit(False, 1, self.str_error_battery)
            else:
                if self.str_error_xlsx != "":
                    self.signals.info.emit(False, 2, self.str_error_xlsx)
                else:
                    self.signals.info.emit(False, 0, "status:success")
                    self.signals.thread_end.emit()
        except RuntimeError:
            # 处理信号对象已被删除的情况
            logging.warning("信号对象已被删除，无法发送完成状态")
    
    def _start_visualizer(self):
        """
        启动可视化工具的内部方法
        """
        # 优化ImageMaker启动逻辑：仅查找与 analyzer 同版本的 visualizer
        exe_dir = os.path.dirname(sys.executable)
        build_type = "Debug" if "Debug" in exe_dir else "Release"

        # 从当前运行的 analyzer 可执行文件名中解析版本（形如 battery-analyzer_1_0_1.exe）
        analyzer_exe_name = os.path.basename(sys.executable)
        m = re.search(r"battery-analyzer_(\d+_\d+_\d+)\.exe", analyzer_exe_name, re.IGNORECASE)
        version_us = None
        if m:
            version_us = m.group(1)
        else:
            # 回退：从项目版本读取，并转换为下划线格式
            try:
                from src.battery_analysis.utils.version import Version
                version_us = Version().version.replace('.', '_')
            except Exception:
                version_us = "2_0_0"  # 与项目默认版本保持一致

        # 仅使用与 analyzer 同版本的候选路径
        exe_candidates = [
            # 可执行文件所在目录（打包/本地运行）
            os.path.join(exe_dir, f"battery-analysis-visualizer_{version_us}.exe"),
            # 项目根目录（少数场景可能存在）
            os.path.join(self.str_path, f"battery-analysis-visualizer_{version_us}.exe"),
            # 项目构建目录（Debug/Release）
            os.path.join(self.str_path, "build", build_type, f"battery-analysis-visualizer_{version_us}.exe"),
        ]
        
        exe_executed = False
        for exe_path in exe_candidates:
            if os.path.exists(exe_path):
                logging.info(f"启动ImageMaker: {exe_path}")
                try:
                    # 使用CREATE_NEW_CONSOLE标志启动，以便新窗口中运行
                    subprocess.run(exe_path, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
                    exe_executed = True
                    break
                except Exception as e:
                    logging.error(f"启动失败 {exe_path}: {e}")
                    continue
        
        if not exe_executed:
            logging.warning("未找到battery-analysis-visualizer可执行文件")
            logging.info("候选路径:")
            for path in exe_candidates:
                logging.info(f"  - {path}: {'存在' if os.path.exists(path) else '不存在'}")
