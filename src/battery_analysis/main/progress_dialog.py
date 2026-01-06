"""
进度对话框模块

这个模块实现了电池分析应用的进度对话框功能，包括：
- 弹出式进度条对话框
- 进度更新和状态显示
- 取消功能支持
- 适合长时间运行的任务
"""

# 标准库导入
import logging

# 第三方库导入
import PyQt6.QtCore as QC
import PyQt6.QtGui as QG
import PyQt6.QtWidgets as QW

# 本地应用/库导入
from battery_analysis.i18n.language_manager import _


class ProgressDialog(QW.QDialog):
    """
    弹出式进度条对话框类

    用于显示详细的进度信息，适合长时间运行的任务
    """
    
    # 信号定义
    canceled = QC.pyqtSignal()  # 取消信号

    def __init__(self, parent=None):
        """
        初始化弹出式进度条

        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        self.setWindowTitle(_("progress_title", "Battery Analysis Progress"))
        self.setModal(False)  # Non-modal window, allows user to operate main interface
        self.setFixedSize(450, 150)
        self.setWindowFlags(QC.Qt.WindowType.Window | QC.Qt.WindowType.WindowTitleHint |
                            QC.Qt.WindowType.WindowCloseButtonHint |
                            QC.Qt.WindowType.WindowStaysOnTopHint |
                            QC.Qt.WindowType.WindowMinimizeButtonHint)
        
        # 设置窗口样式
        self.setObjectName("progress_dialog")

        # 创建布局
        layout = QW.QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 添加状态文本标签
        self.status_label = QW.QLabel(_("progress_ready", "Ready to start analysis..."))
        self.status_label.setAlignment(QC.Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setObjectName("progress_status_label")
        layout.addWidget(self.status_label)

        # 添加进度条
        self.progress_bar = QW.QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setAlignment(QC.Qt.AlignmentFlag.AlignCenter)
        self.progress_bar.setObjectName("progress_bar")
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)
        
        # 添加底部按钮布局
        button_layout = QW.QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setAlignment(QC.Qt.AlignmentFlag.AlignCenter)
        
        # 添加取消按钮
        self.cancel_button = QW.QPushButton(_("cancel", "Cancel"))
        self.cancel_button.setObjectName("cancel_button")
        self.cancel_button.setMinimumHeight(32)
        self.cancel_button.setMinimumWidth(100)
        self.cancel_button.clicked.connect(self._on_cancel)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)

        # 设置布局
        self.setLayout(layout)
        
        # 取消标志
        self.is_canceled = False

    def update_progress(self, progress, status_text):
        """
        更新进度信息

        Args:
            progress: 进度值
            status_text: 状态文本
        """
        self.progress_bar.setValue(progress)
        self.status_label.setText(status_text)
        
        # 更新窗口标题，显示百分比
        self.setWindowTitle(f"{_("progress_title", "Battery Analysis Progress")} - {progress}%")

        # 确保界面实时更新
        QW.QApplication.processEvents()

    def _on_cancel(self):
        """
        处理取消按钮点击事件
        """
        self.is_canceled = True
        self.canceled.emit()
        self.status_label.setText(_("progress_canceled", "Task canceled..."))
        QW.QApplication.processEvents()

    def closeEvent(self, event):
        """
        关闭事件处理

        Args:
            event: 关闭事件
        """
        # 这里可以添加关闭时的处理逻辑
        event.accept()
