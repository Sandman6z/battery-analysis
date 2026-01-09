#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复get_version方法中的冗余代码
"""

# 读取文件内容
file_path = 'src/battery_analysis/main/main_window.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到get_version方法的开始和结束位置
start_index = None
end_index = None
method_found = False

for i, line in enumerate(lines):
    if 'def get_version(self) -> None:' in line:
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
        '    def get_version(self) -> None:\n',
        '        """计算并设置电池分析的版本号，委托给VersionManager"""\n',
        '        from battery_analysis.main.business_logic.version_manager import VersionManager\n',
        '        version_manager = VersionManager(self)\n',
        '        version_manager.get_version()\n'
    ]
    
    # 替换旧方法
    lines[start_index:end_index+1] = new_method
    
    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"已修复 {file_path} 中的 get_version 方法")
else:
    print(f"未找到 get_version 方法")
