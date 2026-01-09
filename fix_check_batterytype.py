#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复check_batterytype方法中的冗余代码
"""

import re

# 读取文件内容
file_path = 'src/battery_analysis/main/main_window.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 定义要替换的方法
old_method_pattern = r'def check_batterytype\(self\) -> None:\s+"""妫€鏌ョ數姹犵被鍨嬪苟鏇存柊鐩稿叧UI缁勪欢锛屽鎵樼粰ValidationManager"""\s+from battery_analysis.main.business_logic.validation_manager import ValidationManager\s+validation_manager = ValidationManager\(self\)\s+validation_manager.check_batterytype\(\)\s+if self.comboBox_BatteryType.currentText\(\) == "Coin Cell":[\s\S]+?pass\s+else:\s+self.checker_battery_type.set_error\([\s\S]+?\)'

new_method = '''    def check_batterytype(self) -> None:
        """妫€鏌ョ數姹犵被鍨嬪苟鏇存柊鐩稿叧UI缁勪欢锛屽鎵樼粰ValidationManager"""
        from battery_analysis.main.business_logic.validation_manager import ValidationManager
        validation_manager = ValidationManager(self)
        validation_manager.check_batterytype()'''

# 替换方法
new_content = re.sub(old_method_pattern, new_method, content, flags=re.DOTALL)

# 写入文件
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"已修复 {file_path} 中的 check_batterytype 方法")
