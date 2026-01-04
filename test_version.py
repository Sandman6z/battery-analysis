#!/usr/bin/env python3
"""
测试版本号获取功能
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from battery_analysis import __version__
from battery_analysis.utils.version import Version

print(f"直接导入的版本号: {__version__}")

# 测试Version类
v = Version()
print(f"Version类获取的版本号: {v.version}")

# 测试多次实例化
v2 = Version()
print(f"第二次实例化获取的版本号: {v2.version}")
print(f"实例是否相同: {v is v2}")
