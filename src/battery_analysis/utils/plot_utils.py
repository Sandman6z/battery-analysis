import math
import matplotlib.pyplot as plt

# 配置matplotlib支持中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans', 'Arial', 'Times New Roman']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

from battery_analysis.utils.exception_type import BatteryAnalysisException


"""
绘图工具函数模块

提供电池分析相关的绘图功能，包括坐标轴设置、样式配置等
"""


def set_plt_axis(battery_type, max_xaxis):
    if battery_type == "Coin Cell":
        plt.axis([10, 600, 1, 3])
        x_ticks = [10, 100, 200, 300, 400, 500, 600]
    elif battery_type == "Pouch Cell":
        maxTicks = math.ceil(max_xaxis/100)*100
        plt.axis([20, maxTicks, 1, 3])
        x_ticks = [20]
        
        # 根据maxTicks选择合适的步长
        step_ranges = [
            (1000, 100),
            (2000, 200),
            (3000, 300),
            (4000, 400),
            (float('inf'), 500)
        ]
        
        step = 100  # 默认步长
        for max_range, step_value in step_ranges:
            if maxTicks <= max_range:
                step = step_value
                break
        
        # 生成刻度
        for i in range(1, 11):
            tick = i * step
            x_ticks.append(tick)
            if tick >= maxTicks:
                break
    else:
        raise BatteryAnalysisException(
            "[Plt LoadVoltageOverCharge Error]: Unknown battery type")
    plt.xticks(x_ticks)
