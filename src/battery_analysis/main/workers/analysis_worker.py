# -*- coding: utf-8 -*-
"""
电池分析工作线程模块
"""
import os
import sys
import re
import time
import shutil
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
        self.list_battery_info = []  # 电池信息列表
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
        # 立即发送取消信号，让主线程知道任务已被取消
        try:
            self.signals.info.emit(False, 0, "status:cancelled")
        except RuntimeError:
            # 处理信号对象已被删除的情况
            logging.warning("信号对象已被删除，无法发送取消状态")
    
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
        self.str_error_battery = ""
        self.str_error_xlsx = ""
        self.str_test_date = ""
        self.list_battery_info = []
        
        # 发送初始运行状态
        self._send_initial_status()
        
        try:
            # 发送初始进度
            self.signals.progress_update.emit(0, "准备分析...")
            
            # 执行任务
            if self._setup_directories() and \
               self._perform_battery_analysis() and \
               self._process_test_date() and \
               self._rename_analysis_directory() and \
               self._generate_report():
                # 发送信号通知主线程启动可视化工具
                try:
                    self.signals.start_visualizer.emit()
                    logging.info("已发送启动可视化工具的信号")
                except RuntimeError:
                    # 处理信号对象已被删除的情况
                    logging.warning("信号对象已被删除，无法发送启动可视化工具的信号")
                
        except FileNotFoundError as e:
            logging.error(f"线程运行过程中发生文件未找到错误: {e}")
            self.str_error_battery = f"文件未找到: {e}"
        except PermissionError as e:
            logging.error(f"线程运行过程中发生权限错误: {e}")
            self.str_error_battery = f"权限错误: {e}"
        except ImportError as e:
            logging.error(f"线程运行过程中发生导入错误: {e}")
            self.str_error_battery = f"导入错误: {e}"
        except Exception as e:
            logging.error(f"线程运行过程中发生未预期的错误: {e}")
            import traceback
            logging.error(f"错误堆栈信息: {traceback.format_exc()}")
            self.str_error_battery = f"发生未预期的错误: {e}"
        finally:
            # 资源清理
            if self.b_cancel_requested:
                logging.info("任务已被取消，进行资源清理")
                # 清理临时目录
                try:
                    version_dir = f"{self.str_output_path}/V{self.list_test_info[16]}"
                    if os.path.exists(version_dir):
                        shutil.rmtree(version_dir)
                        logging.info(f"已清理临时目录: {version_dir}")
                    
                    # 清理可能已创建的测试日期目录
                    if hasattr(self, 'str_test_date') and self.str_test_date:
                        test_date_dir = f"{self.str_output_path}/{self.str_test_date}_V{self.list_test_info[16]}"
                        if os.path.exists(test_date_dir):
                            shutil.rmtree(test_date_dir)
                            logging.info(f"已清理测试日期目录: {test_date_dir}")
                except Exception as e:
                    logging.warning(f"资源清理过程中发生错误: {e}")
                    
            self.b_thread_run = False
            # 发送完成状态
            self._send_completion_status()
    
    def _send_initial_status(self):
        """
        发送初始运行状态信号
        """
        try:
            status_text = "status:run"
            self.signals.info.emit(True, 0, status_text)
            self.signals.info.emit(True, 1, status_text)
            self.signals.info.emit(True, 2, status_text)
            self.signals.info.emit(True, 3, status_text)
        except RuntimeError:
            # 处理信号对象已被删除的情况
            pass
    
    def _setup_directories(self):
        """
        设置分析所需的目录结构
        
        Returns:
            bool: 是否成功设置目录
        """
        if self.b_cancel_requested:
            return False
            
        # 检查并创建目录
        version_dir = f"{self.str_output_path}/V{self.list_test_info[16]}"
        if os.path.exists(version_dir):
            shutil.rmtree(version_dir)
        
        if self.b_cancel_requested:
            return False
        
        os.mkdir(version_dir)
        self.progress_value = 10
        self.signals.progress_update.emit(self.progress_value, "初始化分析...")
        return True
    
    def _perform_battery_analysis(self):
        """
        执行电池分析
        
        Returns:
            bool: 是否成功进行电池分析
        """
        if self.b_cancel_requested:
            return False
            
        # 延迟导入以避免循环引用
        from battery_analysis.utils import battery_analysis
        
        info_battery = battery_analysis.BatteryAnalysis(
            strInDataXlsxDir=self.str_input_path,
            strResultPath=self.str_output_path,
            listTestInfo=self.list_test_info
        )
        
        self.progress_value = 20
        self.signals.progress_update.emit(self.progress_value, "进行电池分析...")
        
        if self.b_cancel_requested:
            return False
            
        self.str_error_battery = info_battery.UBA_GetErrorLog()
        if self.str_error_battery != "":
            return False
            
        self.progress_value = 40
        self.signals.progress_update.emit(self.progress_value, "获取电池信息...")
        
        if self.b_cancel_requested:
            return False
            
        self.list_battery_info = info_battery.UBA_GetBatteryInfo()
        return True
    
    def _process_test_date(self):
        """
        处理测试日期信息
        
        Returns:
            bool: 是否成功处理测试日期
        """
        if self.b_cancel_requested:
            return False
            
        # 获取Test Date和原始周期日期进行验证
        test_date = self.list_battery_info[3]  # 从修改后的UBA_GetBatteryInfo返回值中获取Test Date
        original_cycle_date = self.list_battery_info[4]  # 从修改后的UBA_GetBatteryInfo返回值中获取原始周期日期
        
        logging.info(f"获取到的Test Date: {test_date}, 原始周期日期: {original_cycle_date}")
        
        try:
            # 优先使用从Excel或文件名提取的Test Date（已经是YYYYMMDD格式）
            if test_date and len(test_date) == 8 and test_date.isdigit():
                self.str_test_date = test_date
                logging.info(f"使用YYYYMMDD格式的Test Date: {self.str_test_date}")
            elif test_date:
                # 如果test_date是其他格式，尝试解析
                try:
                    # 尝试处理标准日期格式 YYYY-MM-DD
                    if '-' in test_date:
                        date_part = test_date.split(' ')[0] if ' ' in test_date else test_date
                        [sy, sm, sd] = date_part.split("-")
                        self.str_test_date = f"{sy}{sm}{sd}"
                    elif '/' in test_date:
                        # 尝试处理 YYYY/MM/DD 格式
                        date_part = test_date.split(' ')[0] if ' ' in test_date else test_date
                        [sy, sm, sd] = date_part.split("/")
                        self.str_test_date = f"{sy}{sm}{sd}"
                    else:
                        # 尝试作为YYYYMMDD直接使用
                        self.str_test_date = test_date
                    logging.info(f"从Test Date解析得到: {self.str_test_date}")
                except:
                    # 解析失败时，尝试使用原始周期日期
                    if original_cycle_date:
                        try:
                            # 尝试处理标准日期格式 YYYY-MM-DD
                            if '-' in original_cycle_date:
                                date_part = original_cycle_date.split(' ')[0] if ' ' in original_cycle_date else original_cycle_date
                                [sy, sm, sd] = date_part.split("-")
                                self.str_test_date = f"{sy}{sm}{sd}"
                            elif '/' in original_cycle_date:
                                # 尝试处理 YYYY/MM/DD 格式
                                date_part = original_cycle_date.split(' ')[0] if ' ' in original_cycle_date else original_cycle_date
                                [sy, sm, sd] = date_part.split("/")
                                self.str_test_date = f"{sy}{sm}{sd}"
                            else:
                                # 尝试作为YYYYMMDD直接使用
                                self.str_test_date = original_cycle_date
                            logging.info(f"从原始周期日期解析得到: {self.str_test_date}")
                        except:
                            # 最后尝试回退到原有的日期提取方式
                            try:
                                [sy, sm, sd] = self.list_battery_info[2][0].split(" ")[0].split("-")
                                self.str_test_date = f"{sy}{sm}{sd}"
                                logging.info(f"从list_battery_info解析得到: {self.str_test_date}")
                            except:
                                self.str_test_date = "00000000"
                                logging.error("所有日期解析方式都失败了")
        except Exception as e:
            logging.error(f"解析测试日期失败: {e}")
            self.str_test_date = "00000000"
        
        # 日志记录最终使用的日期
        logging.info(f"最终确定的测试日期: {self.str_test_date}")
        return True
    
    def _rename_analysis_directory(self):
        """
        重命名分析结果目录
        
        Returns:
            bool: 是否成功重命名目录
        """
        if self.b_cancel_requested:
            return False
            
        # 重命名目录
        version_dir = f"{self.str_output_path}/V{self.list_test_info[16]}"
        final_dir = f"{self.str_output_path}/{self.str_test_date}_V{self.list_test_info[16]}"
        if os.path.exists(final_dir):
            shutil.rmtree(final_dir)
        
        self.signals.rename_path.emit(self.str_test_date)
        os.rename(version_dir, final_dir)
        
        self.progress_value = 60
        self.signals.progress_update.emit(self.progress_value, "准备生成报告...")
        return True
    
    def _generate_report(self):
        """
        生成分析报告
        
        Returns:
            bool: 是否成功生成报告
        """
        if self.b_cancel_requested:
            return False
            
        # 文件写入
        from battery_analysis.utils import file_writer
        
        info_file = file_writer.FileWriter(
            strResultPath=self.str_output_path,
            listTestInfo=self.list_test_info,
            listBatteryInfo=self.list_battery_info
        )
        
        self.progress_value = 80
        self.signals.progress_update.emit(self.progress_value, "生成报告中...")
        
        if self.b_cancel_requested:
            return False
            
        self.str_error_xlsx = info_file.UFW_GetErrorLog()
        if self.str_error_xlsx != "":
            logging.error(self.str_error_xlsx)
        else:
            self.progress_value = 100
            self.signals.progress_update.emit(self.progress_value, "分析完成！")
        
        return True
    
    def _send_completion_status(self):
        """
        发送完成状态信号
        """
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
    
