"""
工具函数包
提供各种通用工具函数和装饰器
"""

__all__ = [
    'get_logger',
    'get_log_directory',
    'clear_old_logs',
    'generate_error_report',
    'get_report_info',
]


def __getattr__(name):
    """延迟加载子模块，避免 import battery_analysis 时触发 heavy 导入"""
    if name == 'get_logger':
        from battery_analysis.utils.log_manager import get_logger
        return get_logger
    if name == 'get_log_directory':
        from battery_analysis.utils.log_manager import get_log_directory
        return get_log_directory
    if name == 'clear_old_logs':
        from battery_analysis.utils.log_manager import clear_old_logs
        return clear_old_logs
    if name in ('generate_error_report', 'get_report_info'):
        from battery_analysis.utils.error_report_generator import generate_error_report, get_report_info
        if name == 'generate_error_report':
            return generate_error_report
        return get_report_info
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")