#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final comprehensive fix for remaining Chinese text patterns in battery_chart_viewer.py
"""

import re
import os

def fix_final_chinese_patterns():
    """Fix final remaining Chinese text patterns"""
    
    python_file = "src/battery_analysis/main/battery_chart_viewer.py"
    
    # Read the file
    with open(python_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Define comprehensive replacement rules for final patterns
    replacements = {
        # Layout and sizing terms
        '# 初始化DefaultValue': '# Initialize default value',
        '# According toBatteryNumberAmountCreateNot同的按钮布局': '# Create different button layouts according to battery number amount',
        '# Create第一个按钮区域（Front32个Battery）- 宽Degree减半': '# Create first button area (first 32 batteries) - width halved',
        '# Create第二个按钮区域（剩余Battery ，最多32个）- 宽Degree减半，位置紧凑': '# Create second button area (remaining batteries, max 32) - width halved, compact position',
        '# Create单个按钮区域 - 宽Degree减半': '# Create single button area - width halved',
        '# Create空的第二个按钮区域（占位）- 宽Degree减半，位置紧凑': '# Create empty second button area (placeholder) - width halved, compact position',
        '# 添加占位文本': '# Add placeholder text',
        '# StoreOwnershipButton status引用': '# Store ownership button status reference',
        'logging.info("Successfully添加现代化BatteryChoose按钮")': 'logging.info("Successfully added modern battery choose button")',
        '"""CreateBatteryChoose现代化按钮"""': '"""Create modern battery choose button"""',
        '# Create modern button轴': '# Create modern button axis',
        '# ReadyBatteryInfo和Button status - 改为正序': '# Ready battery info and button status - changed to positive sequence',
        '# 按索引正序排Column（确保正序Show）': '# Arrange columns in positive sequence by index (ensure positive sequence display)',
        '# Calculate按钮布局Parameter - 适配 紧凑布局': '# Calculate button layout parameters - adapt to compact layout',
        '# StoreButton status引用': '# Store button status reference',
        
        # Technical terms with mixed languages
        'BatteryChoose': 'Battery Choose',
        'Button status': 'Button Status',
        'DefaultValue': 'Default Value',
        'BatteryNumberAmount': 'Battery Number Amount',
        '按钮布局': 'Button Layout',
        '按钮区域': 'Button Area',
        '宽Degree': 'Width',
        '位置紧凑': 'Compact Position',
        '占位文本': 'Placeholder Text',
        '现代化': 'Modern',
        '正序': 'Positive Sequence',
        '排Column': 'Arrange Columns',
        '布局Parameter': 'Layout Parameters',
        '紧凑布局': 'Compact Layout',
        
        # Common mixed patterns
        'Front32个Battery': 'First 32 Batteries',
        '剩余Battery': 'Remaining Batteries',
        '最多32个': 'Maximum 32',
        '单个按钮': 'Single Button',
        '空的第二个': 'Empty Second',
        '占位': 'Placeholder',
        'Ownership': 'Ownership',
        'status引用': 'Status Reference',
        '添加': 'Add',
        'Show': 'Show',
        'Ready': 'Ready',
        'Info和': 'Info and',
        '按索引': 'By Index',
        'Calculate': 'Calculate',
        
        # File and data terms
        'BatteryInfo': 'Battery Info',
        'data structure': 'Data Structure',
        'CSVRead器': 'CSV Reader',
        'ProcessData': 'Process Data',
        'current level': 'Current Level',
        'exception detection': 'Exception Detection',
        'invalid row': 'Invalid Row',
        'warning log': 'Warning Log',
        'original data': 'Original Data',
        
        # UI and dialog terms  
        'dialog title': 'Dialog Title',
        'ChooseData': 'Choose Data',
        '目录': 'Directory',
        'Main error info': 'Main Error Info',
        'Default为': 'Default is',
        'Cannot load or show battery data': 'Cannot Load or Show Battery Data',
        
        # Button and control terms
        'modern button': 'Modern Button',
        'modern button组': 'Modern Button Group',
        'Button configure': 'Button Configure',
        'callback': 'Callback',
        'Function': 'Function',
        'initial': 'Initial',
        'Status': 'Status',
        '文本': 'Text',
        'toggle': 'Toggle',
        'filter': 'Filter',
        'show/hide': 'Show/Hide',
        'specific': 'Specific',
        'curves': 'Curves',
        
        # Error and logging terms
        'error occurred': 'Error Occurred',
        'Execute': 'Execute',
        '切换': 'Toggle',
        'Successfully': 'Successfully',
        'when': 'When',
        'logging': 'Logging',
        'info': 'Info',
        'warning': 'Warning',
        'error': 'Error',
        
        # File operations
        'Search': 'Search',
        'Find': 'Find',
        'Load': 'Load',
        'Automated': 'Automated',
        'File': 'File',
        'Project root directory': 'Project Root Directory',
        'Be expected to': 'Expected',
        'Info_Image.csv': 'Info_Image.csv',
        
        # Visibility and state terms
        'visible': 'Visible',
        'visibility': 'Visibility',
        'lines': 'Lines',
        'any': 'Any',
        'check': 'Check',
        'setup': 'Setup',
        'switch': 'Switch',
        'mode': 'Mode',
        'unfilter': 'Unfilter',
        'not yet': 'Not Yet',
        
        # Numeric and indexing terms
        'first': 'First',
        'second': 'Second',
        '32个': '32',
        '最多': 'Maximum',
        '剩余': 'Remaining',
        '索引': 'Index',
        '正序': 'Positive Sequence',
        'amount': 'Amount',
        'number': 'Number',
        
        # Common Chinese characters that appear in mixed text
        '的': '',  # Remove possessive particle
        '并': 'and',
        '该': 'the',
        '如果': 'if',
        '能够': 'can',
        '这个': 'this',
        '在': 'in',
        '底部': 'bottom',
        '所有': 'all',
        '有': 'have',
        '任何': 'any',
        '是否': 'whether',
        '用于': 'for',
        '和': 'and',
        '或': 'or',
        '中': 'in',
        '到': 'to',
        '为': 'is',
        '将': 'will',
        '进行': 'perform',
        '跳过': 'skip',
        '记录': 'record',
        '存储': 'store',
        '分类': 'classify',
        '通过': 'by',
        '根据': 'according to',
        '创建': 'create',
        '添加': 'add',
        '设置': 'setup',
        '切换': 'toggle',
        '显示': 'display',
        '隐藏': 'hide',
        '选择': 'choose',
        '选择': 'select'
    }
    
    # Apply replacements
    changes_made = 0
    for chinese, english in replacements.items():
        if chinese in content:
            content = content.replace(chinese, english)
            changes_made += 1
    
    # Handle remaining mixed patterns with regex
    # Pattern: Chinese word + English word + Chinese word
    mixed_pattern1 = r'([一-龯]+)([A-Z][a-zA-Z]*)([一-龯]+)'
    content = re.sub(mixed_pattern1, lambda m: m.group(2), content)
    
    # Pattern: English word + Chinese word + English word  
    mixed_pattern2 = r'([a-zA-Z]+)([一-龯]+)([a-zA-Z]+)'
    content = re.sub(mixed_pattern2, lambda m: m.group(1) + m.group(3), content)
    
    # Pattern: Chinese characters at start/end of lines in comments
    comment_pattern = r'(#\s*)([一-龯\s]+)([A-Z][a-zA-Z\s]+)'
    content = re.sub(comment_pattern, lambda m: m.group(1) + m.group(3), content)
    
    # Write back if changes were made
    if content != original_content:
        with open(python_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {changes_made} final Chinese text patterns in {python_file}")
        return True
    
    return False

def check_remaining_chinese():
    """Check for any remaining Chinese text"""
    python_file = "src/battery_analysis/main/battery_chart_viewer.py"
    
    with open(python_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all lines with Chinese characters
    chinese_lines = []
    for i, line in enumerate(content.split('\n'), 1):
        if re.search(r'[一-龯]', line):
            chinese_lines.append((i, line.strip()))
    
    if chinese_lines:
        print(f"Found {len(chinese_lines)} lines with Chinese text:")
        for line_num, line in chinese_lines[:10]:  # Show first 10
            print(f"  Line {line_num}: {line}")
        if len(chinese_lines) > 10:
            print(f"  ... and {len(chinese_lines) - 10} more lines")
    else:
        print("No Chinese text found!")
    
    return len(chinese_lines)

if __name__ == "__main__":
    print("Running final Chinese text fix...")
    fixed = fix_final_chinese_patterns()
    
    if fixed:
        print("\nChecking for remaining Chinese text...")
        remaining = check_remaining_chinese()
        
        if remaining == 0:
            print("\n✅ All Chinese text has been successfully internationalized!")
        else:
            print(f"\n⚠️  {remaining} lines still contain Chinese text and need manual review.")
    else:
        print("No changes were made.")
        check_remaining_chinese()