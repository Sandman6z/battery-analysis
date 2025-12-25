#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整工作流程测试脚本

这个脚本模拟了电池分析工具的完整工作流程，包括：
1. 直接运行可视化工具
2. 模拟数据分析完成后的可视化工具启动

通过对比两种方式的行为，帮助定位分析后可视化工具无法打开的问题。
"""

import os
import sys
import logging
import time
import shutil
import tempfile
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_full_workflow.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 将项目根目录添加到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from battery_analysis.main.controllers.visualizer_controller import VisualizerController

def create_mock_data_structure(base_path):
    """
    创建模拟的数据结构，包括分析结果目录和Info_Image.csv文件
    
    Args:
        base_path: 基础路径
    
    Returns:
        str: 创建的Info_Image.csv文件路径
    """
    # 创建3_analysis results目录
    analysis_dir = os.path.join(base_path, "3_analysis results")
    os.makedirs(analysis_dir, exist_ok=True)
    
    # 创建一个子目录用于存储测试结果
    test_subdir = os.path.join(analysis_dir, "Test_V1")
    os.makedirs(test_subdir, exist_ok=True)
    
    # 创建模拟的Info_Image.csv文件
    csv_path = os.path.join(test_subdir, "Info_Image.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        f.write("时间,电压\n")
        f.write("Battery,BTS_1234_5678_001\n")
        f.write("CURRENT_LEVEL,1\n")
        f.write("CHARGE,0.0,10.0,20.0,30.0,40.0,50.0,60.0,70.0,80.0,90.0,100.0\n")
        f.write("VOLTAGE,2.0,2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9,3.0\n")
    
    logger.info(f"创建了模拟的Info_Image.csv文件: {csv_path}")
    return csv_path

def test_direct_visualizer_startup():
    """
    测试直接启动可视化工具
    
    Returns:
        bool: 是否成功
    """
    logger.info("\n=== 测试直接启动可视化工具 ===")
    
    try:
        # 创建VisualizerController实例
        visualizer_controller = VisualizerController()
        
        # 调用run_visualizer方法
        visualizer_controller.run_visualizer()
        
        logger.info("直接启动可视化工具成功")
        return True
    except Exception as e:
        logger.error(f"直接启动可视化工具失败: {str(e)}")
        import traceback
        logger.error(f"异常堆栈: {traceback.format_exc()}")
        return False

def test_post_analysis_visualizer_startup(mock_csv_path):
    """
    测试分析后启动可视化工具
    
    Args:
        mock_csv_path: 模拟的Info_Image.csv文件路径
    
    Returns:
        bool: 是否成功
    """
    logger.info("\n=== 测试分析后启动可视化工具 ===")
    
    try:
        # 切换到模拟的分析结果目录
        original_cwd = os.getcwd()
        csv_dir = os.path.dirname(mock_csv_path)
        os.chdir(csv_dir)
        
        logger.info(f"切换到分析结果目录: {csv_dir}")
        
        # 创建VisualizerController实例
        visualizer_controller = VisualizerController()
        
        # 调用run_visualizer方法
        visualizer_controller.run_visualizer()
        
        # 切换回原始目录
        os.chdir(original_cwd)
        
        logger.info("分析后启动可视化工具成功")
        return True
    except Exception as e:
        logger.error(f"分析后启动可视化工具失败: {str(e)}")
        import traceback
        logger.error(f"异常堆栈: {traceback.format_exc()}")
        # 确保切换回原始目录
        try:
            os.chdir(original_cwd)
        except:
            pass
        return False

def test_visualizer_with_xml_path(xml_path):
    """
    测试使用XML路径启动可视化工具
    
    Args:
        xml_path: XML文件路径
    
    Returns:
        bool: 是否成功
    """
    logger.info(f"\n=== 测试使用XML路径启动可视化工具: {xml_path} ===")
    
    try:
        # 创建VisualizerController实例
        visualizer_controller = VisualizerController()
        
        # 调用run_visualizer方法
        visualizer_controller.run_visualizer(xml_path)
        
        logger.info("使用XML路径启动可视化工具成功")
        return True
    except Exception as e:
        logger.error(f"使用XML路径启动可视化工具失败: {str(e)}")
        import traceback
        logger.error(f"异常堆栈: {traceback.format_exc()}")
        return False

def main():
    """
    主函数，执行完整的测试流程
    """
    logger.info("开始完整工作流程测试")
    
    # 创建临时目录用于模拟数据
    temp_dir = tempfile.mkdtemp()
    logger.info(f"创建临时目录: {temp_dir}")
    
    try:
        # 创建模拟的数据结构
        mock_csv_path = create_mock_data_structure(temp_dir)
        
        # 1. 测试直接启动可视化工具
        direct_result = test_direct_visualizer_startup()
        time.sleep(2)  # 等待窗口显示
        
        # 2. 测试分析后启动可视化工具
        post_analysis_result = test_post_analysis_visualizer_startup(mock_csv_path)
        time.sleep(2)  # 等待窗口显示
        
        # 3. 测试使用XML路径启动可视化工具
        xml_result = test_visualizer_with_xml_path("Not provided")
        time.sleep(2)  # 等待窗口显示
        
        # 汇总测试结果
        logger.info("\n=== 测试结果汇总 ===")
        logger.info(f"直接启动可视化工具: {'成功' if direct_result else '失败'}")
        logger.info(f"分析后启动可视化工具: {'成功' if post_analysis_result else '失败'}")
        logger.info(f"使用XML路径启动可视化工具: {'成功' if xml_result else '失败'}")
        
    finally:
        # 清理临时目录
        logger.info(f"清理临时目录: {temp_dir}")
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main()
