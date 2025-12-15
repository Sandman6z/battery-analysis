"""电池测试数据分析App包初始化"""

import logging
from battery_analysis.utils.version import Version

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 使用version模块获取版本号
__version__ = Version().version

# 导出版本号供外部使用
__all__ = ["__version__"]
