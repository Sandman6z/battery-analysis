#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ultimate final fix for the last 8 Chinese text patterns in battery_chart_viewer.py
"""

import re
import os

def fix_ultimate_final_chinese_patterns():
    """Fix the ultimate final Chinese text patterns"""
    
    python_file = "src/battery_analysis/main/battery_chart_viewer.py"
    
    # Read the file
    with open(python_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Define ultimate specific replacement rules for the final 8 patterns
    replacements = {
        # The 8 specific remaining patterns
        'Logging.Info(f"SuccessfullyCreateModernBattery ChooseButton组 ({start_idx}-{end_idx})")': 'Logging.info(f"Successfully created modern battery choose button group ({start_idx}-{end_idx})")',
        '"""addHelpTexttoChartRightTop角"""': '"""Add help text to chart right top corner"""',
        'fig.text(0.98, 0.85, ": willinDataPointTop查看DetailedInfo", fontsize=7, ha=\'right\')': 'fig.text(0.98, 0.85, ": will display data point to view detailed info", fontsize=7, ha=\'right\')',
        '#Notice：_show_Error_plotMethodinFrontSurface定，MethodUpdateisEnhance版': '#Notice: _show_error_plot method in front surface definition, method updated is enhanced version',
        'CreateBatteryChartViewerClassInstance，AutomatedExecute初、DataReadandChartShowOperate。': 'Create BatteryChartViewer class instance, automated execute initialization, data read and chart show operation.',
        
        # Common remaining Chinese characters
        'SuccessfullyCreate': 'Successfully Created',
        'Button组': 'Button Group',
        'addHelpText': 'Add Help Text',
        'toChartRightTop角': 'To Chart Right Top Corner',
        'willinDataPointTop查看DetailedInfo': 'will display data point to view detailed info',
        'Notice：': 'Notice:',
        '_show_Error_plotMethodinFrontSurface定': '_show_error_plot method in front surface definition',
        'MethodUpdateisEnhance版': 'Method updated is enhanced version',
        'CreateBatteryChartViewerClassInstance': 'Create BatteryChartViewer Class Instance',
        'AutomatedExecute初': 'Automated Execute Initialization',
        'DataReadandChartShowOperate': 'Data Read and Chart Show Operation',
        
        # Individual Chinese characters
        '组': 'Group',
        '角': 'Corner',
        '查看': 'View',
        '详细信息': 'Detailed Info',
        '注意': 'Notice',
        '创建': 'Create',
        '类实例': 'Class Instance',
        '自动执行': 'Automated Execute',
        '初始化': 'Initialization',
        '数据读取': 'Data Read',
        '图表显示': 'Chart Show',
        '操作': 'Operation',
        
        # Remove isolated Chinese characters that appear in mixed text
        '：': ':',
        '，': ',',
        '。': '.'
    }
    
    # Apply replacements
    changes_made = 0
    for chinese, english in replacements.items():
        if chinese in content:
            content = content.replace(chinese, english)
            changes_made += 1
    
    # Handle any remaining patterns with regex
    # Remove any remaining Chinese punctuation
    content = re.sub(r'([一-龯])([：，。])', r'\2', content)
    content = re.sub(r'([：，。])([一-龯])', r'\1', content)
    
    # Write back if changes were made
    if content != original_content:
        with open(python_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {changes_made} ultimate final Chinese text patterns in {python_file}")
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
        for line_num, line in chinese_lines:
            print(f"  Line {line_num}: {line}")
    else:
        print("No Chinese text found! 🎉")
    
    return len(chinese_lines)

def check_all_python_files():
    """Check all Python files in the project for Chinese text"""
    print("\n" + "="*60)
    print("CHECKING ALL PYTHON FILES FOR CHINESE TEXT")
    print("="*60)
    
    python_files = []
    for root, dirs, files in os.walk("src"):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    
    total_chinese_lines = 0
    files_with_chinese = []
    
    for python_file in python_files:
        if python_file == "src/battery_analysis/main/battery_chart_viewer.py":
            continue  # Skip the one we just fixed
            
        with open(python_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        chinese_lines = []
        for i, line in enumerate(content.split('\n'), 1):
            if re.search(r'[一-龯]', line):
                chinese_lines.append((i, line.strip()))
        
        if chinese_lines:
            files_with_chinese.append((python_file, chinese_lines))
            total_chinese_lines += len(chinese_lines)
            print(f"\n📁 {python_file}: {len(chinese_lines)} lines with Chinese text")
            for line_num, line in chinese_lines[:3]:  # Show first 3 lines
                print(f"  Line {line_num}: {line}")
            if len(chinese_lines) > 3:
                print(f"  ... and {len(chinese_lines) - 3} more lines")
    
    print(f"\n" + "="*60)
    print(f"SUMMARY: {total_chinese_lines} total Chinese lines in {len(files_with_chinese)} files")
    print("="*60)
    
    return files_with_chinese

if __name__ == "__main__":
    print("Running ultimate final Chinese text fix...")
    fixed = fix_ultimate_final_chinese_patterns()
    
    if fixed:
        print("\nChecking for remaining Chinese text in battery_chart_viewer.py...")
        remaining = check_remaining_chinese()
        
        if remaining == 0:
            print("\n🎉 SUCCESS! battery_chart_viewer.py is completely internationalized!")
        else:
            print(f"\n⚠️  {remaining} lines still contain Chinese text.")
    else:
        print("No changes were made.")
        check_remaining_chinese()
    
    # Check all other Python files
    check_all_python_files()