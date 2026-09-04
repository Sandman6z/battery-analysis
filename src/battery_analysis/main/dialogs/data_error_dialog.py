"""数据错误对话框模块"""

import logging

from PyQt6 import QtWidgets as QW


class DataErrorRecoveryDialog:
    """数据加载错误恢复对话框"""

    def __init__(self, main_window):
        """
        初始化数据错误恢复对话框

        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)

    def show(self, error_msg: str):
        """
        显示数据错误恢复对话框

        Args:
            error_msg: 错误信息
        """
        # 创建自定义对话框
        dialog = QW.QDialog(self.main_window)
        dialog.setWindowTitle("Data Loading Error - Recovery Options")
        dialog.setModal(True)
        dialog.resize(500, 300)

        layout = QW.QVBoxLayout(dialog)

        # 错误信息标签
        error_label = QW.QLabel("Unable to load battery data. Please choose how to continue:")
        error_label.setWordWrap(True)
        error_label.setStyleSheet("font-weight: bold; color: red;")
        layout.addWidget(error_label)

        # 详细错误信息
        details_label = QW.QLabel(f"Error details: {error_msg}")
        details_label.setWordWrap(True)
        details_label.setStyleSheet(
            "background-color: #f0f0f0; padding: 10px; border: 1px solid #ccc;"
        )
        layout.addWidget(details_label)

        # 恢复选项说明
        help_label = QW.QLabel("Please select one of the following recovery options:")
        help_label.setStyleSheet("margin-top: 10px; font-weight: bold;")
        layout.addWidget(help_label)

        # 按钮组
        button_group = QW.QButtonGroup(dialog)

        # 选项1: 重新选择数据目录
        self.retry_option = QW.QRadioButton("Reselect Data Directory")
        self.retry_option.setChecked(True)
        button_group.addButton(self.retry_option, 1)
        layout.addWidget(self.retry_option)

        # 选项2: 使用默认配置
        self.default_option = QW.QRadioButton("Restart with Default Configuration")
        button_group.addButton(self.default_option, 2)
        layout.addWidget(self.default_option)

        # 选项3: 取消操作
        self.cancel_option = QW.QRadioButton("Cancel Operation")
        button_group.addButton(self.cancel_option, 3)
        layout.addWidget(self.cancel_option)

        # 添加按钮
        button_layout = QW.QHBoxLayout()

        ok_button = QW.QPushButton("OK")
        ok_button.clicked.connect(dialog.accept)
        button_layout.addWidget(ok_button)

        cancel_button = QW.QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        # 显示对话框
        if dialog.exec() == QW.QDialog.DialogCode.Accepted:
            selected_id = button_group.checkedId()

            if selected_id == 1:
                # 重新选择数据目录
                self.main_window.statusBar_BatteryAnalysis.showMessage(
                    "Opening data directory selector..."
                )
                self._open_data_directory_dialog()

            elif selected_id == 2:
                # 使用默认配置重新启动
                self.main_window.statusBar_BatteryAnalysis.showMessage(
                    "Restarting with default configuration..."
                )

                QW.QMessageBox.information(
                    self.main_window,
                    "Restart",
                    "The application will restart with default configuration.\n\nPlease ensure you have valid data files available.",
                    QW.QMessageBox.StandardButton.Ok,
                )
                # 清空配置字段并重新启动
                if hasattr(self.main_window, "lineEdit_TestProfile"):
                    self.main_window.lineEdit_TestProfile.clear()
                # 递归调用，但使用默认配置
                self.main_window.visualization_manager.run_visualizer(xml_path=None)

            else:
                # 取消操作
                self.main_window.statusBar_BatteryAnalysis.showMessage("Operation canceled")
                QW.QMessageBox.information(
                    self.main_window,
                    "Canceled",
                    "Operation canceled. You can try again via the menu 'File -> Open Data'.",
                    QW.QMessageBox.StandardButton.Ok,
                )
        else:
            self.main_window.statusBar_BatteryAnalysis.showMessage("Operation canceled")

    def _open_data_directory_dialog(self):
        """打开数据目录选择对话框"""
        try:
            # 打开目录选择对话框
            directory = QW.QFileDialog.getExistingDirectory(
                self.main_window,
                "Select a directory containing battery data",
                "",
                QW.QFileDialog.Option.ShowDirsOnly | QW.QFileDialog.Option.DontResolveSymlinks,
            )

            if directory:
                self.main_window.statusBar_BatteryAnalysis.showMessage(
                    f"Selected directory: {directory}"
                )

                # 检查目录中是否有Info_Image.csv文件
                import os

                info_image_path = os.path.join(directory, "Info_Image.csv")
                if os.path.exists(info_image_path):
                    QW.QMessageBox.information(
                        self.main_window,
                        "Data Directory Confirmed",
                        f"Found data file: {info_image_path}\n\nThe application will try to restart the visualization tool using this data.",
                        QW.QMessageBox.StandardButton.Ok,
                    )

                    # 更新界面上的配置路径
                    if hasattr(self.main_window, "lineEdit_TestProfile"):
                        self.main_window.lineEdit_TestProfile.setText(directory)

                    # 重新运行可视化工具
                    self.main_window.visualization_manager.run_visualizer(xml_path=directory)
                else:
                    QW.QMessageBox.warning(
                        self.main_window,
                        "Invalid Data Directory",
                        f"No Info_Image.csv file was found in the selected directory:\n\n{directory}\n\nPlease ensure the selected directory contains valid battery data files.",
                        QW.QMessageBox.StandardButton.Ok,
                    )
                    self.main_window.statusBar_BatteryAnalysis.showMessage("Invalid data directory")
            else:
                self.main_window.statusBar_BatteryAnalysis.showMessage("No directory selected")

        except (
            OSError,
            TypeError,
            ValueError,
            RuntimeError,
            PermissionError,
            FileNotFoundError,
        ) as e:
            self.logger.error("Error opening data directory dialog: %s", str(e))
            QW.QMessageBox.critical(
                self.main_window,
                "Error",
                f"Error opening the directory selection dialog:\n\n{e!s}",
                QW.QMessageBox.StandardButton.Ok,
            )
            self.main_window.statusBar_BatteryAnalysis.showMessage("Ready")
