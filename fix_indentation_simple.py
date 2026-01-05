#!/usr/bin/env python3
"""
修复main_window.py中的缩进问题
"""

# 读取原始文件
with open(r'c:\Users\boe\Desktop\battery-analysis\src\battery_analysis\main\main_window.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 查找init_widget方法
init_widget_start = None
for i, line in enumerate(lines):
    if 'def init_widget(self) -> None:' in line:
        init_widget_start = i
        break

if init_widget_start is not None:
    # 查找init_widget方法的结束
    init_widget_end = None
    for i in range(init_widget_start + 1, len(lines)):
        if lines[i].startswith('    def '):
            init_widget_end = i
            break
    
    if init_widget_end is not None:
        # 查找问题区域
        problem_start = init_widget_end
        problem_end = None
        for i in range(problem_start, len(lines)):
            if lines[i].startswith('    def '):
                problem_end = i
                break
        
        if problem_end is None:
            problem_end = len(lines)
        
        # 创建修复后的行列表
        new_lines = []
        
        # 添加init_widget之前的行
        new_lines.extend(lines[:init_widget_end])
        
        # 添加修复的_load_user_settings方法
        new_lines.append('    def _load_user_settings(self) -> None:\n')
        new_lines.append('        """加载用户配置文件中的设置"""\n')
        new_lines.append('        try:\n')
        new_lines.append('            user_config_path = os.path.join(os.path.dirname(\n')
        new_lines.append('                self.config_path), "user_settings.ini") if self.b_has_config else None\n')
        
        # 修复缩进并添加问题区域的行
        for line in lines[problem_start:problem_end]:
            # 修复缩进：将4个空格缩进增加到8个空格
            if line.startswith('            '):
                new_lines.append('        ' + line.lstrip())
            else:
                new_lines.append('        ' + line)
        
        # 添加剩余的行
        new_lines.extend(lines[problem_end:])
        
        # 写回修复后的内容
        with open(r'c:\Users\boe\Desktop\battery-analysis\src\battery_analysis\main\main_window.py', 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        print("缩进问题已修复")
    else:
        print("未找到init_widget方法的结束位置")
else:
    print("未找到init_widget方法")
