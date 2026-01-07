#!/usr/bin/env python3
"""
This script fixes the environment initialization order in main_window.py
"""

file_path = r"c:\Users\boe\Desktop\battery-analysis\src\battery_analysis\main\main_window.py"

# Read the entire file
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the lines to remove
remove_start = None
remove_end = None
for i, line in enumerate(lines):
    if "# 初始化环境适配器" in line:
        remove_start = i
    elif remove_start is not None and "# 初始化语言管理器" in line:
        remove_end = i
        break

# Remove the problematic lines
if remove_start is not None and remove_end is not None:
    del lines[remove_start:remove_end]

# Find where to insert the environment adapter initialization (after env_info is initialized)
insert_pos = None
for i, line in enumerate(lines):
    if "# 环境适配处理 - 使用环境适配器" in line:
        insert_pos = i
        break

# Insert the environment adapter initialization after env_info is initialized
if insert_pos is not None:
    adapter_lines = [
        "        # 初始化环境适配器（在env_info初始化之后）\n",
        "        from battery_analysis.main.environment_adapter import EnvironmentAdapter\n",
        "        self.environment_adapter = EnvironmentAdapter(self)\n",
        "        # 使用环境适配器初始化环境检测器\n",
        "        self.env_detector = self.environment_adapter.initialize_environment_detector()\n",
        "\n"
    ]
    # Insert the lines before the environment adaptation line
    lines.insert(insert_pos, "".join(adapter_lines))

# Write the fixed content back to file
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Fixed environment initialization order")
