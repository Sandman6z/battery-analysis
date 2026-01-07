#!/usr/bin/env python3
"""
This script removes the get_threadinfo method from main_window.py
"""

import os

file_path = r"c:\Users\boe\Desktop\battery-analysis\src\battery_analysis\main\main_window.py"

# Read the file content
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the start and end of get_threadinfo method
start_line = None
end_line = None

for i, line in enumerate(lines):
    if 'def get_threadinfo(' in line:
        start_line = i
    elif start_line is not None and line.strip() and not line.startswith('    ') and 'def ' in line:
        end_line = i - 1
        break

# If we found the method, remove it
if start_line is not None:
    if end_line is None:
        # If it's the last method in the file
        end_line = len(lines) - 1
    
    print(f"Removing get_threadinfo method from lines {start_line + 1} to {end_line + 1}")
    
    # Remove the method
    new_lines = lines[:start_line] + lines[end_line + 1:]
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("Successfully removed get_threadinfo method")
else:
    print("get_threadinfo method not found")
