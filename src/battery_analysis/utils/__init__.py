"""
工具函数包
提供各种通用工具函数和装饰器
"""

# pylint: disable=undefined-all-variable
# PEP 562 __getattr__ 惰性加载：__all__ 名字运行时才解析，静态检查无法识别
__all__ = [
    "clear_old_logs",
    "generate_error_report",
    "get_log_directory",
    "get_logger",
    "get_report_info",
]


def __getattr__(name):
    """延迟加载子模块，避免 import battery_analysis 时触发 heavy 导入"""
    if name == "get_logger":
        from battery_analysis.utils.log_manager import get_logger

        return get_logger
    if name == "get_log_directory":
        from battery_analysis.utils.log_manager import get_log_directory

        return get_log_directory
    if name == "clear_old_logs":
        from battery_analysis.utils.log_manager import clear_old_logs

        return clear_old_logs
    if name in ("generate_error_report", "get_report_info"):
        from battery_analysis.utils.error_report_generator import (
            generate_error_report,
            get_report_info,
        )

        if name == "generate_error_report":
            return generate_error_report
        return get_report_info
    # ── 新模块：允许 from battery_analysis.utils import <name> ──
    lazy_map = {
        "InputValidator": ("battery_analysis.utils.input_validator", "InputValidator"),
        "ValidationResult": ("battery_analysis.utils.input_validator", "ValidationResult"),
        "FieldValues": ("battery_analysis.utils.input_validator", "FieldValues"),
        "AppConfigSchema": ("battery_analysis.utils.config_schema", "AppConfigSchema"),
        "run_migrations": ("battery_analysis.utils.config_migration", "run_migrations"),
    }
    if name in lazy_map:
        mod_path, attr = lazy_map[name]
        import importlib

        mod = importlib.import_module(mod_path)
        return getattr(mod, attr)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
