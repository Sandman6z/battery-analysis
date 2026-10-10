"""鼠标悬停数据提示（线性扫描版 + KDTree 加速版）

从 interaction_controls.py 拆出（大文件拆分重构）。
"""

import logging
import time

import numpy as np

from battery_analysis.main.visualization.interaction_utils import _select_hover_lines

logger = logging.getLogger(__name__)


class HoverControlsMixin:
    """悬停提示控件"""

    def _add_hover_functionality(self, fig, ax, lines_filtered, lines_unfiltered, check_filter):
        """添加鼠标悬停功能，显示数据点信息"""
        try:
            annot = ax.annotate(
                "",
                xy=(0, 0),
                xytext=(10, 10),
                textcoords="offset points",
                bbox=dict(boxstyle="round,pad=0.5", fc="yellow", alpha=0.7),
                arrowprops=dict(arrowstyle="->"),
            )
            annot.set_visible(False)

            def on_hover(event):
                if event.inaxes == ax:
                    current_lines = _select_hover_lines(
                        check_filter, lines_filtered, lines_unfiltered
                    )

                    min_dist = float("inf")
                    closest_point = None
                    closest_line_label = None

                    for line in current_lines:
                        if line.get_visible():
                            try:
                                x_data = line.get_xdata()
                                y_data = line.get_ydata()
                                line_label = line.get_label()

                                for i, (x, y) in enumerate(zip(x_data, y_data)):
                                    dist = ((x - event.xdata) ** 2 + (y - event.ydata) ** 2) ** 0.5
                                    if dist < min_dist and dist < 0.05 * (
                                        self.maxXaxis - self.listAxis[0]
                                    ):
                                        min_dist = dist
                                        closest_point = (x, y, i)
                                        closest_line_label = line_label
                            except (AttributeError, TypeError, ValueError, IndexError):
                                continue

                    if closest_point:
                        x, y, idx = closest_point
                        annot.xy = (x, y)

                        label_text = ""
                        if isinstance(closest_line_label, list) and len(closest_line_label) > 0:
                            label_text = f"{closest_line_label[0]}"
                            if len(closest_line_label) > 1:
                                label_text += f" ({closest_line_label[1]})"
                        else:
                            label_text = str(closest_line_label)

                        annot.set_text(
                            f"{label_text}\nPoint {idx}:\nCharge: {x:.2f} mAh\nVoltage: {y:.4f} V"
                        )
                        annot.set_visible(True)
                        fig.canvas.draw_idle()
                    else:
                        if annot.get_visible():
                            annot.set_visible(False)
                            fig.canvas.draw_idle()

            fig.canvas.mpl_connect("motion_notify_event", on_hover)

        except (AttributeError, TypeError, ValueError) as e:
            logger.warning("Error adding hover functionality: %s", e)

    def _build_kdtree_index(self, lines):
        """为可见曲线构建 KDTree 索引

        Args:
            lines: 曲线列表

        Returns:
            tuple: (kdtree, points_data) 或 (None, None)（失败时）
        """
        try:
            from scipy.spatial import cKDTree

            points = []
            points_data = []  # 存储每个点的元数据 (line_idx, point_idx, x, y, label)

            for line_idx, line in enumerate(lines):
                if line.get_visible():
                    try:
                        x_data = line.get_xdata()
                        y_data = line.get_ydata()
                        line_label = line.get_label()

                        for point_idx, (x, y) in enumerate(zip(x_data, y_data)):
                            points.append([x, y])
                            points_data.append((line_idx, point_idx, x, y, line_label))
                    except (AttributeError, TypeError, ValueError, IndexError):
                        continue

            if not points:
                return None, None

            points_array = np.array(points)
            kdtree = cKDTree(points_array)

            logger.info("KDTree index built with %d points", len(points))
            return kdtree, points_data

        except ImportError:
            logger.warning("scipy not available, falling back to linear search")
            return None, None
        except Exception as e:
            logger.error("Error building KDTree index: %s", e)
            return None, None

    def _find_nearest_point_kdtree(self, kdtree, points_data, x, y, max_dist):
        """使用 KDTree 查找最近点

        Args:
            kdtree: cKDTree 对象
            points_data: 点元数据列表
            x: 查询点 x 坐标
            y: 查询点 y 坐标
            max_dist: 最大距离阈值

        Returns:
            tuple: (line_idx, point_idx, x, y, label) 或 None（未找到时）
        """
        try:
            if kdtree is None:
                return None

            # 查询最近点
            dist, idx = kdtree.query([x, y])

            # 检查距离是否在阈值内
            if dist < max_dist:
                return points_data[idx]

            return None

        except Exception as e:
            logger.error("Error querying KDTree: %s", e)
            return None

    def _add_hover_functionality_kdtree(
        self, fig, ax, lines_filtered, lines_unfiltered, check_filter
    ):
        """添加鼠标悬停功能（KDTree 优化版本）

        使用 KDTree 进行 O(log n) 最近点查找，并添加鼠标移动节流。
        """
        try:
            from PyQt6.QtCore import QTimer

            annot = ax.annotate(
                "",
                xy=(0, 0),
                xytext=(10, 10),
                textcoords="offset points",
                bbox=dict(boxstyle="round,pad=0.5", fc="yellow", alpha=0.7),
                arrowprops=dict(arrowstyle="->"),
            )
            annot.set_visible(False)

            # KDTree 索引缓存
            kdtree_cache = {
                "filtered": {"kdtree": None, "points_data": None},
                "unfiltered": {"kdtree": None, "points_data": None},
            }

            # 节流控制
            throttle_state = {
                "last_update_time": 0,
                "min_interval": 0.05,  # 50ms 最小间隔
                "pending_event": None,
                "timer": None,
            }

            def rebuild_kdtree_if_needed():
                """重建 KDTree 索引（如果曲线可见性发生变化）"""
                current_lines = _select_hover_lines(check_filter, lines_filtered, lines_unfiltered)

                # 确定当前使用的缓存键
                is_filtered = True
                if check_filter is not None and isinstance(check_filter, dict):
                    is_filtered = check_filter.get("active", True)
                cache_key = "filtered" if is_filtered else "unfiltered"

                # 重建 KDTree
                kdtree, points_data = self._build_kdtree_index(current_lines)
                kdtree_cache[cache_key] = {"kdtree": kdtree, "points_data": points_data}

                return kdtree, points_data

            def on_hover(event):
                """鼠标悬停事件处理（带节流）"""
                if event.inaxes != ax:
                    if annot.get_visible():
                        annot.set_visible(False)
                        fig.canvas.draw_idle()
                    return

                # 节流：检查是否需要延迟处理
                current_time = time.time()
                time_since_last = current_time - throttle_state["last_update_time"]

                if time_since_last < throttle_state["min_interval"]:
                    # 还在节流间隔内，保存事件并设置定时器
                    throttle_state["pending_event"] = event

                    # 如果没有活跃的定时器，创建一个
                    if throttle_state["timer"] is None:
                        delay_ms = int((throttle_state["min_interval"] - time_since_last) * 1000)
                        throttle_state["timer"] = QTimer.singleShot(
                            delay_ms, lambda: process_hover_event(throttle_state["pending_event"])
                        )
                    return

                # 直接处理事件
                process_hover_event(event)

            def process_hover_event(event):
                """处理悬停事件"""
                if event is None or event.inaxes != ax:
                    return

                # 更新最后处理时间
                throttle_state["last_update_time"] = time.time()
                throttle_state["pending_event"] = None
                throttle_state["timer"] = None

                # 确定当前应该操作哪组曲线
                is_filtered = True
                if check_filter is not None and isinstance(check_filter, dict):
                    is_filtered = check_filter.get("active", True)
                cache_key = "filtered" if is_filtered else "unfiltered"

                # 获取或重建 KDTree
                cache = kdtree_cache[cache_key]
                if cache["kdtree"] is None:
                    kdtree, points_data = rebuild_kdtree_if_needed()
                else:
                    kdtree = cache["kdtree"]
                    points_data = cache["points_data"]

                # 计算最大距离阈值（相对于坐标轴范围）
                max_dist = 0.05 * (self.maxXaxis - self.listAxis[0])

                # 使用 KDTree 查找最近点
                result = self._find_nearest_point_kdtree(
                    kdtree, points_data, event.xdata, event.ydata, max_dist
                )

                if result:
                    line_idx, point_idx, x, y, label = result
                    annot.xy = (x, y)

                    label_text = ""
                    if isinstance(label, list) and len(label) > 0:
                        label_text = f"{label[0]}"
                        if len(label) > 1:
                            label_text += f" ({label[1]})"
                    else:
                        label_text = str(label)

                    annot.set_text(
                        f"{label_text}\nPoint {point_idx}:\nCharge: {x:.2f} mAh\nVoltage: {y:.4f} V"
                    )
                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                else:
                    if annot.get_visible():
                        annot.set_visible(False)
                        fig.canvas.draw_idle()

            # 连接事件
            fig.canvas.mpl_connect("motion_notify_event", on_hover)

            # 保存 KDTree 缓存引用以便后续更新
            self._kdtree_cache = kdtree_cache

            logger.info("KDTree hover functionality added successfully")

        except (AttributeError, TypeError, ValueError) as e:
            logger.warning("Error adding KDTree hover functionality: %s", e)
            # 回退到普通 hover
            self._add_hover_functionality(fig, ax, lines_filtered, lines_unfiltered, check_filter)
