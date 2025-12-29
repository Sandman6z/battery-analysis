#!/usr/bin/env python3
"""
修复Python文件中的缩进错误
"""

import tokenize
import io
import re

def fix_python_file(file_path):
    """
    使用tokenize修复Python文件中的缩进错误
    """
    try:
        # 读取文件
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # 使用tokenize进行解析
        tokens = list(tokenize.generate_tokens(io.StringIO(code).readline))
        
        # 重建代码，确保正确的缩进
        fixed_code = []
        indent_stack = [0]  # 缩进栈，初始为0
        
        for token in tokens:
            # 保留换行符
            if token.type == tokenize.NEWLINE or token.type == tokenize.NL:
                fixed_code.append('\n')
            # 保留注释
            elif token.type == tokenize.COMMENT:
                # 计算当前缩进
                indent = ' ' * indent_stack[-1]
                fixed_code.append(indent + token.string)
            # 处理缩进和缩出
            elif token.type == tokenize.INDENT:
                # 累加缩进
                indent_stack.append(indent_stack[-1] + len(token.string))
            elif token.type == tokenize.DEDENT:
                # 减少缩进，但不低于0
                indent_stack.pop()
                if not indent_stack:
                    indent_stack.append(0)
            # 处理普通token
            else:
                # 计算缩进
                indent = ' ' * indent_stack[-1]
                
                # 对于某些token类型，需要添加缩进
                if (token.type in (tokenize.NAME, tokenize.STRING, tokenize.NUMBER) and
                    fixed_code and fixed_code[-1] == '\n'):
                    fixed_code.append(indent)
                
                fixed_code.append(token.string)
        
        # 将修复后的代码写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(''.join(fixed_code))
        
        print(f"成功修复文件: {file_path}")
        return True
    
    except Exception as e:
        print(f"修复文件时出错: {e}")
        return False

def remove_empty_lines(file_path):
    """
    移除文件中的多余空行
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 移除多余空行
        new_lines = []
        prev_empty = False
        
        for line in lines:
            is_empty = line.strip() == ''
            
            # 只保留非空行或非连续的多个空行
            if not is_empty or not prev_empty:
                new_lines.append(line)
            
            prev_empty = is_empty
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        print(f"已清理文件中的多余空行: {file_path}")
        return True
    
    except Exception as e:
        print(f"清理空行时出错: {e}")
        return False

if __name__ == "__main__":
    # 修复 battery_chart_viewer.py 文件
    file_path = "src/battery_analysis/main/battery_chart_viewer.py"
    
    # 先移除多余空行
    remove_empty_lines(file_path)
    
    # 修复缩进错误
    fix_python_file(file_path)