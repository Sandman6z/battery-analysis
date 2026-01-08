"""
版本管理模块

这个模块负责处理版本号的计算和更新，包括：
- 从XLSX文件计算MD5校验和
- 根据校验和确定版本号
- 更新版本号记录
- 设置文件隐藏属性
"""

import os
import csv
import logging
from pathlib import Path
from typing import List, Any

# 第三方库导入
import PyQt6.QtWidgets as QW

# 本地应用/库导入
from battery_analysis.i18n.language_manager import _


class VersionManager:
    """
    版本管理器，负责处理版本号的计算和更新
    """
    
    def __init__(self, main_window):
        """
        初始化版本管理器
        
        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
    
    def get_version(self) -> None:
        """
        计算并设置电池分析的版本号
        
        此方法通过分析输入目录中的XLSX文件，计算其MD5校验和，
        然后根据MD5.csv文件中的历史记录确定当前版本号。如果输入文件内容变更，
        版本号会自动增加。
        """
        strInPutDir = self.main_window.lineEdit_InputPath.text()
        strOutoutDir = self.main_window.lineEdit_OutputPath.text()
        if os.path.exists(strInPutDir) and os.path.exists(strOutoutDir):
            listAllInXlsx = [strInPutDir + f"/{f}" for f in os.listdir(
                strInPutDir) if f[:2] != "~$" and f[-5:] == ".xlsx"]
            if not listAllInXlsx:
                self.main_window.lineEdit_Version.setText("")
                return
            strCsvMd5Path = strOutoutDir + "/MD5.csv"
            # 使用FileUtils.calc_md5checksum替换calc_md5checksum
            from battery_analysis.main.utils.file_utils import FileUtils
            self.main_window.md5_checksum = FileUtils.calc_md5checksum(listAllInXlsx)
            if os.path.exists(strCsvMd5Path) and os.path.getsize(strCsvMd5Path) != 0:
                listMD5Reader = []
                f = open(strCsvMd5Path, mode='r', encoding='utf-8')
                csvMD5Reader = csv.reader(f)
                for row in csvMD5Reader:
                    listMD5Reader.append(row)
                f.close()
                # 确保列表长度足够，正确访问CSV行数据
                if len(listMD5Reader) >= 4:
                    listChecksum = listMD5Reader[1] if len(listMD5Reader) > 1 else []
                    listTimes = listMD5Reader[3] if len(listMD5Reader) > 3 else []
                else:
                    listChecksum = []
                    listTimes = []

                os.remove(strCsvMd5Path)
                f = open(strCsvMd5Path, mode='w', newline='', encoding='utf-8')
                csvMD5Writer = csv.writer(f)

                if not listChecksum:
                    csvMD5Writer.writerow(["Checksums:"])
                    csvMD5Writer.writerow([self.main_window.md5_checksum])
                    csvMD5Writer.writerow(["Times:"])
                    csvMD5Writer.writerow(["0"])
                    self.main_window.lineEdit_Version.setText("1.0")
                else:
                    intVersionMajor = 1
                    intVersionMinor = 0
                    for c in range(len(listChecksum)):
                        if self.main_window.md5_checksum == listChecksum[c]:
                            intVersionMajor = c + 1
                            intVersionMinor = int(listTimes[c])
                            # increase it after executing the whole program
                            break
                        if c == len(listChecksum) - 1:
                            intVersionMajor = c + 2
                            listChecksum.append(self.main_window.md5_checksum)
                            listTimes.append("0")
                    csvMD5Writer.writerow(["Checksums:"])
                    csvMD5Writer.writerow(listChecksum)
                    csvMD5Writer.writerow(["Times:"])
                    csvMD5Writer.writerow(listTimes)
                    self.main_window.lineEdit_Version.setText(
                        f"{intVersionMajor}.{intVersionMinor}")
                f.close()
            else:
                f = open(strCsvMd5Path, mode='w', newline='', encoding='utf-8')
                csvMD5Writer = csv.writer(f)
                csvMD5Writer.writerow(["Checksums:"])
                csvMD5Writer.writerow([self.main_window.md5_checksum])
                csvMD5Writer.writerow(["Times:"])
                csvMD5Writer.writerow(["0"])
                f.close()
                self.main_window.lineEdit_Version.setText("1.0")
            # 使用文件服务设置文件隐藏属性
            file_service = self.main_window._get_service("file")
            if file_service:
                file_service.hide_file(strCsvMd5Path)
            else:
                # 降级到直接调用
                try:
                    import win32api
                    import win32con
                    win32api.SetFileAttributes(strCsvMd5Path, win32con.FILE_ATTRIBUTE_HIDDEN)
                except ImportError:
                    self.logger.warning("文件服务不可用，无法设置文件隐藏属性")
        else:
            self.main_window.lineEdit_Version.setText("")
    
    def set_version(self) -> None:
        """
        更新版本号，增加次要版本号
        """
        # 初始化必要的属性如果不存在
        if not hasattr(self.main_window, 'md5_checksum_run'):
            self.main_window.md5_checksum_run = self.main_window.md5_checksum if hasattr(
                self.main_window, 'md5_checksum') else ''

        list_md5_reader = []
        output_path_str = self.main_window.lineEdit_OutputPath.text()

        try:
            # 使用Path对象进行路径处理
            output_path = Path(output_path_str)
            md5_file = output_path / "MD5.csv"

            # 检查路径是否有效
            if not output_path_str or not output_path.is_dir():
                self.main_window.statusBar_BatteryAnalysis.showMessage(
                    f"[Warning]: Invalid output path: {output_path_str}")
                return

            # 读取MD5文件
            if md5_file.exists():
                try:
                    with md5_file.open(mode='r', encoding='utf-8') as f:
                        csv_md5_reader = csv.reader(f)
                        for row in csv_md5_reader:
                            list_md5_reader.append(row)
                except PermissionError:
                    self.main_window.statusBar_BatteryAnalysis.showMessage(
                        f"[Warning]: Permission denied reading {md5_file}")
                    return
                except (IOError, UnicodeDecodeError, csv.Error, OSError) as read_error:
                    self.main_window.statusBar_BatteryAnalysis.showMessage(
                        f"[Warning]: Failed to read MD5 file: {str(read_error)}")
                    return

            # 处理文件内容
            if len(list_md5_reader) >= 4:
                try:
                    # 正确处理CSV数据：每一行是一个列表，我们需要访问特定行的数据
                    list_checksum = list_md5_reader[1] if len(list_md5_reader) > 1 else []
                    list_times = list_md5_reader[3] if len(list_md5_reader) > 3 else []

                    # 创建临时文件避免权限问题
                    temp_file = output_path / "MD5_temp.csv"
                    with temp_file.open(mode='w', newline='', encoding='utf-8') as f:
                        csv_md5_writer = csv.writer(f)
                        for c, checksum in enumerate(list_checksum):
                            if self.main_window.md5_checksum_run == checksum:
                                version_major = c + 1
                                version_minor = int(list_times[c]) + 1
                                list_times[c] = str(version_minor)
                                if self.main_window.md5_checksum_run == getattr(self.main_window, 'md5_checksum', ''):
                                    self.main_window.lineEdit_Version.setText(
                                        f"{version_major}.{version_minor}")
                                break

                        csv_md5_writer.writerow(["Checksums:"])
                        csv_md5_writer.writerow(list_checksum)
                        csv_md5_writer.writerow(["Times:"])
                        csv_md5_writer.writerow(list_times)

                    # 替换原文件
                    if md5_file.exists():
                        try:
                            md5_file.unlink()  # 删除原文件
                        except PermissionError:
                            self.main_window.statusBar_BatteryAnalysis.showMessage(
                                "[Warning]: Cannot remove existing MD5 file, using new location")
                            md5_file = temp_file  # 使用临时文件作为新的MD5文件
                            temp_file = None

                    if temp_file:
                        temp_file.replace(md5_file)  # 替换文件

                    # 尝试设置隐藏属性，但不抛出异常
                    file_service = self.main_window._get_service("file")
                    if file_service:
                        success, error_msg = file_service.hide_file(str(md5_file))
                        if not success:
                            self.logger.warning("无法设置MD5文件隐藏属性: %s", error_msg)
                    else:
                        # 降级到直接调用
                        try:
                            import win32api
                            import win32con
                            win32api.SetFileAttributes(str(md5_file), win32con.FILE_ATTRIBUTE_HIDDEN)
                        except (ImportError, AttributeError, OSError) as e:
                            # 忽略设置隐藏属性失败的错误
                            self.logger.debug("无法设置MD5文件隐藏属性（直接调用）: %s", e)
                except PermissionError:
                    self.main_window.statusBar_BatteryAnalysis.showMessage(
                        f"[Warning]: Permission denied writing to {output_path}")
                except (IOError, UnicodeEncodeError, csv.Error, OSError, PermissionError) as write_error:
                    self.main_window.statusBar_BatteryAnalysis.showMessage(
                        f"[Warning]: Failed to write MD5 file: {str(write_error)}")
            else:
                # 如果文件不存在或格式不正确，创建新文件
                try:
                    with md5_file.open(mode='w', newline='', encoding='utf-8') as f:
                        csv_md5_writer = csv.writer(f)
                        csv_md5_writer.writerow(["Checksums:"])
                        csv_md5_writer.writerow(
                            [self.main_window.md5_checksum_run if self.main_window.md5_checksum_run else ""])
                        csv_md5_writer.writerow(["Times:"])
                        csv_md5_writer.writerow(["1"])

                    try:
                        win32api.SetFileAttributes(
                            str(md5_file), win32con.FILE_ATTRIBUTE_HIDDEN)
                    except (AttributeError, OSError, ImportError) as e:
                        self.logger.debug("无法设置MD5文件隐藏属性: %s", e)
                except PermissionError:
                    self.main_window.statusBar_BatteryAnalysis.showMessage(
                        f"[Warning]: Cannot create MD5 file in {output_path}")
                except (IOError, UnicodeEncodeError, csv.Error, OSError, PermissionError) as create_error:
                    self.main_window.statusBar_BatteryAnalysis.showMessage(
                        f"[Warning]: Failed to create MD5 file: {str(create_error)}")

        except (IOError, UnicodeError, csv.Error, OSError, PermissionError, TypeError, ValueError) as e:
            # 捕获所有其他异常但不中断程序
            self.main_window.statusBar_BatteryAnalysis.showMessage(
                f"[Info]: Version tracking skipped: {str(e)}")
