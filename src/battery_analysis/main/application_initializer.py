"""
应用程序初始化模块

该模块负责应用程序的初始化、异常处理和错误对话框显示，
避免main函数过于复杂，提高代码的可维护性。
"""

import os
import sys
import logging
from PyQt6.QtWidgets import QApplication, QMessageBox, QStyleFactory
from PyQt6.QtGui import QFont, QFontDatabase

# 获取日志记录器
logger = logging.getLogger(__name__)


class ApplicationInitializer:
    """应用程序初始化器，负责处理应用程序的初始化和异常处理"""
    
    def __init__(self):
        """初始化应用程序初始化器"""
        pass
    
    def _setup_global_exception_handler(self):
        """设置全局异常处理"""
        def handle_exception(exctype, value, traceback):
            """处理全局未捕获异常"""
            if issubclass(exctype, KeyboardInterrupt):
                # 允许KeyboardInterrupt正常退出
                sys.__excepthook__(exctype, value, traceback)
                return
            
            # 记录异常信息
            logger.critical("System crash - uncaught exception:", exc_info=(exctype, value, traceback))
            
            # 尝试生成崩溃报告
            report_path = None
            try:
                from battery_analysis.utils.error_report_generator import generate_error_report
                report_path = generate_error_report(max_logs_per_report=5, max_reports=5)
                if report_path:
                    logger.critical(f"Crash report generated: {report_path}")
            except Exception as e:
                logger.critical(f"Failed to generate crash report: {e}")
            
            # 显示友好的错误对话框
            try:
                # 确保QApplication实例存在
                app = QApplication.instance()
                if app is None:
                    app = QApplication(sys.argv)
                    app.setStyle(QStyleFactory.create("Fusion"))
                
                # 创建错误对话框
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Critical)
                msg_box.setWindowTitle("Application Error")

                # 构建错误信息
                error_msg = f"Sorry, the application encountered a problem.\n\nError: {str(value)}\n\n"
                error_msg += "Details have been logged to the log file."

                if report_path:
                    error_msg += f"\n\nCrash report generated: {report_path}"

                error_msg += "\n\nIt is recommended that you restart the application."
                
                msg_box.setText(error_msg)
                msg_box.setStandardButtons(QMessageBox.StandardButton.Close)
                msg_box.exec()
            except Exception as e:
                logger.critical(f"Failed to show error dialog: {e}")
                # 如果对话框无法显示，至少确保程序不会直接闪退
                print(f"Application error: {str(value)}")
                print("Details have been logged to the log file.")
                if report_path:
                    print(f"Crash report generated: {report_path}")
        
        # 设置全局异常钩子
        sys.excepthook = handle_exception
    
    def _setup_qt_message_handler(self):
        """设置Qt消息处理器"""
        def qt_message_handler(mode, context, message):
            """处理Qt的未处理异常"""
            if mode == QApplication.qtHandlerType.CriticalMsg:
                logger.critical("Qt critical error: %s (file: %s, line: %d)",
                              message, context.file, context.line)
            elif mode == QApplication.qtHandlerType.WarningMsg:
                logger.warning("Qt warning: %s (file: %s, line: %d)",
                            message, context.file, context.line)
            elif mode == QApplication.qtHandlerType.InfoMsg:
                logger.debug("Qt info: %s (file: %s, line: %d)",
                         message, context.file, context.line)
            else:
                logger.debug("Qt debug: %s (file: %s, line: %d)",
                          message, context.file, context.line)
        
        # 设置Qt消息处理器
        QApplication.setApplicationName("Battery Analyzer")
        from battery_analysis.utils.version import Version
        app_version = Version().version
        QApplication.setApplicationVersion(app_version)
    
    def _setup_matplotlib(self):
        """设置matplotlib配置"""
        # 延迟导入matplotlib
        import matplotlib
        
        # 优化matplotlib配置，避免font cache构建警告
        # 使用QtAgg后端，自动检测Qt绑定（兼容PyQt6）
        matplotlib.use('QtAgg')
        from battery_analysis.utils.constants import CN_FONT_LIST
        matplotlib.rcParams['font.family'] = 'sans-serif'
        matplotlib.rcParams['font.sans-serif'] = CN_FONT_LIST
        matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    

    
    def _handle_qt_exception(self, app, e):
        """处理Qt事件循环中的异常"""
        logger.critical("Uncaught exception in Qt event loop:", exc_info=True)

        # 显示错误对话框
        try:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle("Application Error")
            error_msg = f"Sorry, the application encountered a problem.\n\nError: {str(e)}\n\n"
            error_msg += "Details have been logged to the log file.\n\n"
            error_msg += "It is recommended that you restart the application."
            msg_box.setText(error_msg)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Close)
            msg_box.exec()
        except Exception as dialog_error:
            logger.critical(f"Failed to show error dialog: {dialog_error}")
        
        # 确保应用程序可以正常关闭
        app.quit()
    
    def _show_startup_error_dialog(self, e):
        """显示应用程序启动失败对话框"""
        try:
            # 确保QApplication实例存在
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
                app.setStyle(QStyleFactory.create("Fusion"))
            
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle("Application Failed to Start")
            error_msg = f"Sorry, the application could not start.\n\nError: {str(e)}\n\n"
            error_msg += "Details have been logged to the log file.\n\n"
            error_msg += "It is recommended that you restart the application."
            msg_box.setText(error_msg)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Close)
            msg_box.exec()
        except Exception as dialog_error:
            logger.critical(f"Failed to show startup error dialog: {dialog_error}")
            print(f"Application failed to start: {str(e)}")
            print("Details have been logged to the log file.")
    

    
    def initialize(self):
        """执行应用程序初始化"""
        try:
            # 设置全局异常处理
            self._setup_global_exception_handler()
            
            # 设置Qt消息处理器
            self._setup_qt_message_handler()
            
            # 设置matplotlib
            self._setup_matplotlib()
            
            return True
        except Exception as e:
            logger.critical("Application initialization failed:", exc_info=True)
            self._show_startup_error_dialog(e)
            return False
    
    def create_application(self):
        """创建QApplication实例"""
        # 如果QApplication已存在，直接返回现有实例
        app = QApplication.instance()
        if app is not None:
            return app

        # 创建QApplication实例
        app = QApplication(sys.argv)
        # 设置应用程序样式为Fusion，确保在不同Windows版本上表现一致
        app.setStyle(QStyleFactory.create("Fusion"))

        # 设置支持 emoji 的字体
        font = QFont()
        # Windows 系统使用 Segoe UI Emoji 支持 emoji
        font.setFamilies(["Segoe UI", "Segoe UI Emoji", "SimHei", "Microsoft YaHei"])
        app.setFont(font)

        return app
    
    def run_application(self, app, window):
        """运行应用程序事件循环"""
        result = 0
        try:
            # 运行应用程序事件循环，捕获所有异常
            result = app.exec()
        except Exception as e:
            logger.critical("Uncaught exception in application event loop:", exc_info=True)
            self._handle_qt_exception(app, e)
            result = 1
        
        return result
