"""电池测试数据分析App包初始化"""

import logging

# 配置日志
logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# 硬编码版本号，避免模块导入时触发 Version() 的 heavy import 链
# 更新版本号时请同步修改 pyproject.toml 中的 version 字段
__version__ = "2.10.0"

# 导出版本号和子模块供外部使用
__all__ = ["__version__", "utils"]

# 导入子模块
import battery_analysis.utils
