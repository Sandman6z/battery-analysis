#!/usr/bin/env python3
"""
修复main_window.py中的缩进问题
"""

# 读取原始文件
with open(r'c:\Users\boe\Desktop\battery-analysis\src\battery_analysis\main\main_window.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 查找问题区域并修复
# 1. 找到init_widget方法的结束位置
init_widget_end = content.find('    def init_widget(self) -> None:')
if init_widget_end != -1:
    # 找到init_widget方法的结束
    method_end = content.find('    def ', init_widget_end + len('    def init_widget(self) -> None:'))
    if method_end != -1:
        # 提取init_widget方法
        init_widget_method = content[init_widget_end:method_end]
        # 查找错误的缩进部分
        problem_start = method_end
        # 查找下一个正确的方法定义或文件结束
        next_method = content.find('    def ', problem_start)
        if next_method != -1:
            problem_end = next_method
        else:
            problem_end = len(content)
        
        # 修复问题：重新添加_load_user_settings方法定义
        fixed_content = content[:method_end] + '\n    def _load_user_settings(self) -> None:\n        """加载用户配置文件中的设置"""\n        try:\n            user_config_path = os.path.join(os.path.dirname(\n                self.config_path), "user_settings.ini") if self.b_has_config else None\n' + content[problem_start:problem_end]
        else:
            fixed_content = content
    else:
        fixed_content = content
else:
    fixed_content = content

# 写回修复后的内容
with open(r'c:\Users\boe\Desktop\battery-analysis\src\battery_analysis\main\main_window.py', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("缩进问题已修复")
