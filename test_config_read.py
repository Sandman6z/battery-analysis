#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试配置文件读取逻辑
"""

import os
import sys
from pathlib import Path

def test_config_path_logic():
    """测试配置文件路径查找逻辑"""
    current_dir = Path.cwd() if not getattr(sys, 'frozen', False) else Path(sys.executable).parent
    config_path = current_dir / "config" / "setting.ini"
    
    print(f"=== 测试配置文件路径逻辑 ===")
    print(f"当前目录: {current_dir}")
    print(f"配置路径: {config_path}")
    print(f"exe环境: {getattr(sys, 'frozen', False)}")
    print(f"配置文件存在: {config_path.exists()}")
    
    # 模拟修复后的查找逻辑
    config_path_v2 = current_dir / "config" / "setting.ini"
    if not config_path_v2.exists():
        config_path_v2 = current_dir / "setting.ini"
    
    print(f"修复后的配置路径: {config_path_v2}")
    print(f"修复后的配置文件存在: {config_path_v2.exists()}")
    
    if config_path_v2.exists():
        print("✓ 找到配置文件")
        try:
            with open(config_path_v2, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"配置文件大小: {len(content)} 字符")
                if 'BatteryConfig' in content:
                    print("✓ 包含BatteryConfig配置")
                else:
                    print("❌ 不包含BatteryConfig配置")
        except Exception as e:
            print(f"❌ 读取配置文件失败: {e}")
    else:
        print("❌ 未找到配置文件")
        # 列出当前目录的所有文件和子目录
        print("当前目录内容:")
        for item in current_dir.iterdir():
            print(f"  {'[DIR] ' if item.is_dir() else '[FILE]'} {item.name}")

def test_ui_import():
    """测试UI模块导入"""
    print(f"\n=== 测试UI模块导入 ===")
    try:
        from src.battery_analysis.main.main_window import Main
        print("✓ 成功导入Main类")
    except ImportError as e:
        print(f"❌ 导入Main失败: {e}")
    except Exception as e:
        print(f"❌ 导入Main时出现其他错误: {e}")

if __name__ == "__main__":
    test_config_path_logic()
    test_ui_import()