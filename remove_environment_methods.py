#!/usr/bin/env python3
"""
This script removes environment-related methods from main_window.py
"""

file_path = r"c:\Users\boe\Desktop\battery-analysis\src\battery_analysis\main\main_window.py"

# Read the entire file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Define the methods to remove
methods_to_remove = [
    "def _initialize_environment_detector",
    "def _handle_environment_adaptation",
    "def _adapt_for_ide_environment",
    "def _adapt_for_container_environment",
    "def _adapt_for_production_environment",
    "def _handle_gui_unavailable"
]

# Remove each method
new_content = content
for method_name in methods_to_remove:
    # Find the start of the method
    start_pos = new_content.find(method_name)
    if start_pos == -1:
        print(f"Method {method_name} not found")
        continue
    
    # Find the end of the method (next method or end of file)
    next_method_pos = new_content.find("def ", start_pos + 1)
    if next_method_pos == -1:
        # It's the last method in the file
        end_pos = len(new_content)
    else:
        end_pos = next_method_pos
    
    # Remove the method
    new_content = new_content[:start_pos] + new_content[end_pos:]
    print(f"Removed method: {method_name}")

# Write the modified content back to file
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("All specified methods have been removed")
