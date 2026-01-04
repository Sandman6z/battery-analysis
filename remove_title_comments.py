#!/usr/bin/env python3
"""
移除refactoring.md文件中问题类型标题后的中文注释
"""

import re

def main():
    # 读取文件内容
    with open('refactoring.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 定义正则表达式匹配问题类型标题及其后的注释
    pattern = r'(## 问题类型: \w[-\w]+)  # .*'
    
    # 替换为只保留标题
    def replace_func(match):
        return match.group(1)
    
    new_content = re.sub(pattern, replace_func, content)
    
    # 写回文件
    with open('refactoring.md', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("已成功移除问题类型标题后的中文注释")

if __name__ == "__main__":
    main()
