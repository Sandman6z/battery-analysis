"""Worker thread for NDAX batch conversion."""

from __future__ import annotations

import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

from battery_analysis.ndax.converter import _convert_pool_task, get_ndax_files
from battery_analysis.utils.data_bundle import bundle_cache
from battery_analysis.utils.ndax_meta import ensure_sidecar


def _now() -> str:
    """Get current timestamp as formatted string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M")


class ConvertWorker(QThread):
    """Worker thread for batch NDAX conversion."""

    progress = pyqtSignal(int, int)  # current, total
    file_status = pyqtSignal(int, str)  # row_index, status_text
    log = pyqtSignal(str)
    finished_signal = pyqtSignal(dict)

    def __init__(self, ndax_files: list[Path], out_dir: Path, force: bool = False) -> None:
        super().__init__()
        self.ndax_files = ndax_files
        self.out_dir = out_dir
        self.force = force
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
                self.log.emit("⚠ 已取消转换")
                self.finished_signal.emit(result)
                return

            xlsx_path = self.out_dir / f"{ndax_path.stem}.xlsx"
            if xlsx_path.exists() and not self.force:
                # 旧转换产物回填 sidecar（已有则秒回，不重转）
                try:
                    ensure_sidecar(ndax_path, xlsx_path)
                except Exception:
                    self.log.emit(f"⚠ sidecar 回填失败: {ndax_path.name}")
                result["skipped"].append(ndax_path.name)
                self.file_status.emit(i, "已跳过")
                self.log.emit(f"⏭ {ndax_path.name} 已存在，跳过")
                done_count += 1
                self.progress.emit(done_count, total)
            else:
                pending.append((i, ndax_path, xlsx_path))
                self.file_status.emit(i, "等待中...")

        if not pending or self._cancelled:
            self.finished_signal.emit(result)
            return

        # Phase 2: parallel conversion
        for i, _, _ in pending:
            self.file_status.emit(i, "转换中...")

        max_workers = min(os.cpu_count() or 1, len(pending))
        self.log.emit(f"⚡ 使用 {max_workers} 个进程并行转换 {len(pending)} 个文件")

        try:
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                fut_map = {
                    executor.submit(_convert_pool_task, ndax_path, xlsx_path): (i, ndax_path.name)
                    for i, ndax_path, xlsx_path in pending
                }

                for future in as_completed(fut_map):
                    if self._cancelled:
                        break

                    i, name = fut_map[future]
                    try:
                        # 子进程内 register 对父进程无效 → 回收结果时在本进程注册
                        xlsx_out, bundle = future.result()
                        bundle_cache.register(xlsx_out, bundle)
                        result["success"].append(name)
                        self.file_status.emit(i, "成功")
                        self.log.emit(f"✔ {name} 转换成功")
                    except Exception as e:
                        result["failed"].append((name, str(e)))
                        self.file_status.emit(i, "失败")
                        self.log.emit(f"✘ {name} 转换失败: {e}")

                    done_count += 1
                    self.progress.emit(done_count, total)
        except Exception as e:
            self.log.emit(f"✘ 并行转换异常: {e}")

        self.finished_signal.emit(result)
