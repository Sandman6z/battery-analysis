#!/usr/bin/env python3
"""
调试模块初始化过程
"""

import sys
import os
import traceback
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("=== 开始导入测试 ===")

try:
    print("导入i18n模块...")
    from battery_analysis import i18n
    print("✓ i18n模块导入成功")
except Exception as e:
    print(f"✗ i18n模块导入失败: {e}")
    traceback.print_exc()

try:
    print("导入language_manager...")
    from battery_analysis.i18n.language_manager import LanguageManager
    print("✓ LanguageManager导入成功")
except Exception as e:
    print(f"✗ LanguageManager导入失败: {e}")
    traceback.print_exc()

print("=== 导入完成 ===")