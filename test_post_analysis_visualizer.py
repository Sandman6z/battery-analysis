#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试脚本：模拟分析后启动visualizer的场景

该脚本用于复现和测试电池分析完成后visualizer无法打开的问题。
它将创建一个模拟的分析结果目录结构和Info_Image.csv文件，
然后尝试启动visualizer，验证其是否能正常显示窗口。
"""

import os
import sys
import tempfile
import shutil
import logging
import csv
import time

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from battery_analysis.main.controllers.visualizer_controller import VisualizerController

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def create_test_environment():
    """
    创建测试环境：
    - 创建临时目录作为项目根目录
    - 创建3_analysis results目录
    - 创建Info_Image.csv文件，包含模拟的电池数据
    """
    logging.info("创建测试环境...")
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp(prefix="battery_analysis_test_")
    logging.info(f"创建临时目录: {temp_dir}")
    
    # 创建3_analysis results目录
    analysis_dir = os.path.join(temp_dir, "3_analysis results")
    os.makedirs(analysis_dir)
    
    # 创建一个测试子目录
    test_subdir = os.path.join(analysis_dir, "Test_V1")
    os.makedirs(test_subdir)
    
    # 创建模拟的Info_Image.csv文件
    csv_data = [
        ["Cycle", "Voltage", "Current", "Capacity"],
        [1, 4.2, 0.5, 2.0],
        [2, 4.1, 0.5, 1.95],
        [3, 4.0, 0.5, 1.9],
        [4, 3.9, 0.5, 1.85],
        [5, 3.8, 0.5, 1.8]
    ]
    
    csv_path = os.path.join(test_subdir, "Info_Image.csv")
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)
    
    logging.info(f"创建模拟的Info_Image.csv文件: {csv_path}")
    
    return temp_dir, test_subdir

def test_direct_visualizer_startup():
    """
    测试直接启动visualizer（不经过分析流程）
    """
    logging.info("\n=== 测试1: 直接启动visualizer ===")
    
    try:
        # 创建VisualizerController实例
        visualizer_controller = VisualizerController()
        
        # 启动visualizer（不提供xml_path，将创建空的visualizer实例）
        visualizer_controller.run_visualizer()
        
        logging.info("直接启动可视化工具成功")
        return True
    except Exception as e:
        logging.error("直接启动可视化工具失败: %s", str(e))
        return False

def test_post_analysis_visualizer_startup(analysis_dir):
    """
    测试分析后启动visualizer（模拟分析完成后的场景）
    """
    logging.info("\n=== 测试2: 分析后启动visualizer ===")
    
    try:
        # 切换到分析结果目录（模拟分析完成后的工作目录）
        original_cwd = os.getcwd()
        os.chdir(analysis_dir)
        
        logging.info(f"当前工作目录: {os.getcwd()}")
        
        # 创建VisualizerController实例
        visualizer_controller = VisualizerController()
        
        # 启动visualizer（不提供xml_path，自动查找当前目录下的分析结果）
        visualizer_controller.run_visualizer()
        
        # 切换回原始目录
        os.chdir(original_cwd)
        
        logging.info("分析后启动可视化工具成功")
        return True
    except Exception as e:
        logging.error("分析后启动可视化工具失败: %s", str(e))
        return False

def test_visualizer_with_xml_path(xml_path):
    """
    测试使用xml_path启动visualizer
    """
    logging.info("\n=== 测试3: 使用xml_path启动visualizer ===")
    
    try:
        # 创建VisualizerController实例
        visualizer_controller = VisualizerController()
        
        # 启动visualizer（提供xml_path）
        visualizer_controller.run_visualizer(xml_path)
        
        logging.info("使用xml_path启动可视化工具成功")
        return True
    except Exception as e:
        logging.error("使用xml_path启动可视化工具失败: %s", str(e))
        return False

def main():
    """
    主函数：执行所有测试用例
    """
    logging.info("开始测试电池分析后visualizer启动功能...")
    
    # 创建测试环境
    temp_dir, test_subdir = create_test_environment()
    
    try:
        # 测试1: 直接启动visualizer
        # test_direct_visualizer_startup()
        
        # 测试2: 分析后启动visualizer
        test_post_analysis_visualizer_startup(test_subdir)
        
        # 测试3: 使用xml_path启动visualizer
        # 创建一个模拟的xml文件路径（实际不存在，但用于测试路径处理）
        # xml_path = os.path.join(temp_dir, "test_profile.xml")
        # test_visualizer_with_xml_path(xml_path)
        
        logging.info("\n所有测试完成！")
        
        # 等待用户确认
        input("按Enter键结束测试...")
        
    finally:
        # 清理测试环境
        logging.info(f"清理测试环境: {temp_dir}")
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main()
