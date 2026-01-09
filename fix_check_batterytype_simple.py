#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复check_batterytype方法中的冗余代码
"""

# 读取文件内容
file_path = 'src/battery_analysis/main/main_window.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到check_batterytype方法的开始和结束位置
start_index = None
end_index = None
method_found = False

for i, line in enumerate(lines):
    if 'def check_batterytype(self) -> None:' in line:
        start_index = i
        method_found = True
    elif method_found and 'def ' in line and i > start_index + 5:
        # 找到下一个方法定义，说明当前方法结束
        end_index = i - 1
        break
    elif method_found and i == len(lines) - 1:
        # 到达文件末尾
        end_index = i
        break

# 如果找到了方法，重写它
if start_index is not None and end_index is not None:
    # 创建新的方法内容
    new_method = [
        '    def check_batterytype(self) -> None:\n',
        '        """检查电池类型并更新相关UI组件，委托给ValidationManager"""\n',
        '        from battery_analysis.main.business_logic.validation_manager import ValidationManager\n',
        '        validation_manager = ValidationManager(self)\n',
        '        validation_manager.check_batterytype()\n'
    ]
    
    # 替换旧方法
    lines[start_index:end_index+1] = new_method
    
    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"已修复 {file_path} 中的 check_batterytype 方法")
else:
    print(f"未找到 check_batterytype 方法")
