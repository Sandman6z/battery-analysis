#!/usr/bin/env python3
"""
专门用于修复battery_chart_viewer.py中的语法错误
"""
import re
import ast
import sys

def fix_battery_chart_syntax():
    file_path = "src/battery_analysis/main/battery_chart_viewer.py"
    
    print(f"开始修复 {file_path} 的语法错误...")
    
    try:
        # 读取文件
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 修复 class 定义
        content = re.sub(r'class(\w+)', r'class \1', content)
        
        # 修复 def 定义  
        content = re.sub(r'def(\w+)', r'def \1', content)
        
        # 修复 if 条件
        content = re.sub(r'if(\w)', r'if \1', content)
        
        # 修复三元运算符
        content = re.sub(r'(\w+)\s*=\s*([^=]+?)\s*if\s*len\(\s*([^)]+?)\s*\)\s*>=\s*(\d+)\s*else\s*f\{', 
                        r'\1 = \2 if len(\3) >= \4 else f\{', content)
        
        content = re.sub(r'(\w+)\s*=\s*([^=]+?)\s*if\s*len\(\s*([^)]+?)\s*\)\s*>\s*(\d+)\s*else\s*([^,]+?),',
                        r'\1 = \2 if len(\3) > \4 else \5,', content)
        
        # 修复 lambda 函数
        content = re.sub(r'lambda(\w+)', r'lambda \1', content)
        
        # 修复 except 语句
        content = re.sub(r'except(\w+)', r'except \1', content)
        
        # 修复 in 操作符
        content = re.sub(r'in(\w+)', r'in \1', content)
        
        # 修复字符串连接操作符
        content = re.sub(r"(\w+)\[\:(\d+)\]\+(\'\.\.\.')", r"\1[:\2] + \3", content)
        
        # 修复函数调用
        content = re.sub(r'(\w+)\((\s*\w+)', r'\1(\2', content)
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("语法修复完成，验证结果...")
        
        # 验证语法
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                new_content = f.read()
            ast.parse(new_content)
            print("✓ 语法错误修复成功！")
            return True
        except SyntaxError as e:
            print(f"✗ 仍有语法错误: {e}")
            print(f"错误位置: 第{e.lineno}行，第{e.offset}列")
            
            # 显示错误行
            lines = new_content.split('\n')
            if e.lineno <= len(lines):
                print(f"错误行内容: {lines[e.lineno-1]}")
                if e.offset and e.offset <= len(lines[e.lineno-1]):
                    print(f"错误位置: {' ' * (e.offset-1) + '^'}")
            return False
            
    except Exception as e:
        print(f"修复过程中出现错误: {e}")
        return False

if __name__ == "__main__":
    success = fix_battery_chart_syntax()
    sys.exit(0 if success else 1)