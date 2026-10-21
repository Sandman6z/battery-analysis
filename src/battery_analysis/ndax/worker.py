"""Worker thread for NDAX batch conversion."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

from battery_analysis.i18n import _
from battery_analysis.ndax.converter import convert_one, get_ndax_files
from battery_analysis.utils.concurrency_policy import (
    conversion_worker_budget,
    get_conversion_worker_count,
)


def _now() -> str:
    """Get current timestamp as formatted string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M")


class ConvertWorker(QThread):
    """Batch conversion with the same worker budget/max_workers semantics as convert_batch."""

    progress = pyqtSignal(int, int)  # current, total
    file_status = pyqtSignal(int, str)  # row_index, status_text
    log = pyqtSignal(str)
    finished_signal = pyqtSignal(dict)

    def __init__(
        self,
        ndax_files: list[Path],
        out_dir: Path,
        force: bool = False,
        *,
        max_workers: int | None = None,
    ) -> None:
        super().__init__()
        # Validate synchronously, even for empty/skipped batches, not inside QThread.run.
        conversion_worker_budget(0, 1, max_workers)
        self.ndax_files = ndax_files
        self.out_dir = out_dir
        self.force = force
        self.max_workers = max_workers
        self._cancelled = False

    def cancel(self) -> None:
        """Request cancellation of the conversion process."""
        self._cancelled = True

    def run(self) -> None:
        """Execute the batch conversion process."""
        total = len(self.ndax_files)
        result: dict = {"success": [], "skipped": [], "failed": []}
        done_count = 0

        # Phase 1: determine which files to convert
        pending = []
        for i, ndax_path in enumerate(self.ndax_files):
            if self._cancelled:
                self.log.emit(_("⚠ Conversion cancelled"))
                self.finished_signal.emit(result)
                return

            xlsx_path = self.out_dir / f"{ndax_path.stem}.xlsx"
            if xlsx_path.exists() and not self.force:
                result["skipped"].append(ndax_path.name)
                self.file_status.emit(i, _("Skipped"))
                self.log.emit(_("⏭ {name} already exists; skipped").format(name=ndax_path.name))
                done_count += 1
                self.progress.emit(done_count, total)
            else:
                pending.append((i, ndax_path, xlsx_path))
                self.file_status.emit(i, _("Waiting..."))

        if not pending or self._cancelled:
            self.finished_signal.emit(result)
            return

        # Phase 2: parallel conversion
        for i, _ndax_path, _xlsx_path in pending:
            self.file_status.emit(i, _("Converting..."))

        max_workers = get_conversion_worker_count(len(pending), self.max_workers)
        self.log.emit(_("⚡ Converting {count} files in parallel using {workers} processes").format(
            count=len(pending), workers=max_workers
        ))

        try:
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                fut_map = {
                    executor.submit(convert_one, ndax_path, xlsx_path): (i, ndax_path.name)
                    for i, ndax_path, xlsx_path in pending
                }

                for future in as_completed(fut_map):
                    if self._cancelled:
                        break

                    i, name = fut_map[future]
                    try:
                        future.result()
                        result["success"].append(name)
                        self.file_status.emit(i, _("Success"))
                        self.log.emit(_("✔ {name} converted successfully").format(name=name))
                    except Exception as e:
                        result["failed"].append((name, str(e)))
                        self.file_status.emit(i, _("Failed"))
                        self.log.emit(_("✘ {name} conversion failed: {error}").format(name=name, error=e))

                    done_count += 1
                    self.progress.emit(done_count, total)
        except Exception as e:
            self.log.emit(_("✘ Parallel conversion error: {error}").format(error=e))

        self.finished_signal.emit(result)
