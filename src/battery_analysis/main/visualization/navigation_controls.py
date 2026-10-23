"""Matplotlib 图表导航：绘图区平移、刻度区单轴平移、滚轮缩放及复位。"""

import numpy as np
from matplotlib.backend_bases import MouseButton
from matplotlib.text import Annotation
from matplotlib.transforms import Bbox
from PyQt6.QtCore import QEvent, QObject


def navigation_active(canvas):
    """悬停回调（包括延迟回调）在任何导航模式下都应停止扫描。"""
    navigator = getattr(canvas, "_battery_navigation", None)
    toolbar = getattr(canvas, "toolbar", None)
    return bool(
        (navigator is not None and navigator.drag is not None)
        or (toolbar is not None and toolbar.mode)
        or canvas.widgetlock.locked()
    )


class ChartNavigation(QObject):
    """由 canvas 强引用；拖动使用起始变换，避免随视野更新累积误差。"""

    def __init__(self, canvas, ax):
        super().__init__(canvas)
        self.canvas = canvas
        self.ax = ax
        self.initial_limits = (ax.get_xlim(), ax.get_ylim())
        self.drag = None
        self.cids = [
            canvas.mpl_connect(name, callback)
            for name, callback in (
                ("button_press_event", self.on_press),
                ("motion_notify_event", self.on_motion),
                ("button_release_event", self.on_release),
                ("scroll_event", self.on_scroll),
                ("close_event", self.disconnect),
            )
        ]
        canvas.installEventFilter(self)
        self.window = canvas.window()
        if self.window is not canvas:
            self.window.installEventFilter(self)

    def eventFilter(self, watched, event):
        if event.type() in (
            QEvent.Type.FocusOut, QEvent.Type.WindowDeactivate, QEvent.Type.Hide,
        ):
            self.on_release(None)
        return False

    def region(self, event):
        """刻度标签在 ax.bbox 之外，不能用 inaxes 判定轴带。"""
        if event.x is None or event.y is None:
            return None
        if event.inaxes is not None and event.inaxes is not self.ax:
            return None  # 图内按钮及其他辅助轴优先。
        bbox = self.ax.bbox
        if bbox.contains(event.x, event.y):
            return "both"
        renderer = self.canvas.get_renderer()
        pad = renderer.points_to_pixels(6)
        hits = []
        for axis, direction in ((self.ax.xaxis, "x"), (self.ax.yaxis, "y")):
            boxes = [
                label.get_window_extent(renderer)
                for label in axis.get_ticklabels()
                if label.get_visible() and label.get_text()
            ]
            if not boxes:
                continue
            ticks = Bbox.union(boxes)
            if direction == "x":
                band = Bbox.from_extents(
                    bbox.x0, min(ticks.y0, bbox.y0) - pad,
                    bbox.x1, max(ticks.y1, bbox.y0) + pad,
                )
            else:
                band = Bbox.from_extents(
                    min(ticks.x0, bbox.x0) - pad, bbox.y0,
                    max(ticks.x1, bbox.x0) + pad, bbox.y1,
                )
            if band.contains(event.x, event.y):
                hits.append(direction)
        return hits[0] if len(hits) == 1 else None

    def available(self):
        return not navigation_active(self.canvas)

    def hide_annotations(self):
        for text in self.ax.texts:
            if isinstance(text, Annotation):
                text.set_visible(False)

    def push_history(self, start=False):
        toolbar = getattr(self.canvas, "toolbar", None)
        if toolbar is not None:
            # 与标准 Pan 一样，仅在历史为空时补起点，避免每次操作产生重复项。
            if not start or toolbar._nav_stack() is None:
                toolbar.push_current()

    def on_press(self, event):
        if not self.available():
            return
        region = self.region(event)
        if region is None:
            return
        if event.button == MouseButton.RIGHT:
            self.push_history(start=True)
            self.ax.set_xlim(self.initial_limits[0])
            self.ax.set_ylim(self.initial_limits[1])
            self.hide_annotations()
            self.push_history()
            self.canvas.draw_idle()
        elif event.button == MouseButton.LEFT:
            self.canvas.widgetlock(self)
            self.drag = (
                region, event.x, event.y, self.ax.transData.frozen(),
                self.ax.bbox.frozen(), False,
            )
            self.hide_annotations()
            self.canvas.draw_idle()

    def on_motion(self, event):
        if self.drag is None or event.x is None or event.y is None:
            return
        region, x, y, transform, bbox, moved = self.drag
        dx, dy = event.x - x, event.y - y
        if not moved:
            if abs(dx) + abs(dy) < 3:
                return
            self.push_history(start=True)
            self.drag = (region, x, y, transform, bbox, True)
        points = transform.inverted().transform(
            [[bbox.x0 - dx, bbox.y0 - dy], [bbox.x1 - dx, bbox.y1 - dy]]
        )
        if not np.isfinite(points).all():
            return
        if region in ("x", "both"):
            self.ax.set_xlim(points[:, 0])
        if region in ("y", "both"):
            self.ax.set_ylim(points[:, 1])
        self.canvas.draw_idle()

    def on_release(self, event):
        if self.drag is None:
            return
        moved = self.drag[-1]
        self.drag = None
        if self.canvas.widgetlock.isowner(self):
            self.canvas.widgetlock.release(self)
        if moved:
            self.push_history()

    def on_scroll(self, event):
        if not self.available() or not np.isfinite(event.step) or not event.step:
            return
        region = self.region(event)
        if region is None:
            return
        anchor = self.ax.transData.inverted().transform((event.x, event.y))
        factor = 1.2 ** -np.clip(event.step, -20, 20)
        limits = []
        for index, axis in enumerate((self.ax.xaxis, self.ax.yaxis)):
            # 在尺度空间计算，也保持倒置轴方向；不依赖轴外的 xdata/ydata。
            transform = axis.get_transform()
            old = (self.ax.get_xlim(), self.ax.get_ylim())[index]
            scaled = transform.transform(np.array([*old, anchor[index]]))
            new = transform.inverted().transform(
                scaled[2] + (scaled[:2] - scaled[2]) * factor
            )
            if not np.isfinite(new).all() or new[0] == new[1]:
                return
            limits.append(new)
        self.push_history(start=True)
        if region in ("x", "both"):
            self.ax.set_xlim(limits[0])
        if region in ("y", "both"):
            self.ax.set_ylim(limits[1])
        self.hide_annotations()
        self.push_history()
        self.canvas.draw_idle()

    def disconnect(self, event=None):
        self.on_release(None)
        for cid in self.cids:
            self.canvas.mpl_disconnect(cid)
        self.cids.clear()
        self.canvas.removeEventFilter(self)
        if self.window is not self.canvas:
            self.window.removeEventFilter(self)


def install_navigation(fig, ax):
    """两种宿主共享交互，重复安装时先断开旧控制器。"""
    canvas = fig.canvas
    previous = getattr(canvas, "_battery_navigation", None)
    if previous is not None:
        previous.disconnect()
        previous.deleteLater()
    canvas._battery_navigation = ChartNavigation(canvas, ax)
    return canvas._battery_navigation
