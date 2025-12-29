#!/usr/bin/env python3
"""
最终语法修复脚本 - 修复battery_chart_viewer.py中的所有语法错误
"""
import re

def final_syntax_fix():
    file_path = "src/battery_analysis/main/battery_chart_viewer.py"
    
    print(f"开始最终修复 {file_path} 的语法错误...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复所有导入语句中的空格问题
        content = re.sub(r'import\s+(\w)', r'import \1', content)
        content = re.sub(r'from\s+(\w)', r'from \1', content)
        
        # 修复特定的导入问题
        content = re.sub(r'loggin g\.', 'logging.', content)
        content = re.sub(r'for mat=', 'format=', content)
        content = re.sub(r'in teractive', 'interactive', content)
        content = re.sub(r'vis ualization', 'visualization', content)
        content = re.sub(r'suppor t', 'support', content)
        content = re.sub(r'dis play', 'display', content)
        content = re.sub(r'axes\.unicode_min us', 'axes.unicode_minus', content)
        content = re.sub(r'bin din gs', 'bindings', content)
        content = re.sub(r'in cludin', 'including', content)
        content = re.sub(r'befor e', 'before', content)
        content = re.sub(r'impor t in g', 'importing', content)
        content = re.sub(r'color s', 'colors', content)
        content = re.sub(r'fin d', 'find', content)
        
        # 修复类和方法定义
        content = re.sub(r'__in it__', '__init__', content)
        
        # 修复 __init__ 方法的参数和缩进
        content = re.sub(r'def __in it__\(self\):', 'def __init__(self):', content)
        
        # 修复 axis_default 变量名
        content = re.sub(r'axis_def ault', 'axis_default', content)
        
        # 修复函数定义中的空格问题
        content = re.sub(r'def\s+(\w+)', r'def \1', content)
        
        # 修复 if 语句
        content = re.sub(r'if\s+(\w+)', r'if \1', content)
        
        # 修复 for 循环
        content = re.sub(r'for\s+(\w+)', r'for \1', content)
        
        # 修复 while 循环
        content = re.sub(r'while\s+(\w+)', r'while \1', content)
        
        # 修复 try-except
        content = re.sub(r'except\s+(\w+)', r'except \1', content)
        
        # 修复列表和字典操作
        content = re.sub(r'\.append\s*\(\s*(\w+)\s*\)', r'.append(\1)', content)
        content = re.sub(r'\.extend\s*\(\s*(\w+)\s*\)', r'.extend(\1)', content)
        
        # 修复字符串和数值操作
        content = re.sub(r'len\s*\(\s*(\w+)\s*\)', r'len(\1)', content)
        content = re.sub(r'str\s*\(\s*(\w+)\s*\)', r'str(\1)', content)
        
        # 修复数学比较
        content = re.sub(r'>=\s*(\d+)', r'>=\1', content)
        content = re.sub(r'<=\s*(\d+)', r'<=\1', content)
        content = re.sub(r'>\s*(\d+)', r'>\1', content)
        content = re.sub(r'<\s*(\d+)', r'<\1', content)
        
        # 修复三元运算符
        content = re.sub(r'if\s+len\s*\(\s*(\w+)\s*\)\s*>=\s*(\d+)\s*else\s*', 
                        r'if len(\1) >= \2 else ', content)
        content = re.sub(r'if\s+len\s*\(\s*(\w+)\s*\)\s*>\s*(\d+)\s*else\s*', 
                        r'if len(\1) > \2 else ', content)
        
        # 修复字符串切片和连接
        content = re.sub(r'\[:(\d+)\]\+', r'[:\1] +', content)
        
        # 修复 lambda 函数
        content = re.sub(r'lambda\s+(\w+)', r'lambda \1', content)
        
        # 修复变量赋值
        content = re.sub(r'=\s*\[', '= [', content)
        content = re.sub(r'\]\s*$', ']', content)
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("最终修复完成")
        return True
        
    except Exception as e:
        print(f"修复过程中出现错误: {e}")
        return False

if __name__ == "__main__":
    final_syntax_fix()