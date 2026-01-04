#!/usr/bin/env python3
"""
移除UI文件中的内联样式脚本

该脚本用于批量移除Qt UI文件中的styleSheet属性，统一使用外部QSS样式文件。
"""

import re
import sys
import os

def remove_inline_styles(file_path):
    """
    移除UI文件中的内联样式
    
    Args:
        file_path: UI文件路径
    """
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 使用正则表达式匹配并移除styleSheet属性
        # 匹配格式：<property name="styleSheet">...</property>
        pattern = r'\s*<property name="styleSheet">[^<]*<string[^<]*>.*?</string>[^<]*</property>\s*'
        new_content = re.sub(pattern, '', content, flags=re.DOTALL)
        
        # 写入修改后的内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✓ 成功移除 {file_path} 中的内联样式")
        return True
    except Exception as e:
        print(f"✗ 处理 {file_path} 时出错: {str(e)}")
        return False

def main():
    """
    主函数
    """
    if len(sys.argv) != 2:
        print("用法: python remove_inline_styles.py <ui_file_path>")
        sys.exit(1)
    
    ui_file = sys.argv[1]
    
    if not os.path.exists(ui_file):
        print(f"✗ 文件不存在: {ui_file}")
        sys.exit(1)
    
    if not ui_file.endswith('.ui'):
        print(f"✗ 不是UI文件: {ui_file}")
        sys.exit(1)
    
    success = remove_inline_styles(ui_file)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()