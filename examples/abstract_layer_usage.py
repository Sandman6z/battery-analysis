# -*- coding: utf-8 -*-
"""
抽象层使用示例

展示如何使用抽象层来替换直接的第三方库调用
"""

import logging
from typing import Any, Optional, Dict, List
from battery_analysis.ui.interfaces.iuiframework import IUIFramework, MessageBoxType, UIFrameworkType
from battery_analysis.ui.frameworks.pyqt6_ui_framework import PyQt6UIFramework


class UIController:
    """UI控制器 - 使用抽象层处理UI操作"""
    
    def __init__(self, ui_framework: IUIFramework):
        """初始化UI控制器
        
        Args:
            ui_framework: UI框架抽象实例
        """
        self.ui_framework = ui_framework
        self.logger = logging.getLogger(__name__)
        self.main_window = None
        self.progress_dialog = None
    
    def initialize_application(self) -> bool:
        """初始化应用程序"""
        try:
            # 使用抽象层创建应用程序
            app = self.ui_framework.create_application()
            
            # 使用抽象层创建主窗口
            self.main_window = self.ui_framework.create_main_window()
            
            self.logger.info("UI应用程序初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"UI应用程序初始化失败: {e}")
            return False
    
    def show_main_window(self) -> None:
        """显示主窗口"""
        try:
            if self.main_window:
                self.main_window.show()
                self.logger.info("主窗口显示成功")
        except Exception as e:
            self.logger.error(f"显示主窗口失败: {e}")
    
    def show_message(self, title: str, message: str, msg_type: MessageBoxType) -> Any:
        """显示消息框
        
        Args:
            title: 窗口标题
            message: 消息内容
            msg_type: 消息类型
            
        Returns:
            Any: 消息框实例
        """
        try:
            # 使用抽象层显示消息框
            return self.ui_framework.show_message_box(
                self.main_window, title, message, msg_type
            )
        except Exception as e:
            self.logger.error(f"显示消息框失败: {e}")
            return None
    
    def show_error(self, message: str) -> None:
        """显示错误消息"""
        self.show_message("错误", message, MessageBoxType.CRITICAL)
    
    def show_info(self, message: str) -> None:
        """显示信息消息"""
        self.show_message("信息", message, MessageBoxType.INFORMATION)
    
    def ask_question(self, message: str) -> bool:
        """询问用户问题
        
        Returns:
            bool: 用户选择（True=是，False=否）
        """
        try:
            result = self.show_message("确认", message, MessageBoxType.QUESTION)
            # 根据UI框架的实现，返回适当的布尔值
            return result in [True, "Yes", "yes", "Y", "y"]
        except Exception as e:
            self.logger.error(f"询问用户问题失败: {e}")
            return False
    
    def select_file(self, caption: str = "选择文件", 
                   directory: str = "", 
                   filter_pattern: str = "") -> Optional[str]:
        """选择文件
        
        Args:
            caption: 对话框标题
            directory: 默认目录
            filter_pattern: 文件过滤器
            
        Returns:
            Optional[str]: 选择的文件路径，失败返回None
        """
        try:
            file_dialog = self.ui_framework.create_file_dialog(
                self.main_window, caption, directory, filter_pattern
            )
            
            # 注意：这里需要根据具体的UI框架实现来处理文件选择结果
            # PyQt6和Tkinter的文件对话框API不同
            if hasattr(file_dialog, 'getOpenFileName'):
                # PyQt6
                file_path, _ = file_dialog.getOpenFileName()
                return file_path if file_path else None
            else:
                # Tkinter直接返回文件路径
                return file_dialog if file_dialog else None
                
        except Exception as e:
            self.logger.error(f"选择文件失败: {e}")
            return None
    
    def create_progress_dialog(self) -> Any:
        """创建进度对话框"""
        try:
            self.progress_dialog = self.ui_framework.create_progress_dialog(self.main_window)
            return self.progress_dialog
        except Exception as e:
            self.logger.error(f"创建进度对话框失败: {e}")
            return None
    
    def update_progress(self, value: int, text: str = "") -> None:
        """更新进度
        
        Args:
            value: 进度值（0-100）
            text: 进度文本
        """
        try:
            if self.progress_dialog:
                # 使用抽象层更新进度（如果支持）
                if hasattr(self.progress_dialog, 'setValue'):
                    self.progress_dialog.setValue(value)
                if hasattr(self.progress_dialog, 'setLabelText') and text:
                    self.progress_dialog.setLabelText(text)
        except Exception as e:
            self.logger.error(f"更新进度失败: {e}")
    
    def close_progress_dialog(self) -> None:
        """关闭进度对话框"""
        try:
            if self.progress_dialog:
                self.progress_dialog.close()
                self.progress_dialog = None
        except Exception as e:
            self.logger.error(f"关闭进度对话框失败: {e}")
    
    def run_application(self) -> int:
        """运行应用程序
        
        Returns:
            int: 退出代码
        """
        try:
            app = self.ui_framework.create_application()
            return self.ui_framework.exec_application(app)
        except Exception as e:
            self.logger.error(f"运行应用程序失败: {e}")
            return 1


# 工厂模式来创建UI控制器
class UIControllerFactory:
    """UI控制器工厂"""
    
    @staticmethod
    def create_ui_controller(framework_type: UIFrameworkType = UIFrameworkType.PYQT6) -> UIController:
        """创建UI控制器
        
        Args:
            framework_type: UI框架类型
            
        Returns:
            UIController: UI控制器实例
        """
        try:
            if framework_type == UIFrameworkType.PYQT6:
                ui_framework = PyQt6UIFramework()
            elif framework_type == UIFrameworkType.TKINTER:
                # 将来可以添加Tkinter实现
                from battery_analysis.ui.frameworks.tkinter_ui_framework import TkinterUIFramework
                ui_framework = TkinterUIFramework()
            else:
                raise ValueError(f"不支持的UI框架类型: {framework_type}")
            
            return UIController(ui_framework)
            
        except Exception as e:
            logging.error(f"创建UI控制器失败: {e}")
            raise


# 使用示例
def example_usage():
    """使用示例"""
    logging.basicConfig(level=logging.INFO)
    
    try:
        # 创建UI控制器 - 使用PyQt6框架
        ui_controller = UIControllerFactory.create_ui_controller(UIFrameworkType.PYQT6)
        
        # 初始化应用程序
        if ui_controller.initialize_application():
            # 显示信息消息
            ui_controller.show_info("应用程序初始化成功！")
            
            # 询问用户确认
            if ui_controller.ask_question("是否要继续操作？"):
                # 选择文件
                file_path = ui_controller.select_file(
                    caption="选择数据文件",
                    filter_pattern="Excel文件 (*.xlsx *.xls);;CSV文件 (*.csv);;所有文件 (*)"
                )
                
                if file_path:
                    ui_controller.show_info(f"选择的文件: {file_path}")
                else:
                    ui_controller.show_info("未选择文件")
            
            # 显示主窗口
            ui_controller.show_main_window()
            
            # 运行应用程序
            ui_controller.run_application()
        else:
            print("应用程序初始化失败")
            
    except Exception as e:
        print(f"示例运行失败: {e}")


if __name__ == "__main__":
    # 运行示例
    example_usage()