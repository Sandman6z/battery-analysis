#!/usr/bin/env python3
"""
测试locale修复是否有效
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import locale
from battery_analysis.i18n import detect_system_locale, set_locale, initialize_default_locale

print("=== 测试locale.getdefaultlocale()返回值 ===")
try:
    result = locale.getdefaultlocale()
    print(f"locale.getdefaultlocale() 返回: {result}")
    print(f"类型: {type(result)}")
    if isinstance(result, tuple):
        print(f"长度: {len(result)}")
        for i, item in enumerate(result):
            print(f"  [{i}]: {item} (类型: {type(item)})")
except Exception as e:
    print(f"locale.getdefaultlocale() 出错: {e}")

print("\n=== 测试detect_system_locale() ===")
try:
    system_locale = detect_system_locale()
    print(f"检测到的系统语言: {system_locale}")
except Exception as e:
    print(f"detect_system_locale() 出错: {e}")

print("\n=== 测试initialize_default_locale() ===")
try:
    result = initialize_default_locale()
    print(f"初始化结果: {result}")
except Exception as e:
    print(f"initialize_default_locale() 出错: {e}")

print("\n=== 测试set_locale() ===")
try:
    # 测试英语
    result = set_locale("en")
    print(f"设置英语: {result}")
except Exception as e:
    print(f"set_locale('en') 出错: {e}")

try:
    # 测试中文
    result = set_locale("zh_CN")
    print(f"设置中文: {result}")
except Exception as e:
    print(f"set_locale('zh_CN') 出错: {e}")