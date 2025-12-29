#!/usr/bin/env python3
"""
专门修复 battery_chart_viewer.py 的缩进问题
"""

import re

def fix_indentation():
    file_path = "src/battery_analysis/main/battery_chart_viewer.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"原始行数: {len(lines)}")
        
        fixed_lines = []
        in_method = False
        method_indent_level = 0
        
        for i, line in enumerate(lines):
            original_line = line
            stripped = line.strip()
            
            # 如果是方法定义
            if stripped.startswith('def ') and not stripped.startswith('def _'):
                in_method = True
                method_indent_level = 0
                # 方法定义应该是8个空格
                if not line.startswith('    def '):
                    line = '    ' + stripped
                    if not line.endswith('\n'):
                        line += '\n'
            
            # 如果是类定义
            elif stripped.startswith('class '):
                in_method = False
                # 类定义应该是0个空格
                line = stripped + '\n'
            
            # 如果是空行或注释
            elif not stripped or stripped.startswith('#'):
                fixed_lines.append(line)
                continue
            
            # 处理方法体内的代码
            elif in_method:
                # 如果行没有缩进且不包含 'def '，则添加8个空格
                if not line.startswith('                            ') and not line.startswith('    def'):
                    # 计算需要的缩进级别
                    if 'try:' in stripped:
                        line = '                            ' + stripped + '\n'
                    elif 'except' in stripped or 'finally:' in stripped:
                        line = '                            ' + stripped + '\n'
                    elif 'if' in stripped and ':' in stripped:
                        line = '                            ' + stripped + '\n'
                    elif 'elif' in stripped and ':' in stripped:
                        line = '                            ' + stripped + '\n'
                    elif 'else:' in stripped:
                        line = '                            ' + stripped + '\n'
                    elif 'for' in stripped and ':' in stripped:
                        line = '                            ' + stripped + '\n'
                    elif 'while' in stripped and ':' in stripped:
                        line = '                            ' + stripped + '\n'
                    elif 'with' in stripped and ':' in stripped:
                        line = '                            ' + stripped + '\n'
                    elif 'return' in stripped or 'logging.' in stripped or 'self.' in stripped:
                        line = '                            ' + stripped + '\n'
                    else:
                        # 其他语句也添加8个空格
                        line = '                            ' + stripped + '\n'
            
            fixed_lines.append(line)
        
        # 写入修复后的文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)
        
        print(f"缩进修复完成，修复后行数: {len(fixed_lines)}")
        return True
        
    except Exception as e:
        print(f"修复过程中出错: {e}")
        return False

if __name__ == "__main__":
    success = fix_indentation()
    if success:
        print("缩进修复成功！")
    else:
        print("缩进修复失败！")