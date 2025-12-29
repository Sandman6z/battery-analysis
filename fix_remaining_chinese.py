#!/usr/bin/env python3
"""
Final comprehensive script to fix all remaining hardcoded Chinese text
"""

import os
import re

def fix_all_remaining_chinese():
    """Fix all remaining Chinese text in battery_chart_viewer.py"""
    
    python_file = "src/battery_analysis/main/battery_chart_viewer.py"
    
    # Read the file
    with open(python_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Define comprehensive replacement rules for ALL remaining Chinese text
    replacements = {
        # CSV processing remaining issues
        '从CSVRead器middleProcessData并填充到data structuremiddle。Classify data in CSV by battery and current level，Store original data。Perform exception detection during processing，Skip invalid row，并Record warning log。': 'Process data from CSV reader middle and fill into data structure middle. Classify data in CSV by battery and current level, store original data. Perform exception detection during processing, skip invalid row, and record warning log.',
        
        # File search remaining issues  
        '这个MethodBe able toSearch in project root directory bottomOwnershipBe expected to的Info_Image.csvFile，如果Find，Be able toAutomatedLoad该File。': 'This method can search for expected Info_Image.csv file in project root directory bottom, if found, can automatically load the file.',
        'StartSearch项目middle的Info_Image.csvFile...': 'Start searching for Info_Image.csv file in project middle...',
        '在项目根目录BottomSearch': 'Search in project root directory bottom',
        'SkipHide目录和venv目录': 'Skip hide directories and venv directories',
        '在项目middleFindInfo_Image.csvFile': 'Find Info_Image.csv file in project middle',
        'SuccessfullyLoadFind的DataFile': 'Successfully load found data file',
        'FindDataFile但LoadFailed': 'Find data file but load failed',
        '在项目middlenot yetFind任何有效的Info_Image.csvFile': 'Not yet find any valid Info_Image.csv file in project middle',
        'SetupDataPath并尝试Load': 'Setup data path and try to load',
        
        # Error dialog remaining issues
        'ErrorTitle，Default为"DataError"': 'Error title, default is "DataError"',
        '主要ErrorInfo，Default为"Cannot load or show battery data"': 'Main error info, default is "Cannot load or show battery data"',
        'DetailedErrorInfo和故障排除Suggestion': 'Detailed error info and troubleshooting suggestions',
        'csvFile是否存在且Formatcorrect': 'csv file exists and format correct',
        'ConfigureFile是否correctChoose': 'configure file is correctly chosen',
        'FilePath是否containsmiddle文字符or特殊字符': 'file path contains middle text characters or special characters',
        'csvFile是否contains有效的BatteryTestData': 'csv file contains valid battery test data',
        'Hide坐标轴': 'Hide coordinate axes',
        'ConstructComplete的ErrorInfo文本': 'Construct complete error info text',
        'ShowErrorLogInfo（如果有）': 'Show error log info (if any)',
        'Error详情': 'Error details',
        '添加版本Info和whenBetween戳': 'Add version info and timestamp',
        '添加边框和Style': 'Add border and style',
        'Add menu bar（Package括Open功Can）': 'Add menu bar (including open function)',
        '在PyQt应用middleShowErrorChart，Ensure compatibility with Qt event loop': 'Show error chart in PyQt application middle, ensure compatibility with Qt event loop',
        'Check是否已经在交互Mode': 'Check if already in interactive mode',
        '显式Update画布': 'Explicitly update canvas',
        
        # Final error fallback remaining issues
        '如果连ErrorChart都CannotShow，尝试Use简单的文本Output': 'If even error chart cannot be shown, try to use simple text output',
        'Critical error: CannotShow图形界Surface的ErrorInfo': 'Critical error: Cannot show graphical interface error info',
        'not yet知Error': 'unknown error',
        '请Check以Bottom事项': 'Please check the following items',
        'Python环境是否correctInstall': 'Python environment is correctly installed',
        'MatplotlibLibrary是否可用': 'Matplotlib library is available',
        'CSVFile是否存在且Formatcorrect': 'CSV file exists and format correct',
        '系统是否有Enough的ResourcesShow图形': 'System has enough resources to show graphics',
        
        # Clean matplotlib status remaining issues
        'CleanMatplotlibStatus，确保新的ChartCanNormalJob': 'Clean matplotlib status, ensure new chart can normally work',
        'ResetMatplotlib的InternalStatus（Not关闭CurrentChart，避免Event绑定失效）': 'Reset matplotlib internal status (not close current chart, avoid event binding failure)',
        '重新Configuremiddle文字体Support，避免ResetBack丢失': 'Reconfigure middle text font support, avoid loss after reset',
        '确保Usecorrect的Back端': 'Ensure to use correct backend',
        'CurrentMatplotlibBack端': 'Current matplotlib backend',
        '切换到QtAggBack端': 'Switch to QtAgg backend',
        
        # File dialog remaining issues
        '打开File对话框，允许用户ChooseDataFile': 'Open file dialog, allow user to choose data file',
        '尝试打开File对话框，ChooseData目录': 'Try to open file dialog, choose data directory',
        'UseQt的File对话框': 'Use Qt file dialog',
        '尝试UseQtFile对话框': 'Try to use Qt file dialog',
        '打开目录Choose对话框': 'Open directory choose dialog',
        '父窗口': 'parent window',
        '对话框Title': 'dialog title',
        'Default目录': 'default directory',
        '只Show目录': 'show directories only',
        'UseQtFile对话框Successfully，ReturnValue': 'Use Qt file dialog successfully, return value',
        'QtFile对话框Failed': 'Qt file dialog failed',
        '用户Choose的Data目录': 'User chosen data directory',
        'SetupDataPath并重新LoadData': 'Setup data path and reload data',
        'CleanMatplotlibStatus（确保新Chart有correct的Event绑定）': 'Clean matplotlib status (ensure new chart has correct event binding)',
        '关闭Current的ChartInstance（如果存在），确保新Create的ChartInstance是唯一的': 'Close current chart instance (if exists), ensure newly created chart instance is unique',
        '打开File对话框whenerror occurred': 'Error occurred when opening file dialog',
        
        # About dialog remaining issues
        'ShowAbout对话框': 'Show about dialog',
        'Get版本Info': 'Get version info',
        'Readpyproject.tomlGet版本Info': 'Read pyproject.toml to get version info',
        'CreateAboutInfo文本': 'Create about info text',
        '版本': 'Version',
        'BatteryTestData可视化Analyze应用': 'Battery Test Data Visualization Analysis Application',
        'SupportMultipleDataFormatImport与Chart生成': 'Support multiple data format import and chart generation',
        '功Can特Point': 'Function features',
        '交互式ChartShow和Operate': 'Interactive chart display and operation',
        'DataFilter和not yetFilter切换': 'Data filter and unfilter toggle',
        'BatteryChoose和ChannelControl': 'Battery choose and channel control',
        '悬停ShowDetailedInfo': 'Hover to show detailed info',
        'Develop者': 'Developer',
        '版权': 'Copyright',
        '感谢UseBattery Analysis Tool!': 'Thank you for using Battery Analysis Tool!',
        'About对话框ShowComplete': 'About dialog show complete',
        'ShowAbout对话框Failed': 'Failed to show about dialog',
        '如果对话框Failed，至少打印到Log': 'If dialog failed, at least print to log',
        'Battery Analysis Tool v2.1.1\nDevelop者': 'Battery Analysis Tool v2.1.1\nDeveloper',
        
        # Menu bar remaining issues
        '为ChartAdd menu bar（UnifyUsePyQt6）': 'Add menu bar for chart (unify use PyQt6)',
        'Start添加PyQt6菜单栏': 'Start adding PyQt6 menu bar',
        'GetChart窗口的manager': 'Get chart window manager',
        'CannotGetmatplotlib窗口Manage器': 'Cannot get matplotlib window manager',
        '添加PyQt6菜单栏': 'Add PyQt6 menu bar',
        '添加File菜单': 'Add file menu',
        '添加Open菜单项': 'Add open menu item',
        'Open菜单项被Point击': 'Open menu item clicked',
        '添加Division线': 'Add division line',
        '添加Exit菜单项': 'Add exit menu item',
        'Exit菜单项被Point击，关闭visualizer窗口': 'Exit menu item clicked, close visualizer window',
        '只关闭Current的visualizer窗口，Not退出整个应用': 'Only close current visualizer window, not exit entire application',
        '已关闭visualizer窗口': 'Visualizer window closed',
        'CurrentNot have打开的visualizer窗口': 'Currently no open visualizer window',
        '添加Help菜单': 'Add help menu',
        '添加About菜单项': 'Add about menu item',
        'About菜单项被Point击': 'About menu item clicked',
        'Successfully添加PyQt6菜单栏': 'Successfully added PyQt6 menu bar',
        '窗口NotSupport菜单栏': 'Window does not support menu bar',
        'PyQt6Depend on缺失': 'PyQt6 dependency missing',
        '请确保已correctInstallPyQt6': 'Please ensure PyQt6 is correctly installed',
        'Not再静默Failed，直接抛出Error': 'No longer silently fail, directly throw error',
        '菜单栏初始化Failed': 'Menu bar initialization failed',
        
        # Chart initialization remaining issues
        '初始化ChartSetup和布局': 'Initialize chart setup and layout',
        'Setup字体Style': 'Setup font style',
        'CreateChart并SetupTitle': 'Create chart and setup title',
        '尝试Setup窗口Title（添加ErrorProcess以兼容Not同Back端）': 'Try to setup window title (add error process to be compatible with different backends)',
        'CannotSetupChart窗口Title': 'Cannot setup chart window title',
        'Setup网格布局': 'Setup grid layout',
        '留出Left侧空Between给按钮': 'Leave left side space for buttons',
        'Setupaxis scope和scale': 'Setup axis scope and scale',
        'SetupY轴主scale': 'Setup Y-axis main scale',
        'SetupTitle和标签': 'Setup title and labels',
        '添加网格线': 'Add grid lines',
        
        # Chart plotting remaining issues
        '绘制OwnershipBattery的原始和FilterBack的曲线': 'Plot original and filtered curves of ownership battery',
        '绘制原始Data曲线（DefaultHide）': 'Plot original data curves (default hide)',
        '绘制FilterBack的Data曲线（DefaultShow）': 'Plot filtered data curves (default show)',
        '绘制Battery %s, current level %s 的曲线whenerror occurred': 'Error occurred when plotting battery %s, current level %s curves',
        
        # Modern button creation remaining issues
        'Create现代化按钮': 'Create modern button',
        'matplotlib轴Object': 'matplotlib axis object',
        '按钮位置': 'button position',
        '按钮尺寸': 'button size',
        '按钮文本': 'button text',
        'Point击CallbackFunction': 'Click callback function',
        '是否为切换按钮（SaveStatus）': 'Whether it is a toggle button (save status)',
        '初始Status': 'Initial status',
        'Create按钮背景': 'Create button background',
        'Create按钮文本': 'Create button text',
        '按钮Status': 'Button status',
        '初始化按钮Style': 'Initialize button style',
        '鼠标悬停Process': 'Mouse hover process',
        '鼠标移出按钮区域，Reset悬停Status': 'Mouse leaves button area, reset hover status',
        'Check鼠标是否在按钮ScopeInside - Unify检测Scope': 'Check if mouse is in button scope inside - unify detection scope',
        '鼠标进入按钮区域': 'Mouse enters button area',
        '鼠标离开按钮区域': 'Mouse leaves button area',
        'CheckPoint击是否在按钮ScopeInside - FixPoint击位置偏移': 'Check if click is in button scope inside - fix click position offset',
        '切换按钮Status': 'Toggle button status',
        '单次按钮，ExecuteBackResetStyle': 'Single button, execute back reset style',
        '按钮CallbackExecuteerror occurred': 'Button callback execute error occurred',
        '重绘': 'Redraw',
        'Create现代化按钮whenerror occurred': 'Error occurred when creating modern button',
        
        # Button style update remaining issues
        'Update按钮Style': 'Update button style',
        '按BottomStatus': 'Button status',
        '悬停Status': 'Hover status',
        '激活Status': 'Active status',
        'not yet激活Status': 'Not yet active status',
        'Update按钮Stylewhenerror occurred': 'Error occurred when updating button style',
        
        # Button delay reset remaining issues
        'DelayReset按钮Status': 'Delay reset button status',
        
        # Modern toggle button group remaining issues
        'Create现代化切换按钮组': 'Create modern toggle button group',
        '按钮组位置': 'Button group position',
        '按钮组尺寸': 'Button group size',
        '按钮ConfigureList': 'Button configure list',
        'Create现代化切换按钮组whenerror occurred': 'Error occurred when creating modern toggle button group',
        
        # File operation button area remaining issues
        '添加FileOperate按钮区域（打开File和退出按钮）': 'Add file operation button area (open file and exit buttons)',
        'CreateFileOperate按钮区域': 'Create file operation button area',
        '按钮Configure': 'Button configure',
        'Create现代化按钮组': 'Create modern button group',
        'Successfully添加现代化FileOperate按钮区域': 'Successfully added modern file operation button area',
        'CreateFileOperate按钮whenerror occurred': 'Error occurred when creating file operation button',
        
        # Close viewer window remaining issues
        '关闭viewer窗口': 'Close viewer window',
        'FileOperate按钮：Exit被Point击，关闭visualizer窗口': 'File operation button: Exit clicked, close visualizer window',
        '只关闭Current的visualizer窗口，Not退出整个应用': 'Only close current visualizer window, not exit entire application',
        '已关闭visualizer窗口': 'Visualizer window closed',
        'CurrentNot have打开的visualizer窗口': 'Currently no open visualizer window',
        '关闭viewer窗口whenerror occurred': 'Error occurred when closing viewer window',
        
        # Filter/unfilter data toggle remaining issues
        '添加Filter/not yetFilterData切换按钮': 'Add filter/unfilter data toggle button',
        'Create按钮区域 - 移至LeftTop角，Channel区域Top方': 'Create button area - move to left top corner, above channel area',
        '按钮StatusVariable': 'Button status variable',
        '切换FilterMode的CallbackFunction': 'Callback function to toggle filter mode',
        'Update按钮文本': 'Update button text',
        '切换到FilterMode': 'Switch to filter mode',
        'Update线条可见性 - Maintain相同Battery的可见性一致': 'Update line visibility - maintain consistent visibility for same battery',
        'GetCurrentBattery的可见性Status（Based on最Back一次Setup）': 'Get current battery visibility status (based on last setup)',
        '对于EveryBattery，Ownershipcurrent level的可见性ShouldMaintain一致': 'For every battery, ownership current level visibility should maintain consistent'
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
        print(f"Fixed {changes_made} remaining Chinese text instances in {python_file}")
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
        for line_num, line in chinese_lines[:20]:  # Show first 20
            print(f"  Line {line_num}: {line}")
        if len(chinese_lines) > 20:
            print(f"  ... and {len(chinese_lines) - 20} more lines")
    else:
        print("No Chinese text found!")
    
    return len(chinese_lines)

if __name__ == "__main__":
    print("Fixing all remaining Chinese text...")
    fixed = fix_all_remaining_chinese()
    
    print("\nChecking for remaining Chinese text...")
    remaining = check_remaining_chinese()
    
    if remaining == 0:
        print("\n✅ All Chinese text has been successfully fixed!")
    else:
        print(f"\n⚠️  {remaining} lines still contain Chinese text")