"""Standalone NDAX converter window — optional batch export to .xlsx.

Provides a full-page interface for selecting folders, viewing NDAX files,
and running batch conversion with progress tracking.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import PyQt6.QtCore as QC
import PyQt6.QtGui as QG
import PyQt6.QtWidgets as QW

from battery_analysis.i18n import _
from battery_analysis.ndax.converter import get_ndax_files
from battery_analysis.ndax.worker import ConvertWorker


def _now() -> str:
    """Get current timestamp as formatted string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M")


class NdaxConverterWindow(QW.QWidget):
    """NDAX → XLSX converter, independent of the main analysis workflow."""

    COL_NAME = 0
    COL_STATUS = 1

    def __init__(self, parent=None):
        super().__init__(parent, QC.Qt.WindowType.Window)
        self.setWindowTitle(_("NDAX Converter"))
        self.setMinimumSize(640, 480)
        self.resize(900, 700)
        self.input_dir: Path | None = None
        self.out_dir: Path | None = None
        self.ndax_files: list[Path] = []
        self.worker: ConvertWorker | None = None
        self._force_overwrite: bool = False

        self._build_ui()

    def _build_ui(self) -> None:
        """Build the user interface."""
        layout = QW.QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # ── 标题栏 ──
        title = QW.QLabel(_("NDAX → XLSX Batch Conversion"))
        title.setFont(QG.QFont("Microsoft YaHei UI", 14, QG.QFont.Weight.Bold))
        title.setAlignment(QC.Qt.AlignmentFlag.AlignLeft | QC.Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(title)

        desc = QW.QLabel(_("Optional export tool: batch convert NDAX files to Excel. The main analysis reads NDAX directly; no conversion is required."))
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #666;")
        layout.addWidget(desc)

        layout.addSpacing(5)

        # ── 文件夹选择行 ──
        folder_row = QW.QHBoxLayout()
        self.btn_select = QW.QPushButton(_("📁 Select Folder"))
        self.btn_select.setMinimumHeight(36)
        self.btn_select.setFont(QG.QFont("Microsoft YaHei UI", 10))
        self.btn_select.setCursor(QG.QCursor(QC.Qt.CursorShape.PointingHandCursor))
        self.btn_select.clicked.connect(self._select_folder)

        self.edit_path = QW.QLineEdit()
        self.edit_path.setReadOnly(True)
        self.edit_path.setPlaceholderText(_("Select a folder containing .ndax files..."))
        self.edit_path.setMinimumHeight(36)

        folder_row.addWidget(self.btn_select)
        folder_row.addWidget(self.edit_path, 1)
        layout.addLayout(folder_row)

        # ── 文件列表 ──
        self.table = QW.QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels([_("File Name"), _("Status")])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(
            0, QW.QHeaderView.ResizeMode.Stretch
        )
        self.table.setEditTriggers(QW.QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #faf7f2;
                alternate-background-color: #f0ece4;
                color: #3d3229;
                gridline-color: #e0d8cc;
            }
            QHeaderView::section {
                background-color: #e8e2d8;
                color: #3d3229;
                padding: 4px;
                border: 1px solid #d0c8b8;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.table, stretch=1)

        # ── 进度条 ──
        self.progress_bar = QW.QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumHeight(20)
        layout.addWidget(self.progress_bar)

        # ── 底部操作行 ──
        bottom_row = QW.QHBoxLayout()

        self.btn_start = QW.QPushButton(_("▶ Start Conversion"))
        self.btn_start.setMinimumHeight(36)
        self.btn_start.setMinimumWidth(160)
        self.btn_start.setFont(QG.QFont("Microsoft YaHei UI", 10, QG.QFont.Weight.Bold))
        self.btn_start.setCursor(QG.QCursor(QC.Qt.CursorShape.PointingHandCursor))
        self.btn_start.clicked.connect(self._start_convert)
        self.btn_start.setEnabled(False)

        self.lbl_summary = QW.QLabel("")
        self.lbl_summary.setStyleSheet("color: #555;")

        bottom_row.addWidget(self.btn_start)
        bottom_row.addWidget(self.lbl_summary, stretch=1)
        layout.addLayout(bottom_row)

        # ── 日志区域 ──
        self.log_area = QW.QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMaximumHeight(150)
        self.log_area.setFont(QG.QFont("Consolas", 9))
        layout.addWidget(self.log_area)

    # ─────────────────────────────────────────────────────
    #  文件夹选择与已有文件检测
    # ─────────────────────────────────────────────────────

    def _select_folder(self) -> None:
        """Open folder selection dialog and load NDAX files."""
        folder = QW.QFileDialog.getExistingDirectory(self, _("Select NDAX Folder"))
        if not folder:
            return

        self.input_dir = Path(folder)
        self.out_dir = self.input_dir.parent / "2_xlsx"
        self.edit_path.setText(str(self.input_dir))

        self.ndax_files = [self.input_dir / p for p in get_ndax_files(folder)]
        self._refresh_file_list()
        self.log_area.clear()

        if not self.ndax_files:
            self.btn_start.setEnabled(False)
            self.log_area.append(f"[{_now()}] " + _("No NDAX files found"))
            return

        self.log_area.append(
            f"[{_now()}] " + _("Loaded {count} NDAX files").format(count=len(self.ndax_files))
        )
        self.log_area.append(f"[{_now()}] " + _("Output folder: {path}").format(path=self.out_dir))

        # 检查 2_xlsx 是否已有 xlsx 文件
        # 按钮始终可用
        self.btn_start.setEnabled(True)

    def _check_existing_xlsx(self) -> bool:
        """Check if 2_xlsx directory already has xlsx files."""
        if not self.out_dir or not self.out_dir.exists():
            return False
        return any(self.out_dir.glob("*.xlsx"))

    # ─────────────────────────────────────────────────────
    #  转换流程
    # ─────────────────────────────────────────────────────

    def _refresh_file_list(self) -> None:
        """Refresh the file list table with current NDAX files."""
        self.table.setRowCount(len(self.ndax_files))
        for i, f in enumerate(self.ndax_files):
            name_item = QW.QTableWidgetItem(f.name)
            self.table.setItem(i, self.COL_NAME, name_item)

            xlsx_path = self.out_dir / f"{f.stem}.xlsx" if self.out_dir else None
            if xlsx_path and xlsx_path.exists():
                status_item = QW.QTableWidgetItem(_("Already Exists"))
                status_item.setForeground(QC.Qt.GlobalColor.gray)
            else:
                status_item = QW.QTableWidgetItem(_("Ready"))
                status_item.setForeground(QC.Qt.GlobalColor.darkGreen)
            self.table.setItem(i, self.COL_STATUS, status_item)

        self.lbl_summary.setText(_("Total files: {count}").format(count=len(self.ndax_files)))

    def _update_status_ui(self, converting: bool) -> None:
        """Update UI elements based on conversion state."""
        self.btn_select.setEnabled(not converting)
        self.btn_start.setEnabled(not converting and len(self.ndax_files) > 0)
        self.progress_bar.setVisible(converting)

    def _start_convert(self) -> None:
        """Start the batch conversion process."""
        if not self.input_dir or not self.out_dir:
            return

        # 检查是否已有转换文件，提示覆盖确认
        self._force_overwrite = False
        if self._check_existing_xlsx():
            reply = QW.QMessageBox.question(
                self,
                _("Confirm Overwrite"),
                _("Converted files already exist in the 2_xlsx folder. Continuing will overwrite existing files. Continue?"),
                QW.QMessageBox.StandardButton.Yes | QW.QMessageBox.StandardButton.No,
                QW.QMessageBox.StandardButton.No,
            )
            if reply != QW.QMessageBox.StandardButton.Yes:
                return
            self._force_overwrite = True

        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.log_area.clear()
        self.log_area.append(f"[{_now()}] " + _("Starting batch conversion..."))

        self._update_status_ui(True)
        self.progress_bar.setMaximum(len(self.ndax_files))
        self.progress_bar.setValue(0)

        self.worker = ConvertWorker(self.ndax_files, self.out_dir, force=self._force_overwrite)
        self.worker.progress.connect(self._on_progress)
        self.worker.file_status.connect(self._on_file_status)
        self.worker.log.connect(self.log_area.append)
        self.worker.finished_signal.connect(self._on_finished)
        self.worker.start()

        self.btn_start.setEnabled(True)
        self.btn_start.setText(_("■ Cancel"))
        self.btn_start.clicked.disconnect()
        self.btn_start.clicked.connect(self._cancel_convert)

    def _cancel_convert(self) -> None:
        """Cancel the ongoing conversion process."""
        if self.worker:
            self.worker.cancel()
        self.btn_start.setEnabled(False)
        self.btn_start.setText(_("Cancelling..."))

    def _on_progress(self, current: int, total: int) -> None:
        """Handle progress updates from worker thread."""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)

    def _on_file_status(self, row: int, status: str) -> None:
        """Handle file status updates from worker thread."""
        item = self.table.item(row, self.COL_STATUS)
        if item:
            item.setText(status)
            if status == _("Success"):
                item.setForeground(QC.Qt.GlobalColor.darkGreen)
            elif status == _("Failed"):
                item.setForeground(QC.Qt.GlobalColor.red)
            elif status == _("Skipped"):
                item.setForeground(QC.Qt.GlobalColor.gray)

    def _on_finished(self, result: dict) -> None:
        """Handle conversion completion."""
        self._update_status_ui(False)
        self.btn_start.setText(_("▶ Start Conversion"))
        self.btn_start.clicked.disconnect()
        self.btn_start.clicked.connect(self._start_convert)
        self._refresh_file_list()

        succ = len(result["success"])
        skip = len(result["skipped"])
        fail = len(result["failed"])
        self.lbl_summary.setText(_("Success: {succ}  Skipped: {skip}  Failed: {fail}").format(
            succ=succ, skip=skip, fail=fail
        ))

        self.log_area.append(
            f"[{_now()}] " + _("Conversion complete: success {succ}, skipped {skip}, failed {fail}").format(
                succ=succ, skip=skip, fail=fail
            )
        )

        if fail > 0:
            QW.QMessageBox.warning(
                self, _("Conversion Complete"),
                _("Conversion complete\n✔ Success: {succ}\n⏭ Skipped: {skip}\n✘ Failed: {fail}").format(
                    succ=succ, skip=skip, fail=fail
                )
            )
        elif succ > 0:
            QW.QMessageBox.information(
                self, _("Conversion Complete"),
                _("All done!\n✔ Success: {succ}\n⏭ Skipped: {skip}").format(
                    succ=succ, skip=skip
                )
            )

    def closeEvent(self, event: QG.QCloseEvent) -> None:
        """Keep the window and its worker alive until conversion has stopped."""
        if self.worker and self.worker.isRunning():
            QW.QMessageBox.warning(
                self,
                _("Conversion in Progress"),
                _("Please cancel the conversion and wait for the current task to finish before closing this window."),
            )
            event.ignore()
            return
        super().closeEvent(event)
