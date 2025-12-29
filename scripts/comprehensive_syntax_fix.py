#!/usr/bin/env python3
"""
全面修复 battery_chart_viewer.py 的语法错误
"""

import re

def fix_battery_chart_viewer_syntax():
    file_path = "src/battery_analysis/main/battery_chart_viewer.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"原始文件大小: {len(content)} 字符")
        
        # 修复模式列表
        fixes = [
            # 修复变量名中的空格
            (r'\blis tPulseCurrentLevel\b', 'listPulseCurrentLevel'),
            (r'\blis tRules\b', 'listRules'),
            (r'\blis t\s+([A-Za-z_][A-Za-z0-9_]*)\b', r'list\1'),
            (r'\bint\s+([A-Za-z_][A-Za-z0-9_]*)\b', r'int\1'),
            (r'\bstr\s+([A-Za-z_][A-Za-z0-9_]*)\b', r'str\1'),
            
            # 修复关键字错误
            (r'\bExceptionase\b', 'Exception as e'),
            (r'\bwarnin g\b', 'warning'),
            (r'\busin g\b', 'using'),
            (r'\bsettin g\b', 'setting'),
            (r'\bhand le\b', 'handle'),
            (r'\bin fo\b', 'info'),
            (r'\bSpecif ication\b', 'Specification'),
            (r'\bConfig_BatteryAnalysis\.in i\b', 'Config_BatteryAnalysis.ini'),
            (r'\bsettin g\.in i\b', 'setting.ini'),
            
            # 修复空格问题
            (r'\bconfig_battery_pathand\b', 'config_battery_path and'),
            (r'\band\s+os\.path\.exists\b', 'and os.path.exists'),
            (r'\breturnself\b', 'return self'),
            (r'\breturndefault_value\b', 'return default_value'),
            (r'\breturnresult\b', 'return result'),
            (r'\breturncleaned_lis t\b', 'return cleaned_list'),
            (r'\breturndefault_title\b', 'return default_title'),
            (r'\breturn\[\]\b', 'return []'),
            (r'\breturnvalue\b', 'return value'),
            
            # 修复函数定义
            (r'def\s+get_axis\s+_special\b', 'def get_axis_special'),
            (r'def\s+set_axis\s+_special\b', 'def set_axis_special'),
            (r'def\s+_get_config_lis t\b', 'def _get_config_list'),
            (r'def\s+_process_rules\b', 'def _process_rules'),
            
            # 修复属性访问
            (r'\bself\.plot_config\.axis\s+_special\b', 'self.plot_config.axis_special'),
            (r'\bself\.plot_config\.axis\s+_default\b', 'self.plot_config.axis_default'),
            
            # 修复列表推导式
            (r'\[in t\s*\(\s*item\.strip\s*\(\s*\)\s*\)\s*for\s+item\s+in\s+listPulseCurrentLevel\s*\]', '[int(item.strip()) for item in listPulseCurrentLevel]'),
            (r'\[item\.strip\s*\(\s*\)\s*for\s+item\s+in\s+list_value\s*\]', '[item.strip() for item in list_value]'),
            
            # 修复缩进问题 - 确保所有缩进都是8个空格或4个空格
            (r'^                            ', '    '),  # 8个空格 → 4个空格
        ]
        
        # 应用修复
        original_content = content
        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content)
            if content != original_content:
                print(f"应用修复: {pattern} → {replacement}")
                original_content = content
        
        # 特殊修复：确保所有方法缩进正确
        lines = content.split('\n')
        fixed_lines = []
        in_method = False
        
        for line in lines:
            # 如果行包含 'def '，这是一个方法开始
            if 'def ' in line and not line.strip().startswith('#'):
                in_method = True
                # 确保方法定义缩进为8个空格
                if not line.startswith('    def '):
                    line = '    ' + line.lstrip()
            elif in_method and line.strip() and not line.strip().startswith('#'):
                # 确保方法体内的代码缩进为8个空格
                if not line.startswith('                            '):
                    line = '                            ' + line.lstrip()
                elif line.startswith('    ') and not line.startswith('                            '):
                    # 如果是4个空格，转换为8个空格
                    line = '                            ' + line[4:]
            
            fixed_lines.append(line)
        
        content = '\n'.join(fixed_lines)
        
        # 写入修复后的文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"修复完成，文件大小: {len(content)} 字符")
        return True
        
    except Exception as e:
        print(f"修复过程中出错: {e}")
        return False

if __name__ == "__main__":
    success = fix_battery_chart_viewer_syntax()
    if success:
        print("语法修复成功！")
    else:
        print("语法修复失败！")