"""
倒计时提示弹框组件

统一实现"OK 按钮旁显示剩余秒数、到时间自动关闭、点击 OK 立即关闭"的确认弹框，
供规格方法默认确认、电池型号配置缺失提示等场景复用。
"""

from collections.abc import Callable

from PyQt6 import QtCore as QC
from PyQt6 import QtWidgets as QW


def show_countdown_notice(
    parent,
    *,
    title: str,
    text: str,
    timeout_seconds: int = 3,
    ok_text: str = "OK",
    extra_button: tuple[str, Callable[[], None]] | None = None,
) -> str:
    """显示带倒计时的确认弹框。

    - OK 按钮文案显示剩余秒数："OK (3)" → "OK (1)"；
    - 到时间自动关闭；点击 OK（或 Esc）立即关闭；
    - extra_button=(文案, 回调) 时追加一个动作按钮（倒计时不影响它），
      点击后关闭弹框并在弹框关闭后执行回调。

    Args:
        parent: 父窗口（None 时屏幕居中由 Qt 处理）。
        title: 弹框标题。
        text: 弹框正文。
        timeout_seconds: 自动关闭秒数；<=0 表示不自动关闭。
        ok_text: OK 按钮文案（不含秒数后缀）。
        extra_button: 可选追加按钮 (label, callback)。

    Returns:
        "ok"（用户点击 OK/Esc）/ "timeout"（倒计时到点自动关闭）/ "extra"（点击追加按钮）
    """
    box = QW.QMessageBox(parent)
    box.setWindowTitle(title)
    box.setText(text)
    box.setStandardButtons(QW.QMessageBox.StandardButton.Ok)
    box.setDefaultButton(QW.QMessageBox.StandardButton.Ok)
    ok_button = box.button(QW.QMessageBox.StandardButton.Ok)
    remaining = max(int(timeout_seconds), 0)
    result = {"value": "ok"}

    def _button_label(n: int) -> str:
        return f"{ok_text} ({n})" if n > 0 else ok_text

    if ok_button is not None and remaining > 0:
        ok_button.setText(_button_label(remaining))

    timer = QC.QTimer(box)
    timer.setInterval(1000)

    def _tick() -> None:
        nonlocal remaining
        remaining -= 1
        if remaining <= 0:
            timer.stop()
            result["value"] = "timeout"
            box.accept()
        elif ok_button is not None:
            ok_button.setText(_button_label(remaining))

    extra_btn = None
    if extra_button is not None:
        extra_btn = box.addButton(extra_button[0], QW.QMessageBox.ButtonRole.ActionRole)

    def _on_clicked(button) -> None:
        timer.stop()
        if extra_btn is not None and button is extra_btn:
            result["value"] = "extra"
            box.reject()
        else:
            result["value"] = "ok"

    box.buttonClicked.connect(_on_clicked)
    if remaining > 0:
        timer.timeout.connect(_tick)
        timer.start()

    # QMessageBox 无 aboutToShow 信号（PyQt6 中该信号属于 QMenu）；
    # 在 exec() 前用 adjustSize() 让布局确定尺寸，随后直接居中。
    box.adjustSize()
    if parent is not None:
        frame = box.frameGeometry()
        frame.moveCenter(parent.geometry().center())
        box.move(frame.topLeft())

    box.exec()
    timer.stop()

    if result["value"] == "extra" and extra_button is not None:
        extra_button[1]()
    return result["value"]
