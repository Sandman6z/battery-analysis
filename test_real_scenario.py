# -*- coding: utf-8 -*-
"""
测试脚本：模拟实际分析完成后启动可视化工具的场景
"""

import logging
import os
import sys
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer

# 设置日志级别
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath('.'))

def create_test_data():
    """创建模拟的电池分析数据文件"""
    # 创建分析结果目录
    analysis_dir = "3_analysis results"
    if not os.path.exists(analysis_dir):
        os.makedirs(analysis_dir)
    
    # 创建测试目录
    test_dir = os.path.join(analysis_dir, "test_analysis_result")
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    
    # 创建Info_Image.csv文件
    csv_path = os.path.join(test_dir, "Info_Image.csv")
    with open(csv_path, 'w', encoding='utf-8') as f:
        f.write("# 电池测试数据\n")
        f.write("BatteryType,纽扣电池\n")
        f.write("TestDate,2025-12-25\n")
        f.write("\n")
        f.write("时间,电压,电流\n")
        for i in range(10):
            voltage = 3.7 - i * 0.1
            current = i * 0.5
            f.write(f"{i},{voltage:.2f},{current:.2f}\n")
    
    logging.info(f"创建了测试数据目录: {test_dir}")
    logging.info(f"创建了测试CSV文件: {csv_path}")
    
    return test_dir

def cleanup_test_data():
    """清理测试数据"""
    analysis_dir = "3_analysis results"
    if os.path.exists(analysis_dir):
        import shutil
        shutil.rmtree(analysis_dir)
        logging.info(f"清理了测试数据目录: {analysis_dir}")

def test_visualizer_after_analysis():
    """测试分析完成后启动可视化工具"""
    # 创建测试数据
    test_dir = create_test_data()
    
    try:
        # 模拟分析完成后的环境
        logging.info("\n=== 模拟分析完成后启动可视化工具 ===")
        
        # 创建应用程序实例
        app = QApplication([])
        
        # 延迟启动可视化工具，模拟分析完成后的场景
        def start_visualizer():
            logging.info("启动可视化工具...")
            try:
                from battery_analysis.main.controllers.visualizer_controller import VisualizerController
                
                # 创建可视化控制器实例
                visualizer_controller = VisualizerController()
                
                # 运行可视化工具
                visualizer_controller.run_visualizer()
                
                logging.info("可视化工具启动成功")
                
                # 3秒后自动关闭应用程序
                QTimer.singleShot(3000, app.quit)
                
            except Exception as e:
                logging.error("启动可视化工具失败: %s", str(e))
                import traceback
                traceback.print_exc()
                app.quit()
        
        # 2秒后启动可视化工具
        QTimer.singleShot(2000, start_visualizer)
        
        # 运行事件循环
        app.exec()
        
        return True
        
    finally:
        # 清理测试数据
        cleanup_test_data()

if __name__ == "__main__":
    logging.info("开始测试实际场景：分析完成后启动可视化工具")
    
    # 运行测试
    success = test_visualizer_after_analysis()
    
    if success:
        logging.info("测试成功：可视化工具在分析完成后能够正常启动并显示窗口")
    else:
        logging.error("测试失败：可视化工具在分析完成后无法正常启动")
    
    logging.info("测试完成")
    sys.exit(0)
