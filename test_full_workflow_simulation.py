#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整工作流模拟测试脚本
模拟分析完成后启动可视化工具的场景
"""

import os
import sys
import logging
import tempfile
import shutil
import csv
from PyQt6 import QtWidgets as QW
from PyQt6 import QtCore as QC

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_full_workflow.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 添加项目路径到Python路径
sys.path.insert(0, os.path.abspath('src'))

# 创建模拟的Info_Image.csv文件
def create_mock_info_image(directory):
    """
    创建模拟的Info_Image.csv文件
    
    Args:
        directory: 保存文件的目录
    """
    csv_path = os.path.join(directory, 'Info_Image.csv')
    
    # 模拟数据
    data = [
        ['Index', '时间', 'OBD总压(VP)', '电池单体电压最小值(Vmin)', '电池单体电压最大值(Vmax)',
         '电池单体温度最小值(Tmin)', '电池单体温度最大值(Tmax)', 'SOH(%)', 'SOC(%)',
         '电池总电流(A)', '累计充放电量(Ah)', '电池健康状态'],
        ['0', '0', '380.5', '3.25', '3.35', '25.5', '30.2', '95', '80', '50.2', '10.5', '正常'],
        ['1', '300', '381.2', '3.26', '3.34', '26.1', '30.5', '95', '81', '49.8', '10.6', '正常'],
        ['2', '600', '382.0', '3.27', '3.33', '26.5', '31.0', '95', '82', '49.5', '10.7', '正常'],
        ['3', '900', '382.8', '3.28', '3.32', '27.0', '31.5', '95', '83', '49.2', '10.8', '正常'],
        ['4', '1200', '383.5', '3.29', '3.31', '27.5', '32.0', '95', '84', '48.8', '10.9', '正常']
    ]
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    
    logger.info(f"创建了模拟的Info_Image.csv文件: {csv_path}")
    return csv_path

# 创建测试环境
def create_test_environment():
    """
    创建测试环境，包括3_analysis results目录结构
    """
    # 创建临时目录作为项目根目录
    test_dir = tempfile.mkdtemp(prefix="battery_test_")
    logger.info(f"创建了测试目录: {test_dir}")
    
    # 创建3_analysis results目录
    analysis_dir = os.path.join(test_dir, "3_analysis results")
    os.makedirs(analysis_dir)
    
    # 创建测试子目录（模拟最新的分析结果）
    test_subdir = os.path.join(analysis_dir, "20240101_V1")
    os.makedirs(test_subdir)
    
    # 创建模拟的Info_Image.csv文件
    create_mock_info_image(test_subdir)
    
    return test_dir, analysis_dir, test_subdir

# 测试直接运行可视化工具
def test_direct_visualizer(test_dir):
    """
    测试直接运行可视化工具
    """
    logger.info('\n=== 测试：直接运行可视化工具 ===')
    
    try:
        from battery_analysis.main.main_window import Main
        from battery_analysis.main.controllers.visualizer_controller import VisualizerController
        
        app = QW.QApplication(sys.argv)
        
        # 创建Main实例
        main_window = Main()
        
        # 直接调用run_visualizer方法
        logger.info('调用main_window.run_visualizer()')
        main_window.run_visualizer()
        
        logger.info('可视化工具启动成功')
        return True
        
    except Exception as e:
        logger.error(f'直接运行可视化工具失败: {str(e)}', exc_info=True)
        return False

# 测试模拟分析完成后运行可视化工具
def test_post_analysis_visualizer(test_subdir):
    """
    测试模拟分析完成后运行可视化工具
    """
    logger.info('\n=== 测试：模拟分析完成后运行可视化工具 ===')
    
    try:
        from battery_analysis.main.main_window import Main
        from battery_analysis.main.controllers.visualizer_controller import VisualizerController
        
        app = QW.QApplication(sys.argv)
        
        # 创建Main实例
        main_window = Main()
        
        # 模拟分析完成后，直接运行可视化工具
        logger.info('模拟分析完成后调用main_window.run_visualizer()')
        
        # 设置当前工作目录为测试目录，模拟分析后的状态
        original_cwd = os.getcwd()
        os.chdir(os.path.dirname(test_subdir))  # 切换到3_analysis results目录
        
        try:
            main_window.run_visualizer()
            logger.info('分析完成后可视化工具启动成功')
            return True
        finally:
            os.chdir(original_cwd)  # 恢复原工作目录
            
    except Exception as e:
        logger.error(f'分析完成后运行可视化工具失败: {str(e)}', exc_info=True)
        return False

# 主测试函数
def main():
    """
    主测试函数
    """
    logger.info('开始完整工作流测试')
    
    # 创建测试环境
    test_dir, analysis_dir, test_subdir = create_test_environment()
    
    try:
        # 测试直接运行可视化工具
        direct_result = test_direct_visualizer(test_dir)
        
        # 测试模拟分析完成后运行可视化工具
        post_analysis_result = test_post_analysis_visualizer(test_subdir)
        
        logger.info('\n=== 测试结果 ===')
        logger.info(f'直接运行可视化工具: {"成功" if direct_result else "失败"}')