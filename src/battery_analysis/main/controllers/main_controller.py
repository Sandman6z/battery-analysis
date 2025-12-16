# -*- coding: utf-8 -*-
"""
主控制器模块
负责处理核心业务逻辑和协调各个组件
"""
import os
from PyQt6 import QtCore as QC
from battery_analysis.main.workers.analysis_worker import AnalysisWorker


class MainController(QC.QObject):
    """
    主控制器类
    负责应用程序的核心业务逻辑控制
    """
    # 定义信号
    progress_updated = QC.pyqtSignal(int, str)  # 进度更新信号
    status_changed = QC.pyqtSignal(bool, int, str)  # 状态变化信号
    analysis_completed = QC.pyqtSignal()  # 分析完成信号
    path_renamed = QC.pyqtSignal(str)  # 路径重命名信号
    
    def __init__(self):
        """
        初始化主控制器
        """
        super().__init__()
        self.thread_pool = QC.QThreadPool.globalInstance()
        self.current_worker = None
        self.is_analysis_running = False
        self.project_path = ""
        self.input_path = ""
        self.output_path = ""
        self.test_info = []
    
    def set_project_context(self, project_path, input_path, output_path):
        """
        设置项目上下文信息
        
        Args:
            project_path: 项目路径
            input_path: 输入数据路径
            output_path: 输出结果路径
        """
        self.project_path = project_path
        self.input_path = input_path
        self.output_path = output_path
    
    def set_test_info(self, test_info):
        """
        设置测试信息
        
        Args:
            test_info: 测试信息列表
        """
        self.test_info = test_info
    
    def start_analysis(self):
        """
        开始电池分析任务
        """
        if self.is_analysis_running:
            return False
        
        # 验证必要的参数
        if not all([self.project_path, self.input_path, self.output_path, self.test_info]):
            self.status_changed.emit(False, 1, "错误：缺少必要的分析参数")
            return False
        
        # 创建工作线程
        self.current_worker = AnalysisWorker()
        self.current_worker.set_info(
            self.project_path,
            self.input_path,
            self.output_path,
            self.test_info
        )
        
        # 连接信号
        self.current_worker.signals.progress_update.connect(self._on_progress_update)
        self.current_worker.signals.info.connect(self._on_status_changed)
        self.current_worker.signals.thread_end.connect(self._on_analysis_completed)
        self.current_worker.signals.rename_path.connect(self._on_path_renamed)
        self.current_worker.signals.start_visualizer.connect(self._on_start_visualizer)
        
        # 启动工作线程
        self.thread_pool.start(self.current_worker)
        self.is_analysis_running = True
        return True
    
    def cancel_analysis(self):
        """
        取消正在进行的分析任务
        """
        if not self.is_analysis_running or not self.current_worker:
            return False
        
        self.current_worker.request_cancel()
        return True
    
    def is_running(self):
        """
        检查分析是否正在运行
        
        Returns:
            bool: True表示正在运行，False表示未运行
        """
        return self.is_analysis_running
    
    def _on_progress_update(self, progress, status_text):
        """
        进度更新回调
        
        Args:
            progress: 进度值(0-100)
            status_text: 状态文本
        """
        self.progress_updated.emit(progress, status_text)
    
    def _on_status_changed(self, is_running, status_code, message):
        """
        状态变化回调
        
        Args:
            is_running: 是否正在运行
            status_code: 状态代码
            message: 状态消息
        """
        self.status_changed.emit(is_running, status_code, message)
    
    def _on_analysis_completed(self):
        """
        分析完成回调
        """
        self.is_analysis_running = False
        self.analysis_completed.emit()
    
    def _on_path_renamed(self, test_date):
        """
        路径重命名回调
        
        Args:
            test_date: 测试日期
        """
        self.path_renamed.emit(test_date)
    
    def _on_start_visualizer(self):
        """
        启动可视化工具的回调方法
        """
        import os
        import sys
        import re
        import subprocess
        import logging
        
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
                from battery_analysis.utils.version import Version
                version_us = Version().version.replace('.', '_')
            except Exception:
                version_us = "2_0_0"  # 与项目默认版本保持一致

        # 仅使用与 analyzer 同版本的候选路径
        exe_candidates = [
            # 可执行文件所在目录（打包/本地运行）
            os.path.join(exe_dir, f"battery-analysis-visualizer_{version_us}.exe"),
            # 项目根目录（少数场景可能存在）
            os.path.join(self.project_path, f"battery-analysis-visualizer_{version_us}.exe"),
            # 项目构建目录（Debug/Release）
            os.path.join(self.project_path, "build", build_type, f"battery-analysis-visualizer_{version_us}.exe"),
        ]
        
        exe_executed = False
        for exe_path in exe_candidates:
            if os.path.exists(exe_path):
                logging.info(f"启动可视化工具: {exe_path}")
                try:
                    # 使用CREATE_NEW_CONSOLE标志启动，以便新窗口中运行，移除shell=True避免重复启动
                    subprocess.run([exe_path], creationflags=subprocess.CREATE_NEW_CONSOLE)
                    exe_executed = True
                    break
                except Exception as e:
                    logging.error(f"启动可视化工具失败 {exe_path}: {e}")
                    continue
        
        if not exe_executed:
            logging.warning("未找到battery-analysis-visualizer可执行文件")
            logging.info("候选路径:")
            for path in exe_candidates:
                logging.info(f"  - {path}: {'存在' if os.path.exists(path) else '不存在'}")
