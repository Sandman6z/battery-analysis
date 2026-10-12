"""
交互控件模块（汇总入口）

提供现代化按钮、菜单栏、过滤切换、电池选择、悬停等功能。
原 1136 行大文件按功能拆分为多个子模块，本文件仅保留：
- 两个模块级纯函数（对外导出，测试依赖）
- 生命周期方法 __del__
- 汇总各子 Mixin 的 InteractionControlsMixin

子模块：
- interaction_utils     纯函数
- button_widgets        图内按钮构件
- filter_controls       过滤切换控件
- battery_selection     电池选择控件
- hover_controls        悬停提示（线性 / KDTree）
- viewer_controls       菜单栏 / 文件操作 / About
"""

import logging

import matplotlib.pyplot as plt

from battery_analysis.main.visualization.battery_selection import BatterySelectionMixin
from battery_analysis.main.visualization.button_widgets import ButtonFactoryMixin
from battery_analysis.main.visualization.filter_controls import FilterControlsMixin
from battery_analysis.main.visualization.hover_controls import HoverControlsMixin
from battery_analysis.main.visualization.interaction_utils import (
    _battery_line_indices,
    _select_hover_lines,
)
from battery_analysis.main.visualization.viewer_controls import ViewerControlsMixin

__all__ = ["InteractionControlsMixin", "_battery_line_indices", "_select_hover_lines"]

logger = logging.getLogger(__name__)


class InteractionControlsMixin(
    ButtonFactoryMixin,
    FilterControlsMixin,
    BatterySelectionMixin,
    HoverControlsMixin,
    ViewerControlsMixin,
):
    """交互控件混入类，提供按钮、菜单、悬停等交互功能

    由下列子 Mixin 组合（基类顺序即 MRO 顺序）：
    - ButtonFactoryMixin:     图内现代化按钮 / 切换按钮组
    - FilterControlsMixin:    过滤切换（图内按钮 + QCheckBox）
    - BatterySelectionMixin:  电池通道选择（图内按钮列 + QCheckBox 列表）
    - HoverControlsMixin:     悬停数据提示（线性 / KDTree）
    - ViewerControlsMixin:    菜单栏、文件操作、帮助文本、About
    各子 Mixin 通过 self 互相调用（按钮创建依赖 ChartStylingMixin 的样式方法）。
    """

    def __del__(self):
        """析构函数，确保在对象销毁时释放所有资源"""
        try:
            if hasattr(self, "current_fig") and self.current_fig is not None:
                plt.close(self.current_fig)
                self.current_fig = None
                logger.info("Destructor: closing chart window")

            if hasattr(self, "_cleanup_matplotlib_state"):
                self._cleanup_matplotlib_state()
                logger.info("Destructor: cleaning up Matplotlib state")

            if hasattr(self, "listPlt"):
                try:
                    for c in range(len(self.listPlt)):
                        if len(self.listPlt[c]) >= 4:
                            self.listPlt[c][0].clear()
                            self.listPlt[c][1].clear()
                            self.listPlt[c][2].clear()
                            self.listPlt[c][3].clear()
                    logger.info("Destructor: releasing data resources")
                except Exception as e:
                    logger.error("Destructor: error releasing data resources: %s", e)

            logger.info("BatteryChartViewer object destroyed, resources released")
        except Exception as e:
            logger.error("Destructor execution exception: %s", e)
