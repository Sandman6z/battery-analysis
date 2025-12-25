#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试可视化工具修复效果的脚本
"""
import logging
import sys
import os

# 设置日志级别为DEBUG
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt6 import QtWidgets
from battery_analysis.main.main_window import Main

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    # 创建主窗口实例
    main_window = Main()
    
    # 测试1: 模拟QAction的triggered信号传递True值
    logging.info("\n=== 测试1: 模拟QAction的triggered信号传递True值 ===")
    main_window.run_visualizer(True)
    
    # 测试2: 模拟QAction的triggered信号传递False值
    logging.info("\n=== 测试2: 模拟QAction的triggered信号传递False值 ===")
    main_window.run_visualizer(False)
    
    # 测试3: 传递None值
    logging.info("\n=== 测试3: 传递None值 ===")
    main_window.run_visualizer(None)
    
    # 测试4: 传递有效路径
    logging.info("\n=== 测试4: 传递有效路径 ===")
    main_window.run_visualizer(os.path.abspath(__file__))
    
    logging.info("\n所有测试完成")
    sys.exit(0)
