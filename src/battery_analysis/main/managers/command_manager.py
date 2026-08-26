# -*- coding: utf-8 -*-
"""
命令管理器

负责管理所有命令对象的初始化，并将其暴露为主窗口的 *_command 属性
"""

import logging
from battery_analysis.main.commands import (
    RunAnalysisCommand, SaveSettingsCommand, ExportReportCommand,
    BatchProcessingCommand, GenerateReportCommand, AnalyzeDataCommand,
    CalculateBatteryCommand
)


class CommandManager:
    """
    命令管理器类，负责管理所有命令对象的初始化，并将其暴露为主窗口的 *_command 属性
    """
    
    def __init__(self, main_window):
        """
        初始化命令管理器
        
        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        # 命令注册表：按 P5-A 计划有意保留（初始化完成后无读取方），请勿删除
        self._commands = {}
        self._initialize_commands()
    
    def _initialize_commands(self):
        """
        初始化所有命令对象
        """
        self.logger.info("Initializing command objects")
        
        # 初始化各种命令并设置为Main类的属性
        self._commands["run_analysis"] = RunAnalysisCommand(self.main_window.analysis_runner)
        self.main_window.run_analysis_command = self._commands["run_analysis"]
        
        self._commands["save_settings"] = SaveSettingsCommand(self.main_window)
        self.main_window.save_settings_command = self._commands["save_settings"]
        
        self._commands["export_report"] = ExportReportCommand(self.main_window.presenter)
        self.main_window.export_report_command = self._commands["export_report"]
        
        self._commands["batch_processing"] = BatchProcessingCommand(self.main_window.presenter)
        self.main_window.batch_processing_command = self._commands["batch_processing"]
        
        self._commands["generate_report"] = GenerateReportCommand(self.main_window.presenter)
        self.main_window.generate_report_command = self._commands["generate_report"]
        
        self._commands["analyze_data"] = AnalyzeDataCommand(self.main_window.presenter)
        self.main_window.analyze_data_command = self._commands["analyze_data"]
        
        self._commands["calculate_battery"] = CalculateBatteryCommand(self.main_window.presenter)
        self.main_window.calculate_battery_command = self._commands["calculate_battery"]
