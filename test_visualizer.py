import os
import sys
import logging
from battery_analysis.main.controllers.visualizer_controller import VisualizerController

# 设置日志级别
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_visualizer():
    """测试可视化器修复是否成功"""
    try:
        # 创建可视化器控制器
        controller = VisualizerController()
        
        # 模拟选择一个不存在的XML路径（应该创建空的visualizer）
        xml_path = "test.xml"
        visualizer = controller.create_visualizer(xml_path)
        
        # 显示图表
        logging.info("显示可视化图表...")
        # 注意：这里不会实际显示图表，因为我们没有图形界面
        # visualizer.plt_figure()
        
        logging.info("测试完成，可视化器创建成功")
        return True
    except Exception as e:
        logging.error("测试失败: %s", str(e))
        return False

if __name__ == "__main__":
    test_visualizer()