#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面修复battery_chart_viewer.py中的缩进问题
"""

import re
import os
import ast
import logging

def fix_indentation_comprehensive(file_path):
    """全面修复缩进问题"""
    
    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    fixed_lines = []
    
    # 追踪当前缩进级别和上下文
    current_class_indent = 0
    in_class = False
    in_method = False
    method_indent_level = 0
    
    # 分析文件结构
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        if not stripped:
            fixed_lines.append(line)
            continue
            
        # 检测类定义
        if stripped.startswith('class '):
            # 检查是否是嵌套类
            if 'class BatteryChartViewer:' in line:
                # 主类定义，应该在0缩进级别
                current_class_indent = 0
                in_class = True
                in_method = False
                fixed_lines.append(line)
            elif 'class PlotConfig:' in line:
                # PlotConfig是嵌套类，应该在8个空格级别
                current_class_indent = 8
                in_class = True
                in_method = False
                fixed_lines.append('    ' + stripped)
            else:
                # 其他类
                current_class_indent = 0
                in_class = True
                in_method = False
                fixed_lines.append(line)
        
        # 检测方法定义
        elif stripped.startswith('def ') and 'self' in line:
            in_method = True
            # 方法应该在类缩进基础上增加8个空格
            method_indent = current_class_indent + 8
            # 检查当前行的缩进
            current_indent = len(line) - len(line.lstrip())
            
            if current_indent != method_indent:
                # 重新缩进行
                new_line = ' ' * method_indent + stripped
                fixed_lines.append(new_line)
            else:
                fixed_lines.append(line)
        
        # 处理普通代码行
        elif in_class or in_method:
            # 确定期望的缩进级别
            if in_method:
                expected_indent = current_class_indent + 8
            else:
                expected_indent = current_class_indent
            
            # 如果是控制结构的子句，调整缩进
            if stripped.startswith(('if ', 'elif ', 'else:', 'try:', 'except ', 'finally:', 'while ', 'for ', 'with ')):
                # 控制结构应该比方法级别多4个空格
                expected_indent += 4
                fixed_lines.append(' ' * expected_indent + stripped)
            elif stripped.startswith(('elif ', 'except ', 'finally:', 'else:')):
                # elif, except等应该与对应的if/try对齐
                expected_indent = current_class_indent + 8
                fixed_lines.append(' ' * expected_indent + stripped)
            else:
                # 普通代码行
                current_indent = len(line) - len(line.lstrip())
                if current_indent != expected_indent and not stripped.startswith(('#', '"""', "'''")):
                    # 如果缩进不正确，调整它
                    if stripped:
                        fixed_lines.append(' ' * expected_indent + stripped)
                    else:
                        fixed_lines.append('')
                else:
                    fixed_lines.append(line)
        else:
            # 不在任何类或方法中，直接添加
            fixed_lines.append(line)
    
    # 写入修复后的内容
    fixed_content = '\n'.join(fixed_lines)
    
    # 使用ast验证语法
    try:
        ast.parse(fixed_content)
        print("✅ 语法验证通过")
    except SyntaxError as e:
        print(f"❌ 语法错误: {e}")
        print(f"   行号: {e.lineno}")
        print(f"   错误信息: {e.msg}")
        return False
    
    # 备份原文件
    backup_path = file_path + '.backup'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"📁 原文件已备份到: {backup_path}")
    
    # 写入修复后的内容
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"✅ 缩进修复完成: {file_path}")
    return True

if __name__ == "__main__":
    file_path = "c:\\Users\\boe\\Desktop\\battery-analysis\\src\\battery_analysis\\main\\battery_chart_viewer.py"
    
    print("开始修复缩进问题...")
    success = fix_indentation_comprehensive(file_path)
    
    if success:
        print("\n✅ 修复完成！现在测试语法...")
        
        # 测试语法
        import subprocess
        result = subprocess.run(['python', '-m', 'py_compile', file_path], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("🎉 语法验证通过！")
        else:
            print(f"❌ 语法错误仍然存在:")
            print(result.stderr)
    else:
        print("❌ 修复失败")