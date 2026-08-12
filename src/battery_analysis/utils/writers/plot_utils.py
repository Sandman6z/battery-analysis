"""
绘图工具函数模块

提供电池分析相关的绘图功能，包括坐标轴设置、样式配置等
"""

import math
import matplotlib.pyplot as plt
from battery_analysis.utils.exceptions import BatteryAnalysisException
from battery_analysis.utils.constants import CN_FONT_LIST

# 配置matplotlib支持中文显示
plt.rcParams['font.sans-serif'] = CN_FONT_LIST
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


def set_plt_axis(battery_type, max_xaxis):
    """根据数据最大值动态设置坐标轴，对所有电池类型统一处理。"""
    maxTicks = math.ceil(max_xaxis / 100) * 100
    if maxTicks < 100:
        maxTicks = 100

    # 根据 maxTicks 选择合适的步长
    step_ranges = [
        (200, 25),
        (500, 50),
        (1000, 100),
        (2000, 200),
        (3000, 300),
        (4000, 400),
        (float('inf'), 500),
    ]
    step = 100
    for max_range, step_value in step_ranges:
        if maxTicks <= max_range:
            step = step_value
            break

    x_start = max(10, int(maxTicks * 0.03))
    plt.axis([x_start, maxTicks, 1, 3])

    # 生成刻度
    x_ticks = [x_start]
    for i in range(1, 21):
        tick = i * step
        x_ticks.append(tick)
        if tick >= maxTicks:
            break

    plt.xticks(x_ticks)
