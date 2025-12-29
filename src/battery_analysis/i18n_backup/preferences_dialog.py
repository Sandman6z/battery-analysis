"""
首选项对话框模块

提供用户界面来配置应用程序首选项，包括：
- 语言选择
- 应用设置
- 首选项保存和恢复
"""

import logging
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, 
    QLabel, QComboBox, QPushButton, QMessageBox,
    QTabWidget, QWidget, QCheckBox, QSpinBox,
    QFormLayout, QDialogButtonBox
)
from battery_analysis.i18n.language_manager import get_language_manager, _


class PreferencesDialog(QDialog):
    """首选项对话框类"""
    
    preferences_applied = pyqtSignal()  # 首选项应用信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.language_manager = get_language_manager()
        
        # 保存原始语言设置
        self.original_language = self.language_manager.get_current_language()
        
        self.init_ui()
        self.load_current_settings()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle(_("preferences", "首选项"))
        self.setModal(True)
        self.resize(400, 300)
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建选项卡控件
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 创建语言选项卡
        self.create_language_tab()
        
        # 创建常规选项卡
        self.create_general_tab()
        
        # 创建按钮框
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Apply,
            Qt.Orientation.Horizontal,
            self
        )
        
        # 连接按钮信号
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        # 为Apply按钮单独连接
        apply_btn = self.button_box.button(QDialogButtonBox.StandardButton.Apply)
        apply_btn.clicked.connect(self.apply_preferences)
        
        main_layout.addWidget(self.button_box)
        
    def create_language_tab(self):
        """创建语言选项卡"""
        language_widget = QWidget()
        layout = QVBoxLayout(language_widget)
        
        # 语言设置组
        language_group = QGroupBox(_("language_settings", "语言设置"))
        language_layout = QFormLayout(language_group)
        
        # 语言选择
        self.language_combo = QComboBox()
        available_languages = self.language_manager.get_available_languages()
        for lang_code, lang_name in available_languages.items():
            self.language_combo.addItem(lang_name, lang_code)
            
        language_layout.addRow(_("select_language", "选择语言:"), self.language_combo)
        
        # 当前语言显示
        current_lang_layout = QHBoxLayout()
        self.current_language_label = QLabel()
        current_lang_layout.addWidget(QLabel(_("current_language", "当前语言:")))
        current_lang_layout.addWidget(self.current_language_label)
        current_lang_layout.addStretch()
        
        language_layout.addRow("", current_lang_layout)
        
        # 语言说明
        language_info = QLabel(_("language_restart_info", 
                               "语言更改将在重启应用程序后生效。"))
        language_info.setWordWrap(True)
        language_layout.addRow("", language_info)
        
        layout.addWidget(language_group)
        layout.addStretch()
        
        # 添加到选项卡
        self.tab_widget.addTab(language_widget, _("language", "语言"))
        
        # 连接语言选择信号
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
        
    def create_general_tab(self):
        """创建常规选项卡"""
        general_widget = QWidget()
        layout = QVBoxLayout(general_widget)
        
        # 界面设置组
        interface_group = QGroupBox(_("interface_settings", "界面设置"))
        interface_layout = QFormLayout(interface_group)
        
        # 自动保存设置
        self.auto_save_checkbox = QCheckBox(_("auto_save_settings", "自动保存设置"))
        interface_layout.addRow("", self.auto_save_checkbox)
        
        # 显示工具提示
        self.show_tooltips_checkbox = QCheckBox(_("show_tooltips", "显示工具提示"))
        interface_layout.addRow("", self.show_tooltips_checkbox)
        
        layout.addWidget(interface_group)
        
        # 行为设置组
        behavior_group = QGroupBox(_("behavior_settings", "行为设置"))
        behavior_layout = QFormLayout(behavior_group)
        
        # 确认对话框
        self.confirm_dialogs_checkbox = QCheckBox(_("confirm_dialogs", "显示确认对话框"))
        behavior_layout.addRow("", self.confirm_dialogs_checkbox)
        
        # 启动when检查更新
        self.check_updates_checkbox = QCheckBox(_("check_updates", "启动when检查更新"))
        behavior_layout.addRow("", self.check_updates_checkbox)
        
        layout.addWidget(behavior_group)
        layout.addStretch()
        
        # 添加到选项卡
        self.tab_widget.addTab(general_widget, _("general", "常规"))
        
    def load_current_settings(self):
        """加载当前设置"""
        # 加载语言设置
        current_language = self.language_manager.get_current_language()
        for i in range(self.language_combo.count()):
            if self.language_combo.itemData(i) == current_language:
                self.language_combo.setCurrentIndex(i)
                break
                
        # 更新当前语言显示
        self.update_current_language_display()
        
        # TODO: 从配置文件加载其他设置
        self.load_general_settings()
        
    def load_general_settings(self):
        """加载常规设置（待实现）"""
        # 这里可以从配置文件加载其他首选项
        # 目前使用默认值
        self.auto_save_checkbox.setChecked(True)
        self.show_tooltips_checkbox.setChecked(True)
        self.confirm_dialogs_checkbox.setChecked(True)
        self.check_updates_checkbox.setChecked(False)
        
    def on_language_changed(self, index):
        """语言选择改变处理"""
        self.update_current_language_display()
        
    def update_current_language_display(self):
        """更新当前语言显示"""
        if self.language_combo.currentData():
            lang_code = self.language_combo.currentData()
            lang_name = self.language_manager.get_language_display_name(lang_code)
            self.current_language_label.setText(lang_name)
            
    def apply_preferences(self):
        """应用首选项"""
        try:
            # 应用语言设置
            selected_language = self.language_combo.currentData()
            if selected_language != self.original_language:
                if self.language_manager.set_language(selected_language):
                    self.logger.info(f"语言已切换到: {selected_language}")
                    # 显示语言切换成功消息
                    QMessageBox.information(
                        self, 
                        _("success", "成功"),
                        _("language_change_restart", "语言已更改。请重启应用程序以使更改生效。")
                    )
                else:
                    QMessageBox.warning(
                        self,
                        _("warning", "警告"),
                        _("language_change_failed", "语言切换失败。")
                    )
                    
            # TODO: 应用其他设置
            self.save_general_settings()
            
            # 发送首选项应用信号
            self.preferences_applied.emit()
            
            self.logger.info("首选项已应用")
            
        except Exception as e:
            self.logger.error(f"应用首选项whenerror occurred: {e}")
            QMessageBox.critical(
                self,
                _("error", "错误"),
                _("apply_preferences_failed", f"应用首选项失败: {str(e)}")
            )
            
    def save_general_settings(self):
        """保存常规设置（待实现）"""
        # 这里可以将设置保存到配置文件
        # 目前只是记录日志
        self.logger.info("常规设置已保存")
        
    def accept(self):
        """确认按钮处理"""
        self.apply_preferences()
        super().accept()
        
    def reject(self):
        """取消按钮处理"""
        # 恢复原始语言设置
        if self.language_manager.get_current_language() != self.original_language:
            self.language_manager.set_language(self.original_language)
        super().reject()
        
    def closeEvent(self, event):
        """关闭事件处理"""
        # 如果对话框被关闭（不是通过按钮），则恢复语言设置
        if self.language_manager.get_current_language() != self.original_language:
            self.language_manager.set_language(self.original_language)
        event.accept()