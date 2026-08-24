import pytest
from unittest.mock import Mock, patch
from PyQt6.QtWidgets import QApplication
from battery_analysis.main.ui_components.progress_dialog import ProgressDialog


class TestProgressDialog:
    def setup_method(self):
        # 确保 QApplication 存在（测试自包含，不依赖其他测试模块）
        if QApplication.instance() is None:
            self._test_app = QApplication([])
        self.dialog = ProgressDialog()

    def test_update_progress(self):
        progress = 50
        message = "Test progress"
        # update_progress 更新状态文本与窗口标题（返回 None，不返回布尔值）
        self.dialog.update_progress(progress, message)
        assert self.dialog.status_label.text() == message
        assert self.dialog.windowTitle().endswith(f"{progress}%")

    def test_close_dialog(self):
        # 关闭对话框使用标准 Qt close()（原 close_dialog 方法已移除）
        self.dialog.close()
        assert not self.dialog.isVisible()

    def test_set_range(self):
        # 进度条范围使用 Qt 原生 setRange（原 set_range 方法已移除）
        self.dialog.progress_bar.setRange(0, 100)
        assert self.dialog.progress_bar.minimum() == 0
        assert self.dialog.progress_bar.maximum() == 100

    def test_update_progress_does_not_process_events(self):
        """update_progress 不调用 processEvents（防重入，roadmap #12）"""
        with patch('battery_analysis.main.ui_components.progress_dialog.QW.QApplication.processEvents') as mock_pe:
            self.dialog.update_progress(50, "Test progress")
            mock_pe.assert_not_called()

    def test_on_cancel_does_not_process_events(self):
        """_on_cancel 不调用 processEvents"""
        with patch('battery_analysis.main.ui_components.progress_dialog.QW.QApplication.processEvents') as mock_pe:
            self.dialog._on_cancel()
            mock_pe.assert_not_called()
