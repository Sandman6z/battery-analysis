# -*- coding: utf-8 -*-
"""
命令模式实现模块

该模块定义了命令模式的基类和具体实现，用于封装用户交互操作，提高扩展性和可测试性。
"""

from battery_analysis.main.commands.base import Command
from battery_analysis.main.commands.analysis_commands import (
    RunAnalysisCommand,
    CalculateBatteryCommand,
)
from battery_analysis.main.commands.report_commands import (
    ExportReportCommand,
    GenerateReportCommand,
    BatchProcessingCommand,
    SaveSettingsCommand,
)
from battery_analysis.main.commands.data_commands import (
    AnalyzeDataCommand,
    ProcessExcelCommand,
    ProcessAllExcelCommand,
    GetXlsxInfoCommand,
    SaveTableCommand,
    UpdateConfigCommand,
    CheckInputCommand,
    HandleDataErrorCommand,
)

__all__ = [
    "Command",
    "RunAnalysisCommand",
    "SaveSettingsCommand",
    "ExportReportCommand",
    "BatchProcessingCommand",
    "GenerateReportCommand",
    "AnalyzeDataCommand",
    "CalculateBatteryCommand",
    "ProcessExcelCommand",
    "ProcessAllExcelCommand",
    "GetXlsxInfoCommand",
    "SaveTableCommand",
    "UpdateConfigCommand",
    "CheckInputCommand",
    "HandleDataErrorCommand",
]
