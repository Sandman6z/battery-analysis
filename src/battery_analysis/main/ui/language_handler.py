"""
语言处理模块

这个模块负责处理主窗口的语言切换、UI文本更新等功能，与语言管理器交互。
"""

import logging
from PyQt6.QtCore import QObject

from battery_analysis.i18n.language_manager import get_language_manager


class LanguageHandler(QObject):
    """
    语言处理类，负责处理主窗口的语言相关功能
    """
    
    def __init__(self, main_window):
        """
        初始化语言处理类
        
        Args:
            main_window: 主窗口实例
        """
        super().__init__()
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        self.language_manager = None
        
        # 连接语言管理器信号
        self._connect_language_signals()
    
    def _connect_language_signals(self):
        """
        连接语言管理器的信号
        """
        try:
            # 初始化语言管理器
            self.language_manager = get_language_manager()
            if self.language_manager:
                self.language_manager.language_changed.connect(self._on_language_changed)
        except (ImportError, AttributeError, TypeError, RuntimeError) as e:
            self.logger.warning("Failed to initialize language manager: %s", e)
    
    def _on_language_changed(self, language_code):
        """
        语言切换处理
        
        Args:
            language_code: 新的语言代码
        """
        window_title = f"Battery Analyzer v{self.main_window.version}"
        self.main_window.setWindowTitle(window_title)
        
        # 更新UI文本
        self.update_ui_texts()
        
        # 更新状态栏消息
        self.update_statusbar_messages()
        
        # 刷新所有对话框
        self.refresh_dialogs()
        
        logging.info("界面语言已切换到: %s", language_code)
    
    def update_ui_texts(self):
        """
        更新UI文本为当前语言
        """
        # 更新进度对话框标题
        if hasattr(self.main_window, 'progress_dialog') and self.main_window.progress_dialog:
            self.main_window.progress_dialog.setWindowTitle(self._("progress_title", "Battery Analysis Progress"))
            self.main_window.progress_dialog.status_label.setText(self._("progress_ready", "Ready to start analysis..."))
    
    def update_statusbar_messages(self):
        """
        更新状态栏消息为当前语言
        """
        # 保存当前消息，以便切换语言后恢复
        if hasattr(self.main_window, 'statusBar_BatteryAnalysis'):
            current_message = self.main_window.statusBar_BatteryAnalysis.currentMessage()
            
            # 获取翻译后的状态消息
            status_ready = self._("status_ready", "状态:就绪")
            
            # 更新状态栏
            if current_message in ("状态:就绪", "Ready"):
                self.main_window.statusBar_BatteryAnalysis.showMessage(status_ready)
    
    def refresh_dialogs(self):
        """
        刷新所有对话框以应用新语言
        """
        # 关闭并重新创建首选项对话框（如果正在显示）
        # 如果需要刷新其他对话框，也在这里处理
        pass
    
    def _(self, text, default=None):
        """
        便捷的翻译方法，使用全局翻译函数
        
        Args:
            text: 要翻译的文本
            default: 默认值，当翻译失败时使用
        
        Returns:
            翻译后的文本
        """
        try:
            from battery_analysis.i18n import _ as gettext_translate
            result = gettext_translate(text)
            return result if result != text or default is None else default
        except (ImportError, AttributeError):
            return default if default is not None else text
    
    def get_current_language(self):
        """
        获取当前语言代码
        
        Returns:
            当前语言代码
        """
        if self.language_manager:
            return self.language_manager.get_current_language()
        return "en"
    
    def set_language(self, language_code):
        """
        设置语言
        
        Args:
            language_code: 要设置的语言代码
        
        Returns:
            是否成功设置语言
        """
        if self.language_manager:
            return self.language_manager.set_language(language_code)
        return False
    
    def get_available_languages(self):
        """
        获取可用的语言列表
        
        Returns:
            可用语言的字典，键为语言代码，值为显示名称
        """
        if self.language_manager:
            return self.language_manager.get_available_languages()
        return {"en": "English"}
    
    def get_installed_languages(self):
        """
        获取已安装的语言列表
        
        Returns:
            已安装语言的字典，键为语言代码，值为显示名称
        """
        if self.language_manager:
            return self.language_manager.get_installed_languages()
        return {"en": "English"}