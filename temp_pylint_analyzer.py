import os
import subprocess
import re
from datetime import datetime

def analyze_python_files():
    # 获取项目中所有Python文件
    python_files = [
        r"c:\Users\boe\Desktop\battery-analysis\src\battery_analysis\utils\exception_type.py",
        r"c:\Users\boe\Desktop\battery-analysis\src\battery_analysis\resources\__init__.py",
        r"c:\Users\boe\Desktop\battery-analysis\src\battery_analysis\main\controllers\__init__.py",
        r"c:\Users\boe\Desktop\battery-analysis\src\battery_analysis\main\controllers\validation_controller.py",
        r"c:\Users\boe\Desktop\battery-analysis\src\battery_analysis\main\workers\__init__.py",
        r"c:\Users\boe\Desktop\battery-analysis\src\battery_analysis\main\models\__init__.py",
        r"c:\Users\boe\Desktop\battery-analysis\src\battery_analysis\utils\resource_manager.py",
        r"c:\Users\boe\Desktop\battery-analysis\src\battery_analysis\main\controllers\file_controller.py",
        r"c:\Users\boe\Desktop\battery-analysis\src\battery_analysis\__init__.py",
        r"c:\Users\boe\Desktop\battery-analysis\src\battery_analysis\utils\battery_analysis.py",
        r"c:\Users\boe\Desktop\battery-analysis\src\battery_analysis\main\image_show.py",
        r"c:\Users\boe\Desktop\battery-analysis\src\battery_analysis\resources\resources_rc.py",
        r"c:\Users\boe\Desktop\battery-analysis\src\battery_analysis\utils\config_utils.py",
        r"c:\Users\boe\Desktop\battery-analysis\src\battery_analysis\ui\ui_main_window.py",
        r"c:\Users\boe\Desktop\battery-analysis\src\battery_analysis\utils\numeric_utils.py",
        r"c:\Users\boe\Desktop\battery-analysis\src\battery_analysis\utils\excel_utils.py",
        r"c:\Users\boe\Desktop\battery-analysis\src\battery_analysis\utils\plot_utils.py",
        r"c:\Users\boe\Desktop\battery-analysis\src\battery_analysis\utils\csv_utils.py",
        r"c:\Users\boe\Desktop\battery-analysis\src\battery_analysis\utils\word_utils.py",
        r"c:\Users\boe\Desktop\battery-analysis\src\battery_analysis\utils\data_utils.py",
        r"c:\Users\boe\Desktop\battery-analysis\src\battery_analysis\utils\file_writer.py",
        r"c:\Users\boe\Desktop\battery-analysis\src\battery_analysis\utils\version.py",
        r"c:\Users\boe\Desktop\battery-analysis\src\battery_analysis\main\controllers\main_controller.py",
        r"c:\Users\boe\Desktop\battery-analysis\src\battery_analysis\main\main_window.py",
        r"c:\Users\boe\Desktop\battery-analysis\src\battery_analysis\main\workers\analysis_worker.py"
    ]
    
    # 定义错误类型和解决方案映射
    error_solutions = {
        'W0611': '删除未使用的导入语句',
        'W0718': '将宽泛的异常捕获改为具体的异常类型',
        'C0301': '将长行拆分为多行，保持每行不超过79个字符',
        'R0912': '重构函数，减少分支数量（使用辅助函数或策略模式）',
        'R0915': '重构函数，减少语句数量（拆分功能为多个小函数）',
        'C0415': '将导入语句移到文件顶部',
        'W0702': '添加具体的异常类型捕获，避免使用裸except',
        'R0904': '减少类的公共方法数量，将相关功能封装为辅助类',
        'R0902': '减少类的实例属性数量，考虑使用数据类或分组相关属性',
        'C0330': '修复缩进问题，确保代码缩进一致',
        'C0116': '添加函数或方法的文档字符串',
        'C0115': '添加类的文档字符串',
        'W0105': '删除不必要的字符串表达式',
        'W0612': '删除未使用的变量',
        'W0613': '删除未使用的函数参数',
        'R0914': '减少函数的局部变量数量',
        'R0913': '减少函数的参数数量',
        'E0401': '安装缺失的依赖包或修复导入路径',
        'C0103': '修改变量、函数或类名，使其符合命名规范',
        'W0231': '在__init__方法中初始化所有实例属性',
        'W0201': '将实例属性的定义移到__init__方法中'
    }
    
    # 解析pylint结果并生成markdown内容
    markdown_content = "# 电池分析工具代码重构计划\n\n"
    markdown_content += f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    for file_path in python_files:
        # 运行pylint分析
        result = subprocess.run(
            ['pylint', '-r=n', file_path],
            capture_output=True,
            text=True,
            cwd=r"c:\Users\boe\Desktop\battery-analysis"
        )
        
        # 解析错误信息
        errors = []
        error_lines = re.findall(r'(.+?:\d+:\d+?: .+?: .+?)', result.stdout)
        
        for line in error_lines:
            match = re.match(r'(.+?):(\d+):(\d+?): (.+?): (.+)', line)
            if match:
                file, line_num, col_num, error_type, description = match.groups()
                errors.append({
                    'file': file,
                    'line_num': int(line_num),
                    'col_num': int(col_num),
                    'error_type': error_type,
                    'description': description.strip()
                })
        
        if errors:
            # 添加文件分析结果
            relative_path = os.path.relpath(file_path, r"c:\Users\boe\Desktop\battery-analysis")
            markdown_content += f"## {relative_path}\n\n"
            markdown_content += "| 行号 | 列号 | 错误类型 | 错误描述 | 解决方案 |\n"
            markdown_content += "|------|------|----------|----------|----------|\n"
            
            for error in errors:
                # 获取解决方案
                solution = error_solutions.get(error['error_type'], '根据具体情况进行修复')
                
                # 添加错误信息行
                markdown_content += f"| {error['line_num']} | {error['col_num']} | {error['error_type']} | {error['description']} | {solution} |\n"
            
            markdown_content += "\n"
        else:
            # 添加无错误的文件
            relative_path = os.path.relpath(file_path, r"c:\Users\boe\Desktop\battery-analysis")
            markdown_content += f"## {relative_path}\n\n"
            markdown_content += "✅ **无代码质量问题**\n\n"
    
    # 将结果写入refactoring_plan.md
    with open(r"c:\Users\boe\Desktop\battery-analysis\refactoring_plan.md", 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print("Pylint分析完成，结果已写入refactoring_plan.md")

if __name__ == "__main__":
    analyze_python_files()
