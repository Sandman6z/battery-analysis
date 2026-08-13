"""电池测试数据分析App包初始化"""

import logging

# 配置日志
logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# 版本号单一来源见 _version.py，升级版本时只需修改该文件
from ._version import __version__

# 导出版本号和子模块供外部使用
__all__ = ["__version__", "utils"]

# 导入子模块
import battery_analysis.utils
