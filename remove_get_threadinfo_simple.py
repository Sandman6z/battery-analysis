#!/usr/bin/env python3
"""
Simple script to remove get_threadinfo method from main_window.py
"""

file_path = r"c:\Users\boe\Desktop\battery-analysis\src\battery_analysis\main\main_window.py"

# Read the entire file with readlines to get a list of lines
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the indices of get_threadinfo method
start_idx = None
end_idx = None

for i, line in enumerate(lines):
    if line.strip() == 'def get_threadinfo(self, threadstate, stateindex, threadinfo) -> None:':
        start_idx = i
    elif start_idx is not None and end_idx is None:
        # Check for next method definition (starts with 'def ' and proper indentation)
        if line.strip().startswith('def ') and line.startswith('    def '):
            end_idx = i - 1
            break

# Handle case where it's the last method in the file
if start_idx is not None and end_idx is None:
    end_idx = len(lines) - 1

# If we found the method, remove it
if start_idx is not None and end_idx is not None:
    print(f"Removing get_threadinfo method from lines {start_idx+1} to {end_idx+1}")
    
    # Create new lines list without the method
    new_lines = lines[:start_idx] + lines[end_idx+1:]
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("Successfully removed get_threadinfo method!")
else:
    print("get_threadinfo method not found or could not determine its boundaries.")
