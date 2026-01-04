#!/usr/bin/env python3
"""
修复项目中所有文件的 logging f-string 问题
将 f"...{var}..." 格式转换为 "...%s...", var 格式
"""

import os
import re
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 匹配 logging 相关的 f-string 模式
LOGGING_PATTERNS = [
    r'(logging|logger|root|self\.logger)\.(info|debug|warning|error|critical|exception)\s*\(\s*f"([^"]*)"\s*\)',
    r'(logging|logger|root|self\.logger)\.(info|debug|warning|error|critical|exception)\s*\(\s*f\'([^\']*)\'\s*\)'
]

# 匹配 f-string 中的占位符 {var} 或 {var:format}
FSTRING_PLACEHOLDER = r'\{(\w+)(?::[^}]*)?\}'


def fix_logging_fstrings(file_path):
    """修复单个文件中的 logging f-string 问题"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = 0
        
        for pattern in LOGGING_PATTERNS:
            matches = list(re.finditer(pattern, content, re.MULTILINE))
            for match in reversed(matches):
                full_match = match.group(0)
                logger_obj = match.group(1)
                log_level = match.group(2)
                fstring_content = match.group(3) if match.group(3) else match.group(6)
                
                # 提取所有占位符
                placeholders = re.findall(FSTRING_PLACEHOLDER, fstring_content)
                if not placeholders:
                    continue
                
                # 替换 f-string 为 % 格式化
                new_format = fstring_content
                for placeholder in placeholders:
                    new_format = new_format.replace(f"{{{placeholder}}}", f"%s")
                    new_format = re.sub(r"\{" + re.escape(placeholder) + r":[^}]*\}", "%s", new_format)
                
                # 构建新的 logging 语句
                new_log_statement = f"{logger_obj}.{log_level}(\"{new_format}\", {', '.join(placeholders)})"
                
                # 替换原内容
                content = content[:match.start()] + new_log_statement + content[match.end():]
                changes_made += 1
        
        if changes_made > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logging.info("已修复 %s 中的 %s 处 logging f-string 问题", file_path, changes_made)
        
        return changes_made
    except Exception as e:
        logging.error("处理文件 %s 时出错: %s", file_path, e)
        return 0


def main():
    """主函数，遍历所有 Python 文件"""
    logging.info("开始修复项目中的 logging f-string 问题...")
    
    total_changes = 0
    total_files = 0
    
    # 遍历当前目录下所有 .py 文件
    for root, dirs, files in os.walk('.'):
        # 跳过 .git 目录
        if '.git' in root:
            continue
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                total_files += 1
                total_changes += fix_logging_fstrings(file_path)
    
    logging.info("修复完成！共检查 %s 个文件，修复 %s 处 logging f-string 问题", total_files, total_changes)


if __name__ == "__main__":
    main()