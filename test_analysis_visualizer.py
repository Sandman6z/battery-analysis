# -*- coding: utf-8 -*-
"""
测试脚本：模拟分析完成后启动可视化工具的流程
"""

import logging
import os
import sys

# 设置日志级别
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath('.'))

def test_direct_visualizer():
    """测试直接运行可视化工具（类似EXE默认行为）"""
    logging.info("\n=== 测试1: 直接运行可视化工具 ===")
    try:
        from battery_analysis.main.controllers.visualizer_controller import VisualizerController
        
        # 创建可视化控制器实例
        visualizer_controller = VisualizerController()
        
        # 直接运行可视化工具，不传递任何参数
        visualizer_controller.run_visualizer()
        
        logging.info("直接运行可视化工具成功")
        return True
    except Exception as e:
        logging.error("直接运行可视化工具失败: %s", str(e))
        import traceback
        traceback.print_exc()
        return False

def test_analysis_completion_visualizer():
    """测试分析完成后启动可视化工具"""
    logging.info("\n=== 测试2: 模拟分析完成后启动可视化工具 ===")
    try:
        # 模拟分析完成后的环境
        # 1. 首先创建一个测试的Info_Image.csv文件
        test_csv_path = "Info_Image.csv"
        with open(test_csv_path, 'w', encoding='utf-8') as f:
            f.write("# 测试数据\n")
            f.write("时间,电压,电流\n")
            f.write("0,3.7,0\n")
            f.write("1,3.6,1\n")
            f.write("2,3.5,2\n")
        logging.info("创建了测试用的Info_Image.csv文件")
        
        # 2. 模拟分析完成后启动可视化工具
        from battery_analysis.main.controllers.visualizer_controller import VisualizerController
        
        # 创建可视化控制器实例
        visualizer_controller = VisualizerController()
        
        # 运行可视化工具
        visualizer_controller.run_visualizer()
        
        logging.info("分析完成后启动可视化工具成功")
        
        # 3. 清理测试文件
        if os.path.exists(test_csv_path):
            os.remove(test_csv_path)
            logging.info("删除了测试用的Info_Image.csv文件")
            
        return True
    except Exception as e:
        logging.error("分析完成后启动可视化工具失败: %s", str(e))
        import traceback
        traceback.print_exc()
        
        # 清理测试文件
        test_csv_path = "Info_Image.csv"
        if os.path.exists(test_csv_path):
            os.remove(test_csv_path)
            logging.info("删除了测试用的Info_Image.csv文件")
            
        return False

def test_signal_chain():
    """测试信号链：从分析完成到可视化工具启动"""
    logging.info("\n=== 测试3: 测试信号链 ===")
    try:
        from PyQt6 import QtCore as QC
        from PyQt6.QtWidgets import QApplication
        from battery_analysis.main.controllers.main_controller import MainController
        from battery_analysis.main.controllers.visualizer_controller import VisualizerController
        
        # 创建应用程序实例
        app = QApplication([])
        
        # 创建主控制器
        main_controller = MainController()
        
        # 模拟可视化工具启动
        def on_start_visualizer():
            logging.info("收到启动可视化工具信号")
            visualizer_controller = VisualizerController()
            visualizer_controller.run_visualizer()
            # 发送信号后退出应用程序
            app.quit()
        
        # 连接信号
        main_controller.start_visualizer.connect(on_start_visualizer)
        
        # 模拟分析完成后发送信号
        main_controller._on_start_visualizer()
        
        # 运行事件循环
        app.exec()
        
        logging.info("信号链测试成功")
        return True
    except Exception as e:
        logging.error("信号链测试失败: %s", str(e))
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logging.info("开始测试可视化工具启动流程")
    
    # 测试直接运行可视化工具
    test_direct_visualizer()
    
    # 测试分析完成后启动可视化工具
    test_analysis_completion_visualizer()
    
    # 测试信号链
    test_signal_chain()
    
    logging.info("所有测试完成")
    sys.exit(0)
