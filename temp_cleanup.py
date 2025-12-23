# 临时清理脚本，用于删除旧的版本信息生成代码
import os

file_path = r'c:\Users\boe\Desktop\battery-analysis\scripts\build.py'

# 读取文件内容
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 删除第192-241行的旧代码
new_lines = lines[:191] + lines[242:]

# 写入新内容
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('旧代码删除完成！')