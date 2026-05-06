"""
工具函数包
提供各种通用工具函数和装饰器
"""

from battery_analysis.utils.log_manager import (
    get_logger,
    get_log_directory,
    clear_old_logs,
)
from battery_analysis.utils.error_report_generator import (
    generate_error_report,
    get_report_info,
)

__all__ = [
    'get_logger',
    'get_log_directory',
    'clear_old_logs',
    'generate_error_report',
    'get_report_info',
]