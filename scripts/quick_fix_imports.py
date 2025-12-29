#!/usr/bin/env python3
"""
快速修复导入语句语法错误
"""
import re

def quick_fix_imports():
    file_path = "src/battery_analysis/main/battery_chart_viewer.py"
    
    print(f"快速修复 {file_path} 的导入语句...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复缺少空格的导入语句
        content = re.sub(r'import(\w)', r'import \1', content)
        content = re.sub(r'from(\w)', r'from \1', content)
        
        # 修复特定模式
        content = re.sub(r'fromPyQt6\.QtWidgetsimport', r'from PyQt6.QtWidgets import ', content)
        content = re.sub(r'fromPyQt6import', r'from PyQt6 import ', content)
        content = re.sub(r'fromPyQt6\.QtCoreimport', r'from PyQt6.QtCore import ', content)
        content = re.sub(r'importsys', r'import sys', content)
        content = re.sub(r'importloggin g', r'import logging', content)
        content = re.sub(r'frompathlibimport', r'from pathlib import ', content)
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("快速修复完成")
        return True
        
    except Exception as e:
        print(f"修复过程中出现错误: {e}")
        return False

if __name__ == "__main__":
    quick_fix_imports()