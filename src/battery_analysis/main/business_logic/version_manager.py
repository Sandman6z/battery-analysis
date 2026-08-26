"""
版本管理模块

这个模块负责处理版本号的计算和更新，包括：
- 从XLSX文件计算SHA-256校验和
- 根据校验和确定版本号
- 更新版本号记录
- 设置文件隐藏属性
"""

import os
import csv
import logging
from pathlib import Path

from battery_analysis.main.workers.task_runner import TaskRunner, TaskManager


class VersionManager:
    """
    版本管理器，负责处理版本号的计算和更新
    """

    def __init__(self, main_window=None, ctx=None):
        """
        初始化版本管理器

        Args:
            main_window: 主窗口实例（旧接口）
            ctx: AppContext（新接口）
        """
        self.main_window = main_window
        self._ctx = ctx
        self.logger = logging.getLogger(__name__)
        self._checksum_generation = 0
        self._task_manager = TaskManager()

    def get_version(self) -> None:
        """
        计算并设置电池分析的版本号

        目录存在性检查在主线程同步完成；SHA-256 校验和计算派发到后台线程，
        完成后由 _on_checksum_ready 在主线程落盘 SHA256.csv 并更新 UI（roadmap #9）。
        """
        strInPutDir = self.main_window.lineEdit_InputPath.text()
        strOutoutDir = self.main_window.lineEdit_OutputPath.text()
        if os.path.exists(strInPutDir) and os.path.exists(strOutoutDir):
            self._checksum_generation += 1
            generation = self._checksum_generation
            self._task_manager.cancel_all()  # 取消在途旧校验和任务（B2 确立模式）
            self._run_async(
                self._calc_checksum_task,
                lambda checksum, g=generation: self._on_checksum_ready(checksum, g),
                lambda error, g=generation: self._on_checksum_error(error, g),
                strInPutDir,
            )
        else:
            self._checksum_generation += 1
            self._task_manager.cancel_all()  # 目录失效也推进代次并取消在途任务，防旧结果误接受
            self.main_window.lineEdit_Version.setText("")

    def _calc_checksum_task(self, strInPutDir, **kwargs):
        """后台线程：计算目录内全部 xlsx 的 SHA-256 校验和（不触碰 UI）。

        目录内无 xlsx 文件时返回 None（回调据此清空版本号）。
        progress_callback 由 TaskRunner 强制注入，此处忽略。
        """
        listAllInXlsx = [strInPutDir + f"/{f}" for f in os.listdir(
            strInPutDir) if f[:2] != "~$" and f[-5:] == ".xlsx"]
        if not listAllInXlsx:
            return None
        from battery_analysis.main.utils.file_utils import FileUtils
        return FileUtils.calc_checksum(listAllInXlsx)

    def _on_checksum_ready(self, checksum, generation):
        """主线程：校验和计算完成后的版本号落盘 + UI 更新"""
        # 过期结果守卫（generation 精确匹配）：用户已切换输入路径时丢弃旧代次结果。
        if generation != self._checksum_generation:
            self.logger.info("Discarding stale checksum result for changed input path")
            return

        if checksum is None:
            # 目录内无 xlsx 文件，清空版本号与校验和缓存
            self.main_window.sha256_checksum = ""
            self.main_window.lineEdit_Version.setText("")
            return
        # 时序保证：sha256_checksum 必须随时可用（analysis_runner.py:173、
        # set_version 均读取它），故在任何读取者之前回写。
        # 已知限制：get_version 异步化后，用户若在后台校验和完成前点 Run，
        # analysis_runner 会快照到旧值/空值，本次版本号递增可能跳过
        #（下次 Run 时校验和已就绪即自愈）。P3 接受的 trade-off，跨文件修复另议。
        self.main_window.sha256_checksum = checksum

        try:
            strOutoutDir = self.main_window.lineEdit_OutputPath.text()
            strCsvPath = strOutoutDir + "/SHA256.csv"

            if os.path.exists(strCsvPath) and os.path.getsize(strCsvPath) != 0:
                listSHA256Reader = []
                f = open(strCsvPath, mode='r', encoding='utf-8')
                csvSHA256Reader = csv.reader(f)
                for row in csvSHA256Reader:
                    listSHA256Reader.append(row)
                f.close()
                # 确保列表长度足够，正确访问CSV行数据
                if len(listSHA256Reader) >= 4:
                    listChecksum = listSHA256Reader[1] if len(listSHA256Reader) > 1 else []
                    listTimes = listSHA256Reader[3] if len(listSHA256Reader) > 3 else []
                else:
                    listChecksum = []
                    listTimes = []

                # 检查当前校验和是否已存在
                current_checksum = checksum
                existing_index = -1
                for i, chk in enumerate(listChecksum):
                    if chk == current_checksum:
                        existing_index = i
                        break

                os.remove(strCsvPath)
                f = open(strCsvPath, mode='w', newline='', encoding='utf-8')
                csvSHA256Writer = csv.writer(f)

                if not listChecksum:
                    # 第一次运行，主版本号从1开始
                    csvSHA256Writer.writerow(["Checksums:"])
                    csvSHA256Writer.writerow([current_checksum])
                    csvSHA256Writer.writerow(["Times:"])
                    csvSHA256Writer.writerow(["0"])
                    self.main_window.lineEdit_Version.setText("1.0")
                elif existing_index >= 0:
                    # 校验和已存在，使用现有的版本号和运行次数
                    intVersionMajor = existing_index + 1
                    try:
                        intVersionMinor = int(listTimes[existing_index]) if existing_index < len(listTimes) and listTimes[existing_index] else 0
                    except (ValueError, IndexError):
                        intVersionMinor = 0

                    csvSHA256Writer.writerow(["Checksums:"])
                    csvSHA256Writer.writerow(listChecksum)
                    csvSHA256Writer.writerow(["Times:"])
                    csvSHA256Writer.writerow(listTimes)
                    self.main_window.lineEdit_Version.setText(
                        f"{intVersionMajor}.{intVersionMinor}")
                else:
                    # 校验和不存在，增加主版本号
                    intVersionMajor = len(listChecksum) + 1
                    intVersionMinor = 0

                    # 将当前校验和添加到列表，作为新的主版本
                    listChecksum.append(current_checksum)
                    listTimes.append("0")

                    csvSHA256Writer.writerow(["Checksums:"])
                    csvSHA256Writer.writerow(listChecksum)
                    csvSHA256Writer.writerow(["Times:"])
                    csvSHA256Writer.writerow(listTimes)
                    self.main_window.lineEdit_Version.setText(
                        f"{intVersionMajor}.{intVersionMinor}")
                f.close()
            else:
                f = open(strCsvPath, mode='w', newline='', encoding='utf-8')
                csvSHA256Writer = csv.writer(f)
                csvSHA256Writer.writerow(["Checksums:"])
                csvSHA256Writer.writerow([checksum])
                csvSHA256Writer.writerow(["Times:"])
                csvSHA256Writer.writerow(["0"])
                f.close()
                self.main_window.lineEdit_Version.setText("1.0")

            # 使用文件服务设置文件隐藏属性
            file_service = self.main_window._get_service("file")
            if file_service:
                file_service.hide_file(strCsvPath)
            else:
                # 降级到直接调用
                try:
                    import win32api
                    import win32con
                    win32api.SetFileAttributes(strCsvPath, win32con.FILE_ATTRIBUTE_HIDDEN)
                except ImportError:
                    self.logger.warning("File service is unavailable; cannot set file hidden attribute")
        except Exception as e:  # pylint: disable=broad-exception-caught
            # 后台派发后不再有 _deferred_init 的 try/except 兜底，这里主动记录
            self.logger.error("Failed to finalize version after checksum: %s", e)

    def _on_checksum_error(self, error_msg, generation):
        """主线程：校验和计算异常兜底"""
        # 过期结果守卫：丢弃旧代次错误兜底（与 _on_checksum_ready 一致）
        if generation != self._checksum_generation:
            self.logger.debug("Discarding stale checksum error for changed input path")
            return
        self.logger.error("Failed to compute SHA-256 checksum: %s", error_msg)
        if hasattr(self.main_window, 'statusBar_BatteryAnalysis'):
            self.main_window.statusBar_BatteryAnalysis.showMessage(
                "[Error]: Failed to compute checksum")

    def _run_async(self, task_func, on_finished, on_error, *args, **kwargs):
        """TaskRunner 派发：回调经 TaskSignals 自动回主线程（AutoConnection Queued）。"""
        runner = TaskRunner(task_func, *args, **kwargs)
        if on_finished:
            runner.signals.finished.connect(on_finished)
        if on_error:
            runner.signals.error.connect(on_error)
        self._task_manager.submit(runner)
        return runner

    def set_version(self) -> None:
        """
        更新版本号，增加次要版本号
        """
        # 初始化必要的属性如果不存在
        if not hasattr(self.main_window, 'sha256_checksum_run'):
            self.main_window.sha256_checksum_run = self.main_window.sha256_checksum if hasattr(
                self.main_window, 'sha256_checksum') else ''

        list_sha256_reader = []
        output_path_str = self.main_window.lineEdit_OutputPath.text()

        try:
            # 使用Path对象进行路径处理
            output_path = Path(output_path_str)
            sha256_file = output_path / "SHA256.csv"

            # 检查路径是否有效
            if not output_path_str or not output_path.is_dir():
                self.main_window.statusBar_BatteryAnalysis.showMessage(
                    f"[Warning]: Invalid output path: {output_path_str}")
                return

            # 读取SHA256文件
            if sha256_file.exists():
                try:
                    with sha256_file.open(mode='r', encoding='utf-8') as f:
                        csv_sha256_reader = csv.reader(f)
                        for row in csv_sha256_reader:
                            list_sha256_reader.append(row)
                except PermissionError:
                    self.main_window.statusBar_BatteryAnalysis.showMessage(
                        f"[Warning]: Permission denied reading {sha256_file}")
                    return
                except (IOError, UnicodeDecodeError, csv.Error, OSError) as read_error:
                    self.main_window.statusBar_BatteryAnalysis.showMessage(
                        f"[Warning]: Failed to read SHA256 file: {str(read_error)}")
                    return

            # 处理文件内容
            if len(list_sha256_reader) >= 4:
                try:
                    # 正确处理CSV数据：每一行是一个列表，我们需要访问特定行的数据
                    list_checksum = list_sha256_reader[1] if len(list_sha256_reader) > 1 else []
                    list_times = list_sha256_reader[3] if len(list_sha256_reader) > 3 else []

                    # 查找匹配的校验和，递增次要版本号
                    checksum_found = False
                    for c, checksum in enumerate(list_checksum):
                        if self.main_window.sha256_checksum_run == checksum:
                            checksum_found = True
                            version_major = c + 1
                            try:
                                current_times = int(list_times[c]) if c < len(list_times) and list_times[c] else 0
                            except (ValueError, IndexError):
                                current_times = 0
                            new_times = current_times + 1
                            list_times[c] = str(new_times)
                            self.main_window.lineEdit_Version.setText(
                                f"{version_major}.{new_times}")
                            break

                    if not checksum_found:
                        self.logger.warning(
                            "Checksum %s was not found in SHA256.csv; unable to update version number",
                            self.main_window.sha256_checksum_run)
                        return

                    # 创建临时文件避免权限问题
                    temp_file = output_path / "SHA256_temp.csv"
                    with temp_file.open(mode='w', newline='', encoding='utf-8') as f:
                        csv_sha256_writer = csv.writer(f)
                        csv_sha256_writer.writerow(["Checksums:"])
                        csv_sha256_writer.writerow(list_checksum)
                        csv_sha256_writer.writerow(["Times:"])
                        csv_sha256_writer.writerow(list_times)

                    # 替换原文件
                    if sha256_file.exists():
                        try:
                            sha256_file.unlink()  # 删除原文件
                        except PermissionError:
                            self.main_window.statusBar_BatteryAnalysis.showMessage(
                                "[Warning]: Cannot remove existing SHA256 file, using new location")
                            sha256_file = temp_file  # 使用临时文件作为新的SHA256文件
                            temp_file = None

                    if temp_file:
                        temp_file.replace(sha256_file)  # 替换文件

                    # 尝试设置隐藏属性，但不抛出异常
                    file_service = self.main_window._get_service("file")
                    if file_service:
                        success, error_msg = file_service.hide_file(str(sha256_file))
                        if not success:
                            self.logger.warning("Unable to set SHA256 file hidden attribute: %s", error_msg)
                    else:
                        # 降级到直接调用
                        try:
                            import win32api
                            import win32con
                            win32api.SetFileAttributes(str(sha256_file), win32con.FILE_ATTRIBUTE_HIDDEN)
                        except (ImportError, AttributeError, OSError) as e:
                            # 忽略设置隐藏属性失败的错误
                            self.logger.debug("Unable to set SHA256 file hidden attribute (direct call): %s", e)
                except PermissionError:
                    self.main_window.statusBar_BatteryAnalysis.showMessage(
                        f"[Warning]: Permission denied writing to {output_path}")
                except (IOError, UnicodeEncodeError, csv.Error, OSError, PermissionError) as write_error:
                    self.main_window.statusBar_BatteryAnalysis.showMessage(
                        f"[Warning]: Failed to write SHA256 file: {str(write_error)}")
            else:
                # 如果文件不存在或格式不正确，创建新文件
                try:
                    with sha256_file.open(mode='w', newline='', encoding='utf-8') as f:
                        csv_sha256_writer = csv.writer(f)
                        csv_sha256_writer.writerow(["Checksums:"])
                        csv_sha256_writer.writerow(
                            [self.main_window.sha256_checksum_run if self.main_window.sha256_checksum_run else ""])
                        csv_sha256_writer.writerow(["Times:"])
                        csv_sha256_writer.writerow(["1"])

                    try:
                        import win32api
                        import win32con
                        win32api.SetFileAttributes(
                            str(sha256_file), win32con.FILE_ATTRIBUTE_HIDDEN)
                    except (ImportError, AttributeError, OSError) as e:
                        self.logger.debug("Unable to set SHA256 file hidden attribute: %s", e)
                except PermissionError:
                    self.main_window.statusBar_BatteryAnalysis.showMessage(
                        f"[Warning]: Cannot create SHA256 file in {output_path}")
                except (IOError, UnicodeEncodeError, csv.Error, OSError, PermissionError) as create_error:
                    self.main_window.statusBar_BatteryAnalysis.showMessage(
                        f"[Warning]: Failed to create SHA256 file: {str(create_error)}")

        except (IOError, UnicodeError, csv.Error, OSError, PermissionError, TypeError, ValueError) as e:
            # 捕获所有其他异常但不中断程序
            self.main_window.statusBar_BatteryAnalysis.showMessage(
                f"[Info]: Version tracking skipped: {str(e)}")
