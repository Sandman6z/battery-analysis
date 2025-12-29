#!/usr/bin/env python3
"""
最终修复battery_chart_viewer.py语法错误的脚本
"""

import re
from pathlib import Path

def fix_battery_chart_syntax():
    """修复battery_chart_viewer.py的语法错误"""
    file_path = "src/battery_analysis/main/battery_chart_viewer.py"
    
    print(f"开始修复 {file_path} 的语法错误...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # 修复缩进问题 - 移除错误的缩进
            if line.strip().startswith('# Get project root config folder path'):
                # 修复这一行的缩进
                if line.startswith('        '):
                    # 移除多余的缩进
                    line = line[4:]  # 移除4个空格
                fixed_lines.append(line)
            
            # 修复__init__方法中的缩进问题
            elif line.strip() == '# Initialize chart configuration object':
                # 检查前面的缩进是否正确
                if i > 0 and lines[i-1].strip():
                    prev_line = lines[i-1].rstrip()
                    if prev_line and not prev_line.startswith('        '):
                        # 添加正确的缩进
                        line = '        ' + line.lstrip()
                fixed_lines.append(line)
            
            # 修复变量名中的空格
            elif 'axis _def ault' in line:
                line = line.replace('axis _def ault', 'axis_default')
                fixed_lines.append(line)
            
            elif 'in tBatteryNum' in line:
                line = line.replace('in tBatteryNum', 'intBatteryNum')
                fixed_lines.append(line)
            
            elif 'lis tColor' in line:
                line = line.replace('lis tColor', 'listColor')
                fixed_lines.append(line)
            
            elif 'lis tAxis' in line:
                line = line.replace('lis tAxis', 'listAxis')
                fixed_lines.append(line)
            
            elif 'lis tXTicks' in line:
                line = line.replace('lis tXTicks', 'listXTicks')
                fixed_lines.append(line)
            
            elif 'lis tPlt' in line:
                line = line.replace('lis tPlt', 'listPlt')
                fixed_lines.append(line)
            
            elif 'lis tBatteryName' in line:
                line = line.replace('lis tBatteryName', 'listBatteryName')
                fixed_lines.append(line)
            
            elif 'def ault' in line:
                line = line.replace('def ault', 'default')
                fixed_lines.append(line)
            
            elif 'in itialization' in line:
                line = line.replace('in itialization', 'initialization')
                fixed_lines.append(line)
            
            elif 'in stance' in line:
                line = line.replace('in stance', 'instance')
                fixed_lines.append(line)
            
            elif 'loadin g' in line:
                line = line.replace('loadin g', 'loading')
                fixed_lines.append(line)
            
            elif 'perfor m' in line:
                line = line.replace('perfor m', 'perform')
                fixed_lines.append(line)
            
            elif 'suppor t' in line:
                line = line.replace('suppor t', 'support')
                fixed_lines.append(line)
            
            elif 'Filterin g' in line:
                line = line.replace('Filterin g', 'Filtering')
                fixed_lines.append(line)
            
            elif 'processin g' in line:
                line = line.replace('processin g', 'processing')
                fixed_lines.append(line)
            
            elif 'drawin g' in line:
                line = line.replace('drawin g', 'drawing')
                fixed_lines.append(line)
            
            elif 'readin g' in line:
                line = line.replace('readin g', 'reading')
                fixed_lines.append(line)
            
            elif 'Loggin g' in line:
                line = line.replace('Loggin g', 'Logging')
                fixed_lines.append(line)
            
            elif 'tracin g' in line:
                line = line.replace('tracin g', 'tracing')
                fixed_lines.append(line)
            
            elif 'parsin g' in line:
                line = line.replace('parsin g', 'parsing')
                fixed_lines.append(line)
            
            elif 'algor ithms' in line:
                line = line.replace('algor ithms', 'algorithms')
                fixed_lines.append(line)
            
            elif 'simulated' in line and 'battery data' in line:
                # 修复注释中的空格问题
                line = re.sub(r'simulated\s+battery data', 'simulated battery data', line)
                fixed_lines.append(line)
            
            elif 'curve Toggle' in line:
                line = line.replace('curve Toggle', 'curveToggle')
                fixed_lines.append(line)
            
            elif 'Chin ese' in line:
                line = line.replace('Chin ese', 'Chinese')
                fixed_lines.append(line)
            
            elif 'Dis play' in line:
                line = line.replace('Dis play', 'Display')
                fixed_lines.append(line)
            
            # 修复__init__方法中的具体缩进问题
            elif line.strip().startswith('self.plot_config = self.PlotConfig()'):
                # 确保这行有正确的缩进
                if not line.startswith('        '):
                    line = '        ' + line.lstrip()
                fixed_lines.append(line)
            
            elif 'self.lis tColor=' in line:
                # 修复多行赋值
                line = line.replace('self.lis tColor=', 'self.listColor =')
                fixed_lines.append(line)
            
            elif 'self.maxXaxis =' in line:
                line = line.replace('self.maxXaxis =', 'self.maxXaxis =')
                fixed_lines.append(line)
            
            elif 'self.in tBatteryNum=' in line:
                line = line.replace('self.in tBatteryNum=', 'self.intBatteryNum =')
                fixed_lines.append(line)
            
            elif 'self.loaded_data =' in line:
                line = line.replace('self.loaded_data =', 'self.loaded_data =')
                fixed_lines.append(line)
            
            elif 'self.current_fig =' in line:
                line = line.replace('self.current_fig =', 'self.current_fig =')
                fixed_lines.append(line)
            
            elif 'self.lis tAxis=' in line:
                line = line.replace('self.lis tAxis=', 'self.listAxis =')
                fixed_lines.append(line)
            
            elif 'self.lis tXTicks=' in line:
                line = line.replace('self.lis tXTicks=', 'self.listXTicks =')
                fixed_lines.append(line)
            
            elif 'self.lis tPlt=' in line:
                line = line.replace('self.lis tPlt=', 'self.listPlt =')
                fixed_lines.append(line)
            
            elif 'self.lis tBatteryName=' in line:
                line = line.replace('self.lis tBatteryName=', 'self.listBatteryName =')
                fixed_lines.append(line)
            
            else:
                fixed_lines.append(line)
            
            i += 1
        
        # 写入修复后的文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)
        
        print(f"✅ 语法修复完成: {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_battery_chart_syntax()
    if success:
        print("\n验证语法...")
        import subprocess
        result = subprocess.run(['python', '-m', 'py_compile', 'src/battery_analysis/main/battery_chart_viewer.py'], 
                               capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 语法验证通过!")
        else:
            print(f"❌ 语法仍有问题:")
            print(result.stderr)
    else:
        print("修复失败")