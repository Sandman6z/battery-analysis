"""countdown_message_box 组件真实（offscreen）冒烟测试。

单元测试大多 mock 掉 show_countdown_notice，历史上漏掉了 QMessageBox 没有
clicked 信号的运行时崩溃（实际应为 buttonClicked），此文件以真实弹框回归。
"""

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QMessageBox

from battery_analysis.main.ui_components.countdown_message_box import show_countdown_notice


def _click_active_modal(button_getter, delay_ms=50):
    """在弹框显示后 delay_ms 毫秒点击其上的指定按钮。"""

    def _do_click():
        box = QApplication.activeModalWidget()
        assert isinstance(box, QMessageBox)
        button = button_getter(box)
        assert button is not None
        button.click()

    QTimer.singleShot(delay_ms, _do_click)


class TestCountdownNotice:
    def setup_method(self):
        if QApplication.instance() is None:
            self._test_app = QApplication([])

    def test_timeout_auto_closes(self):
        """到时间自动关闭，返回 timeout（真实 QTimer 走完倒计时）。"""
        result = show_countdown_notice(None, title="T", text="body", timeout_seconds=1)
        assert result == "timeout"

    def test_ok_click_closes_immediately(self):
        """点击 OK 立即关闭（不等倒计时），返回 ok。"""
        _click_active_modal(lambda box: box.button(QMessageBox.StandardButton.Ok))
        result = show_countdown_notice(None, title="T", text="body", timeout_seconds=10)
        assert result == "ok"

    def test_extra_button_runs_callback(self):
        """点击追加按钮 → 返回 extra 并执行回调。"""
        calls = []
        _click_active_modal(lambda box: box.buttons()[-1])
        result = show_countdown_notice(
            None,
            title="T",
            text="body",
            timeout_seconds=10,
            extra_button=("Go", lambda: calls.append("go")),
        )
        assert result == "extra"
        assert calls == ["go"]

    def test_ok_button_label_counts_down(self):
        """OK 按钮文案带剩余秒数：初始 OK (3)，1 秒后 OK (2)。"""
        labels = []
        box_at = lambda: QApplication.activeModalWidget()  # noqa: E731

        def _grab():
            box = box_at()
            if isinstance(box, QMessageBox):
                labels.append(box.button(QMessageBox.StandardButton.Ok).text())

        QTimer.singleShot(200, _grab)   # 未到第一次 tick → "OK (3)"
        QTimer.singleShot(1200, _grab)  # 过第一次 tick → "OK (2)"
        QTimer.singleShot(1500, lambda: box_at().accept())
        result = show_countdown_notice(None, title="T", text="body", timeout_seconds=3)
        assert result == "ok"
        assert labels == ["OK (3)", "OK (2)"]
