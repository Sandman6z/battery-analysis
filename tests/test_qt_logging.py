"""Qt 日志不依赖控制台标准流，并在两种启动路径中共用。"""

import logging
import sys

import pytest
from PyQt6.QtCore import QtMsgType

from battery_analysis.utils.qt_logging import qt_message_handler


@pytest.mark.parametrize(
    "mode, level",
    [
        (QtMsgType.QtDebugMsg, logging.DEBUG),
        (QtMsgType.QtInfoMsg, logging.INFO),
        (QtMsgType.QtWarningMsg, logging.WARNING),
        (QtMsgType.QtCriticalMsg, logging.ERROR),
        (QtMsgType.QtFatalMsg, logging.CRITICAL),
    ],
)
def test_qt_message_without_console(monkeypatch, caplog, mode, level):
    monkeypatch.setattr(sys, "stderr", None)
    with caplog.at_level(logging.DEBUG, logger="battery_analysis.utils.qt_logging"):
        qt_message_handler(mode, None, "Qt test message")
    assert any(r.message == "Qt test message" and r.levelno == level for r in caplog.records)


def test_known_harmless_message_is_filtered(caplog):
    qt_message_handler(
        QtMsgType.QtWarningMsg, None, "dataChanged() called with an invalid index range"
    )
    assert not caplog.records
