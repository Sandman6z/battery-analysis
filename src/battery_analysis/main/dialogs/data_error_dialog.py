"""数据错误对话框模块"""
import logging
from PyQt6 import QtWidgets as QW
from PyQt6 import QtCore as QC


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
        dialog.setWindowTitle("数据加载错误 - 恢复选项")
        dialog.setModal(True)
        dialog.resize(500, 300)
        
        layout = QW.QVBoxLayout(dialog)
        
        # 错误信息标签
        error_label = QW.QLabel("无法加载电池数据，请选择如何继续:")
        error_label.setWordWrap(True)
        error_label.setStyleSheet("font-weight: bold; color: red;")
        layout.addWidget(error_label)
        
        # 详细错误信息
        details_label = QW.QLabel(f"错误详情: {error_msg}")
        details_label.setWordWrap(True)
        details_label.setStyleSheet("background-color: #f0f0f0; padding: 10px; border: 1px solid #ccc;")
        layout.addWidget(details_label)
        
        # 恢复选项说明
        help_label = QW.QLabel("请选择以下恢复选项之一:")
        help_label.setStyleSheet("margin-top: 10px; font-weight: bold;")
        layout.addWidget(help_label)
        
        # 按钮组
        button_group = QW.QButtonGroup(dialog)
        
        # 选项1: 重新选择数据目录
        self.retry_option = QW.QRadioButton("重新选择数据目录")
        self.retry_option.setChecked(True)
        button_group.addButton(self.retry_option, 1)
        layout.addWidget(self.retry_option)
        
        # 选项2: 使用默认配置
        self.default_option = QW.QRadioButton("使用默认配置重新启动")
        button_group.addButton(self.default_option, 2)
        layout.addWidget(self.default_option)
        
        # 选项3: 取消操作
        self.cancel_option = QW.QRadioButton("取消操作")
        button_group.addButton(self.cancel_option, 3)
        layout.addWidget(self.cancel_option)
        
        # 添加按钮
        button_layout = QW.QHBoxLayout()
        
        ok_button = QW.QPushButton("确定")
        ok_button.clicked.connect(dialog.accept)
        button_layout.addWidget(ok_button)
        
        cancel_button = QW.QPushButton("取消")
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        # 显示对话框
        if dialog.exec() == QW.QDialog.DialogCode.Accepted:
            selected_id = button_group.checkedId()
            
            if selected_id == 1:
                # 重新选择数据目录
                self.main_window.statusBar_BatteryAnalysis.showMessage("正在打开数据目录选择...")
                self._open_data_directory_dialog()
                
            elif selected_id == 2:
                # 使用默认配置重新启动
                self.main_window.statusBar_BatteryAnalysis.showMessage("使用默认配置重新启动...")
                QW.QMessageBox.information(
                    self.main_window,
                    "重新启动",
                    "应用将使用默认配置重新启动。\n\n请确保您有有效的数据文件可用。",
                    QW.QMessageBox.StandardButton.Ok
                )
                # 清空配置字段并重新启动
                if hasattr(self.main_window, 'lineEdit_TestProfile'):
                    self.main_window.lineEdit_TestProfile.clear()
                # 递归调用，但使用默认配置
                self.main_window.run_visualizer(xml_path=None)
                
            else:
                # 取消操作
                self.main_window.statusBar_BatteryAnalysis.showMessage("操作已取消")
                QW.QMessageBox.information(
                    self.main_window,
                    "取消",
                    "操作已取消。您可以通过菜单 'File -> Open Data' 重新尝试。",
                    QW.QMessageBox.StandardButton.Ok
                )
        else:
            self.main_window.statusBar_BatteryAnalysis.showMessage("操作已取消")
    
    def _open_data_directory_dialog(self):
        """打开数据目录选择对话框"""
        try:
            # 打开目录选择对话框
            directory = QW.QFileDialog.getExistingDirectory(
                self.main_window,
                "选择包含电池数据的目录",
                "",
                QW.QFileDialog.Option.ShowDirsOnly | QW.QFileDialog.Option.DontResolveSymlinks
            )
            
            if directory:
                self.main_window.statusBar_BatteryAnalysis.showMessage(f"已选择目录: {directory}")
                
                # 检查目录中是否有Info_Image.csv文件
                import os
                info_image_path = os.path.join(directory, "Info_Image.csv")
                if os.path.exists(info_image_path):
                    QW.QMessageBox.information(
                        self.main_window,
                        "数据目录确认",
                        f"找到数据文件: {info_image_path}\n\n应用将尝试使用此数据重新启动可视化工具。",
                        QW.QMessageBox.StandardButton.Ok
                    )
                    
                    # 更新界面上的配置路径
                    if hasattr(self.main_window, 'lineEdit_TestProfile'):
                        self.main_window.lineEdit_TestProfile.setText(directory)
                    
                    # 重新运行可视化工具
                    self.main_window.run_visualizer(xml_path=directory)
                else:
                    QW.QMessageBox.warning(
                        self.main_window,
                        "数据目录无效",
                        f"在选择的目录中没有找到 Info_Image.csv 文件:\n\n{directory}\n\n请确保选择的目录包含有效的电池数据文件。",
                        QW.QMessageBox.StandardButton.Ok
                    )
                    self.main_window.statusBar_BatteryAnalysis.showMessage("无效的数据目录")
            else:
                self.main_window.statusBar_BatteryAnalysis.showMessage("未选择目录")
                
        except (OSError, TypeError, ValueError, RuntimeError, PermissionError, FileNotFoundError) as e:
            self.logger.error("打开数据目录对话框时出错: %s", str(e))
            QW.QMessageBox.critical(
                self.main_window,
                "错误",
                f"打开目录选择对话框时出错:\n\n{str(e)}",
                QW.QMessageBox.StandardButton.Ok
            )
            self.main_window.statusBar_BatteryAnalysis.showMessage("状态:就绪")
