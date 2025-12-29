#!/usr/bin/env python3
"""
脚本使用Python的ast模块重新格式化Python代码
"""

import ast
import sys
from pathlib import Path

def format_with_ast(file_path):
    """使用ast模块重新格式化Python代码"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # 解析源代码
        tree = ast.parse(source, filename=file_path)
        
        # 重新生成代码
        formatted_code = ast.unparse(tree)
        
        # 写入格式化后的代码
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(formatted_code)
        
        print(f"成功格式化文件: {file_path}")
        return True
    
    except Exception as e:
        print(f"格式化失败: {e}")
        return False

if __name__ == "__main__":
    # 格式化 battery_chart_viewer.py 文件
    file_path = "src/battery_analysis/main/battery_chart_viewer.py"
    if Path(file_path).exists():
        format_with_ast(file_path)
    else:
        print(f"文件 {file_path} 不存在。")