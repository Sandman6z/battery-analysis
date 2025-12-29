#!/usr/bin/env python3
"""
全面修复battery_chart_viewer.py中的所有语法错误
"""
import re
import ast

def comprehensive_fix():
    file_path = "src/battery_analysis/main/battery_chart_viewer.py"
    
    print(f"开始全面修复 {file_path} 的语法错误...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复 __init__ 方法
        content = re.sub(r'__in it__', '__init__', content)
        
        # 修复函数定义 - 多种模式
        content = re.sub(r'def\s+(\w)', r'def \1', content)
        content = re.sub(r'def(\w+)', r'def \1', content)
        
        # 修复参数定义
        content = re.sub(r'self\)=', r'self) =', content)
        content = re.sub(r'self,=', r'self, =', content)
        
        # 修复变量赋值
        content = re.sub(r'self\.axis_def ault', 'self.axis_default', content)
        content = re.sub(r'self\.axis_special', 'self.axis_special', content)
        
        # 修复列表定义
        content = re.sub(r'=\[([^,\]]+),([^,\]]+),([^,\]]+),([^,\]]+)\]', 
                        r'= [\1, \2, \3, \4]', content)
        
        # 修复行内多余空格和格式问题
        content = re.sub(r'>\s*=([^\n]*)', r'>=\1', content)
        content = re.sub(r'<\s*=([^\n]*)', r'<=\1', content)
        
        # 修复 if 语句
        content = re.sub(r'if\s+(\w)', r'if \1', content)
        content = re.sub(r'if(\w)', r'if \1', content)
        
        # 修复 else 语句
        content = re.sub(r'else:', 'else:', content)
        
        # 修复 for 循环
        content = re.sub(r'for\s+(\w)', r'for \1', content)
        content = re.sub(r'for(\w)', r'for \1', content)
        
        # 修复 while 循环
        content = re.sub(r'while\s+(\w)', r'while \1', content)
        content = re.sub(r'while(\w)', r'while \1', content)
        
        # 修复 try-except
        content = re.sub(r'try:', 'try:', content)
        content = re.sub(r'except\s+(\w)', r'except \1', content)
        content = re.sub(r'except(\w)', r'except \1', content)
        
        # 修复 return 语句
        content = re.sub(r'return(\s*\w)', r'return\1', content)
        
        # 修复 and/or 条件
        content = re.sub(r'and\s+(\w)', r'and \1', content)
        content = re.sub(r'and(\w)', r'and \1', content)
        content = re.sub(r'or\s+(\w)', r'or \1', content)
        content = re.sub(r'or(\w)', r'or \1', content)
        
        # 修复 not 条件
        content = re.sub(r'not\s+(\w)', r'not \1', content)
        content = re.sub(r'not(\w)', r'not \1', content)
        
        # 修复 in 操作符
        content = re.sub(r'in\s+(\w)', r'in \1', content)
        content = re.sub(r'in(\w)', r'in \1', content)
        
        # 修复 is 操作符
        content = re.sub(r'is\s+(\w)', r'is \1', content)
        content = re.sub(r'is(\w)', r'is \1', content)
        
        # 修复字符串操作
        content = re.sub(r'len\s*\(\s*(\w+)\s*\)', r'len(\1)', content)
        content = re.sub(r'str\s*\(\s*(\w+)\s*\)', r'str(\1)', content)
        content = re.sub(r'int\s*\(\s*(\w+)\s*\)', r'int(\1)', content)
        content = re.sub(r'float\s*\(\s*(\w+)\s*\)', r'float(\1)', content)
        
        # 修复列表操作
        content = re.sub(r'\.append\s*\(\s*(\w+)\s*\)', r'.append(\1)', content)
        content = re.sub(r'\.extend\s*\(\s*(\w+)\s*\)', r'.extend(\1)', content)
        content = re.sub(r'\.remove\s*\(\s*(\w+)\s*\)', r'.remove(\1)', content)
        content = re.sub(r'\.pop\s*\(\s*(\w+)\s*\)', r'.pop(\1)', content)
        
        # 修复字典操作
        content = re.sub(r'\.keys\s*\(\s*\)', r'.keys()', content)
        content = re.sub(r'\.values\s*\(\s*\)', r'.values()', content)
        content = re.sub(r'\.items\s*\(\s*\)', r'.items()', content)
        
        # 修复函数调用
        content = re.sub(r'(\w+)\s*\(\s*(\w+)\s*\)', r'\1(\2)', content)
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("全面修复完成，验证结果...")
        
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
    comprehensive_fix()