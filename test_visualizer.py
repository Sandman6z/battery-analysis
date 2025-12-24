#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试可视化器功能的脚本
用于验证无XML启动时file-open菜单是否能正常工作
"""

import logging
import sys
import os

# 设置日志级别
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def test_visualizer_no_xml():
    """
    测试无XML启动时的可视化器功能
    """
    try:
        logging.info("开始测试无XML启动的可视化器功能...")
        
        # 导入可视化器模块
        from src.battery_analysis.main.image_show import FIGURE
        
        # 创建可视化器实例（不提供XML路径）
        visualizer = FIGURE()
        
        # 显示图表
        visualizer.plt_figure()
        
        logging.info("可视化器显示完成")
        return True
    except Exception as e:
        logging.error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_visualizer_no_xml()