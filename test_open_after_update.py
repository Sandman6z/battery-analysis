import sys
import os
import logging
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath('.'))

from src.battery_analysis.main.controllers.visualizer_controller import VisualizerController
from src.battery_analysis.main.image_show import FIGURE

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def test_open_after_update():
    """
    测试在分析后更新的visualizer中使用Open功能
    """
    logging.info("=== 开始测试：分析后更新的visualizer中使用Open功能 ===")
    
    try:
        # 步骤1：创建visualizer_controller实例
        logging.info("步骤1：创建visualizer_controller实例")
        controller = VisualizerController()
        
        # 步骤2：运行visualizer（模拟分析完成后更新）
        logging.info("步骤2：运行visualizer（模拟分析完成后更新）")
        controller.run_visualizer()
        
        # 等待用户观察
        logging.info("可视化器已显示，请观察通道选择按钮是否正常工作。")
        logging.info("5秒后，将通过代码模拟使用Open功能打开新数据...")
        time.sleep(5)
        
        # 步骤3：模拟使用Open功能打开新数据
        logging.info("步骤3：模拟使用Open功能打开新数据")
        # 假设visualizer实例存在，我们可以直接调用_open_file_dialog方法
        if controller.visualizer:
            logging.info("调用_open_file_dialog方法")
            # 这里我们不实际打开文件对话框，而是直接设置数据路径并测试
            # controller.visualizer._open_file_dialog()
            
            # 相反，我们直接测试_cleanup_matplotlib_state和plt_figure方法
            logging.info("测试_cleanup_matplotlib_state方法")
            controller.visualizer._cleanup_matplotlib_state()
            
            logging.info("测试plt_figure方法")
            controller.visualizer.plt_figure()
            
            logging.info("请再次观察通道选择按钮是否正常工作。")
            logging.info("测试完成后，请关闭所有可视化器窗口。")
        else:
            logging.error("visualizer实例不存在")
            
    except Exception as e:
        logging.error("测试过程中出错: %s", str(e))
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_open_after_update()