#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证visualizer通道选择按钮功能

该脚本用于测试visualizer中通道选择按钮的功能，包括：
1. 启动visualizer
2. 测试通道选择按钮是否能正常切换线条显示/隐藏
3. 测试过滤/未过滤模式切换是否能保持线条可见性一致
4. 测试通过不同路径启动visualizer时的功能一致性
"""

import sys
import os
import logging
import time
from PyQt6.QtWidgets import QApplication

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 配置日志
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def test_visualizer_direct():
    """直接测试visualizer功能"""
    logging.info("=== 直接测试visualizer功能 ===")
    
    from battery_analysis.main.battery_chart_viewer import BatteryChartViewer
    
    try:
        # 创建BatteryChartViewer实例
        figure = BatteryChartViewer()
        
        # 检查是否有数据可显示
        if figure.loaded_data:
            logging.info("数据加载成功，准备显示图表")
            
            # 显示图表
            figure.plt_figure()
            
            logging.info("图表显示完成，请手动测试以下功能：")
            logging.info("1. 点击左侧通道选择按钮，检查线条是否能显示/隐藏")
            logging.info("2. 切换过滤/未过滤模式，检查线条可见性是否保持一致")
            logging.info("3. 再次点击通道选择按钮，检查功能是否正常")
            
            # 保持程序运行一段时间，以便用户测试
            time.sleep(30)
            
            return True
        else:
            logging.warning("未找到数据文件，无法测试图表功能")
            return False
            
    except Exception as e:
        logging.error("测试visualizer功能时出错: %s", e)
        import traceback
        traceback.print_exc()
        return False

def test_visualizer_controller():
    """通过控制器测试visualizer功能"""
    logging.info("=== 通过控制器测试visualizer功能 ===")
    
    try:
        from battery_analysis.main.controllers.visualizer_controller import VisualizerController
        
        # 创建控制器实例
        visualizer_controller = VisualizerController()
        
        # 运行visualizer
        visualizer_controller.run_visualizer()
        
        logging.info("通过控制器启动visualizer成功")
        logging.info("请手动测试以下功能：")
        logging.info("1. 点击左侧通道选择按钮，检查线条是否能显示/隐藏")
        logging.info("2. 切换过滤/未过滤模式，检查线条可见性是否保持一致")
        
        # 保持程序运行一段时间，以便用户测试
        time.sleep(30)
        
        return True
        
    except Exception as e:
        logging.error("通过控制器测试visualizer功能时出错: %s", e)
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 创建Qt应用程序实例
    app = QApplication(sys.argv)
    
    # 测试直接启动visualizer
    test_visualizer_direct()
    
    # 进入Qt事件循环
    # 用户可以手动测试功能，关闭窗口后程序会退出
    sys.exit(app.exec())
