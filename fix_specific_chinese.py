#!/usr/bin/env python3
"""
Targeted script to fix specific Chinese text patterns remaining in battery_chart_viewer.py
"""

import os
import re

def fix_specific_chinese_patterns():
    """Fix specific Chinese text patterns remaining in battery_chart_viewer.py"""
    
    python_file = "src/battery_analysis/main/battery_chart_viewer.py"
    
    # Read the file
    with open(python_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Define targeted replacement rules for specific patterns
    replacements = {
        # CSV processing - split into parts
        '从CSVRead器middleProcessData并填充到data structuremiddle。': 'Process data from CSV reader middle and fill into data structure middle.',
        'Classify data in CSV by battery and current level，': 'Classify data in CSV by battery and current level,',
        'Store original data。': 'Store original data.',
        'Perform exception detection during processing，Skip invalid row，并Record warning log。': 'Perform exception detection during processing, skip invalid row, and record warning log.',
        
        # File search - split into parts
        '这个MethodBe able toSearch in project root directory bottomOwnershipBe expected to的Info_Image.csvFile，': 'This method can search for expected Info_Image.csv file in project root directory bottom,',
        '如果Find，Be able toAutomatedLoad该File。': 'If found, can automatically load the file.',
        
        # Error dialog parameters
        'Main error info，Default为"Cannot load or show battery data"': 'Main error info, default is "Cannot load or show battery data"',
        
        # File dialog title
        '"ChooseData目录",  # dialog title': '"Choose Data Directory",  # dialog title',
        
        # Button status
        '# 切换Button status': '# Toggle button status',
        
        # Button configuration
        "buttons_config: Button configure list [{'text': '文本', 'callback': Function, 'initial': Status}]": "buttons_config: Button configure list [{'text': 'text', 'callback': function, 'initial': status}]",
        
        # Create modern button group
        '# Create modern button组': '# Create modern button group',
        
        # Filter mode operations
        '# Check该Battery是否有任何可见的线条': '# Check if this battery has any visible lines',
        '# Setup该BatteryOwnershipcurrent level的Filter线条可见性': '# Setup this battery ownership current level filter line visibility',
        '# 切换到not yetFilterMode': '# Switch to unfilter mode',
        '# Check该Battery是否有任何可见的线条': '# Check if this battery has any visible lines',
        '# Setup该BatteryOwnershipcurrent level的原始线条可见性': '# Setup this battery ownership current level original line visibility',
        
        # Filter toggle error
        'logging.error("ExecuteFilter切换whenerror occurred: %s", e)': 'logging.error("Execute filter toggle when error occurred: %s", e)',
        
        # Create filter button
        '# Create现代化Filter按钮': '# Create modern filter button',
        
        # Save button status
        '# SaveButton status引用': '# Save button status reference',
        
        # Filter button success/error
        'logging.info("Successfully添加现代化Filter按钮")': 'logging.info("Successfully added modern filter button")',
        'logging.error("CreateFilter按钮whenerror occurred: %s", e)': 'logging.error("Create filter button when error occurred: %s", e)',
        
        # Battery selection button
        '"""添加BatteryChoose现代化按钮，用于Show/Hide特定Battery的Data曲线"""': '"""Add battery choose modern button for show/hide specific battery data curves"""',
        
        # More filter operations
        '# Check该Battery是否有任何可见的线条': '# Check if this battery has any visible lines',
        '# Setup该BatteryOwnershipcurrent level的Filter线条可见性': '# Setup this battery ownership current level filter line visibility',
        '# 切换到not yetFilterMode': '# Switch to unfilter mode',
        '# Check该Battery是否有任何可见的线条': '# Check if this battery has any visible lines',
        '# Setup该BatteryOwnershipcurrent level的原始线条可见性': '# Setup this battery ownership current level original line visibility',
        'logging.error("ExecuteFilter切换whenerror occurred: %s", e)': 'logging.error("Execute filter toggle when error occurred: %s", e)',
        '# Create现代化Filter按钮': '# Create modern filter button',
        '# SaveButton status引用': '# Save button status reference',
        'logging.info("Successfully添加现代化Filter按钮")': 'logging.info("Successfully added modern filter button")',
        'logging.error("CreateFilter按钮whenerror occurred: %s", e)': 'logging.error("Create filter button when error occurred: %s", e)',
        
        # Channel selection
        '"""添加ChannelChoose现代化按钮，用于Show/Hide特定Channel的Data曲线"""': '"""Add channel choose modern button for show/hide specific channel data curves"""',
        
        # Channel operations
        '# Check该Channel是否有任何可见的线条': '# Check if this channel has any visible lines',
        '# Setup该ChannelOwnershipcurrent level的Filter线条可见性': '# Setup this channel ownership current level filter line visibility',
        '# 切换到not yetFilterMode': '# Switch to unfilter mode',
        '# Check该Channel是否有任何可见的线条': '# Check if this channel has any visible lines',
        '# Setup该ChannelOwnershipcurrent level的原始线条可见性': '# Setup this channel ownership current level original line visibility',
        'logging.error("ExecuteChannelFilter切换whenerror occurred: %s", e)': 'logging.error("Execute channel filter toggle when error occurred: %s", e)',
        '# Create现代化ChannelFilter按钮': '# Create modern channel filter button',
        '# SaveChannelButton status引用': '# Save channel button status reference',
        'logging.info("Successfully添加现代化ChannelFilter按钮")': 'logging.info("Successfully added modern channel filter button")',
        'logging.error("CreateChannelFilter按钮whenerror occurred: %s", e)': 'logging.error("Create channel filter button when error occurred: %s", e)',
        
        # Chart interaction
        '"""添加Chart交互按钮，用于Show/HideChart元素"""': '"""Add chart interaction buttons for show/hide chart elements"""',
        
        # Chart element operations
        '# Check该ChartElement是否有任何可见的线条': '# Check if this chart element has any visible lines',
        '# Setup该ChartElement的可见性': '# Setup this chart element visibility',
        'logging.error("ExecuteChartElement切换whenerror occurred: %s", e)': 'logging.error("Execute chart element toggle when error occurred: %s", e)',
        '# Create现代化ChartElement按钮': '# Create modern chart element button',
        'logging.info("Successfully添加现代化ChartElement按钮")': 'logging.info("Successfully added modern chart element button")',
        'logging.error("CreateChartElement按钮whenerror occurred: %s", e)': 'logging.error("Create chart element button when error occurred: %s", e)',
        
        # Mouse event handling
        '"""Setup鼠标EventProcess，Support悬停ShowDetailedInfo"""': '"""Setup mouse event handling, support hover to show detailed info"""',
        
        # Mouse motion
        '"""鼠标MoveEventProcess"""': '"""Mouse move event handling"""',
        '# Check鼠标是否在有效的DataScopeInside': '# Check if mouse is in valid data scope inside',
        '# 只在有Data的ScopeInsideProcess': '# Only process within data scope',
        
        # Find nearest point
        '# 在OwnershipDataMiddleFind最Close的Point': '# Find closest point in ownership data',
        '# 如果FindClose的Point': '# If find close point',
        
        # Update annotation
        '# UpdateAnnotationPosition和Content': '# Update annotation position and content',
        '# HideAnnotation如果Not在DataScopeInside': '# Hide annotation if not in data scope',
        
        # Mouse leave
        '"""鼠标LeaveEventProcess"""': '"""Mouse leave event handling"""',
        
        # Find closest point function
        '"""在OwnershipDataMiddleFind最Close的Point"""': '"""Find closest point in ownership data"""',
        
        # Distance calculation
        '# Calculate欧几里得Distance': '# Calculate Euclidean distance',
        
        # Setup annotation
        '"""Setup悬停Annotation，用于ShowDetailedInfo"""': '"""Setup hover annotation for show detailed info"""',
        
        # Annotation style
        '# SetupAnnotationStyle': '# Setup annotation style',
        '# 初始HideAnnotation': '# Initially hide annotation',
        
        # Update annotation function
        '"""UpdateAnnotationPosition和Content"""': '"""Update annotation position and content"""',
        
        # Annotation content
        '# ConstructAnnotationContent': '# Construct annotation content',
        '# 如果Point击在ButtonScopeInside，SkipAnnotationUpdate': '# If click is in button scope inside, skip annotation update',
        
        # Chart cleanup
        '"""CleanChartRelatedResource"""': '"""Clean chart related resources"""',
        
        # Cleanup operations
        '# CleanButtonEvent绑定': '# Clean button event binding',
        '# CleanAnnotation': '# Clean annotation',
        '# CleanChartInstance': '# Clean chart instance',
        
        # Main chart function
        '"""Main ChartFunction，集成Ownership有的ChartCreate和ShowLogic"""': '"""Main chart function, integrate all chart creation and show logic"""',
        
        # Show chart steps
        '# 1. CleanExistingChart': '# 1. Clean existing chart',
        '# 2. CreateNewChart': '# 2. Create new chart',
        '# 3. SetupChartLayout': '# 3. Setup chart layout',
        '# 4. PlotData曲线': '# 4. Plot data curves',
        '# 5. AddInteractiveElement': '# 5. Add interactive elements',
        '# 6. ShowChart窗口': '# 6. Show chart window',
        
        # Chart cleanup
        '# CleanExistingChart（如果存在）': '# Clean existing chart (if exists)',
        
        # Chart creation
        '# CreateNewChartInstance': '# Create new chart instance',
        
        # Chart layout
        '# SetupChartLayout和Style': '# Setup chart layout and style',
        
        # Data plotting
        '# PlotOwnershipData曲线': '# Plot ownership data curves',
        
        # Interactive elements
        '# AddInteractive按钮和Control': '# Add interactive buttons and controls',
        
        # Chart display
        '# ShowChart到Screen': '# Show chart to screen',
        
        # Chart show error
        'logging.error("ShowChartFailed: %s", str(e))': 'logging.error("Show chart failed: %s", str(e))',
        
        # Error handling
        '"""HandleChartShowError，提供FallbackScheme"""': '"""Handle chart show error, provide fallback scheme"""',
        
        # Fallback operations
        '# TryShowSimpleErrorChart': '# Try show simple error chart',
        '# 如果EvenSimpleChartCannotShow': '# If even simple chart cannot show',
        'logging.error("CannotShowEvenSimpleErrorChart: %s", str(e))': 'logging.error("Cannot show even simple error chart: %s", str(e))',
        
        # Final fallback
        '# FinalFallback: Use文本Output': '# Final fallback: use text output',
        'print(f"严重Error: CannotShowChart. ErrorDetails: {str(e)}"))': 'print(f"Critical error: Cannot show chart. Error details: {str(e)}"))',
        'print("请CheckLogGetMoreDetails")': 'print("Please check log for more details")',
        
        # Chart error cleanup
        '"""CleanChartErrorStatus，EnsureApplicationCanContinueRun"""': '"""Clean chart error status, ensure application can continue run"""',
        
        # Error cleanup operations
        '# ResetChartStatus': '# Reset chart status',
        '# CleanErrorResource': '# Clean error resources',
        
        # Data loading
        '"""LoadDataFile，SupportMultipleLoadMode"""': '"""Load data file, support multiple load modes"""',
        
        # Load modes
        'strLoadMode="Auto"': 'str_load_mode="Auto"',
        
        # Auto load
        '# AutoLoadMode: SearchDefaultFile': '# Auto load mode: search default file',
        
        # Manual load
        '# ManualLoadMode: UseFileDialog': '# Manual load mode: use file dialog',
        
        # Direct load
        '# DirectLoadMode: UseSpecifiedFile': '# Direct load mode: use specified file',
        
        # Load result handling
        '# HandleLoadResult': '# Handle load result',
        
        # Success
        'logging.info("SuccessfullyLoadDataFile: %s", self.strInfoImageCsvPath)': 'logging.info("Successfully load data file: %s", self.strInfoImageCsvPath)',
        
        # Failure
        'logging.error("FailedToLoadDataFile: %s", str(e))': 'logging.error("Failed to load data file: %s", str(e))',
        
        # Show error
        'self.show_error_chart("DataLoadError", "CannotLoadDataFile", str(e))': 'self.show_error_chart("DataLoadError", "CannotLoadDataFile", str(e))',
        
        # Data reload
        '"""重新LoadDataFile，TypicallyUseAfterFileChange"""': '"""Reload data file, typically use after file change"""',
        
        # Clean before reload
        '# CleanExistingDataBeforeReload': '# Clean existing data before reload',
        
        # Reload operation
        '# ExecuteDataReload': '# Execute data reload',
        
        # Reload result
        '# HandleReloadResult': '# Handle reload result'
    }
    
    # Apply replacements
    changes_made = 0
    for chinese, english in replacements.items():
        if chinese in content:
            content = content.replace(chinese, english)
            changes_made += 1
    
    # Write back if changes were made
    if content != original_content:
        with open(python_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {changes_made} specific Chinese text patterns in {python_file}")
        return True
    
    return False

if __name__ == "__main__":
    fix_specific_chinese_patterns()