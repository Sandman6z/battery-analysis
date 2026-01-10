"""路径管理类"""
import os
import logging
from pathlib import Path
from PyQt6 import QtWidgets as QW


class PathManager:
    """路径管理类，负责处理文件和目录路径的选择、验证和管理"""
    
    def __init__(self, main_window):
        """
        初始化路径管理器
        
        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
    
    def select_test_profile(self):
        """
        选择测试配置文件
        
        Returns:
            选中的文件路径，或None如果取消选择
        """
        selected_file, _ = QW.QFileDialog.getOpenFileName(
            self.main_window, "Select Test Profile", self.main_window.current_directory, "XML Files(*.xml)")
        
        return selected_file.strip() if selected_file else None
    
    def validate_test_profile(self, file_path):
        """
        验证测试配置文件
        
        Args:
            file_path: 要验证的文件路径
            
        Returns:
            bool: 验证是否通过
        """
        # 验证文件是否存在
        if not os.path.exists(file_path):
            QW.QMessageBox.warning(
                self.main_window,
                "文件错误",
                f"选择的文件不存在:\n{file_path}",
                QW.QMessageBox.StandardButton.Ok
            )
            return False
        
        # 验证文件扩展名
        if not file_path.lower().endswith('.xml'):
            QW.QMessageBox.warning(
                self.main_window,
                "文件格式错误",
                "请选择XML格式的Test Profile文件",
                QW.QMessageBox.StandardButton.Ok
            )
            return False
        
        return True
    
    def get_parent_directory(self, file_path):
        """
        获取文件的父目录
        
        Args:
            file_path: 文件路径
            
        Returns:
            父目录路径，或None如果获取失败
        """
        try:
            # 获取Test Profile的目录
            test_profile_dir = os.path.dirname(file_path)
            
            # 验证目录是否有效
            if not test_profile_dir or not os.path.exists(test_profile_dir):
                self.logger.error("无效的Test Profile目录: %s", test_profile_dir)
                return None
            
            # 获取父目录（项目根目录）
            parent_dir = os.path.dirname(test_profile_dir)
            
            # 验证父目录是否存在
            if not parent_dir or not os.path.exists(parent_dir):
                self.logger.error("无效的父目录: %s", parent_dir)
                return None
            
            return parent_dir
        except Exception as e:
            self.logger.error("获取父目录时发生错误: %s", e)
            return None
    
    def set_input_path(self, parent_dir):
        """
        设置输入路径
        
        Args:
            parent_dir: 父目录路径
        """
        # 自动设置input path为同级的2_xlsx文件夹
        input_path = os.path.join(parent_dir, "2_xlsx")
        if os.path.exists(input_path) and os.path.isdir(input_path):
            self.main_window.lineEdit_InputPath.setText(input_path)
            self.main_window.sigSetVersion.emit()
            self.logger.info("自动设置输入路径: %s", input_path)
        else:
            self.logger.info("未找到输入目录: %s", input_path)
    
    def set_output_path(self, parent_dir):
        """
        设置输出路径
        
        Args:
            parent_dir: 父目录路径
        """
        # 自动设置output path为同级的3_analysis results文件夹
        output_path = os.path.join(parent_dir, "3_analysis results")
        if os.path.exists(output_path) and os.path.isdir(output_path):
            self.main_window.lineEdit_OutputPath.setText(output_path)
        else:
            # 如果输出目录不存在，询问用户是否创建
            reply = QW.QMessageBox.question(
                self.main_window,
                "创建输出目录",
                f"输出目录不存在，是否创建？\n\n路径: {output_path}",
                QW.QMessageBox.StandardButton.Yes | QW.QMessageBox.StandardButton.No,
                QW.QMessageBox.StandardButton.Yes
            )
            
            if reply == QW.QMessageBox.StandardButton.Yes:
                try:
                    os.makedirs(output_path, exist_ok=True)
                    self.main_window.lineEdit_OutputPath.setText(output_path)
                    self.logger.info("创建并设置输出目录: %s", output_path)
                except (OSError, PermissionError, FileNotFoundError) as e:
                    self.logger.error("创建输出目录失败: %s", e)
                    QW.QMessageBox.critical(
                        self.main_window,
                        "创建失败",
                        f"无法创建输出目录:\n{str(e)}",
                        QW.QMessageBox.StandardButton.Ok
                    )
                    return False
            else:
                # 用户选择不创建，手动设置路径但不创建目录
                self.main_window.lineEdit_OutputPath.setText(output_path)
                self.logger.info("手动设置输出目录（未创建）: %s", output_path)
        
        return True
    
    def select_inputpath(self) -> None:
        """
        选择输入路径
        """
        selected_dir = QW.QFileDialog.getExistingDirectory(
            self.main_window, "Select Input Path", self.main_window.current_directory)
        
        if selected_dir != "":
            self.main_window.lineEdit_InputPath.setText(selected_dir)
            self.main_window.sigSetVersion.emit()
            self.main_window.current_directory = os.path.join(selected_dir, "../../")
            self.logger.info("手动设置输入路径: %s", selected_dir)
    
    def select_outputpath(self) -> None:
        """
        选择输出路径
        """
        selected_dir = QW.QFileDialog.getExistingDirectory(
            self.main_window, "Select Output Path", self.main_window.current_directory)
        
        if selected_dir != "":
            self.main_window.lineEdit_OutputPath.setText(selected_dir)
            self.main_window.sigSetVersion.emit()
            self.main_window.current_directory = os.path.join(selected_dir, "../")
            self.logger.info("手动设置输出路径: %s", selected_dir)
