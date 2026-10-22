"""开发与无控制台 EXE 共用的 Qt 消息处理器。"""

import logging

from PyQt6.QtCore import QtMsgType

logger = logging.getLogger(__name__)


def qt_message_handler(mode, context, message):
    """过滤已知无害消息，其余写日志，不依赖 sys.stderr。"""
    if "dataChanged() called with an invalid index range" in message:
        return
    levels = {
        QtMsgType.QtDebugMsg: logging.DEBUG,
        QtMsgType.QtInfoMsg: logging.INFO,
        QtMsgType.QtWarningMsg: logging.WARNING,
        QtMsgType.QtCriticalMsg: logging.ERROR,
        QtMsgType.QtFatalMsg: logging.CRITICAL,
    }
    logger.log(levels.get(mode, logging.WARNING), "%s", message)
