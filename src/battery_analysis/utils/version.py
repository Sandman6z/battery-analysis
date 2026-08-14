"""版本管理模块

版本号唯一来源是 `src/battery_analysis/_version.py`（`__version__`）。
本模块提供 `Version` 类作为历史调用方的兼容封装，以及 `get_version()` 便捷函数。
debug 环境下版本号会附加 `.debug` 后缀。
"""

import logging
import os
import sys

from battery_analysis._version import __version__

logger = logging.getLogger(__name__)


def _is_debug_environment() -> bool:
    """检测是否为 debug 环境。

    通过 DEBUG / APP_DEBUG 环境变量或 --debug 命令行参数判定。
    """
    for var in ("DEBUG", "APP_DEBUG"):
        if os.environ.get(var, "").lower() in ("true", "1", "yes"):
            return True
    if "--debug" in sys.argv:
        return True
    return False


def get_version() -> str:
    """返回应用版本号；debug 环境附加 `.debug` 后缀。"""
    version = __version__
    if _is_debug_environment():
        version += ".debug"
        logger.info("Debug environment detected, version with suffix: %s", version)
    return version


class Version:
    """版本信息访问（兼容历史调用方）。"""

    def __init__(self):
        self.version = get_version()
