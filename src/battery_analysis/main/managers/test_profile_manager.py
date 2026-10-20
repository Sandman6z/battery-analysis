"""
测试配置文件管理器

负责处理测试配置文件的选择、验证和处理逻辑
"""

# 标准库导入
import logging

# 第三方库导入
import PyQt6.QtWidgets as QW


class TestProfileManager:
    """
    测试配置文件管理器
    负责处理测试配置文件的选择、验证和处理逻辑
    """

    def __init__(self, main_window=None):
        """
        初始化测试配置文件管理器

        Args:
            main_window: 主窗口实例（旧接口）
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)

    def select_testprofile(self):
        """
        选择测试配置文件并处理相关逻辑
        """
        try:
            # 1. 选择测试配置文件
            selected_file = self.main_window.path_manager.select_test_profile()

            if not selected_file:
                return

            # 2. 验证测试配置文件
            if not self.main_window.path_manager.validate_test_profile(selected_file):
                return

            # 3. 显示选中的文件路径
            self.main_window.lineEdit_TestProfile.setText(selected_file)

            # 4. 获取父目录
            parent_dir = self.main_window.path_manager.get_parent_directory(selected_file)
            if not parent_dir:
                return

            # 5. 设置输入路径
            self.main_window.path_manager.set_input_path(parent_dir)

            # 6. 设置输出路径
            if not self.main_window.path_manager.set_output_path(parent_dir):
                return

            # 7. 发出版本设置信号
            self.main_window.sigSetVersion.emit()

            # 8. 更新当前目录
            self.main_window.current_directory = parent_dir
            self.logger.info("Setting current directory to project root: %s", parent_dir)

        except (
            OSError,
            ValueError,
            TypeError,
            RuntimeError,
            FileNotFoundError,
            PermissionError,
        ) as e:
            self.logger.error("Error selecting Test Profile: %s", e)
            QW.QMessageBox.critical(
                self.main_window,
                "Error",
                f"Error processing Test Profile:\n{e!s}",
                QW.QMessageBox.StandardButton.Ok,
            )
