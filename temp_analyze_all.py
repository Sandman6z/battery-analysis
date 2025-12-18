import os
import subprocess
import json

# 获取所有Python文件
python_files = [
    "src/battery_analysis/utils/exception_type.py",
    "src/battery_analysis/resources/__init__.py",
    "src/battery_analysis/main/controllers/__init__.py",
    "src/battery_analysis/main/controllers/validation_controller.py",
    "src/battery_analysis/main/workers/__init__.py",
    "src/battery_analysis/main/models/__init__.py",
    "src/battery_analysis/utils/resource_manager.py",
    "src/battery_analysis/main/controllers/file_controller.py",
    "src/battery_analysis/__init__.py",
    "src/battery_analysis/utils/battery_analysis.py",
    "src/battery_analysis/main/image_show.py",
    "src/battery_analysis/resources/resources_rc.py",
    "src/battery_analysis/utils/config_utils.py",
    "src/battery_analysis/ui/ui_main_window.py",
    "src/battery_analysis/utils/numeric_utils.py",
    "src/battery_analysis/utils/excel_utils.py",
    "src/battery_analysis/utils/plot_utils.py",
    "src/battery_analysis/utils/csv_utils.py",
    "src/battery_analysis/utils/word_utils.py",
    "src/battery_analysis/utils/data_utils.py",
    "src/battery_analysis/utils/file_writer.py",
    "src/battery_analysis/utils/version.py",
    "src/battery_analysis/main/controllers/main_controller.py",
    "src/battery_analysis/main/main_window.py",
    "src/battery_analysis/main/workers/analysis_worker.py"
]

# 分析结果字典
analysis_results = {}

# 逐个分析每个文件
for file_path in python_files:
    print(f"分析文件: {file_path}")
    try:
        # 运行pylint分析，使用默认输出格式
        result = subprocess.run(
            ["pylint", "-r=n", file_path],
            capture_output=True,
            text=True,
            cwd=r"c:\Users\boe\Desktop\battery-analysis"
        )
        
        if result.returncode == 0:
            # 没有错误
            analysis_results[file_path] = {"errors": [], "output": "", "stderr": result.stderr}
        else:
            # 直接保存输出
            analysis_results[file_path] = {"errors": [], "output": result.stdout, "stderr": result.stderr}
                
    except Exception as e:
        # 记录执行错误
        analysis_results[file_path] = {"errors": [], "output": f"执行失败: {str(e)}", "stderr": ""}

# 保存分析结果到JSON文件
with open("pylint_analysis_results.txt", "w", encoding="utf-8") as f:
    for file_path, result in analysis_results.items():
        f.write(f"========================================\n")
        f.write(f"文件: {file_path}\n")
        f.write(f"========================================\n")
        f.write(f"标准输出:\n{result['output']}\n")
        f.write(f"标准错误:\n{result['stderr']}\n")
        f.write(f"\n\n")

print("分析完成，结果保存到 pylint_analysis_results.txt")
