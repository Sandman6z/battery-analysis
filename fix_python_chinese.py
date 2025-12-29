#!/usr/bin/env python3
"""
Script to fix hardcoded Chinese text in Python files
"""

import os
import re

def fix_chinese_in_file(file_path):
    """Fix Chinese text in a single Python file"""
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Define replacement rules for mixed Chinese-English technical terms
    replacements = {
        # Coordinate axis and scale related
        '坐标轴Scope': 'axis scope',
        '刻Degree': 'scale',
        'SynchronousUpdate坐标轴Scope和刻Degree': 'Synchronously update axis scope and scale',
        
        # File checking related
        'CheckFile是否存在': 'Check if file exists',
        'CheckFile大小': 'Check file size',
        'CheckFile': 'Check file',
        
        # Data structure related
        '初始化DataStructure': 'Initialize data structure',
        'DataStructure': 'data structure',
        
        # File reading and management
        'UseTopBottom文Manage器安全ReadFile': 'Use top/bottom manager to safely read file',
        'ReadOwnershipRow以VerifyDataAmount': 'Read ownership row to verify data amount',
        '至少Need几RowData才Be expected toPackage含有效BatteryInfo': 'At least need several row data to be expected to contain valid battery info',
        
        # Data processing
        'ResetRead器以ProcessData': 'Reset reader to process data',
        'Check是否Read到有效Data': 'Check if valid data was read',
        '有效的BatteryInfo': 'valid battery information',
        'VerifyFilterBack的Data': 'Verify filtered data',
        'CheckFilterBack的Data': 'Check filtered data',
        '有效的BatteryData可供Show': 'valid battery data available for display',
        'SuccessRead并ProcessCSVData': 'Successfully read and process CSV data',
        'Package含': 'contains',
        '真实TestData': 'real test data',
        'Not have权限访问File': 'No permission to access file',
        'ReadCSVFile时HappenException': 'Exception occurred while reading CSV file',
        
        # Data structure initialization
        'Create并初始化用于StoreBatteryData的DataStructure': 'Create and initialize data structure for storing battery data',
        '生成三维List用于StoreEvery电StreamLevelBottomOwnershipBattery的原始和FilterBack的Data': 'Generate 3D list for storing original and filtered data of every current level bottom ownership battery',
        'ListStructure': 'List structure',
        '其MiddleDataType': 'where data type',
        '原始充电Data': 'original charging data',
        '原始电压Data': 'original voltage data',
        'FilterBack充电Data': 'filtered charging data',
        'FilterBack电压Data': 'filtered voltage data',
        
        # CSV data processing
        'ProcessCSVData并填充到DataStructureMiddle': 'Process CSV data and fill into data structure',
        '从CSVRead器MiddleProcessData并填充到DataStructureMiddle': 'Process data from CSV reader and fill into data structure',
        '将CSVMiddle的Data按Battery和电StreamLevel分Class': 'Classify data in CSV by battery and current level',
        'Store原始Data': 'Store original data',
        'ProcessProcessMiddle进RowException检测': 'Perform exception detection during processing',
        'SkipNone效Row': 'Skip invalid row',
        'RecordWarningLog': 'Record warning log',
        'CSVDataRead器': 'CSV data reader',
        
        # Row processing
        '新Battery的StartRow': 'New battery start row',
        'DataRow': 'Data row',
        'According toFormatRule填充Data': 'Fill data according to format rules',
        '确保索引在有效ScopeInside': 'Ensure index is within valid scope',
        '尝试将OwnershipDataConvert为float': 'Try to convert ownership data to float',
        'ParseCSVRowData时出错': 'Error parsing CSV row data',
        'Skip此Row': 'Skip this row',
        
        # Battery name parsing
        'ParseBatteryName，Extract有Meaning的标识符': 'Parse battery name, extract meaningful identifier',
        '从BatteryNameMiddleExtract有Meaning的Part': 'Extract meaningful part from battery name',
        '生成简洁易读的Battery标识符': 'Generate concise and readable battery identifier',
        '优先SearchBTS标识Back的Part': 'Priority search for BTS identifier back part',
        '如果存在则Extract其Middle的KeyInfo': 'If exists, extract key info from middle',
        '如果Not存在BTS标识': 'If BTS identifier does not exist',
        'UseName的BackPart或DefaultName': 'Use back part of name or default name',
        'ParseProcessMiddle进RowException检测': 'Perform exception detection during parsing process',
        'ParseBatteryName时出错': 'Error parsing battery name',
        'UseDefaultName': 'Use default name',
        
        # Data filtering
        'FilterData以去除ExceptionValue和噪声': 'Filter data to remove exception values and noise',
        'Achieve一个Based on斜率和电压差异的Filter算法': 'Implement a filter algorithm based on slope and voltage difference',
        '用于去除BatteryDataMiddle的ExceptionValue和噪声': 'Used to remove exception values and noise in battery data',
        '通过多次IterateFilter': 'Through multiple iterations of filtering',
        '逐步平滑Data曲线': 'Gradually smooth data curve',
        'At the same timeRetainData的Whole趋势': 'While retaining overall trend of data',
        '充电DataList': 'charging data list',
        '电压DataList': 'voltage data list',
        'FilterIterate次Number': 'Filter iteration count',
        '允许的Maximum斜率': 'Allowed maximum slope',
        '允许的Maximum电压差异': 'Allowed maximum voltage difference',
        'FilterBack的充电Data和电压Data': 'Filtered charging data and voltage data',
        
        # Battery data filtering
        'FilterOwnershipBattery的Data': 'Filter ownership battery data',
        '对OwnershipBatteryData应用Filter算法': 'Apply filter algorithm to ownership battery data',
        'TraverseEvery电StreamLevel和Battery的Data': 'Traverse every current level and battery data',
        '应用filter_dataMethod进RowData平滑Process': 'Apply filter_data method for data smoothing process',
        '去除ExceptionValue和噪声': 'Remove exception values and noise',
        '确保单个BatteryDataProcessFailedNotBe able toImpactWholeProcessStream程': 'Ensure single battery data processing failure cannot impact whole process',
        'CheckData是否有效': 'Check if data is valid',
        'FilterData时出错': 'Error filtering data',
        '电StreamLevel': 'current level',
        
        # Chart creation and display
        'Create并ShowBatteryDataChart，Package含交互控件以切换DataShow': 'Create and show battery data chart, including interactive controls to switch data display',
        '重要Explain': 'Important explanation',
        '此Method只UseCSVFileMiddle的真实Data': 'This method only uses real data from CSV file',
        '如果Not have有效的BatteryData或绘图ProcessMiddle出错': 'If there is no valid battery data or error occurs during plotting process',
        'Be able toShowDetailed的ErrorInfo和故障排除Suggestion': 'Can show detailed error info and troubleshooting suggestions',
        'Start绘制Chart': 'Start drawing chart',
        'Execute多Layer次的Data有效性Check': 'Perform multi-level data validity checks',
        'Not have有效的BatteryData可供Show': 'No valid battery data available for display',
        'CheckNecessary的DataStructure是否有效': 'Check if necessary data structure is valid',
        'BatteryDataStructureNot yet初始化或为空': 'Battery data structure not yet initialized or empty',
        '初始化Chart和轴': 'Initialize chart and axes',
        'None法初始化Chart或坐标轴': 'Cannot initialize chart or coordinate axes',
        'SaveCurrentChartInstance引用': 'Save current chart instance reference',
        '添加菜单栏': 'Add menu bar',
        'Chart初始化Failed': 'Chart initialization failed',
        '绘制BatteryData曲线': 'Plot battery data curves',
        'Success绘制了': 'Successfully plotted',
        '条Filter曲线和': 'filtered curves and',
        '条原始曲线': 'original curves',
        '绘制Battery曲线时出错': 'Error plotting battery curves',
        'Check是否Success绘制了曲线': 'Check if curves were successfully plotted',
        '严重Error': 'Critical error',
        'None法绘制任何BatteryData曲线': 'Cannot plot any battery data curves',
        '添加交互控件': 'Add interactive controls',
        'Success添加Chart交互控件': 'Successfully added chart interactive controls',
        '添加交互控件时出错': 'Error adding interactive controls',
        '即使交互控件添加Failed': 'Even if interactive controls addition failed',
        '仍然尝试ShowChart': 'Still try to show chart',
        'ChartCreateComplete': 'Chart creation complete',
        'ShowCSVFileMiddle的真实BatteryTestData': 'Show real battery test data from CSV file',
        '在PyQt应用MiddleShowChart': 'Show chart in PyQt application',
        '确保与QtEventLoop兼容': 'Ensure compatibility with Qt event loop',
        'Setup为交互Mode': 'Setup as interactive mode',
        '确保窗口Always在最FrontSurface并正确Show': 'Ensure window is always on top and correctly shown',
        '确保窗口在最FrontSurfaceShow并Obtain焦Point': 'Ensure window shows on top and obtains focus',
        '对于QtBack端': 'For Qt backend',
        'Setup窗口标志': 'Setup window flags',
        '激活并Show窗口': 'Activate and show window',
        '确保窗口Not是Minimum化Status': 'Ensure window is not minimized status',
        '确保窗口可见': 'Ensure window is visible',
        'Setup窗口位置在屏幕Middle央': 'Setup window position at screen center',
        '强制Refresh窗口': 'Force refresh window',
        'None法将窗口置于最FrontSurface': 'Cannot bring window to top',
        '增加Pause时Between确保窗口正确渲染': 'Add pause time to ensure correct window rendering',
        '显式UpdateChart': 'Explicitly update chart',
        '再次Update以确保窗口稳定Show': 'Update again to ensure stable window display',
        '严重Error': 'Critical error',
        '绘制Chart时HappenNot yet预期的Exception': 'Unexpected exception occurred during chart drawing',
        
        # File search
        'Search项目MiddleBe expected to存在的Info_Image.csvFile': 'Search for expected Info_Image.csv file in project',
        
        # Error messages
        'Error': 'Error',
        'Not': 'Not',
        'None': 'None',
        'Not足': 'insufficient',
        'Middle': 'middle',
        'Have': 'have',
        '可供': 'available for',
        '时': 'when',
        '出错': 'error occurred',
        '请Confirm': 'Please confirm',
        '正确': 'correct',
        'Package含': 'contains',
        '真实': 'real',
        'Not yet': 'not yet',
        '或': 'or',
        '为空': 'empty',
        'None法': 'Cannot',
        'Success': 'Successfully',
        'Complete': 'Complete',
        'Failed': 'Failed',
        '严重': 'Critical',
        'Happen': 'Occurred',
        'Exception': 'Exception'
    }
    
    # Apply replacements
    changes_made = 0
    for chinese, english in replacements.items():
        if chinese in content:
            content = content.replace(chinese, english)
            changes_made += 1
    
    # Write back if changes were made
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {changes_made} Chinese text instances in {file_path}")
        return True
    
    return False

