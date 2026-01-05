#!/usr/bin/env python3
"""
删除main_window.py中重复的方法
"""

import os

# 定义文件路径
file_path = r'c:\Users\boe\Desktop\battery-analysis\src\battery_analysis\main\main_window.py'

# 读取文件内容
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 定义要删除的方法范围
# 格式：(start_line, end_line)
# 注意：行号从1开始
methods_to_remove = [
    (786, 882),   # _setup_accessibility方法
    (883, 926),   # init_lineedit方法
    (1042, 1083), # init_combobox方法
    (1084, 1157), # init_table方法
]

# 创建新的行列表，排除要删除的行
new_lines = []
current_line = 1

for i, line in enumerate(lines, 1):
    # 检查当前行是否在任何要删除的范围内
    in_remove_range = any(start <= i <= end for start, end in methods_to_remove)
    if not in_remove_range:
        new_lines.append(line)

# 写回文件
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"成功删除了{len(methods_to_remove)}个方法")
print(f"修改后的文件包含{len(new_lines)}行")
