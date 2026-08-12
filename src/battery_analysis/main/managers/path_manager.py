"""路径管理类"""
import os
import logging
from pathlib import Path
from PyQt6 import QtWidgets as QW


class PathManager:
    """路径管理类，负责处理文件和目录路径的选择、验证和管理"""

    def __init__(self, main_window=None, ctx=None):
        """
        初始化路径管理器

        Args:
            main_window: 主窗口实例（旧接口）
            ctx: AppContext（新接口）
        """
        self.main_window = main_window
        self._ctx = ctx
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
                "File Error",
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
                "Filename Error",
                error_msg,
                QW.QMessageBox.StandardButton.Ok
            )
            return False
        
        # 验证文件是否为空
        is_valid, error_msg = validator.validate_file_not_empty(file_path)
        if not is_valid:
            QW.QMessageBox.warning(
                self.main_window,
                "File Error",
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
                    "File Format Error",
                    f"Invalid XML file format: {filename} is missing a root element",
                    QW.QMessageBox.StandardButton.Ok
                )
                return False
            
        except ET.ParseError as e:
            QW.QMessageBox.warning(
                self.main_window,
                "File Format Error",
                f"Failed to parse XML file: {filename} - {str(e)}",
                QW.QMessageBox.StandardButton.Ok
            )
            return False
        except Exception as e:
            QW.QMessageBox.warning(
                self.main_window,
                "File Error",
                f"Error validating XML file: {filename} - {str(e)}",
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
                self.logger.error("Invalid Test Profile directory: %s", test_profile_dir)
                return None
            
            # 获取父目录（项目根目录）
            parent_dir = os.path.dirname(test_profile_dir)
            
            # 验证父目录是否存在
            if not parent_dir or not os.path.exists(parent_dir):
                self.logger.error("Invalid parent directory: %s", parent_dir)
                return None
            
            return parent_dir
        except Exception as e:
            self.logger.error("Error getting parent directory: %s", e)
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
            self.logger.info("Input path set automatically: %s", input_path)
        else:
            self.logger.info("Input directory not found: %s", input_path)
    
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
            self.logger.warning("Output directory validation failed: %s", error_msg)
            # 仍然设置路径，但会在创建时失败
            self.main_window.lineEdit_OutputPath.setText(output_path)
            return True
        
        if os.path.exists(output_path) and os.path.isdir(output_path):
            self.main_window.lineEdit_OutputPath.setText(output_path)
        else:
            # 如果输出目录不存在，询问用户是否创建
            reply = QW.QMessageBox.question(
                self.main_window,
                "Create Output Directory",
                f"The output directory does not exist. Create it?\n\nPath: {output_path}",
                QW.QMessageBox.StandardButton.Yes | QW.QMessageBox.StandardButton.No,
                QW.QMessageBox.StandardButton.Yes
            )
            
            if reply == QW.QMessageBox.StandardButton.Yes:
                try:
                    os.makedirs(output_path, exist_ok=True)
                    self.main_window.lineEdit_OutputPath.setText(output_path)
                    self.logger.info("Output directory created and set: %s", output_path)
                except (OSError, PermissionError, FileNotFoundError) as e:
                    self.logger.error("Failed to create output directory: %s", e)
                    QW.QMessageBox.critical(
                        self.main_window,
                        "Creation Failed",
                        f"Unable to create output directory:\n{str(e)}",
                        QW.QMessageBox.StandardButton.Ok
                    )
                    return False
            else:
                # 用户选择不创建，手动设置路径但不创建目录
                self.main_window.lineEdit_OutputPath.setText(output_path)
                self.logger.info("Output directory set manually (not created): %s", output_path)
        
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
                self.logger.info("Input path set manually: %s", selected_dir)
            else:
                self.logger.warning("Input directory validation failed: %s", error_msg)
                QW.QMessageBox.warning(
                    self.main_window,
                    "Directory Error",
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
                self.logger.info("Output path set manually: %s", selected_dir)
            else:
                self.logger.warning("Output directory validation failed: %s", error_msg)
                QW.QMessageBox.warning(
                    self.main_window,
                    "Directory Error",
                    error_msg,
                    QW.QMessageBox.StandardButton.Ok
                )
