"""图表交互纯函数（从 interaction_controls.py 拆出）"""

import logging

logger = logging.getLogger(__name__)


def _battery_line_indices(battery_index, current_level_num):
    """返回属于指定电池的所有曲线索引。

    曲线按电池主序构建（figure_builder 中 line = b*current_level + c），
    因此电池 b 的曲线索引区间为 [b*level, (b+1)*level)。
    """
    start = battery_index * current_level_num
    return range(start, start + current_level_num)


def _select_hover_lines(check_filter, lines_filtered, lines_unfiltered):
    """根据过滤按钮状态选择悬停应扫描的曲线集合。

    修复：check_filter 实为过滤按钮状态 dict（含 'active' 键），
    旧代码对其调用 .get_status() 必抛 AttributeError，导致悬停永远扫描 Filtered 曲线。
    """
    filtered = True
    if check_filter is not None and isinstance(check_filter, dict):
        filtered = check_filter.get("active", True)
    return lines_filtered if filtered else lines_unfiltered
