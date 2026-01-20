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
        from battery_analysis.utils.file_validator import FileValidator
        
        validator = FileValidator()
        
        # 验证文件是否存在
        is_valid, error_msg = validator.validate_file_exists(file_path)
        if not is_valid:
            QW.QMessageBox.warning(
                self.main_window,
                "文件错误",
                error_msg,
                QW.QMessageBox.StandardButton.Ok
            )
            return False
        
        # 获取文件名
        filename = os.path.basename(file_path)
        
        # 验证XML文件名
        is_valid, error_msg = validator.validate_xml_filename(filename)
        if not is_valid:
            QW.QMessageBox.warning(
                self.main_window,
                "文件名错误",
                error_msg,
                QW.QMessageBox.StandardButton.Ok
            )
            return False
        
        # 验证文件是否为空
        is_valid, error_msg = validator.validate_file_not_empty(file_path)
        if not is_valid:
            QW.QMessageBox.warning(
                self.main_window,
                "文件错误",
                error_msg,
                QW.QMessageBox.StandardButton.Ok
            )
            return False
        
        # 验证XML文件内容
        try:
            import xml.etree.ElementTree as ET
            
            # 尝试使用不同编码解析XML文件
            try:
                # 尝试默认编码解析
                tree = ET.parse(file_path)
                root = tree.getroot()
            except UnicodeDecodeError:
                # 尝试使用UTF-8编码解析
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    xml_content = f.read()
                tree = ET.ElementTree(ET.fromstring(xml_content))
                root = tree.getroot()
            except Exception as e:
                # 尝试使用GBK编码解析
                with open(file_path, 'r', encoding='gbk', errors='ignore') as f:
                    xml_content = f.read()
                tree = ET.ElementTree(ET.fromstring(xml_content))
                root = tree.getroot()
            
            # 验证XML是否有根元素
            if root is None:
                QW.QMessageBox.warning(
                    self.main_window,
                    "文件格式错误",
                    f"XML文件格式错误: {filename} 缺少根元素",
                    QW.QMessageBox.StandardButton.Ok
                )
                return False
            
        except ET.ParseError as e:
            QW.QMessageBox.warning(
                self.main_window,
                "文件格式错误",
                f"XML文件解析失败: {filename} - {str(e)}",
                QW.QMessageBox.StandardButton.Ok
            )
            return False
        except Exception as e:
            QW.QMessageBox.warning(
                self.main_window,
                "文件错误",
                f"验证XML文件时发生错误: {filename} - {str(e)}",
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
        from battery_analysis.utils.file_validator import FileValidator
        validator = FileValidator()
        
        # 自动设置output path为同级的3_analysis results文件夹
        output_path = os.path.join(parent_dir, "3_analysis results")
        
        # 验证输出目录
        is_valid, error_msg = validator.validate_output_directory(output_path)
        if not is_valid:
            self.logger.warning("输出目录验证失败: %s", error_msg)
            # 仍然设置路径，但会在创建时失败
            self.main_window.lineEdit_OutputPath.setText(output_path)
            return True
        
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
        from battery_analysis.utils.file_validator import FileValidator
        validator = FileValidator()
        
        selected_dir = QW.QFileDialog.getExistingDirectory(
            self.main_window, "Select Input Path", self.main_window.current_directory)
        
        if selected_dir != "":
            # 验证输入目录
            is_valid, error_msg = validator.validate_input_directory(selected_dir)
            if is_valid:
                self.main_window.lineEdit_InputPath.setText(selected_dir)
                self.main_window.sigSetVersion.emit()
                self.main_window.current_directory = os.path.join(selected_dir, "../../")
                self.logger.info("手动设置输入路径: %s", selected_dir)
            else:
                self.logger.warning("输入目录验证失败: %s", error_msg)
                QW.QMessageBox.warning(
                    self.main_window,
                    "目录错误",
                    error_msg,
                    QW.QMessageBox.StandardButton.Ok
                )
    
    def select_outputpath(self) -> None:
        """
        选择输出路径
        """
        from battery_analysis.utils.file_validator import FileValidator
        validator = FileValidator()
        
        selected_dir = QW.QFileDialog.getExistingDirectory(
            self.main_window, "Select Output Path", self.main_window.current_directory)
        
        if selected_dir != "":
            # 验证输出目录
            is_valid, error_msg = validator.validate_output_directory(selected_dir)
            if is_valid:
                self.main_window.lineEdit_OutputPath.setText(selected_dir)
                self.main_window.sigSetVersion.emit()
                self.main_window.current_directory = os.path.join(selected_dir, "../")
                self.logger.info("手动设置输出路径: %s", selected_dir)
            else:
                self.logger.warning("输出目录验证失败: %s", error_msg)
                QW.QMessageBox.warning(
                    self.main_window,
                    "目录错误",
                    error_msg,
                    QW.QMessageBox.StandardButton.Ok
                )
