#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复日志中的f-string格式，替换为lazy % formatting

将 logger.info("text %s", var) 替换为 logger.info("text %s", var)
"""

import re
import os
import glob


def fix_logging_fstrings(file_path):
    """修复单个文件中的日志f-string格式"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 正则表达式匹配日志f-string格式 - 最终版本，支持更多情况
    # 匹配 logger.info("text %s text %s", var1, var2) 格式
    # 匹配 logging.info("text %s text %s", var1, var2) 格式
    # 支持多种日志记录器：logger, root, self.logger, logging等
    # 支持多种日志级别：info, warning, error, debug, critical等
    pattern = r'((?:logger|root|self\.logger|\w+\.logger|logging)\.\w+\()f"([^"}]*(?:\{[^}]+\}[^"}]*)*)"\)'
    
    def replace_fstring(match):
        prefix = match.group(1)  # 例如: logging.info(
        f_content = match.group(2)  # 例如: text {var1} text {var2}
        
        # 提取所有变量
        vars_pattern = r'\{([^}]+)\}'
        vars_list = re.findall(vars_pattern, f_content)
        
        # 构建新的格式化字符串
        formatted_content = re.sub(vars_pattern, '%s', f_content)
        
        # 构建新的日志语句
        if vars_list:
            vars_str = ', '.join(vars_list)
            new_log = f'{prefix}"{formatted_content}", {vars_str})'
        else:
            # 没有变量的情况，直接去掉f前缀
            new_log = f'{prefix}"{formatted_content}")'
        
        return new_log
    
    # 替换所有匹配项
    new_content = re.sub(pattern, replace_fstring, content)
    
    # 只在内容有变化时写入文件
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False


def main():
    """主函数，处理所有Python文件"""
    # 获取所有Python文件
    python_files = []
    patterns = [
        "src/**/*.py",
        "scripts/**/*.py",
        "tests/**/*.py"
    ]
    
    for pattern in patterns:
        python_files.extend(glob.glob(pattern, recursive=True))
    
    print(f"找到 {len(python_files)} 个Python文件")
    
    # 修复每个文件
    fixed_count = 0
    for file_path in python_files:
        if fix_logging_fstrings(file_path):
            print(f"已修复: {file_path}")
            fixed_count += 1
    
    print(f"\n修复完成！共修复了 {fixed_count} 个文件中的日志f-string格式")


if __name__ == "__main__":
    main()
