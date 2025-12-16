"""
电池数据分析图像显示模块

本模块提供了用于电池数据分析和可视化的协调功能。它整合了配置管理、数据处理和
图表显示模块，提供了完整的电池数据分析流程。

主要功能：
- 协调配置管理、数据处理和图表显示模块
- 提供统一的接口进行电池数据可视化
- 处理模块间的交互和错误处理

依赖：
- matplotlib: 用于图表绘制
- logging: 用于日志记录
- traceback: 用于错误跟踪
"""

import os
import sys
import logging
import traceback
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 导入自定义模块
from battery_analysis.main.config_manager import ConfigManager
from battery_analysis.main.data_processor import DataProcessor
from battery_analysis.main.ui.chart import Chart


class FIGURE:
    """
    电池数据可视化协调器类
    
    这个类负责协调配置管理、数据处理和图表显示模块，实现电池数据的可视化流程。
    它不再直接处理具体的配置读取、数据处理或图表绘制逻辑，而是作为一个协调器，
    整合各个专业模块的功能。
    """
    
    def __init__(self):
        """
        初始化FIGURE类，协调各个模块的工作流程
        
        初始化流程：
        1. 获取项目根目录路径
        2. 初始化配置管理器并加载配置
        3. 初始化数据处理器并读取数据
        4. 初始化图表显示模块并绘制图表
        """
        try:
            # 获取项目根目录路径
            current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
            self.project_root = current_dir.parent.parent
            
            # 初始化配置管理器
            self.config_manager = ConfigManager(self.project_root)
            self.config_manager.load_config_file()
            self.config_manager.read_configurations()
            self.config_manager.read_rules_configuration()
            
            # 初始化数据处理器
            self.data_processor = DataProcessor(
                self.config_manager.strInfoImageCsvPath,
                self.config_manager.intCurrentLevelNum
            )
            
            # 处理数据
            if not self.data_processor.csv_read():
                logging.error("数据处理失败，无法生成图表")
                return
            
            # 初始化图表显示
            self.chart = Chart(self.data_processor, self.config_manager)
            
            # 显示图表
            self.chart.plt_figure()
            
        except Exception as e:
            logging.error(f"初始化FIGURE类时出错: {e}")
            traceback.print_exc()