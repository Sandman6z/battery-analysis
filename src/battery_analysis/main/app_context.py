# -*- coding: utf-8 -*-
"""
应用上下文模块

解耦 Manager 与 MainWindow 的中间层。
Manager 通过 AppContext 访问服务和有限的 UI 操作，
不再直接引用 MainWindow 的控件。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional, Any


# ── 路径上下文 ──────────────────────────────────────────────────


@dataclass
class PathContext:
    """当前项目的输入/输出路径。"""
    project_path: str = ""
    input_path: str = ""
    output_path: str = ""


# ── UI 桥接 — Manager 可调用的 UI 操作 ─────────────────────────


class UIBridge:
    """Manager -> UI 的有限接口。

    MainWindow 在初始化时创建 UIBridgeImpl 实例并传入 AppContext，
    Manager 只能通过此桥操作 UI——不能直接访问 MainWindow 的控件树。
    """

    def show_message(self, title: str, message: str) -> None:
        raise NotImplementedError

    def show_warning(self, title: str, message: str) -> None:
        raise NotImplementedError

    def show_critical(self, title: str, message: str) -> None:
        raise NotImplementedError

    def update_statusbar(self, message: str) -> None:
        raise NotImplementedError

    def get_combo_text(self, widget_name: str) -> str:
        """获取 ComboBox 当前文本（如 'BatteryType'）。"""
        raise NotImplementedError

    def get_lineedit_text(self, widget_name: str) -> str:
        """获取 QLineEdit 当前文本（如 'InputPath'）。"""
        raise NotImplementedError

    def set_pushbutton_enabled(self, widget_name: str, enabled: bool) -> None:
        """启用/禁用按钮。"""
        raise NotImplementedError

    def get_widget_value(self, widget_name: str) -> Any:
        """通用获取控件值（转型为具体类型）。"""
        raise NotImplementedError


# ── UI 桥接 默认实现 ──────────────────────────────────────────


class UIBridgeImpl(UIBridge):
    """UIBridge 的 MainWindow 绑定实现。"""

    def __init__(self, main_window):
        self._mw = main_window
        self._logger = logging.getLogger(__name__)

    def show_message(self, title: str, message: str) -> None:
        from PyQt6 import QtWidgets as QW
        QW.QMessageBox.information(self._mw, title, message)

    def show_warning(self, title: str, message: str) -> None:
        from PyQt6 import QtWidgets as QW
        QW.QMessageBox.warning(self._mw, title, message)

    def show_critical(self, title: str, message: str) -> None:
        from PyQt6 import QtWidgets as QW
        QW.QMessageBox.critical(self._mw, title, message)

    def update_statusbar(self, message: str) -> None:
        if hasattr(self._mw, 'statusBar_BatteryAnalysis'):
            self._mw.statusBar_BatteryAnalysis.showMessage(message)

    def get_combo_text(self, widget_name: str) -> str:
        attr = f"comboBox_{widget_name}"
        combo = getattr(self._mw, attr, None)
        if combo is None:
            self._logger.warning("UIBridge: ComboBox '%s' not found", widget_name)
            return ""
        return combo.currentText()

    def get_lineedit_text(self, widget_name: str) -> str:
        attr = f"lineEdit_{widget_name}"
        le = getattr(self._mw, attr, None)
        if le is None:
            self._logger.warning("UIBridge: LineEdit '%s' not found", widget_name)
            return ""
        return le.text()

    def set_pushbutton_enabled(self, widget_name: str, enabled: bool) -> None:
        attr = f"pushButton_{widget_name}"
        btn = getattr(self._mw, attr, None)
        if btn is not None:
            btn.setEnabled(enabled)

    def get_widget_value(self, widget_name: str) -> Any:
        """依次尝试 ComboBox / QLineEdit / 普通属性。"""
        for prefix in ("comboBox_", "lineEdit_", ""):
            attr = prefix + widget_name
            w = getattr(self._mw, attr, None)
            if w is not None:
                if hasattr(w, 'currentText'):
                    return w.currentText()
                if hasattr(w, 'text'):
                    return w.text()
                return w
        self._logger.warning("UIBridge: widget '%s' not found", widget_name)
        return ""


# ── 应用上下文 ──────────────────────────────────────────────────


@dataclass
class AppContext:
    """Manager 可获取的全部上下文。

    替代将 main_window 传给 Manager 构造函数的做法。
    """
    services: Any = None           # Services 实例
    ui: Optional[UIBridge] = None  # UI 桥接
    paths: PathContext = field(default_factory=PathContext)
    test_info: Optional[Any] = None  # TestInfo 实例或 list

    def get_service(self, name: str) -> Any:
        if self.services is None:
            return None
        if hasattr(self.services, 'get'):
            return self.services.get(name)
        return getattr(self.services, name, None)