def main():
    """Main function to fix Chinese text in Python files"""
    
    # Target Python files
    python_files = [
        'src/battery_analysis/main/battery_chart_viewer.py',
        'src/battery_analysis/main/main_window.py',
        'src/battery_analysis/main/controllers/visualizer_controller.py',
        'src/battery_analysis/main/controllers/main_controller.py',
        'src/battery_analysis/main/controllers/validation_controller.py',
        'src/battery_analysis/main/controllers/file_controller.py',
        'src/battery_analysis/main/workers/analysis_worker.py',
        'src/battery_analysis/utils/battery_analysis.py',
        'src/battery_analysis/utils/plot_utils.py',
        'src/battery_analysis/utils/file_writer.py',
        'src/battery_analysis/utils/version.py',
        'src/battery_analysis/utils/word_utils.py',
        'src/battery_analysis/utils/resource_manager.py',
        'src/battery_analysis/utils/numeric_utils.py',
        'src/battery_analysis/utils/data_utils.py',
        'src/battery_analysis/utils/config_utils.py',
        'src/battery_analysis/utils/csv_utils.py',
        'src/battery_analysis/i18n/language_manager.py',
        'src/battery_analysis/i18n/preferences_dialog.py',
        'src/battery_analysis/ui/ui_main_window.py',
        'src/battery_analysis/__init__.py'
    ]
    
    fixed_files = []
    
    for file_path in python_files:
        if os.path.exists(file_path):
            if fix_chinese_in_file(file_path):
                fixed_files.append(file_path)
        else:
            print(f"File not found: {file_path}")
    
    print(f"\nFixed Chinese text in {len(fixed_files)} files:")
    for file_path in fixed_files:
        print(f"  - {file_path}")

if __name__ == "__main__":
    main()