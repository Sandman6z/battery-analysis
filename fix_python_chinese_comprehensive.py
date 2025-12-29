#!/usr/bin/env python3
"""
Comprehensive script to fix remaining hardcoded Chinese text in Python files
"""

import os
import re

def fix_remaining_chinese():
    """Fix remaining Chinese text in battery_chart_viewer.py"""
    
    python_file = "src/battery_analysis/main/battery_chart_viewer.py"
    
    # Read the file
    with open(python_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Define comprehensive replacement rules for remaining mixed Chinese-English text
    replacements = {
        # Remaining coordinate axis and scale issues
        'SynchronousUpdateaxis scope和scale': 'Synchronously update axis scope and scale',
        
        # Data processing remaining issues
        'Successfullyfully read and process CSV data，contains%d个Battery的real test data': 'Successfully read and process CSV data, contains %d batteries\' real test data',
        'Create并初始化用于StoreBatteryData的data structure。': 'Create and initialize data structure for storing battery data.',
        'List structure: listPlt[current level][DataType][Battery索引][DataPoint]': 'List structure: listPlt[current level][data type][battery index][data point]',
        'ProcessCSVData并填充到data structuremiddle': 'Process CSV data and fill into data structure middle',
        '从CSVRead器middleProcessData并填充到data structuremiddle。Classify data in CSV by battery and current level，Store original data。Perform exception detection during processing，Skip invalid row，并Record warning log。': 'Process data from CSV reader middle and fill into data structure middle. Classify data in CSV by battery and current level, store original data. Perform exception detection during processing, skip invalid row, and record warning log.',
        'If BTS identifier does not exist，则Use back part of name or default name。': 'If BTS identifier does not exist, use back part of name or default name.',
        'Perform exception detection during processing，确保即使ParseFailed也CanReturn有效的DefaultName。': 'Perform exception detection during processing, ensure even if parse failed can return valid default name.',
        
        # BTS parsing remaining issues
        '尝试ExtractBTSBack的标识符Part': 'Try to extract BTS back identifier part',
        '如果DivisionBackPartinsufficient，Use可用Part': 'If division back part insufficient, use available part',
        '如果Not haveBTS标识，Use原始Name的BackPartorDefaultName': 'If not have BTS identifier, use original name\'s back part or default name',
        
        # Filter parameters remaining issues
        'times: Filter iteration count，Default为5次': 'times: filter iteration count, default is 5 times',
        'slope_max: Allowed maximum slope，Default为0.2': 'slope_max: allowed maximum slope, default is 0.2',
        'difference_max: Allowed maximum voltage difference，Default为0.05': 'difference_max: allowed maximum voltage difference, default is 0.05',
        'Calculate斜率，避免除以零': 'Calculate slope, avoid division by zero',
        'According to斜率和电压差异进RowFilter': 'According to slope and voltage difference for row filter',
        
        # Chart creation remaining issues
        'Create并ShowBatteryDataChart，contains交互控件以切换DataShow': 'Create and show battery data chart, contains interactive controls to switch data display',
        'CheckNecessary的data structure是否有效': 'Check if necessary data structure is valid',
        'Batterydata structurenot yet初始化orempty': 'Battery data structure not yet initialized or empty',
        'Check是否Successfullyfully plotted曲线': 'Check if curves were successfully plotted',
        
        # File search remaining issues
        '这个MethodBe able to在项目根目录BottomSearchOwnershipBe expected to的Info_Image.csvFile，如果Find，Be able toAutomatedLoad该File。': 'This method can search for expected Info_Image.csv file in project root directory bottom, if found, can automatically load the file.',
        'StartSearch项目middle的Info_Image.csvFile...': 'Start searching for Info_Image.csv file in project middle...',
        '在项目根目录BottomSearch': 'Search in project root directory bottom',
        'SkipHide目录和venv目录': 'Skip hide directories and venv directories',
        '在项目middleFindInfo_Image.csvFile': 'Find Info_Image.csv file in project middle',
        'SuccessfullyLoadFind的DataFile': 'Successfully load found data file',
        'FindDataFile但LoadFailed': 'Find data file but load failed',
        '在项目middlenot yetFind任何有效的Info_Image.csvFile': 'Not yet find any valid Info_Image.csv file in project middle',
        
        # Error chart remaining issues
        'ShowDetailed的ErrorInfoChart，提供清晰的Error反馈和故障排除Suggestion': 'Show detailed error info chart, provide clear error feedback and troubleshooting suggestions',
        '主要ErrorInfo': 'Main error info',
        'CannotLoadorShowBatteryData': 'Cannot load or show battery data',
        'DetailedErrorInfo和故障排除Suggestion': 'Detailed error info and troubleshooting suggestions',
        'csvFile是否存在且Formatcorrect': 'csv file exists and format correct',
        'ConfigureFile是否correctChoose': 'configure file is correctly chosen',
        'FilePath是否containsmiddle文字符or特殊字符': 'file path contains middle text characters or special characters',
        'csvFile是否contains有效的BatteryTestData': 'csv file contains valid battery test data',
        
        # Hide axis and error details
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
        
        # Final error fallback
        '如果连ErrorChart都CannotShow，尝试Use简单的文本Output': 'If even error chart cannot be shown, try to use simple text output',
        'Critical error: CannotShow图形界Surface的ErrorInfo': 'Critical error: Cannot show graphical interface error info',
        'Error详情': 'Error details',
        'not yet知Error': 'unknown error',
        'CannotLoadData': 'Cannot load data',
        '请Check以Bottom事项': 'Please check the following items',
        'Python环境是否correctInstall': 'Python environment is correctly installed',
        'MatplotlibLibrary是否可用': 'Matplotlib library is available',
        'CSVFile是否存在且Formatcorrect': 'CSV file exists and format correct',
        '系统是否有Enough的ResourcesShow图形': 'System has enough resources to show graphics',
        
        # Clean matplotlib status
        'CleanMatplotlibStatus，确保新的ChartCanNormalJob': 'Clean matplotlib status, ensure new chart can normally work',
        'ResetMatplotlib的InternalStatus（Not关闭CurrentChart，避免Event绑定失效）': 'Reset matplotlib internal status (not close current chart, avoid event binding failure)',
        '重新Configuremiddle文字体Support，避免ResetBack丢失': 'Reconfigure middle text font support, avoid loss after reset',
        '确保Usecorrect的Back端': 'Ensure to use correct backend',
        'CurrentMatplotlibBack端': 'Current matplotlib backend',
        '切换到QtAggBack端': 'Switch to QtAgg backend',
        
        # File dialog
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
        
        # About dialog
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
        
        # Menu bar
        '为ChartAdd menu bar（UnifyUsePyQt6）': 'Add menu bar for chart (unify use PyQt6)',
        'Start添加PyQt6菜单栏': 'Start adding PyQt6 menu bar'
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

if __name__ == "__main__":
    fix_remaining_chinese()