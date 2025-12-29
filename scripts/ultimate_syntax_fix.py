#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
终极语法修复脚本 - 系统性修复battery_chart_viewer.py的所有语法错误
"""

import re
import ast

def fix_all_syntax_errors(file_path):
    """系统性地修复所有语法错误"""
    
    print(f"📖 读取文件: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 开始修复语法错误...")
    
    # 修复模式列表
    fixes = [
        # 1. 修复变量名中的空格
        (r'\blis tPulseCurrentLevel\b', 'listPulseCurrentLevel'),
        (r'\blis tRules\b', 'listRules'),
        (r'\blis t\s+([A-Za-z_][A-Za-z0-9_]*)\b', r'list\1'),
        (r'\bin tCurrentLevelNum\b', 'intCurrentLevelNum'),
        (r'\bint\s+([A-Za-z_][A-Za-z0-9_]*)\b', r'int\1'),
        (r'\bstr\s+([A-Za-z_][A-Za-z0-9_]*)\b', r'str\1'),
        
        # 2. 修复关键字错误
        (r'\bExceptionase\b', 'Exception as e'),
        (r'\bwarnin g\b', 'warning'),
        (r'\busin g\b', 'using'),
        (r'\bsettin g\b', 'setting'),
        (r'\bhand le\b', 'handle'),
        (r'\bin fo\b', 'info'),
        (r'\bSpecif ication\b', 'Specification'),
        (r'\bConfig_BatteryAnalysis\.in i\b', 'Config_BatteryAnalysis.ini'),
        (r'\bsettin g\.in i\b', 'setting.ini'),
        
        # 3. 修复空格问题
        (r'\bconfig_battery_pathand\b', 'config_battery_path and'),
        (r'\band\s+os\.path\.exists\b', 'and os.path.exists'),
        (r'\breturnself\b', 'return self'),
        (r'\breturndefault_value\b', 'return default_value'),
        (r'\breturnresult\b', 'return result'),
        (r'\breturncleaned_lis t\b', 'return cleaned_list'),
        (r'\breturndefault_title\b', 'return default_title'),
        (r'\breturn\[\]\b', 'return []'),
        (r'\breturnvalue\b', 'return value'),
        
        # 4. 修复复合问题
        (r'\bfor\s+rulein\b', 'for rule in'),
        (r'\bspec_typein\b', 'spec_type in'),
        (r'\bin\s+ruleand\b', 'in rule and'),
        
        # 5. 修复缩进问题
        (r'^([^\s].*)$', r'\1'),  # 清理行首空格
        
        # 6. 修复其他常见错误
        (r'\bself\.\s*self\b', 'self.'),
    ]
    
    # 应用修复
    for i, (pattern, replacement) in enumerate(fixes):
        old_content = content
        content = re.sub(pattern, replacement, content)
        if content != old_content:
            print(f"  ✅ 修复 {i+1}: {pattern} -> {replacement}")
    
    # 清理多余的空行和空格
    lines = content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # 清理行尾空格
        cleaned_line = line.rstrip()
        cleaned_lines.append(cleaned_line)
    
    content = '\n'.join(cleaned_lines)
    
    # 验证语法
    print("🔍 验证语法...")
    try:
        ast.parse(content)
        print("✅ 语法验证通过！")
        syntax_ok = True
    except SyntaxError as e:
        print(f"❌ 语法错误在第{e.lineno}行: {e.msg}")
        lines = content.split('\n')
        if e.lineno <= len(lines):
            print(f"错误行: {lines[e.lineno-1]}")
        syntax_ok = False
    
    # 备份原文件
    backup_path = file_path + '.backup_ultimate'
    with open(backup_path, 'w', encoding='utf-8') as f:
        with open(file_path, 'r', encoding='utf-8') as original:
            f.write(original.read())
    print(f"📁 原文件已备份到: {backup_path}")
    
    # 如果语法正确，保存文件
    if syntax_ok:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 文件已保存: {file_path}")
        return True
    else:
        print("❌ 语法仍然错误，需要手动修复")
        return False

if __name__ == "__main__":
    file_path = "c:\\Users\\boe\\Desktop\\battery-analysis\\src\\battery_analysis\\main\\battery_chart_viewer.py"
    
    print("🚀 开始终极语法修复...")
    success = fix_all_syntax_errors(file_path)
    
    if success:
        print("\n🎉 修复完成！现在运行完整测试...")
        
        # 运行完整测试
        import subprocess
        result = subprocess.run(['python', '-m', 'py_compile', file_path], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("🎉 编译测试通过！")
        else:
            print(f"❌ 编译测试失败:")
            print(result.stderr)
    else:
        print("❌ 修复失败，需要进一步处理")