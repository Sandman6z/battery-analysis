"""
对话框管理器模块

这个模块实现了电池分析应用的对话框管理功能，包括：
- 退出确认对话框
- 关于对话框
- 首选项对话框
- 信息/警告/错误对话框
- 文件选择对话框
- 数据加载错误恢复选项对话框
"""

# 标准库导入
import logging
import os
import traceback
from pathlib import Path

# 第三方库导入
import PyQt6.QtCore as QC
import PyQt6.QtGui as QG
import PyQt6.QtWidgets as QW

# 本地应用/库导入
from battery_analysis.i18n.language_manager import _
from battery_analysis.i18n.preferences_dialog import PreferencesDialog


class DialogManager:
    """
    对话框管理器类，负责各种对话框的处理
    """
    
    def __init__(self, main_window):
        """
        初始化对话框管理器
        
        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
    
    def handle_exit(self):
        """
        处理退出操作，显示确认对话框
        """
        reply = QW.QMessageBox.question(
            self.main_window,
            '确认退出',
            '确定要退出应用程序吗？',
            QW.QMessageBox.StandardButton.Yes | QW.QMessageBox.StandardButton.No,
            QW.QMessageBox.StandardButton.No
        )

        if reply == QW.QMessageBox.StandardButton.Yes:
            self.main_window.close()
    
    def handle_about(self):
        """
        显示关于对话框
        """
        import time
        about_text = f"""
        <h3>Battery Analyzer</h3>
        <p>版本: v{self.main_window.version}</p>
        <p>电池分析工具，用于电池性能测试和数据分析。</p>
        <p>© {time.localtime().tm_year} Battery Testing System</p>
        """

        QW.QMessageBox.about(
            self.main_window,
            '关于 Battery Analyzer',
            about_text
        )
    
    def show_preferences(self):
        """
        显示首选项对话框
        """
        try:
            preferences_dialog = PreferencesDialog(self.main_window)
            
            # 连接首选项应用信号
            preferences_dialog.preferences_applied.connect(self.main_window.on_preferences_applied)
            
            # 显示对话框
            preferences_dialog.exec()
            
        except (OSError, ValueError, ImportError) as e:
            self.logger.error("显示首选项对话框时发生错误: %s", e)
            QW.QMessageBox.critical(
                self.main_window,
                _("error", "错误"),
                f"{_('show_preferences_failed', '显示首选项对话框失败')}: {str(e)}"
            )
    
    def show_user_manual(self):
        """
        显示用户手册
        """
        try:
            # 首先尝试从当前目录查找手册
            manual_paths = [
                # 相对路径
                Path(self.main_window.current_directory) / "docs" / "user_manual.pdf",
                Path(self.main_window.current_directory) / "user_manual.pdf",
                # 绝对路径 - 项目目录
                Path(__file__).parent.parent.parent / "docs" / "user_manual.pdf",
                Path(__file__).parent.parent.parent / "user_manual.pdf",
                # 常见的文档位置
                Path(os.getcwd()) / "docs" / "user_manual.pdf",
                Path(os.getcwd()) / "user_manual.pdf",
            ]
            
            manual_found = False
            for manual_path in manual_paths:
                if manual_path.exists() and manual_path.is_file():
                    try:
                        # 使用安全的文件打开方式
                        os.startfile(str(manual_path))
                        manual_found = True
                        self.logger.info("成功打开用户手册: %s", manual_path)
                        break
                    except (OSError, ValueError, RuntimeError, PermissionError) as open_error:
                        self.logger.warning("打开手册文件失败 %s: %s", manual_path, open_error)
                        continue
            
            if not manual_found:
                # 如果找不到手册文件，显示提示并提供解决方案
                QW.QMessageBox.information(
                    self.main_window,
                    "用户手册",
                    "未找到用户手册文件。\n\n"
                    "请确保以下文件存在：\n"
                    "• docs/user_manual.pdf\n"
                    "• user_manual.pdf\n\n"
                    "如需帮助，请联系技术支持。",
                    QW.QMessageBox.StandardButton.Ok
                )
                
        except (OSError, TypeError, ValueError, RuntimeError) as e:
            self.logger.error("打开用户手册失败: %s", e)
            QW.QMessageBox.warning(
                self.main_window,
                _("error", "错误"),
                f"{_('cannot_open_user_manual', '无法打开用户手册')}: {str(e)}",
                QW.QMessageBox.StandardButton.Ok
            )
    
    def show_online_help(self):
        """
        显示在线帮助
        """
        try:
            # 打开在线帮助网页
            help_url = "https://example.com/battery-analyzer-help"
            QG.QDesktopServices.openUrl(QC.QUrl(help_url))
        except (OSError, ValueError, RuntimeError, TypeError) as e:
            logging.error("打开在线帮助失败: %s", e)
            QW.QMessageBox.information(
                self.main_window,
                "在线帮助",
                "无法打开在线帮助。请检查网络连接or联系技术支持。\n\n帮助中心网址: https://example.com/battery-analyzer-help",
                QW.QMessageBox.StandardButton.Ok
            )
    
    def handle_data_error_recovery(self, error_msg):
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
                self.main_window._open_data_directory_dialog()
                
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
        """
        打开数据目录选择对话框
        """
        # 这个方法会在main_window中实现，因为它需要访问特定的界面元素
        pass
    
    def show_critical_message(self, title, message):
        """
        显示关键错误消息对话框
        
        Args:
            title: 对话框标题
            message: 错误消息
        """
        QW.QMessageBox.critical(
            self.main_window,
            title,
            message,
            QW.QMessageBox.StandardButton.Ok
        )
    
    def show_warning_message(self, title, message):
        """
        显示警告消息对话框
        
        Args:
            title: 对话框标题
            message: 警告消息
        """
        QW.QMessageBox.warning(
            self.main_window,
            title,
            message,
            QW.QMessageBox.StandardButton.Ok
        )
    
    def show_information_message(self, title, message):
        """
        显示信息消息对话框
        
        Args:
            title: 对话框标题
            message: 信息消息
        """
        QW.QMessageBox.information(
            self.main_window,
            title,
            message,
            QW.QMessageBox.StandardButton.Ok
        )
    
    def show_question_message(self, title, message, buttons=QW.QMessageBox.StandardButton.Yes | QW.QMessageBox.StandardButton.No, default_button=QW.QMessageBox.StandardButton.No):
        """
        显示问题对话框
        
        Args:
            title: 对话框标题
            message: 问题消息
            buttons: 对话框按钮
            default_button: 默认按钮
            
        Returns:
            用户的选择
        """
        return QW.QMessageBox.question(
            self.main_window,
            title,
            message,
            buttons,
            default_button
        )
