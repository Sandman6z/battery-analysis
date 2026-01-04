# -*- coding: utf-8 -*-
"""
测试现代化电池查看器界面
"""

import sys
import os
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# 设置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# 添加项目路径到系统路径
sys.path.insert(0, os.path.abspath('.'))

def main():
    """主函数"""
    try:
        # 创建Qt应用程序
        app = QApplication(sys.argv)
        
        # 尝试加载样式表
        try:
            from battery_analysis.ui.styles.style_manager import StyleManager
            style_manager = StyleManager()
            
            # 使用新的统一样式文件
            unified_style_path = Path(__file__).parent / "src" / "battery_analysis" / "ui" / "styles" / "battery_analyzer.qss"
            
            logging.info("尝试加载统一样式文件: %s", unified_style_path)
            
            if unified_style_path.exists():
                with open(unified_style_path, 'r', encoding='utf-8') as f:
                    style = f.read()
                    app.setStyleSheet(style)
                    logging.info("已应用统一电池分析器样式")
            else:
                logging.warning("统一样式文件不存在: %s", unified_style_path)
                # 使用标准样式
                style_manager.apply_global_style(app, "battery_analyzer")
                logging.info("已应用全局主题样式")
        except Exception as e:
            logging.error("应用样式失败: %s", e)
            # 尝试使用标准样式
            try:
                from battery_analysis.ui.styles.style_manager import StyleManager
                style_manager = StyleManager()
                style_manager.apply_global_style(app, "modern")
                logging.info("备用样式已应用")
            except Exception as e2:
                logging.error("备用样式应用也失败: %s", e2)
        
        # 创建现代化电池查看器
        try:
            from battery_analysis.ui.modern_battery_viewer import ModernBatteryViewer
            
            # 获取数据路径（如果有）
            data_path = None
            if len(sys.argv) > 1:
                data_path = sys.argv[1]
                logging.info("从命令行接收数据路径: %s", data_path)
            
            viewer = ModernBatteryViewer(data_path=data_path)
            viewer.show()
            
            logging.info("已启动现代化电池查看器")
            
            # 运行应用
            sys.exit(app.exec())
            
        except Exception as e:
            logging.error("创建现代化电池查看器失败: %s", e)
            import traceback
            traceback.print_exc()
            
            # 如果创建失败，尝试创建基础窗口
            from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget
            
            window = QMainWindow()
            window.setWindowTitle("Battery Analysis - 测试界面")
            window.setMinimumSize(800, 600)
            
            central_widget = QWidget()
            layout = QVBoxLayout(central_widget)
            
            label = QLabel("这是一个测试窗口，用于验证样式是否正确应用。")
            layout.addWidget(label)
            
            window.setCentralWidget(central_widget)
            window.show()
            
            logging.info("已创建基础测试窗口")
            sys.exit(app.exec())
            
    except Exception as e:
        logging.error("应用程序启动失败: %s", e)
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())