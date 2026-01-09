# -*- coding: utf-8 -*-
"""
可视化管理器

负责处理可视化工具的启动、管理和错误处理
"""

import logging
import matplotlib
import subprocess
import sys
import traceback
from pathlib import Path
from typing import Optional

# 第三方库导入
from PyQt6 import QtWidgets as QW
from PyQt6 import QtCore as QC
from PyQt6 import QtGui as QG

# 本地应用/库导入
from battery_analysis.i18n.language_manager import _
from battery_analysis.main.factories.visualizer_factory import VisualizerFactory


class VisualizationManager:
    """
    可视化管理器类，负责处理可视化工具的启动和管理
    """
    
    def __init__(self, main_window):
        """
        初始化可视化管理器
        
        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        self.visualizer_factory = VisualizerFactory()
        
    def run_visualizer(self, xml_path=None) -> None:
        """
        运行可视化工具，使用工厂模式解耦依赖
        
        Args:
            xml_path: 可选的XML数据路径
        """
        self.logger.info("进入visualization_manager.run_visualizer方法")
        
        # 检查xml_path是否为布尔值，如果是，则忽略（可能来自QAction的triggered信号）
        if isinstance(xml_path, bool):
            self.logger.info("检测到布尔类型的xml_path参数，忽略它")
            xml_path = None
        
        # viewer是独立工具，不需要从主UI获取数据路径，让其自行处理数据搜索
        
        self.main_window.statusBar_BatteryAnalysis.showMessage(_("starting_visualizer", "启动可视化工具..."))

        try:
            # 确保所有matplotlib资源都被释放（只清理全局资源，不涉及实例）
            try:
                import matplotlib.pyplot as plt
                plt.close('all')  # 关闭所有打开的matplotlib窗口
            except (ImportError, RuntimeError) as e:
                self.logger.warning("清理matplotlib全局资源时出错: %s", e)
            
            # 使用工厂模式创建可视化器（使用局部变量，不存储为实例属性）
            self.logger.info("使用工厂模式创建可视化器")
            visualizer = self.visualizer_factory.create_visualizer("battery_chart")
            
            if visualizer is None:
                raise RuntimeError("无法创建可视化器实例")

            # 显示可视化（不传递数据路径，让viewer自行处理数据搜索和加载）
            self.logger.info("显示可视化，让viewer独立处理数据")
            show_success = visualizer.show_figure()
            
            if show_success:
                # 更新状态栏
                self.main_window.statusBar_BatteryAnalysis.showMessage(_("visualizer_started", "可视化工具已启动"))
                self.logger.info("可视化工具启动完成")
            else:
                raise RuntimeError("显示可视化失败")

        except (AttributeError, TypeError, OSError, ValueError, RuntimeError, ImportError, PermissionError, subprocess.SubprocessError) as e:
            error_msg = str(e)
            self.logger.error("启动可视化工具时出错: %s", error_msg)
            self.logger.error("异常堆栈: %s", traceback.format_exc())
            
            # 判断是否为数据相关错误
            data_error_keywords = ['data', 'csv', 'load', 'file', 'path', 'config', 'info_image', '数据']
            is_data_error = any(keyword in error_msg.lower() for keyword in data_error_keywords)
            
            if is_data_error:
                # 对于数据相关错误，提供恢复选项
                self._handle_data_error_recovery(error_msg)
            else:
                # 对于其他错误，显示标准错误对话框
                QW.QMessageBox.critical(
                    self.main_window,
                    "错误",
                    f"启动可视化工具时出错:\n\n{error_msg}\n\n请检查配置文件或联系技术支持。",
                    QW.QMessageBox.StandardButton.Ok
                )
            
            self.main_window.statusBar_BatteryAnalysis.showMessage("状态:就绪")
    
    def _handle_data_error_recovery(self, error_msg: str):
        """
        处理数据相关错误的恢复选项
        
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
        retry_option = QW.QRadioButton("重新选择数据目录")
        retry_option.setChecked(True)
        button_group.addButton(retry_option, 1)
        layout.addWidget(retry_option)
        
        # 选项2: 使用默认配置
        default_option = QW.QRadioButton("使用默认配置重新启动")
        button_group.addButton(default_option, 2)
        layout.addWidget(default_option)
        
        # 选项3: 取消操作
        cancel_option = QW.QRadioButton("取消操作")
        button_group.addButton(cancel_option, 3)
        layout.addWidget(cancel_option)
        
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
                self.run_visualizer(xml_path=None)
                
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
        """
        打开数据目录选择对话框
        """
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
                    self.run_visualizer(xml_path=directory)
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
            self.main_window.statusBar_BatteryAnalysis.showMessage(_("status_ready", "状态:就绪"))
    
    def show_visualizer_error(self, error_msg: str):
        """
        在主线程中显示可视化工具错误消息
        
        Args:
            error_msg: 错误信息
        """
        QW.QMessageBox.critical(
            self.main_window,
            _("error", "错误"),
            f"{_('visualizer_start_error', '启动可视化工具时发生错误')}: {error_msg}",
            QW.QMessageBox.StandardButton.Ok
        )
        self.main_window.statusBar_BatteryAnalysis.showMessage(_("status_ready", "状态:就绪"))
