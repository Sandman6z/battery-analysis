#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证Matplotlib字体设置

该脚本用于测试Matplotlib的字体设置是否正确，特别是中文字体支持。
"""

import sys
import os
import logging
import matplotlib
import matplotlib.pyplot as plt

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def test_font_settings():
    """测试Matplotlib字体设置"""
    logging.info("=== 测试Matplotlib字体设置 ===")
    
    try:
        # 检查当前Matplotlib后端
        logging.info(f"当前Matplotlib后端: {matplotlib.get_backend()}")
        
        # 检查当前字体设置
        logging.info(f"当前字体设置: {matplotlib.rcParams['font.sans-serif']}")
        logging.info(f"负号显示设置: {matplotlib.rcParams['axes.unicode_minus']}")
        
        # 模拟visualizer_controller中的重置和重新设置
        logging.info("\n=== 模拟重置和重新设置字体 ===")
        
        # 重置Matplotlib的内部状态
        matplotlib.rcParams.update(matplotlib.rcParamsDefault)
        logging.info(f"重置后字体设置: {matplotlib.rcParams['font.sans-serif']}")
        
        # 重新配置中文字体支持
        matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans', 'Arial', 'Times New Roman']
        matplotlib.rcParams['axes.unicode_minus'] = False
        logging.info(f"重新设置后字体设置: {matplotlib.rcParams['font.sans-serif']}")
        
        # 创建一个简单的图表来测试字体显示
        logging.info("\n=== 创建测试图表 ===")
        
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot([1, 2, 3], [4, 5, 6], label='测试曲线')
        ax.set_title('测试图表标题（中文）')
        ax.set_xlabel('X轴标签（中文）')
        ax.set_ylabel('Y轴标签（中文）')
        ax.legend()
        ax.grid(True)
        
        logging.info("测试图表创建成功，字体应该能正常显示中文")
        
        # 不显示图表，仅测试创建过程
        plt.close(fig)
        
        return True
        
    except Exception as e:
        logging.error("测试字体设置时出错: %s", e)
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_font_settings()
    logging.info("\n=== 测试完成 ===")
