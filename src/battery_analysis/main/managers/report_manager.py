"""报告管理类"""
import os
from pathlib import Path
import logging
from PyQt6 import QtWidgets as QW


class ReportManager:
    """报告管理类"""
    
    def __init__(self, main_window):
        """
        初始化报告管理器
        
        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
    
    def open_report(self, dialog=None):
        """
        打开生成的docx格式报告
        
        Args:
            dialog: 父对话框，可选
        """
        output_path_str = self.main_window.lineEdit_OutputPath.text()
        version = self.main_window.lineEdit_Version.text()
        
        try:
            output_path = Path(output_path_str)
            
            if not output_path.exists() or not output_path.is_dir():
                QW.QMessageBox.warning(self.main_window, "警告", f"无效的输出路径: {output_path}")
                return
            
            # 搜索docx文件
            docx_files = list(output_path.rglob("*.docx"))
            
            if not docx_files:
                QW.QMessageBox.information(self.main_window, "信息", f"未找到docx报告文件\n搜索路径: {output_path}")
                return
            
            # 找到与当前版本匹配的报告
            target_docx = None
            for docx_file in docx_files:
                if f"_V{version}" in docx_file.name:
                    target_docx = docx_file
                    break
            
            # 如果没有匹配版本，使用最新的报告
            if not target_docx and docx_files:
                target_docx = sorted(docx_files, key=lambda f: f.stat().st_mtime, reverse=True)[0]
            
            # 打开报告
            if target_docx:
                target_path = str(target_docx)
                try:
                    os.startfile(target_path)
                except Exception as popen_error:
                    self.logger.error("打开报告失败: %s", popen_error)
                    QW.QMessageBox.critical(self.main_window, "错误", f"打开报告失败: {str(popen_error)}")
                    
                # 关闭对话框（如果提供）
                if dialog:
                    dialog.accept()
        except Exception as e:
            QW.QMessageBox.critical(self.main_window, "错误", f"打开报告失败: {str(e)}")
            self.logger.error("打开报告失败: %s", e)
    
    def open_report_path(self, dialog=None):
        """
        打开报告所在的文件夹
        
        Args:
            dialog: 父对话框，可选
        """
        output_path_str = self.main_window.lineEdit_OutputPath.text()
        
        try:
            output_path = Path(output_path_str)
            
            if not output_path.exists() or not output_path.is_dir():
                QW.QMessageBox.warning(self.main_window, "警告", f"无效的输出路径: {output_path}")
                return
            
            # 直接打开输出路径
            try:
                os.startfile(str(output_path))
            except Exception as popen_error:
                self.logger.error("打开报告文件夹失败: %s", popen_error)
                QW.QMessageBox.critical(self.main_window, "错误", f"打开文件夹失败: {str(popen_error)}")
            
            # 关闭对话框（如果提供）
            if dialog:
                dialog.accept()
        except Exception as e:
            QW.QMessageBox.critical(self.main_window, "错误", f"打开文件夹失败: {str(e)}")
            self.logger.error("打开报告文件夹失败: %s", e)
    
    def show_analysis_complete_dialog(self):
        """
        显示分析完成对话框，包含"打开报告"、"打开路径"和"确定"按钮
        """
        dialog = QW.QDialog(self.main_window)
        dialog.setWindowTitle("分析完成")
        dialog.setFixedSize(450, 150)
        dialog.setWindowFlags(
            QW.Qt.WindowType.Window | 
            QW.Qt.WindowType.WindowTitleHint |
            QW.Qt.WindowType.WindowCloseButtonHint
        )
        
        layout = QW.QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 添加状态文本标签
        status_label = QW.QLabel("电池分析已完成！")
        status_label.setAlignment(QW.Qt.AlignmentFlag.AlignCenter)
        status_label.setWordWrap(True)
        layout.addWidget(status_label)
        
        # 添加底部按钮布局
        button_layout = QW.QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setAlignment(QW.Qt.AlignmentFlag.AlignCenter)
        
        # 添加打开报告按钮
        open_report_button = QW.QPushButton("打开报告")
        open_report_button.setMinimumHeight(32)
        open_report_button.setMinimumWidth(120)
        open_report_button.clicked.connect(lambda: self.open_report(dialog))
        button_layout.addWidget(open_report_button)
        
        # 添加打开路径按钮
        open_path_button = QW.QPushButton("打开路径")
        open_path_button.setMinimumHeight(32)
        open_path_button.setMinimumWidth(120)
        open_path_button.clicked.connect(lambda: self.open_report_path(dialog))
        button_layout.addWidget(open_path_button)
        
        # 添加确定按钮
        ok_button = QW.QPushButton("确定")
        ok_button.setMinimumHeight(32)
        ok_button.setMinimumWidth(120)
        ok_button.clicked.connect(dialog.accept)
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        dialog.exec()
