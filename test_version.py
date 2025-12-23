#!/usr/bin/env python3
"""
测试version.py模块是否能正确读取版本号
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('.'))

from src.battery_analysis.utils.version import Version
from src.battery_analysis import __version__

def test_version():
    """测试版本号读取功能"""
    print("=== 版本号测试 ===")
    
    # 测试直接从Version类获取版本号
    version_instance = Version()
    version_from_class = version_instance.version
    print(f"从Version类获取的版本号: {version_from_class}")
    
    # 测试从__init__.py获取版本号
    print(f"从__init__.py获取的版本号: {__version__}")
    
    # 验证两个版本号是否一致
    if version_from_class == __version__:
        print("✓ 版本号一致")
    else:
        print("✗ 版本号不一致")
    
    # 验证版本号格式是否正确
    try:
        major, minor, patch = map(int, version_from_class.split('.')[:3])
        print(f"✓ 版本号格式正确: {major}.{minor}.{patch}")
    except ValueError:
        print(f"✗ 版本号格式不正确: {version_from_class}")
    
    return version_from_class

if __name__ == "__main__":
    version = test_version()
    print(f"\n最终版本号: {version}")
