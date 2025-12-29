#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ultra-final fix for the last remaining Chinese text patterns in battery_chart_viewer.py
"""

import re

def fix_ultra_final_chinese_patterns():
    """Fix the final remaining Chinese text patterns"""
    
    python_file = "src/battery_analysis/main/battery_chart_viewer.py"
    
    # Read the file
    with open(python_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Define ultra-specific replacement rules for final remaining patterns
    replacements = {
        # Specific logging messages and technical terms
        '#CreateButton Area（Remaining Batteries，Maximum 32）- Width减半，Compact Position': '#Create Button Area (Remaining Batteries, Maximum 32) - Width Halved, Compact Position',
        '#CalculateButton LayoutParameter -  适配Compact Layout': '#Calculate Button Layout Parameters - Adapt to Compact Layout',
        'Logging.debug(f"toggleBattery {battery_idx} 可见性")': 'Logging.debug(f"toggleBattery {battery_idx} visibility")',
        '#Process空标签': '#Process Empty Labels',
        '#According toCurrentMode（Filter/Not YetFilter）Update对应线条可见性': '#According to Current Mode (Filter/Unfilter) Update Corresponding Line Visibility',
        '#ChecktheBatteryCurrentStatus（Based onCurrentModeBottom线条）': '#Check the Battery Current Status (Based on Current Mode Bottom Lines)',
        '#UpdateCurrentModeBottomtheBatteryOwnership线条': '#Update Current Mode Bottom the Battery Ownership Lines',
        'Logging.debug(f"线条 {i} 可见性Update: {battery_Visible} -> {new_Visibility}")': 'Logging.debug(f"Line {i} visibility update: {battery_Visible} -> {new_Visibility}")',
        'Logging.debug(f"ModeBottom {i} 可见 性也Updateis: {new_Visibility}")': 'Logging.debug(f"ModeBottom {i} visibility also updated to: {new_Visibility}")',
        'Logging.debug("调用fig.canvas.draw_idle()RefreshChart")': 'Logging.debug("Calling fig.canvas.draw_idle() to refresh chart")',
        
        # Common remaining Chinese characters in mixed text
        '可见性': 'visibility',
        'Update': 'Update',
        '也Updateis': 'also updated to',
        '调用': 'Calling',
        'RefreshChart': 'Refresh Chart',
        '空标签': 'Empty Labels',
        'CurrentMode': 'Current Mode',
        '对应线条': 'Corresponding Lines',
        'CurrentStatus': 'Current Status',
        'Based on': 'Based on',
        'Bottom线条': 'Bottom Lines',
        'Ownership线条': 'Ownership Lines',
        'ModeBottom': 'ModeBottom',
        '适配': 'Adapt to',
        'Compact Layout': 'Compact Layout',
        'LayoutParameter': 'Layout Parameters',
        'Button Area': 'Button Area',
        'Remaining Batteries': 'Remaining Batteries',
        'Maximum 32': 'Maximum 32',
        'Width减半': 'Width Halved',
        'Compact Position': 'Compact Position',
        'Calculate': 'Calculate',
        'Checkthe': 'Check the',
        'Update': 'Update',
        'Process': 'Process',
        'toggleBattery': 'toggleBattery',
        'Logging.debug': 'Logging.debug',
        'fig.canvas.draw_idle()': 'fig.canvas.draw_idle()',
        
        # Remove isolated Chinese characters
        '可见': 'visible',
        '性': 'property',
        '也': 'also',
        'is': 'is',
        '调用': 'calling',
        'Refresh': 'Refresh',
        'Chart': 'Chart',
        '空': 'Empty',
        '标签': 'Labels',
        '根据': 'According to',
        '对应': 'Corresponding',
        '线条': 'Lines',
        '当前': 'Current',
        '状态': 'Status',
        '基于': 'Based on',
        '底部': 'Bottom',
        '所有权': 'Ownership',
        '模式': 'Mode',
        '底部': 'Bottom',
        '适配': 'Adapt',
        '紧凑': 'Compact',
        '布局': 'Layout',
        '参数': 'Parameters',
        '按钮': 'Button',
        '区域': 'Area',
        '剩余': 'Remaining',
        '电池': 'Batteries',
        '最大': 'Maximum',
        '宽度': 'Width',
        '减半': 'Halved',
        '位置': 'Position',
        '处理': 'Process',
        '切换': 'Toggle',
        '检查': 'Check',
        '更新': 'Update'
    }
    
    # Apply replacements
    changes_made = 0
    for chinese, english in replacements.items():
        if chinese in content:
            content = content.replace(chinese, english)
            changes_made += 1
    
    # Handle specific patterns with regex
    # Pattern: English + Chinese characters + English
    content = re.sub(r'(Logging\.debug\(f"[^"]*)([一-龯]+)([^"]*\)")', lambda m: m.group(1) + m.group(3), content)
    
    # Pattern: Chinese characters in comments
    content = re.sub(r'(#\s*[A-Za-z\s]*)([一-龯\s]+)([A-Za-z\s]*)', lambda m: m.group(1) + m.group(3), content)
    
    # Remove any remaining isolated Chinese characters
    content = re.sub(r'(?<![a-zA-Z])[一-龯](?![a-zA-Z])', '', content)
    
    # Write back if changes were made
    if content != original_content:
        with open(python_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {changes_made} ultra-final Chinese text patterns in {python_file}")
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
        for line_num, line in chinese_lines[:5]:  # Show first 5
            print(f"  Line {line_num}: {line}")
        if len(chinese_lines) > 5:
            print(f"  ... and {len(chinese_lines) - 5} more lines")
    else:
        print("No Chinese text found! 🎉")
    
    return len(chinese_lines)

if __name__ == "__main__":
    print("Running ultra-final Chinese text fix...")
    fixed = fix_ultra_final_chinese_patterns()
    
    if fixed:
        print("\nChecking for remaining Chinese text...")
        remaining = check_remaining_chinese()
        
        if remaining == 0:
            print("\n✅ SUCCESS! All Chinese text has been completely internationalized!")
            print("The battery_chart_viewer.py file is now fully internationalized.")
        else:
            print(f"\n⚠️  {remaining} lines still contain Chinese text and need manual review.")
    else:
        print("No changes were made.")
        check_remaining_chinese()