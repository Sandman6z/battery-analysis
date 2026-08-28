"""
文件验证工具模块

提供文件和目录验证的公共功能
"""

import logging
import os


class FileValidator:
    """
    文件验证器类
    提供文件和目录验证的公共功能
    """

    def __init__(self):
        """
        初始化文件验证器
        """
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def _validate_name(name: str, label: str) -> tuple[bool, str]:
        """验证名称（文件/目录）的基本规则：长度、无效字符、中文、保留名"""
        if len(name) > 255:
            return False, f"{label} name is too long: {name} exceeds 255 characters"
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            if char in name:
                return False, f"{label} name contains invalid characters: {name} contains '{char}'"
        for char in name:
            if "一" <= char <= "鿿":
                return False, f"{label} name must not contain Chinese characters: {name}"
        reserved_names = [
            "CON",
            "PRN",
            "AUX",
            "NUL",
            "COM1",
            "COM2",
            "COM3",
            "COM4",
            "COM5",
            "COM6",
            "COM7",
            "COM8",
            "COM9",
            "LPT1",
            "LPT2",
            "LPT3",
            "LPT4",
            "LPT5",
            "LPT6",
            "LPT7",
            "LPT8",
            "LPT9",
        ]
        base_name = name.split(".")[0].upper()
        if base_name in reserved_names:
            return False, f"Invalid {label} name: {name} is a reserved name"
        return True, ""

    def validate_filename(self, filename: str) -> tuple[bool, str]:
        """验证文件名的有效性"""
        return self._validate_name(filename, "File")

    def validate_file_extension(self, filename: str, expected_extensions: list) -> tuple[bool, str]:
        """
        验证文件扩展名的有效性

        Args:
            filename: 文件名
            expected_extensions: 期望的文件扩展名列表

        Returns:
            tuple: (是否有效, 错误消息)
        """
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in expected_extensions:
            return (
                False,
                f"Invalid file format: {filename} is not a valid {', '.join(expected_extensions)} file",
            )
        return True, ""

    def validate_file_exists(self, file_path: str) -> tuple[bool, str]:
        """验证文件是否存在"""
        if not os.path.exists(file_path):
            return False, f"Selected file does not exist:\n{file_path}"
        return True, ""

    def validate_file_not_empty(self, file_path: str) -> tuple[bool, str]:
        """验证文件是否为空"""
        if os.path.getsize(file_path) == 0:
            return False, f"File is empty: {os.path.basename(file_path)}"
        return True, ""

    def validate_directory_exists(self, directory_path: str) -> tuple[bool, str]:
        """验证目录是否存在"""
        if not os.path.exists(directory_path):
            return False, f"Directory does not exist:\n{directory_path}"
        if not os.path.isdir(directory_path):
            return False, f"Path is not a directory:\n{directory_path}"
        return True, ""

    def validate_directory_name(self, directory_name: str) -> tuple[bool, str]:
        """验证目录名的有效性"""
        return self._validate_name(directory_name, "Directory")

    def validate_excel_filename(self, filename: str) -> tuple[bool, str]:
        """
        验证Excel文件名的有效性

        Args:
            filename: 文件名

        Returns:
            tuple: (是否有效, 错误消息)
        """
        is_valid, error_msg = self.validate_file_extension(filename, [".xlsx"])
        if not is_valid:
            return is_valid, error_msg
        is_valid, error_msg = self.validate_filename(filename)
        if not is_valid:
            return is_valid, error_msg

        base_name = filename.replace(".xlsx", "")
        if "DC" not in base_name:
            return (
                False,
                f"Invalid filename format: {filename} missing batch date code (starting with DC)",
            )
        if "mA" not in base_name:
            return False, f"Invalid filename format: {filename} missing current info (mA)"
        if "," not in base_name:
            return False, f"Invalid filename format: {filename} missing required separator (, )"

        has_temperature = False
        if "°C" in base_name or "C" in base_name or ("(" in base_name and ")" in base_name):
            has_temperature = True
        if not has_temperature:
            return False, f"Invalid filename format: {filename} missing temperature info"

        return True, ""

    def validate_xml_filename(self, filename: str) -> tuple[bool, str]:
        """验证XML文件名的有效性"""
        is_valid, error_msg = self.validate_file_extension(filename, [".xml"])
        if not is_valid:
            return is_valid, error_msg
        return self.validate_filename(filename)

    def validate_full_path(self, path: str) -> tuple[bool, str]:
        """验证完整路径的有效性"""
        if len(path) > 260:
            return False, f"Path is too long: {path} exceeds 260 characters"
        invalid_chars = "<>|?*"
        for char in invalid_chars:
            if char in path:
                return False, f"Path contains invalid characters: {path} contains '{char}'"
        return True, ""

    def validate_path_length(self, path: str) -> tuple[bool, str]:
        """验证路径长度"""
        if len(path) > 260:
            return False, f"Path is too long: {path} exceeds 260 characters"
        return True, ""

    def validate_directory_structure(self, directory: str) -> tuple[bool, str]:
        """验证目录结构"""
        is_valid, error_msg = self.validate_directory_exists(directory)
        if not is_valid:
            return is_valid, error_msg
        dir_name = os.path.basename(directory)
        return self.validate_directory_name(dir_name)

    def validate_input_directory(self, directory: str) -> tuple[bool, str]:
        """验证输入目录"""
        is_valid, error_msg = self.validate_directory_structure(directory)
        if not is_valid:
            return is_valid, error_msg
        if os.path.basename(directory) != "2_xlsx":
            return False, f"Input path is not a 2_xlsx directory: {directory}"
        if not os.access(directory, os.R_OK):
            return False, f"Unable to read directory: {directory}"
        return True, ""

    def validate_output_directory(self, directory: str) -> tuple[bool, str]:
        """验证输出目录"""
        is_valid, error_msg = self.validate_path_length(directory)
        if not is_valid:
            return is_valid, error_msg
        dir_name = os.path.basename(directory)
        is_valid, error_msg = self.validate_directory_name(dir_name)
        if not is_valid:
            return is_valid, error_msg
        if os.path.exists(directory):
            if not os.path.isdir(directory):
                return False, f"Path is not a directory: {directory}"
            if not os.access(directory, os.W_OK):
                return False, f"Unable to write to directory: {directory}"
        else:
            parent_dir = os.path.dirname(directory)
            if parent_dir and not os.path.exists(parent_dir):
                return False, f"Parent directory does not exist: {parent_dir}"
            if parent_dir and not os.access(parent_dir, os.W_OK):
                return False, f"Unable to create directory in parent directory: {parent_dir}"
        return True, ""

    def validate_path_access(self, path: str, access_type: str = "r") -> tuple[bool, str]:
        """验证路径的访问权限"""
        if not os.path.exists(path):
            return False, f"Path does not exist: {path}"
        if "r" in access_type and not os.access(path, os.R_OK):
            return False, f"Unable to read path: {path}"
        if "w" in access_type and not os.access(path, os.W_OK):
            return False, f"Unable to write to path: {path}"
        if "x" in access_type and not os.access(path, os.X_OK):
            return False, f"Unable to execute path: {path}"
        return True, ""
